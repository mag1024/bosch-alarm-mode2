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

class Observable:
    def __init__(self):
        self._observers = []

    def attach(self, observer): self._observers.append(observer)
    def detach(self, observer): self._observers.remove(observer)

    def _notify(self):
        for observer in self._observers: observer()

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
    def __init__(self, name = None, status = AREA_STATUS_UNKNOWN):
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
        return self.status == AREA_STATUS_DISARMED
    def is_arming(self):
        return self.status in AREA_STATUS_ARMING
    def is_pending(self):
        return self.status in AREA_STATUS_PENDING
    def is_part_armed(self):
        return self.status in AREA_STATUS_PART_ARMED
    def is_all_armed(self):
        return self.status in AREA_STATUS_ALL_ARMED
    def is_triggered(self):
        return (self.is_part_armed() or self.is_all_armed()) and self._alarms.intersection(ALARM_MEMORY_PRIORITY_ALARMS)

    def reset(self):
        self.status = AREA_STATUS_UNKNOWN
        self._set_ready(AREA_READY_NOT, 0)
        self._alarms = set()

    def __repr__(self):
        return "%s: %s [%s] (%d)" % (
            self.name, AREA_STATUS[self.status],
            AREA_READY[self._ready], self._faults)

class Point(PanelEntity):
    def __init__(self, name = None, status = POINT_STATUS_UNKNOWN):
        PanelEntity.__init__(self, name, status)

    def is_open(self) -> bool:
        return self.status == POINT_STATUS_OPEN
    def is_normal(self) -> bool:
        return self.status == POINT_STATUS_NORMAL

    def reset(self):
        self.status = POINT_STATUS_UNKNOWN

    def __repr__(self):
        return f"{self.name}: {POINT_STATUS[self.status]}"

class Panel:
    """ Connection to a Bosch Alarm Panel using the "Mode 2" API. """
    def __init__(self, host, port, passcode, arming_code=None):
        LOG.debug("Panel created")
        self._host = host
        self._port = port
        self._passcode = passcode
        self._arming_code=arming_code

        self.connection_status_observer = Observable()
        self._connection = None
        self._last_msg = None
        self._poll_task = None

        self.model = None
        self.protocol_version = None
        self.serial_number = None
        self.areas = {}
        self.points = {}
        self._part_arming_type = AREA_ARMING_PERIMETER_DELAY
        self._all_arming_type = AREA_ARMING_MASTER_DELAY
        self._featureProtocol02 = False
        self._featureCommandRequestAreaTextCF03 = False

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
            if self._featureProtocol02:
                await self._subscribe()
            else:
                loop = asyncio.get_running_loop()
                self._poll_task = loop.create_task(self._poll())
                print("Panel does not support subscriptions, falling back to polling")


    async def disconnect(self):
        if self._monitor_connection_task:
            self._monitor_connection_task.cancel()
            try:
                await self._monitor_connection_task
            except asyncio.CancelledError:
                pass
            finally:
                self._monitor_connection_task = None
        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            finally:
                self._poll_task = None
        if self._connection: self._connection.close()

    async def area_disarm(self, area_id, code):
        await self._area_arm(area_id, AREA_ARMING_DISARM, code)
    async def area_arm_part(self, area_id, code):
        await self._area_arm(area_id, self._part_arming_type, code)
    async def area_arm_all(self, area_id, code):
        await self._area_arm(area_id, self._all_arming_type, code)

    def has_arming_code(self) -> bool:
        return self._arming_code != None

    def connection_status(self) -> bool:
        return self._connection != None and self.points and self.areas

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
        await self._model()
        await self._authenticate()
        await self.load(load_selector)
        self.connection_status_observer._notify()

    def _on_disconnect(self):
        self._connection = None
        self._last_msg = None
        for a in self.areas.values(): a.reset()
        for p in self.points.values(): p.reset()
        self.connection_status_observer._notify()

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
        LOG.debug("Authentication success!")
    
    async def _authenticate_automation(self):
        creds = bytearray(b'\x01')  # automation user
        creds.extend(map(ord, self._passcode))
        creds.append(0x00) # null terminate
        result = await self._connection.send_command(CMD.AUTHENTICATE, creds)
        if result != b'\x01':
            self._connection.close()
            error = ["Not Authorized", "Authorized", "Max Connections"][result[0]]
            raise PermissionError("Authentication failed: " + error)
        LOG.debug("Authentication success!")
    
    async def _authenticate(self):
        if self.model in ["Solution 2000", "Solution 3000"]:
            await self._login_remote_user()
        else:
            await self._authenticate_automation()

    async def _model(self):
        data = await self._connection.send_command(CMD.WHAT_ARE_YOU)
        self.model = PANEL_MODEL[data[0]]
        self.protocol_version = 'v%d.%d' % (data[5], data[6])
        # Solution and AMAX panels use one set of arming types, B series panels use another.
        if data[0] <= 0x24:
            self._part_arming_type = AREA_ARMING_STAY1
            self._all_arming_type = AREA_ARMING_AWAY
        else:
            self._part_arming_type = AREA_ARMING_PERIMETER_DELAY
            self._all_arming_type = AREA_ARMING_MASTER_DELAY

    async def _basicinfo(self):
        commandformat = bytearray()
        commandformat.append(3)
        
        data = await self._connection.send_command(CMD.WHAT_ARE_YOU, commandformat)
        self.model = PANEL_MODEL[data[0]]
        self.protocol_version = 'v%d.%d' % (data[5], data[6])
        if data[13]: LOG.warning('busy flag: %d', data[13])
        bitmask = data[23:].ljust(33, b'\0')
        self._featureProtocol02 = (bitmask[0] & 0x40) != 0
        self._featureCommandRequestAreaTextCF01 = (bitmask[7] & 0x20) != 0
        self._featureCommandRequestAreaTextCF03 = (bitmask[7] & 0x08) != 0
        # Check if serial read command is supported before sending it
        if (bitmask[11] & 0x04) != 0:
            data = await self._connection.send_command(
                    CMD.PRODUCT_SERIAL, b'\x00\x00')
            self.serial_number = int.from_bytes(data[0:6], 'big')

    async def _load_areas(self):
        names = await self._load_names(CMD.AREA_TEXT, CMD.REQUEST_CONFIGURED_AREAS, "AREA")
        self.areas = {id: Area(name) for id, name in names.items()}

    async def _load_points(self):
        names = await self._load_names(CMD.POINT_TEXT, CMD.REQUEST_CONFIGURED_POINTS, "POINT")
        self.points = {id: Point(name) for id, name in names.items()}

    async def _load_names_cf03(self, name_cmd) -> dict[int, str]:
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

    async def _load_names_cf01(self, name_cmd, names) -> dict[int, str]:
        for id in names.keys():
            request = bytearray(id.to_bytes(2, 'big'))
            request.append(0x00)  # primary language
            data = await self._connection.send_command(name_cmd, request)
            name = data.split(b'\x00', 1)[0]
            names[id] = name.decode('ascii')
        return names

    async def _load_configured_names(self, config_cmd, type):
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
            index+=8
        return names
    async def _load_names(self, name_cmd, config_cmd, type) -> dict[int, str]:
        if self._featureCommandRequestAreaTextCF03:
            return await self._load_names_cf03(name_cmd)
        
        names = await self._load_configured_names(config_cmd, type)

        if self._featureCommandRequestAreaTextCF01:
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
            area = _get_int16(response_detail)
            # item_type = response_detail[2]
            point = _get_int16(response_detail, 3)
            if point == 0xFFFF:
                await self._get_alarms_for_priority(priority, area, point)
            if area in self.areas:
                self.areas[area]._set_alarm(priority, True)
            else:
                print(f"Found unknown area {area}, supported areas: [{self.areas.keys()}]")
            response_detail = response_detail[5:]

    async def _get_alarm_status(self):
        data = await self._connection.send_command(CMD.ALARM_MEMORY_SUMMARY)
        for priority in ALARM_MEMORY_PRIORITIES.keys():
            i = (priority - 1) * 2
            count = _get_int16(data, i)
            if count:
                await self._get_alarms_for_priority(priority)
            else:
                # If events have been cleared, then we can just clear all areas instead of asking the panel for more info
                for area in self.areas.values():
                    area._set_alarm(priority, False)

    async def _load_entity_status(self, status_cmd, entities):
        request = bytearray()
        for id in entities.keys(): request.extend(id.to_bytes(2, 'big'))
        response = await self._connection.send_command(status_cmd, request)
        while response:
            entities[_get_int16(response)].status = response[2]
            response = response[3:]

    async def _area_arm(self, area_id, arm_type, code):
        if self._arming_code != None and code != self._arming_code:
            return
        request = bytearray([arm_type])
        # bitmask with only i-th bit from the left being 1 (section 3.1.4)
        request.extend(bytearray((area_id-1)//8)) # leading 0 bytes
        request.append(1<<(7-((area_id-1) % 8))) # i%8-th bit from the left (top) set
        await self._connection.send_command(CMD.AREA_ARM, request)

    async def _subscribe(self):
        IGNORE = b'\x00'
        SUBSCRIBE = b'\x01'
        data = bytearray(b'\x01') # format
        data += SUBSCRIBE # confidence / heartbeat
        data += SUBSCRIBE # event mem
        data += IGNORE    # event log
        data += IGNORE    # config change
        data += SUBSCRIBE # area on/off
        data += SUBSCRIBE # area ready
        data += IGNORE    # output status
        data += SUBSCRIBE # point status
        data += IGNORE    # door status
        data += IGNORE    # unused
        await self._connection.send_command(CMD.SET_SUBSCRIPTION, data)

    def _area_on_off_consumer(self, data) -> int:
        area_id = _get_int16(data)
        area_status = self.areas[area_id].status = data[2]
        LOG.debug("Area %d: %s" % (area_id, AREA_STATUS[area_status]))
        return 3

    def _area_ready_consumer(self, data) -> int:
        area_id = _get_int16(data)
        ready_status = data[2]
        faults = _get_int16(data, 3)
        self.areas[area_id]._set_ready(ready_status, faults)
        LOG.debug("Area %d: %s (%d faults)" % (
            area_id, AREA_READY[ready_status], faults))
        return 5

    def _point_status_consumer(self, data) -> int:
        point_id = _get_int16(data)
        self.points[point_id].status = data[2]
        LOG.debug("Point updated: %s", self.points[point_id])
        return 3
    
    def _event_summary_consumer(self, data) -> int:
        priority = data[0]
        count = _get_int16(data, 1)
        if count:
            loop = asyncio.get_running_loop()
            loop.create_task(self._get_alarms_for_priority(priority))
        else:
            # If events have been cleared, then we can just clear all areas instead of asking the panel for more info
            for area in self.areas.values():
                area._set_alarm(priority, False)
        return 3

    def _on_status_update(self, data):
        CONSUMERS = {
            0x00: lambda data: 0,  # heartbeat
            0x01: self._event_summary_consumer,
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
            for i in range(0, n_updates): pos += consumer(data[pos:])
