/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace Lab1
{
    public partial class MailingForm : Form
    {

        public MailingForm()
        {
            InitializeComponent();
            this.HandleCreated += new EventHandler(YourWindow_HandleCreated);
        }

        void YourWindow_HandleCreated(object sender, EventArgs e)
        {
            this.BeginInvoke(new MethodInvoker(FocusFirst));
        }

        void FocusFirst()
        {
            this.firstNameTextBox.Focus();
        }

        private void displayLabelInfoButton_Click(object sender, EventArgs e)
        {
            infoLabel.Text = firstNameTextBox.Text + " " + lastNameTextBox.Text + "\n" + streetTextBox.Text + "\n" + cityTextBox.Text + ", " + stateTextBox.Text + "  " + zipcodeTextBox.Text;
        }

        private void clearButton_Click(object sender, EventArgs e)
        {
            firstNameTextBox.Text = "";
            lastNameTextBox.Text = "";
            streetTextBox.Text = "";
            cityTextBox.Text = "";
            stateTextBox.Text = "";
            zipcodeTextBox.Text = "";
            infoLabel.Text = "";
            firstNameTextBox.Focus();
        }

        private void exitButton_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void toolStripContainer1_TopToolStripPanel_Click(object sender, EventArgs e)
        {
          private void openToolStripMenuItem_Click(object sender, EventArgs e)
          {
            this.Close();
          }
        }

    }
}
