using System;

namespace Float32ToBytesArray {
  public static class FloatHelper {

    /// <summary>
    /// 将32位浮点数转换为大端序字节数组
    /// </summary>
    /// <param name="value">32位浮点数</param>
    /// <returns>大端序字节数组（4字节）</returns>
    public static byte[] ToBigEndianBytes(float value) {
      byte[] bytes = BitConverter.GetBytes(value);
      if (BitConverter.IsLittleEndian) {
        Array.Reverse(bytes);
      }
      return bytes;
    }


    /// <summary>
    /// 将字符串形式的浮点数转换为大端序字节数组
    /// </summary>
    /// <param name="floatString">浮点数字符串</param>
    /// <returns>大端序字节数组（4字节）</returns>
    public static byte[] ParseToBigEndianBytes(string floatString) {
      float value = float.Parse(floatString);
      return ToBigEndianBytes(value);
    }

  }
}
