import os
import shutil
import subprocess
import logging
import datetime
import time
from email.message import EmailMessage
import smtplib

# Set environment variable to Prod or QA
env = "DEV"

# Set number of days to keep old log files
daysToKeep = 10

# Set job type
jobType = ""

# Set log file directory
log_dir = ".\\logs"

# Set backup file directory
backup_dir = "C:/Program Files/Tableau/Tableau Server/data/tabsvc/files/backups"

# Set shared drive path
shared_dir = "\\\\abc\\tableau\\backups\\daily"

isFileMoved = False
isBackUpCompleted = False
isRebootCompleted = False

smtp_host = 'mail.abc.com'
smtp_port = 25
From = 'backup@abc.com'
To = 'admin@abc.com'
Bcc = ''
admin_dl = 'admin@abc.com'


if not os.path.exists(log_dir):
    os.makedirs(log_dir)
current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_name = f"backup_{current_time}.log"
log_file_path = os.path.join(log_dir, log_file_name)
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


def checkDay():
    # Get the current day
    today = datetime.date.today()
    if today.weekday() < 5 or today.weekday() == 6:
        logging.info('backup type is Daily')
        return 'Daily'
    else:
        logging.info('backup type is Weekly')
        return 'Weekly'


def createLogFile(jobType, log_dir):
    # Create a log file and configure the logging settings
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"{jobType}_{current_time}.log"
    log_file_path = os.path.join(log_dir, log_file_name)
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    return log_file_path


def moveBackupFiles():
    global isFileMoved
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.tsbak')]
    if backup_files:
        # Move backup files to shared directory
        try:
            for backup_file in backup_files:
                move_command = shutil.move(os.path.join(backup_dir, backup_file), shared_dir)
                move_result = subprocess.check_call(move_command.split(), shell=True)
                if move_result == 0:
                    isFileMoved = True
                    logging.info(f'file was moved successfully: {backup_file}')
                else:
                    isFileMoved = False
                    logging.error(f'There was an error while moving file : {backup_file}')
        except Exception as e:
            isFileMoved = False
            logging.exception(f'Exception occurred in moveBackupFiles(): {str(e)}')
    else:
        isFileMoved = True
        logging.info(f'There are no backup files to move: {backup_files}')


def takeBackup(jobType):
    global isBackUpCompleted
    backup_filename = f"{jobType}Backup-{env}"
    # Execute backup command and wait until completion
    backup_command = f"tsm maintenance backup -f {backup_filename} -d --override-disk-space-check --ignore-prompt"
    try:
        # subprocess.check_call() is used to execute the backup_command command and check its return code.
        # If the return code is not zero, an error will be raised.
        backup_result = subprocess.check_call(backup_command.split(), shell=True)
        if backup_result == 0:
            isBackUpCompleted = True
            logging.info(f'Backup was taken successfully: {backup_command}')
        else:
            isBackUpCompleted = False
            logging.error(f'Backup command was failed : {backup_command}')
    except subprocess.CalledProcessError as e:
        isBackUpCompleted = False
        logging.error(f"Backup command failed with error code: {e.returncode}")
        logging.exception(f'Exception occurred in takeBackup(): {str(e)}')


def rebootTableau():
    global isRebootCompleted
    # Execute reboot command and wait until completion
    reboot_command = "tsm restart"
    try:
        # subprocess.check_call() is used to execute the backup_command command and check its return code.
        # If the return code is not zero, an error will be raised.
        reboot_result = subprocess.check_call(reboot_command.split(), shell=True)
        if reboot_result == 0:
            logging.info("tsm restart command executed successfully.")
            # Execute tsm status command
            tsm_status_result = subprocess.check_output(['tsm', 'status'], shell=True)
            # Convert the output to a string
            result_str = tsm_status_result.decode('utf-8')
            # Loop until the string "Running" is present in the output
            while "RUNNING" not in result_str:
                logging.info("Tableau is not started yet. Waiting for 60 seconds")
                time.sleep(60)  # Wait for 60 seconds
                tsm_status_result = subprocess.check_output(['tsm', 'status'])
                result_str = tsm_status_result.decode('utf-8')
            isRebootCompleted = True
            logging.info(f'Reboot was done successfully: {reboot_command}')
        else:
            isRebootCompleted = False
            logging.error(f'Reboot command was failed : {reboot_command}')
    except subprocess.CalledProcessError as e:
        isRebootCompleted = False
        logging.error(f"Reboot command failed with error code: {e.returncode}")
        logging.exception(f'Exception occurred in rebootTableau(): {str(e)}')


def sendSuccessEmail(jobType):
    logging.info(f"Job succeeded: {jobType}")
    try:
        # Set up email message
        msg = EmailMessage()
        msg['Subject'] = f'SUCCESS: {env} {jobType} BACKUP'
        msg['From'] = From
        msg['To'] = To
        msg['Bcc'] = ''
        # Create HTML table with updated role information for the user
        email_body = ""
        msg.set_content(email_body)
        msg.add_alternative(f"""
                        <!DOCTYPE html>
                        <html>
                          <body style='font-family: Merriweather; font-size: 11px;'>
                            <p style='color: #44546A;'>Dear Admin Team,</p>
                            <p style='color: #44546A;'><b>{env} {jobType} BACKUP COMPLETED.</b></p>
                            <p style='color: #44546A;'>Regards, <br>Backup Automation</p>
                          </body>
                        </html>""", subtype='html')
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")


def sendFailedEmail(jobType, log_file_path):
    logging.error(f"Job failed: {jobType}")
    # isFileMoved and isBackUpCompleted and isRebootCompleted log_file_path
    if not isFileMoved:
        body = f"{env} {jobType} BACKUP FAILED WHILE MOVING BACKUP FILE."
    elif not isBackUpCompleted:
        body = f"{env} {jobType} BACKUP FAILED WHILE TAKING BACKUP."
    else:
        body = f"{env} {jobType} BACKUP FAILED WHILE REBOOTING TABLEAU SERVER."
    try:
        # Set up email message
        msg = EmailMessage()
        msg['Subject'] = f'FAILED: {env} {jobType} BACKUP'
        msg['From'] = From
        msg['To'] = To
        msg['Bcc'] = ''
        # Create HTML table with updated role information for the user
        msg.set_content(body)
        msg.add_alternative(f"""
                        <!DOCTYPE html>
                        <html>
                          <body style='font-family: Merriweather; font-size: 11px;'>
                            <p style='color: #44546A;'>Dear Admin Team,</p>
                            <p style='color: #44546A;'>{body}</p>
                            <p style='color: #44546A;'>Please refer to attached log file for more details.</p>
                            <p style='color: #44546A;'>Regards, <br>Backup Automation</p>
                          </body>
                        </html>""", subtype='html')
        with open(log_file_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(log_file_path)
        msg.add_attachment(file_data, maintype='application', subtype='text', filename=file_name)
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")


def delete_old_logs(log_dir):
    current_time = time.time()
    age_cutoff = current_time - (daysToKeep * 86400)  # convert days to seconds
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            if file_time < age_cutoff:
                os.remove(filepath)
                logging.info(f"Deleted {filepath}")


if __name__ == '__main__':
    jobType = checkDay()  # Used to check whether its daily or weekly.
    moveBackupFiles()  # Used to move existing backup files.
    delete_old_logs(log_dir)
    if jobType == "Daily":
        takeBackup(jobType)  # Used to take backup only.
        moveBackupFiles()
        if isFileMoved and isBackUpCompleted:
            sendSuccessEmail(jobType)
        else:
            sendFailedEmail(jobType, log_file_path)
    else:
        takeBackup(jobType)  # Used to take backup only.
        moveBackupFiles()
        rebootTableau()  # Used to reboot Tableau server.
        if isFileMoved and isBackUpCompleted and isRebootCompleted:
            sendSuccessEmail(jobType)
        else:
            sendFailedEmail(jobType, log_file_path)
