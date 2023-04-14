import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()
# Disable SSL certificate verification
requests.packages.urllib3.disable_warnings()

url = os.getenv('URL')

sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
receiver_email = os.getenv('RECEIVER_EMAIL')
subject = 'Erasmus Sitesi Güncellendi'
message = """\
<html>
  <head></head>
  <body>
    <p>Merhaba,</p>
    <p>Erasmus sınav sonuçları websitesinde bir güncelleme oldu. İncelemek için aşağıdaki linke tıklayabilirsiniz:</p>
    <p><a href="{url}">{url}</a></p>
  </body>
</html>
""".format(url=url)
server = os.getenv('SERVER')
port = os.getenv('PORT')

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(message, 'html'))

prev_value = None

while True:

    response = requests.get(url, verify=False)

    # Check the status code of the response
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        div_tag = soup.find('div', {'class': 'col-md-8 text-left'})
        ul_tag = div_tag.find('ul')
        first_li = ul_tag.find_all('li')[1]

        if prev_value is not None and first_li.text.strip() != prev_value:
            # Send a notification
            print('Value has changed from {} to {}'.format(prev_value, first_li.text.strip()))

            try:
                with smtplib.SMTP_SSL(server, port) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                    server.quit()
                print("Email sent successfully!")
                break;
            except:
                print("An error occured while sending the email")
                break;

        prev_value = first_li.text.strip()
        print(first_li.text.strip())

    else:
        print('Failed to fetch data')

    time.sleep(5)
