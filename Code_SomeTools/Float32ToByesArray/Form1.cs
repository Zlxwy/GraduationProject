using System;
using System.Linq;

namespace Float32ToBytesArray {
  public partial class Form1: Form {

    public Form1() {
        InitializeComponent();
    }



    /// <summary>
    /// 将float转换为大端序字节串
    /// </summary>
    private void GenerateButton_Click(object sender, EventArgs e) {
      if (sender is not Button btn) return;
      if (String.IsNullOrEmpty(txtInput.Text)) {
        txtOutput.Text = "请输入浮点数！";
        return;
      }
      try {
        byte[] bytes = FloatHelper.ParseToBigEndianBytes(txtInput.Text.Trim());
        txtOutput.Text = string.Join(" ", bytes.Select(b => $"{b:X2}"));
      }
      catch (FormatException) {
        txtOutput.Text = "输入格式错误，请输入有效的浮点数！";
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
