namespace CRC16Calculation
{
  partial class Form1
  {
    /// <summary>
    ///  Required designer variable.
    /// </summary>
    private System.ComponentModel.IContainer components = null;

    /// <summary>
    ///  Clean up any resources being used.
    /// </summary>
    /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
    protected override void Dispose(bool disposing) {
      if (disposing && (components != null)) {
        components.Dispose();
      }
      base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    /// <summary>
    ///  Required method for Designer support - do not modify
    ///  the contents of this method with the code editor.
    /// </summary>
    private void InitializeComponent() {
      this.label1 = new System.Windows.Forms.Label();
      this.txtInput = new System.Windows.Forms.TextBox();
      this.GenerateButton = new System.Windows.Forms.Button();
      this.label2 = new System.Windows.Forms.Label();
      this.txtOutput = new System.Windows.Forms.TextBox();
      this.ClearButton = new System.Windows.Forms.Button();
      this.SuspendLayout();
      //
      // label1
      //
      this.label1.AutoSize = true;
      this.label1.Location = new System.Drawing.Point(30, 30);
      this.label1.Name = "label1";
      this.label1.Size = new System.Drawing.Size(68, 17);
      this.label1.TabIndex = 0;
      this.label1.Text = "输入数据：";
      //
      // txtInput
      //
      this.txtInput.Location = new System.Drawing.Point(110, 27);
      this.txtInput.Name = "txtInput";
      this.txtInput.Size = new System.Drawing.Size(300, 23);
      this.txtInput.TabIndex = 2;
      //
      // GenerateButton
      //
      this.GenerateButton.Location = new System.Drawing.Point(430, 25);
      this.GenerateButton.Name = "GenerateButton";
      this.GenerateButton.Size = new System.Drawing.Size(100, 30);
      this.GenerateButton.TabIndex = 4;
      this.GenerateButton.Text = "生成";
      this.GenerateButton.UseVisualStyleBackColor = true;
      this.GenerateButton.Click += new System.EventHandler(this.GenerateButton_Click);
      //
      // label2
      //
      this.label2.AutoSize = true;
      this.label2.Location = new System.Drawing.Point(30, 73);
      this.label2.Name = "label2";
      this.label2.Size = new System.Drawing.Size(80, 17);
      this.label2.TabIndex = 1;
      this.label2.Text = "CRC16结果：";
      //
      // txtOutput
      //
      this.txtOutput.Location = new System.Drawing.Point(110, 70);
      this.txtOutput.Name = "txtOutput";
      this.txtOutput.ReadOnly = true;
      this.txtOutput.Size = new System.Drawing.Size(300, 23);
      this.txtOutput.TabIndex = 3;
      //
      // ClearButton
      //
      this.ClearButton.Location = new System.Drawing.Point(430, 68);
      this.ClearButton.Name = "ClearButton";
      this.ClearButton.Size = new System.Drawing.Size(100, 30);
      this.ClearButton.TabIndex = 5;
      this.ClearButton.Text = "清空";
      this.ClearButton.UseVisualStyleBackColor = true;
      this.ClearButton.Click += new System.EventHandler(this.ClearButton_Click);
      //
      // Form1
      //
      this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 17F);
      this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
      this.ClientSize = new System.Drawing.Size(560, 125);
      this.Controls.Add(this.label1);
      this.Controls.Add(this.txtInput);
      this.Controls.Add(this.GenerateButton);
      this.Controls.Add(this.label2);
      this.Controls.Add(this.txtOutput);
      this.Controls.Add(this.ClearButton);
      this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
      this.MaximizeBox = false;
      this.Name = "Form1";
      this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
      this.Text = "CRC16计算器";

      this.ResumeLayout(false);
      this.PerformLayout();
    }

    #endregion

    private System.Windows.Forms.Label label1;
    private System.Windows.Forms.TextBox txtInput;
    private System.Windows.Forms.Button GenerateButton;
    private System.Windows.Forms.Label label2;
    private System.Windows.Forms.TextBox txtOutput;
    private System.Windows.Forms.Button ClearButton;
  }
}
