using System.IO.Ports;
using System.Text;

namespace ParseStickData
{
    public partial class Form1 : Form
    {
        private SerialPort? _serialPort;
        private bool _isPortOpen;
        private StringBuilder _receiveBuffer = new StringBuilder();
        private object _bufferLock = new object();
        private const int MaxTextBoxLines = 100;
        private const int MaxBufferLines = 50;
        private DateTime _lastUpdateTime = DateTime.MinValue;
        private const int UpdateIntervalMs = 50;
        private StringBuilder _pendingText = new StringBuilder();
        private bool _updatePending = false;
        private long _totalBytesReceived = 0;

        public Form1()
        {
            InitializeComponent();
            LoadPortNames();
        }

        private void Form1_Resize(object? sender, EventArgs e)
        {
            splitContainer1.SplitterDistance = splitContainer1.Width / 2;
        }

        private void Form1_FormClosing(object? sender, FormClosingEventArgs e)
        {
            if (_isPortOpen)
                ClosePort();
        }

        private void LoadPortNames()
        {
            cmbPortName.Items.Clear();
            foreach (var name in SerialPort.GetPortNames())
                cmbPortName.Items.Add(name);
            if (cmbPortName.Items.Count > 0)
                cmbPortName.SelectedIndex = 0;
        }

        private void btnRefresh_Click(object? sender, EventArgs e)
        {
            LoadPortNames();
        }

        private void btnClear_Click(object? sender, EventArgs e)
        {
            txtReceive.Clear();
            lock (_bufferLock)
            {
                _receiveBuffer.Clear();
            }
            lock (_pendingText)
            {
                _pendingText.Clear();
            }
            _totalBytesReceived = 0;
            UpdateDataCount();
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
                btnRefresh.Enabled = false;
                UpdateStatus($"已连接 {portName} @ {baudRate}");
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
            btnRefresh.Enabled = true;
            UpdateStatus("未连接");
        }

        private void UpdateStatus(string status)
        {
            lblStatus.Text = status;
        }

        private void UpdateDataCount()
        {
            lblDataCount.Text = $"接收: {_totalBytesReceived:N0} 字节";
        }

        private void SerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            if (_serialPort == null) return;
            try
            {
                var buf = new byte[_serialPort.BytesToRead];
                _serialPort.Read(buf, 0, buf.Length);
                var text = _serialPort.Encoding.GetString(buf);
                
                _totalBytesReceived += buf.Length;
                
                lock (_bufferLock)
                {
                    _receiveBuffer.Append(text);
                }

                lock (_pendingText)
                {
                    _pendingText.Append(text);
                }

                if (!_updatePending)
                {
                    _updatePending = true;
                    var now = DateTime.Now;
                    var delay = Math.Max(0, UpdateIntervalMs - (int)(now - _lastUpdateTime).TotalMilliseconds);
                    
                    Task.Delay(delay).ContinueWith(t =>
                    {
                        BeginInvoke(() =>
                        {
                            string textToAppend;
                            lock (_pendingText)
                            {
                                textToAppend = _pendingText.ToString();
                                _pendingText.Clear();
                            }
                            
                            txtReceive.AppendText(textToAppend);
                            
                            if (txtReceive.Lines.Length > MaxTextBoxLines)
                            {
                                var lines = txtReceive.Lines.Skip(txtReceive.Lines.Length - MaxTextBoxLines).ToArray();
                                txtReceive.Clear();
                                txtReceive.Lines = lines;
                            }
                            
                            ParseAndUpdateData();
                            UpdateDataCount();
                            _lastUpdateTime = DateTime.Now;
                            _updatePending = false;
                        });
                    });
                }
            }
            catch { /* ignore read errors during close */ }
        }

        private void ParseAndUpdateData()
        {
            string bufferText;
            lock (_bufferLock)
            {
                bufferText = _receiveBuffer.ToString();
            }
            var lines = bufferText.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            
            if (lines.Length > MaxBufferLines)
            {
                lock (_bufferLock)
                {
                    _receiveBuffer.Clear();
                    var recentLines = lines.Skip(lines.Length - MaxBufferLines / 2);
                    foreach (var line in recentLines)
                    {
                        _receiveBuffer.AppendLine(line);
                    }
                }
            }

            var adcData = new Dictionary<string, int>();
            var voltageData = new Dictionary<string, string>();
            var percentData = new Dictionary<string, string>();

            foreach (var line in lines)
            {
                if (line.Contains("V"))
                {
                    ParseKeyValuePairs(line, voltageData, "V");
                }
                else if (line.Contains("%"))
                {
                    ParseKeyValuePairs(line, percentData, "%");
                }
                else if (line.Contains(":"))
                {
                    ParseKeyValuePairs(line, adcData);
                }
            }

            UpdateDisplay(adcData, voltageData, percentData);
        }

        private void ParseKeyValuePairs<T>(string line, Dictionary<string, T> result, string? unit = null)
        {
            var pairs = line.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var pair in pairs)
            {
                var kv = pair.Split(new[] { ':' }, 2);
                if (kv.Length == 2)
                {
                    var key = kv[0].Trim();
                    var valueStr = kv[1].Trim();

                    if (!string.IsNullOrEmpty(unit))
                    {
                        valueStr = valueStr.Replace(unit, "").Trim();
                    }

                    if (typeof(T) == typeof(int))
                    {
                        if (int.TryParse(valueStr, out int intValue))
                        {
                            result[key] = (T)(object)intValue;
                        }
                    }
                    else if (typeof(T) == typeof(string))
                    {
                        result[key] = (T)(object)valueStr;
                    }
                }
            }
        }

        private void UpdateDisplay(Dictionary<string, int> adcData, Dictionary<string, string> voltageData, Dictionary<string, string> percentData)
        {
            if (adcData.TryGetValue("LeftStick_Y", out int ly))
                lblLeftStickY_ADC.Text = $"Y轴 (ADC): {ly}";
            if (adcData.TryGetValue("LeftStick_X", out int lx))
                lblLeftStickX_ADC.Text = $"X轴 (ADC): {lx}";
            if (adcData.TryGetValue("RightStick_Y", out int ry))
                lblRightStickY_ADC.Text = $"Y轴 (ADC): {ry}";
            if (adcData.TryGetValue("RightStick_X", out int rx))
                lblRightStickX_ADC.Text = $"X轴 (ADC): {rx}";

            if (voltageData.TryGetValue("LeftStick_Y", out string lyv))
                lblLeftStickY_V.Text = $"Y轴 (V): {lyv}V";
            if (voltageData.TryGetValue("LeftStick_X", out string lxv))
                lblLeftStickX_V.Text = $"X轴 (V): {lxv}V";
            if (voltageData.TryGetValue("RightStick_Y", out string ryv))
                lblRightStickY_V.Text = $"Y轴 (V): {ryv}V";
            if (voltageData.TryGetValue("RightStick_X", out string rxv))
                lblRightStickX_V.Text = $"X轴 (V): {rxv}V";

            if (percentData.TryGetValue("LeftStick_Y", out string lyp))
                lblLeftStickY_Percent.Text = $"Y轴 (%): {lyp}%";
            if (percentData.TryGetValue("LeftStick_X", out string lxp))
                lblLeftStickX_Percent.Text = $"X轴 (%): {lxp}%";
            if (percentData.TryGetValue("RightStick_Y", out string ryp))
                lblRightStickY_Percent.Text = $"Y轴 (%): {ryp}%";
            if (percentData.TryGetValue("RightStick_X", out string rxp))
                lblRightStickX_Percent.Text = $"X轴 (%): {rxp}%";
        }
    }
}
