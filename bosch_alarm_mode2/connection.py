import asyncio
import logging
import binascii
from datetime import datetime

from collections import deque

from .const import ERROR, PROTOCOL
from .utils import BE_INT

LOG = logging.getLogger(__name__)

class Connection(asyncio.Protocol):
    def __init__(self, passcode, on_status_update, on_disconnect):
        self.protocol = PROTOCOL.BASIC
        self._passcode = passcode
        self._on_status_update = on_status_update
        self._on_disconnect = on_disconnect
        self._transport = None
        self._buffer = bytearray()
        self._pending = deque()
        self._pending_last_empty = datetime.now()
        self.set_max_commands_in_flight(1)

    def set_max_commands_in_flight(self, command_count):
        self._command_semaphore = asyncio.Semaphore(command_count)

    def connection_made(self, transport):
        self._transport = transport

    def connection_lost(self, exc):
        LOG.info("Connection terminated.")
        self._on_disconnect()

    def data_received(self, data):
        LOG.debug("<< %s", binascii.hexlify(data))
        self._buffer += data
        self._consume_buffer()

    async def send_command(self, code, data = bytearray()) -> bytearray:
        # Some panels don't like receiving multiple commands at once 
        # so we limit the amount of commands that are in flight at a given time
        async with self._command_semaphore:
            request = bytearray([self.protocol])
            length_size = 2 if self.protocol == PROTOCOL.EXTENDED else 1
            request.extend((len(data) + 1).to_bytes(length_size, 'big'))
            request.append(code)
            request.extend(data)
            LOG.debug(">> %s", binascii.hexlify(request))
            response = asyncio.get_running_loop().create_future()
            self._pending.append(response)
            self._transport.write(request)
            return await response

    def close(self):
        if self._transport:
            self._transport.abort()
            self._transport = None

    @property
    def pending_last_empty(self) -> datetime:
        return self._pending_last_empty if len(self._pending) else datetime.now()

    def _consume_buffer(self):
        while self._buffer:
            msg_len = 0
            if self._buffer[0] == 0x01:
                msg_len = self._buffer[1] + 2
                if len(self._buffer) < msg_len: break
                self._process_response(self._buffer[2:msg_len])
            elif self._buffer[0] == 0x02:
                msg_len = BE_INT.int16(self._buffer, 1) + 3
                if len(self._buffer) < msg_len: break
                self._on_status_update(self._buffer[3:msg_len])
            elif self._buffer[0] == 0x04:
                msg_len = BE_INT.int16(self._buffer, 1) + 3
                if len(self._buffer) < msg_len: break
                self._process_response(self._buffer[3:msg_len])
            else:
                raise RuntimeError('unknown protocol ' + str(self._buffer))
            self._buffer = self._buffer[msg_len:]

    def _process_response(self, data):
        response = self._pending.popleft()
        if len(self._pending) == 0: self._pending_last_empty = datetime.now()
        if data[0] == 0xFC: response.set_result(None)
        elif data[0] == 0xFD: response.set_exception(Exception("NACK: ", ERROR[data[1]]))
        elif data[0] == 0xFE: response.set_result(data[1:])
        else: response.set_exception(Exception("unexpected response code:", data))
