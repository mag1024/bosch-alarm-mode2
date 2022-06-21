import asyncio
import ssl

from .const import *

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT')

def _mask_to_indeces(bytes):
    as_bits = ''.join(format(byte, '08b') for byte in bytes)
    return [i + 1 for i, c in enumerate(as_bits) if c == '1']

class Connection(asyncio.Protocol):
    def __init__(self, passcode, ready_cb, state_cb):
        self._passcode = passcode
        self._ready_cb = ready_cb
        self._state_cb = state_cb
        self._transport = None
        self.on_disconnect = asyncio.get_running_loop().create_future()
        self._buffer = bytearray()
        self._pending = asyncio.Queue()

    def connection_made(self, transport):
        print("ready callback")
        self._transport = transport
        asyncio.ensure_future(self._authenticate())

    def connection_lost(self, exc):
        print("disconnected callback")
        self.on_disconnect.set_result(True)

    def data_received(self, data):
        print("<<", data)
        self._buffer += data
        self._consume_buffer()

    def send_command(self, code, data = bytearray()):
        request = bytearray(b'\x01')  # protocol version
        request.append(len(data) + 1)
        request.append(code)
        request.extend(data)
        response = asyncio.get_running_loop().create_future()
        self._pending.put_nowait(response)
        print(">>", bytes(request))
        self._transport.write(request)
        return response

    async def _authenticate(self):
        creds = bytearray(b'\x01')  # automation user
        creds.extend(map(ord, self._passcode))
        creds.append(0x00); # null terminate
        result = await self.send_command(0x06, creds)
        if result == b'\x01':
            print("Authentication success!")
            await self._ready_cb()
        else:
            print("Authentication failed:",
                    ["Not Authorized", "Authorized", "Max Connections"][result])
            self._transport.close()

    def _consume_buffer(self):
        while self._buffer:
            msg_len = 0
            match self._buffer[0]:
                case 0x01:
                    msg_len = self._buffer[1] + 2
                    if len(self._buffer) < msg_len: break
                    self._process_response(self._buffer[2:msg_len])
                case 0x02:
                    msg_len = int.from_bytes(self._buffer[1:3], 'big') + 3
                    if len(self._buffer) < msg_len: break
                    self._state_cb(self._buffer[3:msg_len])
                case _:
                    raise RuntimeError('unknown protocol ' + str(self._buffer))
            self._buffer = self._buffer[msg_len:]
  
    def _process_response(self, data):
      response = self._pending.get_nowait()
      match data[0]:
          case 0xFC: response.set_result(None)
          case 0xFD:
              response.set_exception(Exception("NACK: %s" % ERROR[data[1]]))
          case 0xFE:
              response.set_result(data[1:])
          case _:
              response.set_exception(Exception("unexpected response code:", data))

class Area:
    def __init__(self, name = None, status = AREA_STATUS_UNKNOWN):
        self.name = name
        self.status = status
    
    def __repr__(self):
        return f"{self.name}: {AREA_STATUS[self.status]}"

class Point:
    def __init__(self, name = None, status = POINT_STATUS_UNKNOWN):
        self.name = name
        self.status = status
    
    def __repr__(self):
        return f"{self.name}: {POINT_STATUS[self.status]}"

class Panel:
    """ Connection to a Bosch Alarm Panel using the "Mode 2" API. """
    def __init__(self, host, port, passcode):
        self._host = host
        self._port = port
        self._passcode = passcode
        self.model = None
        self.protocol_version = None
        self.areas = {}
        self.points = {}

    def run(self):
        """ Initiates operation inside an already established asyncio loop """
        asyncio.ensure_future(self._maintain_connection())

    def run_and_loop(self):
        """ Establishes a new asyncio loop, and initiates operation,
            and runs for ever. """
        asyncio.run(self._maintain_connection())

    def print(self):
        if self.model: print('Model:', self.model)
        if self.protocol_version: print('Protocol version:',
                self.protocol_version)
        if self.areas:
            print('Areas:')
            print(self.areas)
        if self.points:
            print('Points:')
            print(self.points)

    async def _maintain_connection(self):
        while True:
            print('Reconnecting to %s:%d...' % (self._host, self._port))
            try:
                self._connection = None
                connection_factory = lambda: Connection(
                        self._passcode, self._ready, self._state_update)
                transport, connection = await asyncio.wait_for(
                        asyncio.get_running_loop().create_connection(
                            connection_factory,
                            host=self._host, port=self._port, ssl=ssl_context),
                        timeout=5)
                self._connection = connection
                await connection.on_disconnect
            except Exception as e:
                print(e)
                await asyncio.sleep(10)

    async def _ready(self):
        print('Panel connection is ready!')
        await asyncio.gather(
                self._whatareyou(),
                self._loadareas(),
                self._loadpoints(),
                )
        await self._subscribe()
        self.print()

    async def _whatareyou(self):
        data = await self._connection.send_command(CMD.WHAT_ARE_YOU)
        self.model = PANEL_MODEL[data[0]]
        self.protocol_version = 'v%d.%d' % (data[5], data[6])
        if data[13]: print ('Busy: %d' % data[13])

    async def _loadareas(self):
        self.areas = {}
        for id, name, status in await self._load_id_name_status(
                CMD.CONFIGURED_AREAS, CMD.AREA_STATUS, CMD.AREA_TEXT):
            self.areas[id] = Area(name, status)

    async def _loadpoints(self):
        self.points = {}
        for id, name, status in await self._load_id_name_status(
                CMD.CONFIGURED_POINTS, CMD.POINT_STATUS, CMD.POINT_TEXT):
            self.points[id] = Point(name, status)

    async def _load_id_name_status(self, list_cmd, status_cmd, name_cmd):
        output = []
        data = await self._connection.send_command(list_cmd)
        for id in _mask_to_indeces(data):
            id_bytes = id.to_bytes(2, 'big')
            name_request = bytearray(id_bytes)
            name_request.append(0x00)  # primary language
            name_future = self._connection.send_command(name_cmd, name_request)
            status_response = await self._connection.send_command(status_cmd, id_bytes)
            name_response = await name_future
            output.append((
                id, name_response[0:-1].decode('ascii'), status_response[2]))
        return output

    async def _subscribe(self):
        kIgnore = bytearray(b'\x00')
        kSubscribe = bytearray(b'\x01')
        data = bytearray(b'\x01') # format
        data += kIgnore    # confidence / heartbeat
        data += kIgnore    # event mem
        data += kIgnore    # event log
        data += kIgnore    # config change
        data += kSubscribe # area on/off
        data += kSubscribe # area ready
        data += kIgnore    # output state
        data += kSubscribe # point state
        data += kSubscribe # door state
        data += kIgnore    # unused
        await self._connection.send_command(CMD.SET_SUBSCRIPTION, data)

    def _state_update(self, data):
        if data[0] == 0x07: # point state
            point = int.from_bytes(data[2:4], 'big')
            self.points[point].status = data[4]
            print("Point updated:", self.points[point])
        else:
            print("Unhandled state update", data[0])
