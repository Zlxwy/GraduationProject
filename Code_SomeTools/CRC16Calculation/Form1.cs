using System;
using System.Linq;
namespace CRC16Calculation {
  public partial class Form1: Form {

    public Form1() {
        InitializeComponent();
    }



    /// <summary>
    /// 将十六进制字符串转换为字节数组
    /// </summary>
    /// <param name="HexString">十六进制字符串</param>
    /// <returns>字节数组</returns>
    private static byte[] HexStringToByteArray(string HexString) {
      var HexParts = HexString.Split(new[]{' ','\t'}, StringSplitOptions.RemoveEmptyEntries);
      return HexParts.Select(part => Convert.ToByte(part, 16)).ToArray();
    }



    /// <summary>
    /// 生成CRC16校验和
    /// </summary>
    private void GenerateButton_Click(object sender, EventArgs e) {
      if (sender is not Button btn) return;
      if (String.IsNullOrEmpty(txtInput.Text)) {
        txtOutput.Text = "请输入字节串！";
        return;
      }
      try {
        byte[] ba = HexStringToByteArray(txtInput.Text); // 将输入的十六进制字符串转换为字节数组
        ushort crc = CRC16Calculator.Calculate(ba); // 使用CRC16Calculator模块计算CRC16校验和
        byte crc_high =  (byte)(crc >> 8); // 获取校验和的高8位
        byte crc_low = (byte)(crc & 0xFF); // 获取校验和的低8位
        txtOutput.Text = $"{crc_high:X2} {crc_low:X2}"; // 显示校验和
      }
      catch (FormatException) {
        txtOutput.Text = "输入格式错误，请确保输入有效的十六进制字符！";
      }
      catch (Exception ex) {
        txtOutput.Text = $"发生错误：{ex.Message}";
      }
    }



    /// <summary>
    /// 清空输入和输出
    /// </summary>
    private void ClearButton_Click(object sender, EventArgs e) {
      if (sender is not Button btn) return;
      txtInput.Text = "";
      txtOutput.Text = "";
    }


  }
}
