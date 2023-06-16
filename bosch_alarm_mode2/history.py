import datetime
import abc
import re
from typing import NamedTuple
from .history_const import B_G_HISTORY_FORMAT, AMAX_HISTORY_FORMAT, SOLUTION_HISTORY_FORMAT
from .utils import BE_INT, LE_INT

class HistoryEvent(NamedTuple):
    event_id: int
    event: str

class History:
    def __init__(self, panel, events) -> None:
        self._events = events
        self._panel = panel
        self._parser = TextHistory()

    @property
    def events(self):
        return self._events

    @property
    def last_event_id(self):
        if not self._events:
            return 0
        return self._events[-1][0]

    def init_raw_history(self, panel_type):
        if panel_type <= 0x21:
            self._parser = SolutionHistory()
            return

        if panel_type <= 0x24:
            self._parser = AmaxHistory()
            return

        self._parser = BGHistory()
    
    def parse_polled_events(self, start, event_data, count):
        if not self._parser:
            return []
        
        self._events.extend(self._parser.parse_events(start, event_data, count))
        self._panel.history_observer._notify()

    def parse_subscription_event(self, raw_event):
        text_len = BE_INT.int16(raw_event, 23)
        line = raw_event[25:25 + text_len].decode()
        date, time, message = re.split(r"\s+", line, 2)
        date = datetime.datetime.strptime(f"{date} {time}","%m/%d/%Y %I:%M%p")
        self._events.append((BE_INT.int16(raw_event, 4), f"{date} | {message}"))
        self._panel.history_observer._notify()
        return 25 + text_len

class HistoryParser(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def parse_events(self, start, event_data, count):
        return

class TextHistory(HistoryParser):    
    def parse_events(self, start, event_data, count):
        events = []
        if not count:
            return events
        for i in range(count):
            line = event_data[:event_data.index(0)].decode()
            date, time, message = re.split(r"\s+", line, 2)
            date = datetime.datetime.strptime(f"{date} {time}","%m/%d/%Y %I:%M%p")
            events.append((start + i + 1, f"{date} | {message}"))
            event_data = event_data[len(line)+1:]
        return events

class RawHistory(HistoryParser):
    def parse_events(self, start, event_data, count):
        events = []
        if not count:
            return events
        event_length = len(event_data) // count
        for i in range(count):
            events.append((start + i + 1, self._parse_event(event_data)))
            event_data = event_data[event_length:]
        return events
    @abc.abstractmethod
    def _parse_event(self, event):
        return

class SolutionAmaxHistory(RawHistory):
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
        return "Unknown event"

class BGHistory(RawHistory):
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
