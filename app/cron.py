import datetime
from app.views import create_excel
from email.header import Header
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib


def push_email(user=1):
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    select_dict = {'company__user_id': user}
    select_dict['order_date'] = yesterday
    file_path = create_excel(select_dict, True, user)
    return file_path


def test():
    from_addr = '2403847839@qq.com'
    password = 'qgplbzmznbudeceh'
    to_addr = '2403847839@qq.com'
    smtp_server = 'smtp.qq.com'
    header = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    file_path = push_email()
    file_name = file_path.split('/')[-1]
    xls = MIMEApplication(open(file_path, 'rb').read())  # 打开Excel,读取Excel文件
    xls["Content-Type"] = 'application/octet-stream'     # 设置内容类型
    xls.add_header('Content-Disposition', 'attachment', filename=file_name) # 添加到header信息

    content = MIMEText(header)
    msg = MIMEMultipart()
    msg.attach(content)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = Header(header, 'utf-8').encode()
    msg.attach(xls)

    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    print('{}  发送成功  {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file_name))
    server.quit()
