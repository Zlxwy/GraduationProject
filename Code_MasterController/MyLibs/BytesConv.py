import struct

# # 导入示例
# from BytesConv import BytesToUint16_BigEndian as b2u16
# from BytesConv import BytesToUint32_BigEndian as b2u32
# from BytesConv import BytesToUint64_BigEndian as b2u64
# from BytesConv import BytesToInt16_BigEndian as b2s16
# from BytesConv import BytesToInt32_BigEndian as b2s32
# from BytesConv import BytesToInt64_BigEndian as b2s64
# from BytesConv import BytesToFloat32_BigEndian as b2f32
# from BytesConv import Uint16ToBytes_BigEndian as u162b
# from BytesConv import Uint32ToBytes_BigEndian as u322b
# from BytesConv import Uint64ToBytes_BigEndian as u642b
# from BytesConv import Int16ToBytes_BigEndian as s162b
# from BytesConv import Int32ToBytes_BigEndian as s322b
# from BytesConv import Int64ToBytes_BigEndian as s642b
# from BytesConv import Float32ToBytes_BigEndian as f322b

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




def Uint16ToBytes_BigEndian(value):
    return bytes([(value >> 8) & 0xFF, value & 0xFF])

def Uint32ToBytes_BigEndian(value):
    return bytes([
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ])

def Uint64ToBytes_BigEndian(value):
    return bytes([
        (value >> 56) & 0xFF,
        (value >> 48) & 0xFF,
        (value >> 40) & 0xFF,
        (value >> 32) & 0xFF,
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ])

def Int16ToBytes_BigEndian(value):
    if value < 0:
        value += 65536
    return Uint16ToBytes_BigEndian(value)

def Int32ToBytes_BigEndian(value):
    if value < 0:
        value += 4294967296
    return Uint32ToBytes_BigEndian(value)

def Int64ToBytes_BigEndian(value):
    if value < 0:
        value += 18446744073709551616
    return Uint64ToBytes_BigEndian(value)

def Float32ToBytes_BigEndian(value):
    return struct.pack('>f', value)  # 大端浮点数，最标准

# def SendCommand_BasicMove(MotorId, ActionType, Steps, Speed):
#   """发送基本运动命令"""
#   Bytes_CommandType = Uint16ToBytes_BigEndian(0x0000)
#   Bytes_MotorId = bytes([MotorId & 0xFF])
#   Bytes_ActionType = bytes([ActionType & 0xFF])
#   Bytes_Steps = Int64ToBytes_BigEndian(Steps)
#   Bytes_Speed = Uint32ToBytes_BigEndian(Speed)
#   Bytes_BasicMove = Bytes_CommandType + Bytes_MotorId + Bytes_ActionType + Bytes_Steps + Bytes_Speed
#   return Bytes_BasicMove

# if __name__ == "__main__":
#   Bytes_BasicMove = SendCommand_BasicMove(0,1,100,300)
#   for i in Bytes_BasicMove:
#     print(hex(i), end=" ")
