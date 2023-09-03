import asyncio
import logging
import ssl
import time
from datetime import datetime, timedelta

from .const import *
from .connection import Connection
from .history import History, HistoryEvent
from .utils import BE_INT, Observable

LOG = logging.getLogger(__name__)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT')
class PanelEntity:
    def __init__(self, name, status):
        self.name = name
        self.status_observer = Observable()
        self.status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.status_observer._notify()

class Area(PanelEntity):
    def __init__(self, name = None, status = AREA_STATUS.UNKNOWN):
        PanelEntity.__init__(self, name, status)
        self.ready_observer = Observable()
        self.alarm_observer = Observable()
        self._set_ready(AREA_READY_NOT, 0)
        self._alarms = set()

    @property
    def all_ready(self): return self._ready == AREA_READY_ALL
    @property
    def part_ready(self): return self._ready == AREA_READY_PART
    @property
    def faults(self): return self._faults
    @property
    def alarms(self): return [ALARM_MEMORY_PRIORITIES[x] for x in self._alarms]

    def _set_ready(self, ready, faults):
        self._ready = ready
        self._faults = faults
        self.ready_observer._notify()

    def _set_alarm(self, priority, state):
        if state:
            self._alarms.add(priority)
        else:
            self._alarms.discard(priority)
        self.alarm_observer._notify()

    def is_disarmed(self):
        return self.status == AREA_STATUS.DISARMED
    def is_arming(self):
        return self.status in AREA_STATUS.ARMING
    def is_pending(self):
        return self.status in AREA_STATUS.PENDING
    def is_part_armed(self):
        return self.status in AREA_STATUS.PART_ARMED
    def is_all_armed(self):
        return self.status in AREA_STATUS.ALL_ARMED
    def is_armed(self):
        return self.status in AREA_STATUS.ARMED
    def is_triggered(self):
        return self.is_armed() and self._alarms.intersection(ALARM_MEMORY_PRIORITY_ALARMS)

    def reset(self):
        self.status = AREA_STATUS.UNKNOWN
        self._set_ready(AREA_READY_NOT, 0)
        self._alarms = set()

    def __repr__(self):
        return "%s: %s [%s] (%d)" % (
            self.name, AREA_STATUS.TEXT[self.status],
            AREA_READY[self._ready], self._faults)

class Point(PanelEntity):
    def __init__(self, name = None, status = POINT_STATUS.UNKNOWN):
        PanelEntity.__init__(self, name, status)

    def is_open(self) -> bool:
        return self.status in POINT_STATUS.OPEN

    def is_normal(self) -> bool:
        return self.status == POINT_STATUS.NORMAL

    def reset(self):
        self.status = POINT_STATUS.UNKNOWN

    def __repr__(self):
        return f"{self.name}: {POINT_STATUS.TEXT[self.status]}"

class Panel:
    """ Connection to a Bosch Alarm Panel using the "Mode 2" API. """

    def __init__(self, host, port, passcode):
        LOG.debug("Panel created")
        self._host = host
        self._port = port
        self._passcode = passcode

        self.connection_status_observer = Observable()
        self.history_observer = Observable()
        self._connection = None
        self._monitor_connection_task = None
        self._last_msg = None
        self._poll_task = None

        self.model = None
        self.protocol_version = None
        self.serial_number = None
        self._history = History()
        self._history_cmd = None
        self.areas = {}
        self.points = {}
        self._partial_arming_id = AREA_ARMING_PERIMETER_DELAY
        self._all_arming_id = AREA_ARMING_MASTER_DELAY
        self._supports_subscriptions = False
        self._supports_command_request_area_text_cf01 = False
        self._supports_command_request_area_text_cf03 = False

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
            await self._load_areas()
            await self._load_points()
        if load_selector & self.LOAD_STATUS:
            await self._load_entity_status(CMD.AREA_STATUS, self.areas)
            await self._load_entity_status(CMD.POINT_STATUS, self.points)
            await self._load_history()
            if self._supports_subscriptions:
                await self._subscribe()
            else:
                loop = asyncio.get_running_loop()
                self._poll_task = loop.create_task(self._poll())
                LOG.info(
                    "Panel does not support subscriptions, falling back to polling")

    @property
    def events(self) -> list[HistoryEvent]:
        return self._history.events

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

    async def area_disarm(self, area_id):
        await self._area_arm(area_id, AREA_ARMING_DISARM)

    async def area_arm_part(self, area_id):
        await self._area_arm(area_id, self._partial_arming_id)

    async def area_arm_all(self, area_id):
        await self._area_arm(area_id, self._all_arming_id)

    def connection_status(self) -> bool:
        return self._connection is not None and self.points and self.areas

    def print(self):
        if self.model: print('Model:', self.model)
        if self.protocol_version: print('Protocol version:', self.protocol_version)
        if self.serial_number: print('Serial number:', self.serial_number)
        if self.areas:
            print('Areas:')
            print(self.areas)
        if self.points:
            print('Points:')
            print(self.points)
        if self.events:
            print('Events:')
            print(*self.events, sep="\n")

    async def _connect(self, load_selector):
        LOG.info('Connecting to %s:%d...', self._host, self._port)
        def connection_factory(): return Connection(
                self._passcode, self._on_status_update, self._on_disconnect)
        _, connection = await asyncio.wait_for(
                asyncio.get_running_loop().create_connection(
                    connection_factory,
                    host=self._host, port=self._port, ssl=ssl_context),
                timeout=10)
        self._last_msg = datetime.now()
        self._connection = connection
        await self._authenticate()
        LOG.debug("Authentication success!")
        await self.load(load_selector)
        self.connection_status_observer._notify()

    def _on_disconnect(self):
        self._connection = None
        self._last_msg = None
        for a in self.areas.values():
            a.reset()
        for p in self.points.values():
            p.reset()
        self.connection_status_observer._notify()
        if self._poll_task:
            self._poll_task.cancel()
            self._poll_task = None

    async def _load_history(self):
        # Don't retrieve history when armed, as panels do not support this.
        if any(area.is_armed() for area in self.areas):
            return
        start_size = len(self.events)
        start_t = time.perf_counter()
        event_id = self._history.last_event_id
        while event_id is not None:
            request = bytearray(b'\xFF')
            request.extend(event_id.to_bytes(4, 'big'))
            data = await self._connection.send_command(self._history_cmd, request)
            self._last_msg = datetime.now()
            if (event_id := self._history.parse_polled_events(data)):
                self.history_observer._notify()
        if len(self.events) != start_size:
            LOG.debug("Loaded %d history events in %.2fs" % (
                len(self.events) - start_size, time.perf_counter() - start_t))

    async def _monitor_connection(self):
        while True:
            try:
                await asyncio.sleep(30)
                await self._monitor_connection_once()
            except asyncio.exceptions.CancelledError:
                raise
            except:
                logging.exception("Connection monitor exception")

    async def _poll(self):
        while True:
            try:
                await asyncio.sleep(1)
                await self._load_entity_status(CMD.AREA_STATUS, self.areas)
                await self._load_entity_status(CMD.POINT_STATUS, self.points)
                await self._get_alarm_status()
                await self._load_history()
                self._last_msg = datetime.now()
            except asyncio.exceptions.CancelledError:
                raise
            except:
                logging.exception("Polling exception")

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

    async def _login_remote_user(self):
        creds = int(str(self._passcode).ljust(8, "F"), 16)
        creds = creds.to_bytes(4, "big")
        await self._connection.send_command(CMD.LOGIN_REMOTE_USER, creds)

    async def _authenticate(self):
        creds = bytearray(b'\x01')  # automation user
        creds.extend(map(ord, self._passcode))
        creds.append(0x00) # null terminate
        result = await self._connection.send_command(CMD.AUTHENTICATE, creds)
        if result and result[0] == 0x01:
            return

        # Fallback on user authentication
        if self._passcode.isnumeric():
            LOG.info("Authentication failed, trying remote user")
            try:
                await self._login_remote_user()
                return
            except Exception:
                pass

        self._connection.close()
        error = ["Not Authorized", "Authorized",
                "Max Connections"][result[0] if result else 0]
        raise PermissionError("Authentication failed: " + error)

    async def _basicinfo(self):
        try:
            data = await self._connection.send_command(CMD.WHAT_ARE_YOU, bytearray([3]))
        except Exception:
            # If the panel doesn't support CF03, then use CF01
            data = await self._connection.send_command(CMD.WHAT_ARE_YOU)
        self.model = PANEL_MODEL[data[0]]
        self.protocol_version = 'v%d.%d' % (data[5], data[6])
        if data[13]:
            LOG.warning('busy flag: %d', data[13])
        # Solution and AMAX panels use different arming types from B/G series panels.
        if data[0] <= 0x24:
            self._partial_arming_id = AREA_ARMING_STAY1
            self._all_arming_id = AREA_ARMING_AWAY
        else:
            self._partial_arming_id = AREA_ARMING_PERIMETER_DELAY
            self._all_arming_id = AREA_ARMING_MASTER_DELAY
        # Section 13.2 of the protocol spec.
        bitmask = data[23:].ljust(33, b'\0')
        if bitmask[0] & 0x10:
            self._connection.protocol = PROTOCOL.EXTENDED
        self._supports_subscriptions = bitmask[0] & 0x40
        self._supports_command_request_area_text_cf01 = bitmask[7] & 0x20
        self._supports_command_request_area_text_cf03 = bitmask[7] & 0x08
        self._history.init_for_panel(data[0])
        self._history_cmd = (
                CMD.REQUEST_RAW_HISTORY_EVENTS_EXT if bitmask[16] & 0x02 else
                CMD.REQUEST_RAW_HISTORY_EVENTS)
        if bitmask[13] & 0x04:  # supports serial read
            data = await self._connection.send_command(
                CMD.PRODUCT_SERIAL, b'\x00\x00')
            self.serial_number = int.from_bytes(data[0:6], 'big')

    async def _load_areas(self):
        names = await self._load_names(CMD.AREA_TEXT, CMD.REQUEST_CONFIGURED_AREAS, "AREA")
        self.areas = {id: Area(name) for id, name in names.items()}

    async def _load_points(self):
        names = await self._load_names(CMD.POINT_TEXT, CMD.REQUEST_CONFIGURED_POINTS, "POINT")
        self.points = {id: Point(name) for id, name in names.items()}

    async def _load_names_cf03(self, name_cmd, names) -> dict[int, str]:
        id = 0
        while True:
            request = bytearray(id.to_bytes(2, 'big'))
            request.append(0x00)  # primary language
            request.append(0x01)  # return many
            data = await self._connection.send_command(name_cmd, request)
            if not data: break
            while data:
                id = BE_INT.int16(data)
                name, data = data[2:].split(b'\x00', 1)
                if id in names:
                    names[id] = name.decode('ascii')
        return names

    async def _load_names_cf01(self, name_cmd, names) -> dict[int, str]:
        for id in names.keys():
            request = bytearray(id.to_bytes(2, 'big'))
            request.append(0x00)  # primary language
            data = await self._connection.send_command(name_cmd, request)
            name = data.split(b'\x00', 1)[0]
            names[id] = name.decode('ascii')
        return names

    async def _load_enabled_entities(self, config_cmd, type) -> dict[int, str]:
        data = await self._connection.send_command(config_cmd)
        names = {}
        index = 0
        while data:
            b = data.pop(0)
            for i in range(8):
                id = index + (8 - i)
                if b & 1 != 0:
                    names[id] = f"{type}{id}"
                b >>= 1
            index += 8
        return names

    async def _load_names(self, name_cmd, config_cmd, type) -> dict[int, str]:
        names = await self._load_enabled_entities(config_cmd, type)

        if self._supports_command_request_area_text_cf03:
            return await self._load_names_cf03(name_cmd, names)

        if self._supports_command_request_area_text_cf01:
            return await self._load_names_cf01(name_cmd, names)

        # And then if CF01 isn't available, we can just return a list of names
        return names

    async def _get_alarms_for_priority(self, priority, last_area=None, last_point=None):
        request = bytearray([priority])
        if last_area and last_point:
            request.append(last_area.to_bytes(2, 'big'))
            request.append(last_point.to_bytes(2, 'big'))
        response_detail = await self._connection.send_command(CMD.ALARM_MEMORY_DETAIL, request)
        while response_detail:
            area = BE_INT.int16(response_detail)
            # item_type = response_detail[2]
            point = BE_INT.int16(response_detail, 3)
            if point == 0xFFFF:
                await self._get_alarms_for_priority(priority, area, point)
            if area in self.areas:
                self.areas[area]._set_alarm(priority, True)
            else:
                LOG.warning(
                    f"Found unknown area {area}, supported areas: [{self.areas.keys()}]")
            response_detail = response_detail[5:]

    async def _get_alarm_status(self):
        data = await self._connection.send_command(CMD.ALARM_MEMORY_SUMMARY)
        for priority in ALARM_MEMORY_PRIORITIES.keys():
            i = (priority - 1) * 2
            count = BE_INT.int16(data, i)
            if count:
                await self._get_alarms_for_priority(priority)
            else:
                # Nothing triggered, clear alarms
                for area in self.areas.values():
                    area._set_alarm(priority, False)

    async def _load_entity_status(self, status_cmd, entities):
        request = bytearray()
        for id in entities.keys(): request.extend(id.to_bytes(2, 'big'))
        response = await self._connection.send_command(status_cmd, request)
        while response:
            entities[BE_INT.int16(response)].status = response[2]
            response = response[3:]

    async def _area_arm(self, area_id, arm_type):
        request = bytearray([arm_type])
        # bitmask with only i-th bit from the left being 1 (section 3.1.4)
        request.extend(bytearray((area_id-1)//8)) # leading 0 bytes
        request.append(1 << (7-((area_id-1) % 8))) # i%8-th bit from the left (top) set
        await self._connection.send_command(CMD.AREA_ARM, request)

    async def _subscribe(self):
        IGNORE = b'\x00'
        SUBSCRIBE = b'\x01'
        data = bytearray(b'\x01') # format
        data += SUBSCRIBE # confidence / heartbeat
        data += SUBSCRIBE # event mem
        data += SUBSCRIBE # event log
        data += IGNORE    # config change
        data += SUBSCRIBE # area on/off
        data += SUBSCRIBE # area ready
        data += IGNORE    # output status
        data += SUBSCRIBE # point status
        data += IGNORE    # door status
        data += IGNORE    # unused
        await self._connection.send_command(CMD.SET_SUBSCRIPTION, data)

    def _area_on_off_consumer(self, data) -> int:
        area_id = BE_INT.int16(data)
        area_status = self.areas[area_id].status = data[2]
        LOG.debug("Area %d: %s" % (area_id, AREA_STATUS.TEXT[area_status]))
        # Retrieve panel history, as it is possible that a panel may have been armed during 
        # initialisation, and history can not be retrived when a panel is armed.
        asyncio.create_task(self._load_history())
        return 3

    def _area_ready_consumer(self, data) -> int:
        area_id = BE_INT.int16(data)
        # Skip message if it is for an unconfigured area
        if area_id not in self.areas:
            return 5
        ready_status = data[2]
        faults = BE_INT.int16(data, 3)
        self.areas[area_id]._set_ready(ready_status, faults)
        LOG.debug("Area %d: %s (%d faults)" % (
            area_id, AREA_READY[ready_status], faults))
        return 5

    def _point_status_consumer(self, data) -> int:
        point_id = BE_INT.int16(data)
        self.points[point_id].status = data[2]
        LOG.debug("Point updated: %s", self.points[point_id])
        return 3

    def _event_summary_consumer(self, data) -> int:
        priority = data[0]
        count = BE_INT.int16(data, 1)
        if count:
            asyncio.create_task(self._get_alarms_for_priority(priority))
        else:
            # Alarms are no longer triggered, clear
            for area in self.areas.values():
                area._set_alarm(priority, False)
        return 3

    def _event_history_consumer(self, data) -> int:
        r = self._history.parse_subscription_event(data)
        self.history_observer._notify()
        return r

    def _on_status_update(self, data):
        CONSUMERS = {
            0x00: lambda data: 0,  # heartbeat
            0x01: self._event_summary_consumer,
            0x02: self._event_history_consumer,
            0x04: self._area_on_off_consumer,
            0x05: self._area_ready_consumer,
            0x07: self._point_status_consumer,
        }
        pos = 0
        while pos < len(data):
            (update_type, n_updates) = data[pos:pos+2]
            pos += 2
            self._last_msg = datetime.now()
            consumer = CONSUMERS[update_type]
            for _ in range(0, n_updates): pos += consumer(data[pos:])
