import struct

def BytesToUint16_BigEndian(HandleBytes):
    """大端序 uint8_t[2] -> uint16_t"""
    return (HandleBytes[0] << 8) | (HandleBytes[1] << 0)

def BytesToUint32_BigEndian(HandleBytes):
    """大端序 uint8_t[4] -> uint32_t"""
    return (HandleBytes[0] << 24) | (HandleBytes[1] << 16) | (HandleBytes[2] << 8) | (HandleBytes[3] << 0)

def BytesToUint64_BigEndian(HandleBytes):
    """大端序 uint8_t[8] -> uint64_t"""
    val = 0
    val |= (HandleBytes[0] << 56)
    val |= (HandleBytes[1] << 48)
    val |= (HandleBytes[2] << 40)
    val |= (HandleBytes[3] << 32)
    val |= (HandleBytes[4] << 24)
    val |= (HandleBytes[5] << 16)
    val |= (HandleBytes[6] << 8)
    val |= (HandleBytes[7] << 0)
    return val

def BytesToInt16_BigEndian(HandleBytes):
    """大端序 uint8_t[2] -> int16_t"""
    val = BytesToUint16_BigEndian(HandleBytes)
    return val - 65536 if val >= 32768 else val

def BytesToInt32_BigEndian(HandleBytes):
    """大端序 uint8_t[4] -> int32_t"""
    val = BytesToUint32_BigEndian(HandleBytes)
    return val - 4294967296 if val >= 2147483648 else val

def BytesToInt64_BigEndian(HandleBytes):
    """大端序 uint8_t[8] -> int64_t"""
    val = BytesToUint64_BigEndian(HandleBytes)
    return val - 18446744073709551616 if val >= 9223372036854775808 else val

def BytesToFloat32_BigEndian(HandleBytes):
    """大端序 uint8_t[4] -> float32"""
    # 完全对应C语言指针反转字节逻辑
    reversed_bytes = bytes([HandleBytes[3], HandleBytes[2], HandleBytes[1], HandleBytes[0]])
    return struct.unpack('<f', reversed_bytes)[0]