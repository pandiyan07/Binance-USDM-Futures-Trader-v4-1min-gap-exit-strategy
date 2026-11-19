from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from datetime import datetime
from email import encoders
import pandas as pd
import smtplib
import time
import traceback
import logging
import os


# Configure the logging
log_file = "binfut_trading_bot.log"  # Define the log file name
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),  # Log to a file
        logging.StreamHandler()  # Log to the console (terminal)
    ]
)

# Create a logger instance
logger = logging.getLogger()
# Get the absolute path of the log file
log_file_path = os.path.abspath(log_file)

error_file = 'error_log.txt'
error_file_path = os.path.abspath(error_file)




def ERROR_FLOWCHART(e):
    tb = traceback.extract_tb(e.__traceback__)
    line_number = tb[-1].lineno
    with open("error_log.txt", "w") as f:
        f.write(f"Error occurred on line: {line_number}")
        f.write('\n')
        f.write(f"An error occurred: {e}")
        f.write('\n\n')
        traceback.print_exc(file=f)


# Function to send an email with a text file attachment
def EMAIL_SENDER(status,argument):
    # Create the email object
    msg = MIMEMultipart()
    current_time = datetime.now()
    if argument is not None:
        liv_pos = argument[0]  
    else:
        liv_pos = None

    if status == 'ORDER PLACED':
        subject = f"OPENED A ORDER"
        body = f"<b>{liv_pos}</b> open order placed at = <b>{current_time.strftime('%Y-%m-%d')}</b> at  <b>{current_time.strftime('%H:%M:%S')}</b>" 
        mo = argument[1]
        body1 = f"<b>{mo['type']}</b> ====> {mo['side']} , {mo['orderId']} , {mo['symbol']} , {mo['status']} , {mo['origQty']} , {mo['updateTime']}"
        
        slo = argument[2]
        body2 = f"<b>{slo['type']}</b> ====> {slo['side']} , {slo['orderId']} , {slo['symbol']} , {slo['status']} , {slo['origQty']} , {slo['updateTime']}"
        
        tslo = argument[3]
        body3 = f"<b>{tslo['type']}</b> ====> {tslo['side']} , {tslo['orderId']} , {tslo['symbol']} , {tslo['status']} , {tslo['origQty']} , {tslo['updateTime']}"
        
        df = argument[4]
        html_table = df.to_html(index=False)
        
        full_body = f"{body}<br><br>{body1}<br>{body2}<br>{body3}<br><br>{html_table}"
        #full_body = f"{body}{body1}{body2}{body3}"
        msg.attach(MIMEText(full_body, 'html'))
    
    if status == 'ORDER CLOSED':
        subject = f"CLOSED A ORDER"
        body = f"<b>{liv_pos}</b> close order placed at = <b>{current_time.strftime('%Y-%m-%d')}</b> at  <b>{current_time.strftime('%H:%M:%S')}</b>" 
        
        co = argument[1]
        
        if co:
            body1 = f"<b>{co['type']}</b> ====> {co['side']} , {co['orderId']} , {co['symbol']} , {co['status']} , {co['origQty']} , {co['updateTime']}"
        else:
            body1 = f"CLOSE ORDER has NOT been placed, it seems the SL/TSL has been executed"
            logger.info(f'CLOSE ORDER has NOT been placed, it seems the SL/TSL has been executed')
        
        body2 = f"The current status of all the orders are = <br><b>{argument[2]}</b>"
        
        df = argument[3]
        html_table = df.to_html(index=False)
        
        # Attach the body text
        full_body = f"{body}<br><br>{body1}<br><br>{body2}<br><br>{html_table}"
        msg.attach(MIMEText(full_body, 'html'))
    
    if status == 'PRE-EXISTING ORDER CLOSED':
        subject = f"A PRE-EXISTING ORDER HAS BEEN CLOSED"
        body = f"This Error popped up on {argument[0]}"
        body1 = f"Please find the attached trading bot log file located at = {argument[1]}"
        
        # Attach the body text
        full_body = f"{body}<br><br>{body1}"
        msg.attach(MIMEText(full_body, 'html'))
        
    if status == 'ERROR':
        subject = f"ERROR IN THE BINANCE FUTURE TRADING BOT"
        body = f"This Error popped up on {current_time.strftime('%Y-%m-%d')} at {current_time.strftime('%H:%M:%S')} = {argument[0]}"
        body1 = f"Please find the attached trading bot log file located at = {log_file_path}"
        # Attach the body text
        msg.attach(MIMEText(f"{body} <br><br> {body1}", 'html'))
        
        # Attach the log files
        with open(log_file_path, "rb") as attachment1:
            part1 = MIMEBase('application', 'octet-stream')
            part1.set_payload((attachment1).read())
            encoders.encode_base64(part1)
            part1.add_header('Content-Disposition', f"attachment1; filename= {os.path.basename(log_file_path)}")
            msg.attach(part1)
        with open(error_file_path, "rb") as attachment2:
            part2 = MIMEBase('application', 'octet-stream')
            part2.set_payload(attachment2.read())
            encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', f"attachment2; filename= {os.path.basename(error_file_path)}")
            msg.attach(part2)
    
    if status == 'START':
        import requests

        def get_public_ip():
            try:
                response = requests.get('https://api.ipify.org?format=json')
                response.raise_for_status()  # Check if request was successful
                ip = response.json().get('ip')
                return ip
            except requests.RequestException as e:
                print(f"Error fetching IP address: {e}")
                return None

        # Usage
        my_ip = get_public_ip()
        if my_ip:
            print("Your public current IP address is = ", my_ip)
        else:
            print("Could not retrieve my current IP address = ", my_ip)
        
        if liv_pos:
            print ('the argument is =\n',liv_pos)
            arg = {}
            arg.update({'symbol':liv_pos['symbol']})
            arg.update({'positionAmt':liv_pos['positionAmt']})
            arg.update({'BTCUSDT':liv_pos['entryPrice']})
            arg.update({'entryPrice':liv_pos['unRealizedProfit']})
            arg.update({'leverage':liv_pos['leverage']})
            arg.update({'isolatedMargin':liv_pos['isolatedMargin']})
            arg.update({'notional':liv_pos['notional']})
            arg.update({'marginType':liv_pos['marginType']})
            arg.update({'isolatedWallet':liv_pos['isolatedWallet']})
            
            body1 = "\nHere are the details:\n"
            for key, value in arg.items():
                body1 += f"{key}: {value}\n"
        else:
            body1 = None
            
        subject = "TRADING PYTHON BOT IN THE VPS HAS STARTED RUNNING"
        body = f"{my_ip} = Program has started running on {current_time.strftime('%Y-%m-%d')} at  {current_time.strftime('%H:%M:%S')}" 
        
        body2 = argument[1]
        
        full_body = f"{body}<br><br>{body1}<br><br>{body2}"
        
        # Attach the body text
        msg.attach(MIMEText(full_body, 'html'))
        
    
    if status == 'DUMP':
        subject = "PANDIYAN'S DAILY BINANCE FUTURE TRADING REPORT"
        body = "Please find the attached trading report for today's session as well as the table below."
        filtered_df = argument[0]
        
        if filtered_df is not None:
            # Convert DataFrame to HTML and attach it in the body
            html_table = filtered_df.to_html(index=False)  # Convert DataFrame to HTML format (without index)
            body_with_table = f"{body} <br><br> {html_table}"
            # Attach the HTML-formatted DataFrame in the email body
            msg.attach(MIMEText(body_with_table, 'html'))

            # Create a text file (or use an existing file)
            excel_file = "daily_report.xlsx"
            filtered_df.to_excel(excel_file, index=False)  # Save DataFrame as CSV

            # Open the file to attach
            with open(excel_file, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {excel_file}")
                msg.attach(part)
        else:
            print('\n\n\nTHERE IS NO TRADE TODAY\n\n\n')
    
    
    sender_email = "becool.pandiyan@gmail.com"
    sender_password = "bymthsinqckstzod"
    receiver_email = ["nithyananth3377@gmail.com","becool.pandiyan@gmail.com"] 

    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_email)
    msg['Subject'] = subject
    
    # Connect to the Gmail SMTP server and send the email
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=60)  # Gmail SMTP server
    except Exception as e:
        retry_delay = 10
        print(f"Retrying in {retry_delay} seconds...")
        ERROR_FLOWCHART(e)
        EMAIL_SENDER('ERROR',e)
        time.sleep(retry_delay)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    logger.info(f"EMAIL SENT = to {receiver_email} at {current_time}, with the email's subject as follows =")
    logger.info(f'{subject} at {datetime.now()}')
    server.quit()



if __name__ == "__main__":
    logger.warning(f'\n\nThis is just a support file which has some extra code.\n Run the main file = main.py')