class EndianInt:
    def __init__(self, endianness) -> None:
        self.byteorder = endianness

    def int8(self, data, offset=0):
        return int.from_bytes(data[offset:offset+1], self.byteorder)
    def int16(self, data, offset=0):
        return int.from_bytes(data[offset:offset+2], self.byteorder)
    def int32(self, data, offset=0):
        return int.from_bytes(data[offset:offset+4], self.byteorder)

BE_INT = EndianInt('big')
LE_INT = EndianInt('little')

class Observable:
    def __init__(self):
        self._observers = []

    def attach(self, observer): self._observers.append(observer)
    def detach(self, observer): self._observers.remove(observer)

    def _notify(self):
        for observer in self._observers: observer()