using System.IO.Ports;
using System.Text;

namespace SimpleUartHelper
{
    public partial class Form1 : Form
    {
        private SerialPort? _serialPort;
        private bool _isPortOpen;
        private bool _isDarkTheme = true;

        public Form1()
        {
            InitializeComponent();
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

        private void btnToggleTheme_Click(object? sender, EventArgs e)
        {
            _isDarkTheme = !_isDarkTheme;
            if (_isDarkTheme)
            {
                txtReceive.BackColor = Color.FromArgb(30, 30, 30);
                txtReceive.ForeColor = Color.FromArgb(220, 220, 220);
                btnToggleTheme.Text = "浅色模式";
            }
            else
            {
                txtReceive.BackColor = Color.White;
                txtReceive.ForeColor = Color.Black;
                btnToggleTheme.Text = "深色模式";
            }
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
                BeginInvoke(() =>
                {
                    txtReceive.AppendText(text);
                });
            }
            catch { /* ignore read errors during close */ }
        }
    }
}
