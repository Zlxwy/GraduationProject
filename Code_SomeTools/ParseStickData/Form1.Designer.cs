namespace ParseStickData
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
            btnRefresh = new Button();
            btnClear = new Button();
            splitContainer1 = new SplitContainer();
            panelDataLeft = new Panel();
            lblLeftStickTitle = new Label();
            lblLeftStickY_ADC = new Label();
            lblLeftStickX_ADC = new Label();
            lblLeftStickY_V = new Label();
            lblLeftStickX_V = new Label();
            lblLeftStickY_Percent = new Label();
            lblLeftStickX_Percent = new Label();
            panelDataRight = new Panel();
            lblRightStickTitle = new Label();
            lblRightStickY_ADC = new Label();
            lblRightStickX_ADC = new Label();
            lblRightStickY_V = new Label();
            lblRightStickX_V = new Label();
            lblRightStickY_Percent = new Label();
            lblRightStickX_Percent = new Label();
            txtReceive = new TextBox();
            statusStrip1 = new StatusStrip();
            lblStatus = new ToolStripStatusLabel();
            lblDataCount = new ToolStripStatusLabel();
            panelTop.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)splitContainer1).BeginInit();
            splitContainer1.Panel1.SuspendLayout();
            splitContainer1.Panel2.SuspendLayout();
            splitContainer1.SuspendLayout();
            panelDataLeft.SuspendLayout();
            panelDataRight.SuspendLayout();
            statusStrip1.SuspendLayout();
            SuspendLayout();

            // panelTop
            panelTop.Dock = DockStyle.Top;
            panelTop.Height = 45;
            panelTop.Padding = new Padding(6, 8, 6, 0);
            panelTop.Controls.AddRange(new Control[] { cmbPortName, cmbBaudRate, cmbDataBits, cmbParity, cmbStopBits, btnOpenClose, btnRefresh, btnClear });

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

            // btnRefresh
            btnRefresh.Location = new Point(482, 7);
            btnRefresh.Size = new Size(50, 28);
            btnRefresh.Text = "刷新";
            btnRefresh.UseVisualStyleBackColor = true;
            btnRefresh.TabStop = false;
            btnRefresh.Click += btnRefresh_Click;

            // btnClear
            btnClear.Location = new Point(538, 7);
            btnClear.Size = new Size(50, 28);
            btnClear.Text = "清空";
            btnClear.UseVisualStyleBackColor = true;
            btnClear.TabStop = false;
            btnClear.Click += btnClear_Click;

            // splitContainer1
            splitContainer1.Dock = DockStyle.Fill;
            splitContainer1.SplitterDistance = 285;
            splitContainer1.Panel1.Controls.Add(panelDataLeft);
            splitContainer1.Panel2.Controls.Add(panelDataRight);

            // panelDataLeft
            panelDataLeft.Dock = DockStyle.Fill;
            panelDataLeft.BackColor = Color.FromArgb(30, 30, 30);
            panelDataLeft.Padding = new Padding(10);
            panelDataLeft.Controls.Add(lblLeftStickTitle);
            panelDataLeft.Controls.Add(lblLeftStickY_ADC);
            panelDataLeft.Controls.Add(lblLeftStickX_ADC);
            panelDataLeft.Controls.Add(lblLeftStickY_V);
            panelDataLeft.Controls.Add(lblLeftStickX_V);
            panelDataLeft.Controls.Add(lblLeftStickY_Percent);
            panelDataLeft.Controls.Add(lblLeftStickX_Percent);

            // lblLeftStickTitle
            lblLeftStickTitle.AutoSize = true;
            lblLeftStickTitle.Font = new Font("Microsoft YaHei UI", 12F, FontStyle.Bold);
            lblLeftStickTitle.ForeColor = Color.FromArgb(100, 200, 255);
            lblLeftStickTitle.Location = new Point(10, 10);
            lblLeftStickTitle.Text = "左摇杆";

            // lblLeftStickY_ADC
            lblLeftStickY_ADC.AutoSize = true;
            lblLeftStickY_ADC.Font = new Font("Consolas", 10F);
            lblLeftStickY_ADC.ForeColor = Color.FromArgb(220, 220, 220);
            lblLeftStickY_ADC.Location = new Point(10, 45);
            lblLeftStickY_ADC.Text = "Y轴 (ADC): --";

            // lblLeftStickX_ADC
            lblLeftStickX_ADC.AutoSize = true;
            lblLeftStickX_ADC.Font = new Font("Consolas", 10F);
            lblLeftStickX_ADC.ForeColor = Color.FromArgb(220, 220, 220);
            lblLeftStickX_ADC.Location = new Point(10, 70);
            lblLeftStickX_ADC.Text = "X轴 (ADC): --";

            // lblLeftStickY_V
            lblLeftStickY_V.AutoSize = true;
            lblLeftStickY_V.Font = new Font("Consolas", 10F);
            lblLeftStickY_V.ForeColor = Color.FromArgb(220, 220, 220);
            lblLeftStickY_V.Location = new Point(10, 100);
            lblLeftStickY_V.Text = "Y轴 (V): --";

            // lblLeftStickX_V
            lblLeftStickX_V.AutoSize = true;
            lblLeftStickX_V.Font = new Font("Consolas", 10F);
            lblLeftStickX_V.ForeColor = Color.FromArgb(220, 220, 220);
            lblLeftStickX_V.Location = new Point(10, 125);
            lblLeftStickX_V.Text = "X轴 (V): --";

            // lblLeftStickY_Percent
            lblLeftStickY_Percent.AutoSize = true;
            lblLeftStickY_Percent.Font = new Font("Consolas", 10F);
            lblLeftStickY_Percent.ForeColor = Color.FromArgb(220, 220, 220);
            lblLeftStickY_Percent.Location = new Point(10, 155);
            lblLeftStickY_Percent.Text = "Y轴 (%): --";

            // lblLeftStickX_Percent
            lblLeftStickX_Percent.AutoSize = true;
            lblLeftStickX_Percent.Font = new Font("Consolas", 10F);
            lblLeftStickX_Percent.ForeColor = Color.FromArgb(220, 220, 220);
            lblLeftStickX_Percent.Location = new Point(10, 180);
            lblLeftStickX_Percent.Text = "X轴 (%): --";

            // panelDataRight
            panelDataRight.Dock = DockStyle.Fill;
            panelDataRight.BackColor = Color.FromArgb(30, 30, 30);
            panelDataRight.Padding = new Padding(10);
            panelDataRight.Controls.Add(lblRightStickTitle);
            panelDataRight.Controls.Add(lblRightStickY_ADC);
            panelDataRight.Controls.Add(lblRightStickX_ADC);
            panelDataRight.Controls.Add(lblRightStickY_V);
            panelDataRight.Controls.Add(lblRightStickX_V);
            panelDataRight.Controls.Add(lblRightStickY_Percent);
            panelDataRight.Controls.Add(lblRightStickX_Percent);

            // lblRightStickTitle
            lblRightStickTitle.AutoSize = true;
            lblRightStickTitle.Font = new Font("Microsoft YaHei UI", 12F, FontStyle.Bold);
            lblRightStickTitle.ForeColor = Color.FromArgb(255, 150, 100);
            lblRightStickTitle.Location = new Point(10, 10);
            lblRightStickTitle.Text = "右摇杆";

            // lblRightStickY_ADC
            lblRightStickY_ADC.AutoSize = true;
            lblRightStickY_ADC.Font = new Font("Consolas", 10F);
            lblRightStickY_ADC.ForeColor = Color.FromArgb(220, 220, 220);
            lblRightStickY_ADC.Location = new Point(10, 45);
            lblRightStickY_ADC.Text = "Y轴 (ADC): --";

            // lblRightStickX_ADC
            lblRightStickX_ADC.AutoSize = true;
            lblRightStickX_ADC.Font = new Font("Consolas", 10F);
            lblRightStickX_ADC.ForeColor = Color.FromArgb(220, 220, 220);
            lblRightStickX_ADC.Location = new Point(10, 70);
            lblRightStickX_ADC.Text = "X轴 (ADC): --";

            // lblRightStickY_V
            lblRightStickY_V.AutoSize = true;
            lblRightStickY_V.Font = new Font("Consolas", 10F);
            lblRightStickY_V.ForeColor = Color.FromArgb(220, 220, 220);
            lblRightStickY_V.Location = new Point(10, 100);
            lblRightStickY_V.Text = "Y轴 (V): --";

            // lblRightStickX_V
            lblRightStickX_V.AutoSize = true;
            lblRightStickX_V.Font = new Font("Consolas", 10F);
            lblRightStickX_V.ForeColor = Color.FromArgb(220, 220, 220);
            lblRightStickX_V.Location = new Point(10, 125);
            lblRightStickX_V.Text = "X轴 (V): --";

            // lblRightStickY_Percent
            lblRightStickY_Percent.AutoSize = true;
            lblRightStickY_Percent.Font = new Font("Consolas", 10F);
            lblRightStickY_Percent.ForeColor = Color.FromArgb(220, 220, 220);
            lblRightStickY_Percent.Location = new Point(10, 155);
            lblRightStickY_Percent.Text = "Y轴 (%): --";

            // lblRightStickX_Percent
            lblRightStickX_Percent.AutoSize = true;
            lblRightStickX_Percent.Font = new Font("Consolas", 10F);
            lblRightStickX_Percent.ForeColor = Color.FromArgb(220, 220, 220);
            lblRightStickX_Percent.Location = new Point(10, 180);
            lblRightStickX_Percent.Text = "X轴 (%): --";

            // txtReceive
            txtReceive.Dock = DockStyle.Bottom;
            txtReceive.Height = 100;
            txtReceive.Multiline = true;
            txtReceive.ReadOnly = true;
            txtReceive.ScrollBars = ScrollBars.Vertical;
            txtReceive.Font = new Font("Consolas", 9F);
            txtReceive.BackColor = Color.FromArgb(25, 25, 25);
            txtReceive.ForeColor = Color.FromArgb(180, 180, 180);

            // statusStrip1
            statusStrip1.Dock = DockStyle.Bottom;
            statusStrip1.Items.AddRange(new ToolStripItem[] { lblStatus, lblDataCount });
            statusStrip1.BackColor = Color.FromArgb(45, 45, 45);
            statusStrip1.ForeColor = Color.FromArgb(200, 200, 200);

            // lblStatus
            lblStatus.Text = "未连接";
            lblStatus.ForeColor = Color.FromArgb(200, 200, 200);
            lblStatus.Margin = new Padding(5, 0, 20, 0);

            // lblDataCount
            lblDataCount.Text = "接收: 0 字节";
            lblDataCount.ForeColor = Color.FromArgb(150, 200, 150);
            lblDataCount.Spring = true;
            lblDataCount.TextAlign = ContentAlignment.MiddleRight;

            // Form1
            AutoScaleDimensions = new SizeF(7F, 17F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(600, 450);
            Controls.Add(splitContainer1);
            Controls.Add(txtReceive);
            Controls.Add(statusStrip1);
            Controls.Add(panelTop);
            Text = "摇杆数据显示";
            StartPosition = FormStartPosition.CenterScreen;
            Resize += Form1_Resize;
            FormClosing += Form1_FormClosing;

            panelTop.ResumeLayout(false);
            panelTop.PerformLayout();
            splitContainer1.Panel1.ResumeLayout(false);
            splitContainer1.Panel2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)splitContainer1).EndInit();
            splitContainer1.ResumeLayout(false);
            panelDataLeft.ResumeLayout(false);
            panelDataLeft.PerformLayout();
            panelDataRight.ResumeLayout(false);
            panelDataRight.PerformLayout();
            statusStrip1.ResumeLayout(false);
            statusStrip1.PerformLayout();
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
        private Button btnRefresh;
        private Button btnClear;
        private SplitContainer splitContainer1;
        private Panel panelDataLeft;
        private Label lblLeftStickTitle;
        private Label lblLeftStickY_ADC;
        private Label lblLeftStickX_ADC;
        private Label lblLeftStickY_V;
        private Label lblLeftStickX_V;
        private Label lblLeftStickY_Percent;
        private Label lblLeftStickX_Percent;
        private Panel panelDataRight;
        private Label lblRightStickTitle;
        private Label lblRightStickY_ADC;
        private Label lblRightStickX_ADC;
        private Label lblRightStickY_V;
        private Label lblRightStickX_V;
        private Label lblRightStickY_Percent;
        private Label lblRightStickX_Percent;
        private TextBox txtReceive;
        private StatusStrip statusStrip1;
        private ToolStripStatusLabel lblStatus;
        private ToolStripStatusLabel lblDataCount;
    }
}
