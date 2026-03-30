namespace ParseVoltageData
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            _serialPort?.Dispose();
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            panelTop = new Panel();
            cmbPortName = new ComboBox();
            cmbBaudRate = new ComboBox();
            cmbStopBits = new ComboBox();
            cmbDataBits = new ComboBox();
            cmbParity = new ComboBox();
            btnOpenClose = new Button();
            panelDisplay = new Panel();
            lblAdc0 = new Label();
            lblAdc1 = new Label();
            lblAdc2 = new Label();
            lblAdc3 = new Label();
            panelTop.SuspendLayout();
            panelDisplay.SuspendLayout();
            SuspendLayout();

            // panelTop
            panelTop.Dock = DockStyle.Top;
            panelTop.Height = 45;
            panelTop.Padding = new Padding(6, 8, 6, 0);
            panelTop.Controls.AddRange(new Control[] { cmbPortName, cmbBaudRate, cmbDataBits, cmbParity, cmbStopBits, btnOpenClose });

            // cmbPortName
            cmbPortName.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbPortName.Location = new Point(6, 8);
            cmbPortName.Size = new Size(90, 25);
            cmbPortName.TabStop = false;

            // cmbBaudRate
            cmbBaudRate.DropDownStyle = ComboBoxStyle.DropDown;
            cmbBaudRate.Location = new Point(102, 8);
            cmbBaudRate.Size = new Size(80, 25);
            cmbBaudRate.Items.AddRange(new object[] { "9600", "19200", "38400", "57600", "115200" });
            cmbBaudRate.Text = "115200";
            cmbBaudRate.TabStop = false;

            // cmbDataBits
            cmbDataBits.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbDataBits.Location = new Point(188, 8);
            cmbDataBits.Size = new Size(65, 25);
            cmbDataBits.Items.AddRange(new object[] { "7", "8" });
            cmbDataBits.SelectedIndex = 1;
            cmbDataBits.TabStop = false;

            // cmbParity
            cmbParity.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbParity.Location = new Point(259, 8);
            cmbParity.Size = new Size(65, 25);
            cmbParity.Items.AddRange(new object[] { "None", "Odd", "Even", "Mark", "Space" });
            cmbParity.SelectedIndex = 0;
            cmbParity.TabStop = false;

            // cmbStopBits
            cmbStopBits.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbStopBits.Location = new Point(330, 8);
            cmbStopBits.Size = new Size(65, 25);
            cmbStopBits.Items.AddRange(new object[] { "1", "1.5", "2" });
            cmbStopBits.SelectedIndex = 0;
            cmbStopBits.TabStop = false;

            // btnOpenClose
            btnOpenClose.Location = new Point(401, 7);
            btnOpenClose.Size = new Size(75, 28);
            btnOpenClose.Text = "打开串口";
            btnOpenClose.UseVisualStyleBackColor = true;
            btnOpenClose.TabStop = false;
            btnOpenClose.Click += btnOpenClose_Click;

            // panelDisplay
            panelDisplay.Dock = DockStyle.Fill;
            panelDisplay.Padding = new Padding(20);

            // lblAdc0
            lblAdc0.Dock = DockStyle.Top;
            lblAdc0.Font = new Font("Consolas", 12F, FontStyle.Bold);
            lblAdc0.TextAlign = ContentAlignment.MiddleCenter;
            lblAdc0.Text = "ADC[0]: --";

            // lblAdc1
            lblAdc1.Dock = DockStyle.Top;
            lblAdc1.Font = new Font("Consolas", 12F, FontStyle.Bold);
            lblAdc1.TextAlign = ContentAlignment.MiddleCenter;
            lblAdc1.Text = "ADC[1]: --";

            // lblAdc2
            lblAdc2.Dock = DockStyle.Top;
            lblAdc2.Font = new Font("Consolas", 12F, FontStyle.Bold);
            lblAdc2.TextAlign = ContentAlignment.MiddleCenter;
            lblAdc2.Text = "ADC[2]: --";

            // lblAdc3
            lblAdc3.Dock = DockStyle.Top;
            lblAdc3.Font = new Font("Consolas", 12F, FontStyle.Bold);
            lblAdc3.TextAlign = ContentAlignment.MiddleCenter;
            lblAdc3.Text = "ADC[3]: --";

            panelDisplay.Controls.Add(lblAdc3);
            panelDisplay.Controls.Add(lblAdc2);
            panelDisplay.Controls.Add(lblAdc1);
            panelDisplay.Controls.Add(lblAdc0);

            // Form1
            AutoScaleDimensions = new SizeF(7F, 17F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(600, 400);
            Controls.Add(panelDisplay);
            Controls.Add(panelTop);
            Text = "电压数据解析";
            StartPosition = FormStartPosition.CenterScreen;

            panelTop.ResumeLayout(false);
            panelTop.PerformLayout();
            panelDisplay.ResumeLayout(false);
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Panel panelTop;
        private ComboBox cmbPortName;
        private ComboBox cmbBaudRate;
        private ComboBox cmbDataBits;
        private ComboBox cmbParity;
        private ComboBox cmbStopBits;
        private Button btnOpenClose;
        private Panel panelDisplay;
        private Label lblAdc0;
        private Label lblAdc1;
        private Label lblAdc2;
        private Label lblAdc3;
    }
}
