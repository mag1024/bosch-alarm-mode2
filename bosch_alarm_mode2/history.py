import abc
import logging
from datetime import datetime
from typing import NamedTuple
from .history_const import (
    B_G_HISTORY_FORMAT,
    AMAX_HISTORY_FORMAT,
    SOLUTION_HISTORY_FORMAT,
    SOLUTION_USERS,
    EVENT_LOOKBACK_COUNT,
)
from .utils import BE_INT, LE_INT

LOG = logging.getLogger(__name__)


class HistoryEvent(NamedTuple):
    id: int
    date: datetime
    message: str

    def __repr__(self) -> str:
        return f"[{self.id}] {self.date} | {self.message}"


class HistoryEventParams(NamedTuple):
    date: datetime
    code: str
    area: int
    param1: int
    param2: int
    param3: int


class HistoryParser:
    __metaclass__ = abc.ABCMeta

    def parse_subscription_event(self, raw_event: bytearray) -> HistoryEvent:
        event_code = str(BE_INT.int16(raw_event, 4))
        area = BE_INT.int16(raw_event, 6)
        param123 = _sequential_params(raw_event[8:])
        timestamp = BE_INT.int32(raw_event, 14)
        date = self._parse_subscription_event_timestamp(timestamp)
        params = HistoryEventParams._make((date, event_code, area, *param123))
        return HistoryEvent(BE_INT.int32(raw_event) + 1, *self._parse_event(params))

    def parse_polled_event(self, id: int, event_data: bytearray) -> HistoryEvent:
        return HistoryEvent(id, *self._parse_event(self._parse_event_params(event_data)))

    def parse_start_event_id(self, event_data: bytearray) -> int:
        return BE_INT.int32(event_data, 1)

    @abc.abstractmethod
    def _parse_subscription_event_timestamp(self, timestamp: int) -> datetime:
        pass

    @abc.abstractmethod
    def _parse_event_params(self, event: bytearray) -> HistoryEventParams:
        pass

    @abc.abstractmethod
    def _parse_event(self, event: HistoryEventParams) -> tuple[datetime, str]:
        pass


def _parse_sol_amax_params(event: bytearray) -> HistoryEventParams:
    timestamp = LE_INT.int16(event)
    minute = timestamp & 0x3F
    hour = (timestamp >> 6) & 0x1F
    day = (timestamp >> 11) & 0x1F
    timestamp = LE_INT.int16(event, 2)
    second = timestamp & 0x3F
    month = (timestamp >> 6) & 0x0F
    year = 2000 + (timestamp >> 10)
    date = datetime(year, month, day, hour, minute, second)

    event_code = str(event[6])
    area = LE_INT.int16(event, 4)
    param123 = (area, event[7], 0)
    return HistoryEventParams._make((date, event_code, area, *param123))


def _parse_sol_amax_timestamp(timestamp: int) -> datetime:
    minute = timestamp & 0x3F
    hour = (timestamp >> 6) & 0x1F
    day = (timestamp >> 11) & 0x1F
    month = (timestamp >> 16) & 0x0F
    year = 2000 + ((timestamp >> 20) & 0x1F)
    second = timestamp >> 26
    return datetime(year, month, day, hour, minute, second)


class SolutionHistoryParser(HistoryParser):
    def _parse_event_params(self, event: bytearray) -> HistoryEventParams:
        return _parse_sol_amax_params(event)

    def _parse_event(self, event: HistoryEventParams) -> tuple[datetime, str]:
        user = SOLUTION_USERS.get(
            event.param2, f"User {event.param2}" if event.param2 <= 32 else ""
        )
        return (
            event.date,
            SOLUTION_HISTORY_FORMAT[event.code].format(
                user=user, param1=event.param1, param2=event.param2
            ),
        )

    def _parse_subscription_event_timestamp(self, timestamp: int) -> datetime:
        return _parse_sol_amax_timestamp(timestamp)


class AmaxHistoryParser(HistoryParser):
    def _parse_event_params(self, event: bytearray) -> HistoryEventParams:
        return _parse_sol_amax_params(event)

    def _parse_subscription_event_timestamp(self, timestamp: int) -> datetime:
        return _parse_sol_amax_timestamp(timestamp)

    def parse_start_event_id(self, event_data: bytearray) -> int:
        # AMAX panels use some bytes of the event id as flags
        # Apply a mask to only keep the actual event id
        return BE_INT.int32(event_data, 1) & 0x001FF

    def _parse_event(self, event: HistoryEventParams) -> tuple[datetime, str]:
        # Amax requires different strings depending on param1 sometimes
        key_specs = [
            ("", None),
            ("_%d" % event.param1, None),
            ("_zone", None),
            ("_keypad", lambda p: p <= 16),
            ("_dx2", lambda p: p <= 108),
            ("_dx3", lambda p: p in (150, 151)),
            ("_b4", lambda p: p in (150, 151)),
        ]
        for suffix, predicate in key_specs:
            if predicate and not predicate(event.param1):
                continue
            if template := AMAX_HISTORY_FORMAT.get(event.code + suffix):
                return (
                    event.date,
                    template.format(param1=event.param1, param2=event.param2),
                )
        return (event.date, f"Unknown event {event}")


class BGHistoryParser(HistoryParser):
    def _parse_event_params(self, event: bytearray) -> HistoryEventParams:
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
        param123 = _sequential_params(event[4:])
        return HistoryEventParams._make((date, event_code, area, *param123))

    def _parse_subscription_event_timestamp(self, timestamp: int) -> datetime:
        minute = timestamp & 0x3F
        hour = (timestamp >> 6) & 0x1F
        day = ((timestamp >> 11) & 0x1F) + 1
        month = ((timestamp >> 16) & 0x0F) + 1
        year = 2010 + ((timestamp >> 20) & 0x1F)
        second = timestamp >> 26
        return datetime(year, month, day, hour, minute, second)

    def _parse_event(self, event: HistoryEventParams) -> tuple[datetime, str]:
        return (
            event.date,
            B_G_HISTORY_FORMAT[event.code].format(
                area=event.area,
                param1=event.param1,
                param2=event.param2,
                param3=event.param3,
            ),
        )


class History:
    def __init__(self) -> None:
        self._events: list[HistoryEvent] = []
        self._parser: HistoryParser | None = None
        self._max_count = 0
        self.has_errored = False

    @property
    def events(self) -> list[HistoryEvent]:
        return self._events

    @property
    def last_event_id(self) -> int:
        # Requesting a very large starting event id causes the panel to reply
        # with the event number of the next event to be written to the history,
        # allowing us to discover the max existing event id.
        return self._events[-1][0] if self._events else 0xFFFFFFFF

    def init_for_panel(self, panel_type: int) -> None:
        if panel_type <= 0x21 or panel_type == 0x28:
            self._parser = SolutionHistoryParser()
        elif panel_type <= 0x24:
            self._parser = AmaxHistoryParser()
        else:
            self._parser = BGHistoryParser()

    def _append_error(self, id: int, excp: Exception) -> None:
        error_str = f"parse error: {repr(excp)}"
        LOG.error("History event " + error_str)
        self._events.append(HistoryEvent(id, datetime.now(), error_str))

    def parse_polled_events(self, event_data: bytearray | None) -> int | None:
        if not event_data or not self._parser:
            return None
        count = event_data[0]
        start = self._parser.parse_start_event_id(event_data) + 1
        event_data = event_data[5:]
        # Panels can have large numbers of history events, which take a very
        # long time load. Limit to EVENT_LOOKBACK_COUNT most recent events.
        if count == 0:
            return max(0, start - EVENT_LOOKBACK_COUNT - 1) if len(self._events) == 0 else None

        event_length = len(event_data) // count
        for i in range(start, start + count):
            try:
                e = self._parser.parse_polled_event(i, event_data)
                if self._events and e.date < self._events[-1].date:
                    return None
                LOG.debug(e)
                self._events.append(e)
                event_data = event_data[event_length:]
            except Exception as excp:
                self._append_error(i, excp)

        if count > self._max_count:
            self._max_count = count
        # A truncated batch indicates the end of events.
        return self.last_event_id if count == self._max_count else None

    def parse_subscription_event(self, raw_event: bytearray) -> int:
        if not self._parser:
            return 0
        event_id = None
        try:
            text_len = BE_INT.int16(raw_event, 23)
            event_id = BE_INT.int32(raw_event)
            total_len = 25 + text_len
            e = self._parser.parse_subscription_event(raw_event)
            LOG.debug(e)
            self._events.append(e)
            return total_len
        except Exception as excp:
            if event_id:
                self._append_error(event_id + 1, excp)
            return len(raw_event)


def _sequential_params(data: bytearray) -> tuple[int, int, int]:
    return (BE_INT.int16(data, 0), BE_INT.int16(data, 2), BE_INT.int16(data, 4))
