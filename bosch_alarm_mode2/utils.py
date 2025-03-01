from typing import Literal
from collections.abc import Callable


class EndianInt:
    def __init__(self, endianness: Literal["little", "big"]) -> None:
        self.byteorder = endianness

    def int8(self, data: bytearray, offset: int = 0) -> int:
        return int.from_bytes(data[offset : offset + 1], self.byteorder)

    def int16(self, data: bytearray, offset: int = 0) -> int:
        return int.from_bytes(data[offset : offset + 2], self.byteorder)

    def int32(self, data: bytearray, offset: int = 0) -> int:
        return int.from_bytes(data[offset : offset + 4], self.byteorder)


BE_INT = EndianInt("big")
LE_INT = EndianInt("little")


class Observable:
    def __init__(self) -> None:
        self._observers: list[Callable[[], None]] = []

    def attach(self, observer: Callable[[], None]) -> None:
        self._observers.append(observer)

    def detach(self, observer: Callable[[], None]) -> None:
        self._observers.remove(observer)

    def _notify(self) -> None:
        for observer in self._observers:
            observer()
