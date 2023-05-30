class BE_INT:
    @classmethod
    def get_int8(cls, data, offset=0):
        return int.from_bytes(data[offset:offset+1], 'big')

    @classmethod
    def get_int16(cls, data, offset=0):
        return int.from_bytes(data[offset:offset+2], 'big')

    @classmethod
    def get_int32(cls, data, offset=0):
        return int.from_bytes(data[offset:offset+4], 'big')


class LE_INT:
    @classmethod
    def get_int8(cls, data, offset=0):
        return int.from_bytes(data[offset:offset+1], 'little')

    @classmethod
    def get_int16(cls, data, offset=0):
        return int.from_bytes(data[offset:offset+2], 'little')

    @classmethod
    def get_int32(cls, data, offset=0):
        return int.from_bytes(data[offset:offset+4], 'little')
