import datetime
import abc
from .history_const import B_G_HISTORY_FORMAT, AMAX_HISTORY_FORMAT, SOLUTION_HISTORY_FORMAT
from .utils import BE_INT, LE_INT, Observable

class History(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, panel) -> None:
        self._events = []
        self._panel = panel

    @property
    def events(self):
        return self._events

    @property
    def last_event_id(self):
        if not self._events:
            return 0
        return self._events[-1][0]
    
    def _add_event(self, event, last_event_id):
        self._events.append((last_event_id, event))
        self._panel.history_observer._notify()
    
    @abc.abstractmethod
    def _parse_event(self, event):
        return
    
    def parse_events(self, start, events, count):
        if not count:
            return
        event_length = len(events) // count
        for i in range(count):
            self._add_event(self._parse_event(events), start + i + 1)
            events = events[event_length:]
    
    def parse_subscription_event(self, event):
        text_len = BE_INT.int16(event, 23)
        timestamp = LE_INT.int32(event, 14)
        year = 2010 + (timestamp >> 26)
        month = (timestamp >> 22) & 0x0F
        day = (timestamp >> 17) & 0x1F
        hour = (timestamp >> 12) & 0x1F
        minute = (timestamp >> 6) & 0x3F
        second = timestamp & 0x3F
        date = datetime.datetime(year, month, day, hour, minute, second)
        event = event[25:].decode()
        event = f"{date} | {event}"
        self._add_event(event, BE_INT.int16(event, 4))
        return 25 + text_len

class SolutionAmaxHistory(History):
    def __init__(self, panel) -> None:
        super().__init__(panel)
        
    def _parse_params(self, event):
        timestamp = LE_INT.int16(event)
        minute = timestamp & 0x3F
        hour = (timestamp >> 6) & 0x1F
        day = (timestamp >> 11) & 0x1F
        timestamp = LE_INT.int16(event, 2)
        second = timestamp & 0x3F
        month = (timestamp >> 6) & 0x0F
        year = 2000 + (timestamp >> 10)
        first_param = LE_INT.int16(event, 4)
        second_param = event[7]
        event_code = event[6]
        date = datetime.datetime(year, month, day, hour, minute, second)
        return (event_code, date, first_param, second_param)

class SolutionHistory(SolutionAmaxHistory):
    SOLUTION_USERS = {
        0: "Quick",
        994: "PowerUp",
        995: "Telephone",
        997: "Schedule",
        998: "A-Link",
        999: "Installer",
    }
    def __init__(self, panel) -> None:
        super().__init__(panel)
    
    def _parse_event(self, event):
        (event_code, date, first_param, second_param) = self._parse_params(event)
        date = f"{date} | "
        event_code = str(event_code)
        user = ""
        if second_param in SolutionHistory.SOLUTION_USERS:
            user = SolutionHistory.SOLUTION_USERS[second_param]
        elif second_param <= 32:
            user = f"User {second_param}"
        return date + SOLUTION_HISTORY_FORMAT[event_code].format(
            user=user, param1=first_param, param2=second_param)

class AmaxHistory(SolutionAmaxHistory):
    def __init__(self, panel) -> None:
        super().__init__(panel)
    
    def _check_history_key(self, id, date, first_param, second_param):
        if id in AMAX_HISTORY_FORMAT:
            return date + AMAX_HISTORY_FORMAT[id].format(param1=first_param, param2=second_param)
        return None

    def _parse_event(self, event):
        (event_code, date, first_param, second_param) = self._parse_params(event)
        date = f"{date} | "
        id = str(event_code)
        # Amax requires different strings depending on param1 sometimes
        check = self._check_history_key(id, date, first_param, second_param)
        if check:
            return check
        check = self._check_history_key(f"{id}_{first_param}", date, first_param, second_param)
        if check:
            return check
        check = self._check_history_key(f"{id}_zone", date, first_param, second_param)
        if check:
            return check
        check = self._check_history_key(f"{id}_keypad", date, first_param, second_param)
        if check and first_param <= 16:
            return check
        check = self._check_history_key(f"{id}_dx2", date, first_param, second_param)
        if check and first_param <= 108:
            return check
        check = self._check_history_key(f"{id}_dx3", date, first_param, second_param)
        if check and first_param in (150, 151):
            return check
        check = self._check_history_key(f"{id}_b4", date, first_param, second_param)
        if check and first_param in (150, 151):
            return check

class BGHistory(History):
    def __init__(self, panel) -> None:
        super().__init__(panel)

    def _parse_event(self, event):
        timestamp = LE_INT.int32(event, 10)
        year = 2010 + (timestamp >> 26)
        month = (timestamp >> 22) & 0x0F
        day = (timestamp >> 17) & 0x1F
        hour = (timestamp >> 12) & 0x1F
        minute = (timestamp >> 6) & 0x3F
        second = timestamp & 0x3F

        date = datetime.datetime(year, month, day, hour, minute, second)
        event_code = LE_INT.int16(event)
        area = LE_INT.int16(event, 2)
        param1 = LE_INT.int16(event, 4)
        param2 = LE_INT.int16(event, 6)
        param3 = LE_INT.int16(event, 8)
        date = f"{date} | "
        event_code = str(event_code)
        event = date + B_G_HISTORY_FORMAT[event_code].format(
            area=area, param1=param1, param2=param2, param3=param3)
        return event

class TextHistory(History):
    def __init__(self, panel) -> None:
        super().__init__(panel)
    
    def _consume_text(self, event_data, length=-1):
        # if the length is -1, then the string is null terminated
        if length == -1:
            length = event_data.index(0)
        text = event_data[:length].strip()
        event_data = event_data[length+1:]
        return event_data, text.decode()
    
    def parse_events(self, start, events, count):
        if not count:
            return
        for i in range(count):
            events, date = self._consume_text(events, 10)
            events, time = self._consume_text(events, 7)
            events, text = self._consume_text(events)
            date = datetime.datetime.strptime(f"{date} {time}","%m/%d/%Y %I:%M%p")
            self._add_event(f"{date} | {text}", start + i + 1)

def construct_raw_parser(panel_type, panel) -> History:
    if panel_type <= 0x21:
        return SolutionHistory(panel)

    if panel_type <= 0x24:
        return AmaxHistory(panel)

    return BGHistory(panel)