using System.IO.Ports;
using System.Text;
using System.Text.RegularExpressions;

namespace ParseVoltageData
{
    public partial class Form1 : Form
    {
        private SerialPort? _serialPort;
        private bool _isPortOpen;
        private readonly StringBuilder _buffer = new();
        private static readonly Regex AdcRegex = new(@"ADC_ConvValue\[(\d+)\]\s*=\s*(\d+)", RegexOptions.Compiled);
        private readonly Label[] _adcLabels;
        private volatile bool _parsePending;

        public Form1()
        {
            InitializeComponent();
            _adcLabels = [lblAdc0, lblAdc1, lblAdc2, lblAdc3];
            LoadPortNames();
        }

        private void LoadPortNames()
        {
            cmbPortName.Items.Clear();
            foreach (var name in SerialPort.GetPortNames())
                cmbPortName.Items.Add(name);
            if (cmbPortName.Items.Count > 0)
                cmbPortName.SelectedIndex = 0;
        }

        private void btnOpenClose_Click(object? sender, EventArgs e)
        {
            if (!_isPortOpen)
                OpenPort();
            else
                ClosePort();
        }

        private void OpenPort()
        {
            var portName = cmbPortName.SelectedItem?.ToString();
            if (string.IsNullOrEmpty(portName))
            {
                MessageBox.Show("请选择串口", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (!int.TryParse(cmbBaudRate.Text, out var baudRate) || baudRate <= 0)
            {
                MessageBox.Show("请输入有效的波特率", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            _serialPort = new SerialPort(portName, baudRate)
            {
                DataBits = int.Parse(cmbDataBits.SelectedItem?.ToString() ?? "8"),
                Parity = Enum.Parse<Parity>(cmbParity.SelectedItem?.ToString() ?? "None"),
                StopBits = Enum.Parse<StopBits>(cmbStopBits.SelectedItem?.ToString() ?? "1"),
                Encoding = Encoding.UTF8,
                ReadBufferSize = 4096,
            };

            try
            {
                _serialPort.Open();
                _serialPort.DataReceived += SerialPort_DataReceived;
                _isPortOpen = true;
                btnOpenClose.Text = "关闭串口";
                cmbPortName.Enabled = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"打开串口失败: {ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                _serialPort.Dispose();
                _serialPort = null;
            }
        }

        private void ClosePort()
        {
            if (_serialPort != null)
            {
                _serialPort.DataReceived -= SerialPort_DataReceived;
                _serialPort.Close();
                _serialPort.Dispose();
                _serialPort = null;
            }
            _isPortOpen = false;
            btnOpenClose.Text = "打开串口";
            cmbPortName.Enabled = true;
        }

        private void SerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            if (_serialPort == null) return;
            try
            {
                var buf = new byte[_serialPort.BytesToRead];
                _serialPort.Read(buf, 0, buf.Length);
                var text = _serialPort.Encoding.GetString(buf);

                lock (_buffer)
                {
                    _buffer.Append(text);
                }

                if (!_parsePending)
                {
                    _parsePending = true;
                    BeginInvoke(() => ParseAndUpdateLabels());
                }
            }
            catch { /* ignore read errors during close */ }
        }

        private void ParseAndUpdateLabels()
        {
            string fullText;
            lock (_buffer)
            {
                fullText = _buffer.ToString();
            }

            var updated = new bool[4];
            foreach (Match match in AdcRegex.Matches(fullText))
            {
                var index = int.Parse(match.Groups[1].Value);
                var value = match.Groups[2].Value;
                if (index is >= 0 and < 4)
                {
                    // _adcLabels[index].Text = $"ADC[{index}]: {value.PadLeft(4)}";
                    double vol = double.Parse(value) * 3.3 / 4096;
                    _adcLabels[index].Text = $"ADC[{index}]: {vol.ToString("0.00").PadLeft(6)}V";
                    updated[index] = true;
                }
            }

            // 解析完成，清空缓冲区并重置标志
            lock (_buffer)
            {
                _buffer.Clear();
            }
            _parsePending = false;

            // 如果解析期间又有新数据到达，再触发一次
            lock (_buffer)
            {
                if (_buffer.Length > 0)
                {
                    _parsePending = true;
                    BeginInvoke(() => ParseAndUpdateLabels());
                }
            }
        }
    }
}
