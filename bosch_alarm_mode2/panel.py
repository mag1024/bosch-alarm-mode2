import asyncio
import ssl
import logging
from datetime import datetime, timedelta

from .const import *
from .connection import Connection

LOG = logging.getLogger(__name__)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT')

def _get_int8(data, offset = 0):
    return int.from_bytes(data[offset:offset+1], 'big')
def _get_int16(data, offset = 0):
    return int.from_bytes(data[offset:offset+2], 'big')

class PanelEntity:
    def __init__(self, name, status):
        self._observer = None
        self.name = name
        self.status = status

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        self._status = value
        self._notify()

    def attach(self, observer): self._observer = observer

    def _notify(self):
        if self._observer: self._observer()


class Area(PanelEntity):
    def __init__(self, name = None, status = AREA_STATUS_UNKNOWN):
        PanelEntity.__init__(self, name, status)

    def __repr__(self):
        return f"{self.name}: {AREA_STATUS[self.status]}"

class Point(PanelEntity):
    def __init__(self, name = None, status = POINT_STATUS_UNKNOWN):
        PanelEntity.__init__(self, name, status)

    def is_open(self) -> bool:
        return self.status == POINT_STATUS_OPEN
    def is_normal(self) -> bool:
        return self.status == POINT_STATUS_NORMAL

    def __repr__(self):
        return f"{self.name}: {POINT_STATUS[self.status]}"

class Panel:
    """ Connection to a Bosch Alarm Panel using the "Mode 2" API. """
    def __init__(self, host, port, passcode):
        LOG.debug("Panel created")
        self._host = host
        self._port = port
        self._passcode = passcode

        self._connection = None
        self._connection_status_observer = None
        self._last_msg = None

        self.model = None
        self.protocol_version = None
        self.serial_number = None
        self.areas = {}
        self.points = {}

    LOAD_BASIC_INFO = 1 << 0
    LOAD_ENTITIES = 1 << 1
    LOAD_STATUS = 1 << 2
    LOAD_ALL = LOAD_BASIC_INFO | LOAD_ENTITIES | LOAD_STATUS

    async def connect(self, load_selector = LOAD_ALL):
        loop = asyncio.get_running_loop()
        self._monitor_connection_task = loop.create_task(self._monitor_connection())
        await self._connect(load_selector)

    async def load(self, load_selector):
        if load_selector & self.LOAD_BASIC_INFO:
            await self._basicinfo()
        if load_selector & self.LOAD_ENTITIES:
            await asyncio.gather(self._load_areas(), self._load_points())
        if load_selector & self.LOAD_STATUS:
            await asyncio.gather(
                    self._load_entity_status(CMD.AREA_STATUS, self.areas),
                    self._load_entity_status(CMD.POINT_STATUS, self.points))
            await self._subscribe()

    async def disconnect(self):
        if self._monitor_connection_task:
            self._monitor_connection_task.cancel()
            try:
                await self._monitor_connection_task
            except asyncio.CancelledError:
                pass
            finally:
                self._monitor_connection_task = None
        if self._connection: self._connection.close()

    def connection_status(self) -> bool:
        return self._connection != None and self.points and self.areas

    def connection_status_attach(self, observer):
        self._connection_status_observer = observer

    def print(self):
        if self.model: print('Model:', self.model)
        if self.protocol_version: print('Protocol version:',
                self.protocol_version)
        if self.serial_number: print('Serial number:', self.serial_number)
        if self.areas:
            print('Areas:')
            print(self.areas)
        if self.points:
            print('Points:')
            print(self.points)

    async def _connect(self, load_selector):
        LOG.info('Connecting to %s:%d...', self._host, self._port)
        connection_factory = lambda: Connection(
                self._passcode, self._on_status_update, self._on_disconnect)
        transport, connection = await asyncio.wait_for(
                asyncio.get_running_loop().create_connection(
                    connection_factory,
                    host=self._host, port=self._port, ssl=ssl_context),
                timeout=10)
        self._last_msg = datetime.now()
        self._connection = connection
        await self._authenticate()
        await self.load(load_selector)
        self._connection_status_notify()

    def _on_disconnect(self):
        self._connection = None
        self._last_msg = None
        for a in self.areas.values(): a.state = AREA_STATUS_UNKNOWN
        for p in self.points.values(): p.state = POINT_STATUS_UNKNOWN
        self._connection_status_notify()

    async def _monitor_connection(self):
        while True:
            try:
                await asyncio.sleep(30)
                await self._monitor_connection_once()
            except asyncio.exceptions.CancelledError:
                raise
            except:
                logging.exception("Connection monitor exception")

    async def _monitor_connection_once(self):
        if self._connection:
            idle_time = datetime.now() - (self._last_msg or datetime.fromtimestamp(0))
            if idle_time > timedelta(minutes=3):
                LOG.warning("Heartbeat expired (%s): resetting connection.", idle_time)
                self._connection.close()
        else:
            loaded = self.areas and self.points
            load_selector = self.LOAD_STATUS if loaded else self.LOAD_ALL
            try:
                await self._connect(load_selector)
            except asyncio.exceptions.TimeoutError as e:
                LOG.debug("Connection timed out...")

    def _connection_status_notify(self):
        if self._connection_status_observer: self._connection_status_observer()

    async def _authenticate(self):
        creds = bytearray(b'\x01')  # automation user
        creds.extend(map(ord, self._passcode))
        creds.append(0x00); # null terminate
        result = await self._connection.send_command(CMD.AUTHENTICATE, creds)
        if result != b'\x01':
            self._connection.close()
            error = ["Not Authorized", "Authorized", "Max Connections"][result[0]]
            raise PermissionError("Authentication failed: " + error)
        LOG.debug("Authentication success!")

    async def _basicinfo(self):
        data = await self._connection.send_command(CMD.WHAT_ARE_YOU)
        self.model = PANEL_MODEL[data[0]]
        self.protocol_version = 'v%d.%d' % (data[5], data[6])
        if data[13]: LOG.warning('busy flag: %d', data[13])

        data = await self._connection.send_command(
                CMD.PRODUCT_SERIAL, b'\x00\x00')
        self.serial_number = int.from_bytes(data[0:6], 'big')

    async def _load_areas(self):
        names = await self._load_names(CMD.AREA_TEXT)
        self.areas = {id: Area(name) for id, name in names.items()}

    async def _load_points(self):
        names = await self._load_names(CMD.POINT_TEXT)
        self.points = {id: Point(name) for id, name in names.items()}

    async def _load_names(self, name_cmd) -> dict[int, str]:
        names = {}
        id = 0
        while True:
            request = bytearray(id.to_bytes(2, 'big'))
            request.append(0x00)  # primary language
            request.append(0x01)  # return many
            data = await self._connection.send_command(name_cmd, request)
            if not data: break
            while data:
                id = _get_int16(data)
                name, data = data[2:].split(b'\x00', 1)
                names[id] = name.decode('ascii')
        return names

    async def _load_entity_status(self, status_cmd, entities):
        request = bytearray()
        for id in entities.keys(): request.extend(id.to_bytes(2, 'big'))
        response = await self._connection.send_command(status_cmd, request)
        while response:
            entities[_get_int16(response)].status = response[2]
            response = response[3:]

    async def _subscribe(self):
        IGNORE = bytearray(b'\x00')
        SUBSCRIBE = bytearray(b'\x01')
        data = bytearray(b'\x01') # format
        data += SUBSCRIBE # confidence / heartbeat
        data += IGNORE    # event mem
        data += IGNORE    # event log
        data += IGNORE    # config change
        data += IGNORE    # area on/off
        data += SUBSCRIBE # area ready
        data += IGNORE    # output status
        data += SUBSCRIBE # point status
        data += IGNORE    # door status
        data += IGNORE    # unused
        await self._connection.send_command(CMD.SET_SUBSCRIPTION, data)

    def _area_status_consumer(self, data) -> int:
        area = _get_int16(data)
        ready_status = ["Not", "Part", "Full"][data[2]]
        faults = _get_int16(data, 3)
        LOG.debug("Area %d: %s Ready (%d faults)" % (area, ready_status, faults))
        return 5

    def _point_status_consumer(self, data) -> int:
        point = _get_int16(data)
        self.points[point].status = data[2]
        LOG.debug("Point updated: %s", self.points[point])
        return 3

    def _on_status_update(self, data):
        CONSUMERS = {
            0x00: lambda data: 0,  # heartbeat
            0x05: self._area_status_consumer,
            0x07: self._point_status_consumer,
        }
        pos = 0
        while pos < len(data):
            (update_type, n_updates) = data[pos:pos+2]
            pos += 2
            self._last_msg = datetime.now()
            consumer = CONSUMERS[update_type]
            for i in range(0, n_updates): pos += consumer(data[pos:])
