---

# 🚀 **Tableau Server Backup Automation Script**

## 📝 **Overview**

This Python script is your go-to solution for automating Tableau Server backups. It ensures that backups are systematically created, securely stored, and managed without manual intervention. Whether it's daily maintenance or weekly deep dives, this script has you covered!

## 🌟 **Key Features**

- **🕒 Automated Scheduling**: Seamlessly switches between daily and weekly backups based on the day of the week.
- **💾 Backup Management**: Effortlessly moves backup files to a specified shared network drive.
- **🔄 Server Reboot**: Automatically restarts Tableau Server after weekly backups to maintain optimal performance.
- **🗑️ Log Maintenance**: Keeps your log files tidy by deleting old logs after a specified retention period.
- **📧 Email Alerts**: Sends detailed email notifications for both successful and failed backup operations.

## ⚙️ **Configuration**

- **🌐 Environment**: 
  - `env`: Set the environment (`DEV`, `QA`, `PROD`) based on your deployment.
- **📁 Directories**: 
  - `log_dir`: Directory for storing log files (Default: `.\\logs`).
  - `backup_dir`: Tableau's backup file location (Default: `C:/Program Files/Tableau/Tableau Server/data/tabsvc/files/backups`).
  - `shared_dir`: Network path for backup file storage (Default: `\\\\abc\\tableau\\backups\\daily`).
- **✉️ Email Settings**:
  - `smtp_host`: SMTP server hostname (e.g., `mail.abc.com`).
  - `smtp_port`: SMTP server port (Default: `25`).
  - `From`: Email address used for sending notifications (e.g., `backup@abc.com`).
  - `To`: Email address for receiving notifications (e.g., `admin@abc.com`).

## 📜 **Script Workflow**

1. **📅 Determine Backup Type**:
   - The script intelligently identifies whether to perform a daily or weekly backup based on the current day.

2. **📤 Move Existing Backups**:
   - Before a new backup is created, the script relocates existing backups to a secure shared drive.

3. **🧹 Cleanup Old Logs**:
   - Automatically deletes log files older than the configured retention period to keep your storage clean.

4. **💽 Execute Backup**:
   - Runs the Tableau Server backup command and ensures completion with robust error handling.

5. **🔄 Reboot Server (Weekly Only)**:
   - For weekly backups, the script performs a safe reboot of the Tableau Server and verifies its status.

6. **📧 Email Notifications**:
   - Success or failure notifications are dispatched with detailed logs, ensuring you’re always in the loop.

## ⚠️ **Error Handling**

- **🔍 Detailed Logging**: Each step is meticulously logged, capturing successes and any potential issues.
- **📤 Failure Alerts**: In case of failure, an email is sent with an attached log file detailing the issue.

## 💡 **Usage Instructions**

1. Ensure Python is installed and properly configured on the system.
2. Adjust the environment variables and file paths to suit your setup.
3. Schedule the script using Windows Task Scheduler or a similar tool for regular execution.

## 🛠️ **Sample Execution**

```bash
python tableau_backup.py
```

## 📜 **License**

This project is licensed under the MIT License. Please see the [LICENSE](./LICENSE) file for more details.

---
