import abc
import logging
import re
from datetime import datetime
from typing import NamedTuple
from .history_const import B_G_HISTORY_FORMAT, AMAX_HISTORY_FORMAT, SOLUTION_HISTORY_FORMAT, EVENT_LOOKBACK_COUNT
from .utils import BE_INT, LE_INT

LOG = logging.getLogger(__name__)
class HistoryEvent(NamedTuple):
    event_id: int
    event: str

class History:
    def __init__(self, events) -> None:
        self._events = events
        self._parser = TextHistory()

    @property
    def events(self):
        return self._events

    @property
    def last_event_id(self):
        # Requesting a very large starting event id causes the panel to reply
        # with the event number of the next event to be written to the history,
        # allowing us to discover the max existing event id.
        return self._events[-1][0] if self._events else 0xFFFFFFFF

    def init_raw_history(self, panel_type):
        if panel_type <= 0x21:
            self._parser = SolutionHistory()
        elif panel_type <= 0x24:
            self._parser = AmaxHistory()
        else:
            self._parser = BGHistory()

    def parse_polled_events(self, event_data):
        count = event_data[0]
        start = BE_INT.int32(event_data, 1) + 1
        event_data = event_data[5:]
        if count == 0 and len(self._events) == 0:
            return max(0, start - EVENT_LOOKBACK_COUNT - 1)
        if not count:
            return None

        try:
            events = self._parser.parse_events(start, event_data, count)
            for (id, text) in events:
                LOG.debug(f"[{id}]: {text}")
            self._events.extend(events)
        except Exception as e:
            error_str = f"parse error: {repr(e)}"
            LOG.error("History event " + error_str)
            self._events.append((start + count, error_str))
        return self.last_event_id

    def parse_subscription_event(self, raw_event):
        text_len = BE_INT.int16(raw_event, 23)
        total_len = 25 + text_len
        line = raw_event[25:total_len - 1].decode()
        # Not sure why, but there is an extra 0 in subscription text
        date, time, _, message = re.split(r"\s+", line, 3)
        date = datetime.strptime(f"{date} {time}","%m/%d/%Y %I:%M%p")
        self._events.append((BE_INT.int16(raw_event, 4), f"{date} | {message}"))
        return total_len

class HistoryParser(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse_events(self, start, event_data, count):
        pass

class TextHistory(HistoryParser):
    def parse_events(self, start, event_data, count):
        events = []
        for i in range(count):
            line = event_data[:event_data.index(0)].decode()
            date, time, message = re.split(r"\s+", line, 2)
            date = datetime.strptime(f"{date} {time}","%m/%d/%Y %I:%M%p")
            events.append((start + i, f"{date} | {message}"))
            event_data = event_data[len(line)+1:]
        return events

class RawHistory(HistoryParser):
    def parse_events(self, start, event_data, count):
        events = []
        event_length = len(event_data) // count
        for i in range(count):
            events.append((start + i, self._parse_event(event_data)))
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
        date = datetime(year, month, day, hour, minute, second)
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
        timestamp = BE_INT.int32(event, 10)
        year = 2010 + (timestamp >> 26)
        month = (timestamp >> 22) & 0x0F
        day = (timestamp >> 17) & 0x1F
        hour = (timestamp >> 12) & 0x1F
        minute = (timestamp >> 6) & 0x3F
        second = timestamp & 0x3F

        date = datetime(year, month, day, hour, minute, second)
        event_code = str(BE_INT.int16(event))
        area = BE_INT.int16(event, 2)
        param1 = BE_INT.int16(event, 4)
        param2 = BE_INT.int16(event, 6)
        param3 = BE_INT.int16(event, 8)
        date = f"{date} | "
        return date + B_G_HISTORY_FORMAT[event_code].format(
            area=area, param1=param1, param2=param2, param3=param3)
