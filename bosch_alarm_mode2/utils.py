def get_int8(data, offset = 0):
    return int.from_bytes(data[offset:offset+1], 'big')

def get_int16(data, offset = 0):
    return int.from_bytes(data[offset:offset+2], 'big')

def get_int32(data, offset = 0):
    return int.from_bytes(data[offset:offset+4], 'big')

def get_int16_little(data, offset=0):
    return int.from_bytes(data[offset:offset+2], 'little')

def get_int32_little(data, offset=0):
    return int.from_bytes(data[offset:offset+4], 'little')
