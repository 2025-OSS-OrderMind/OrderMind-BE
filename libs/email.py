import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr
import os
# 위 패키지들은 기본 파이썬에 내장된 패키지들이기 때문에 requirements.txt를 수정할 필요가 없음

GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

def send_email(sender_email, sender_name, receiver_email, subject, body, password, attachments=[]):
    '''
    ### 매개 변수
    sender_email: 발신자 이메일  
    sender_name: 발신자 이름 (한글 가능)  
    receiver_email: 수신자 이메일  
    subject: 이메일 제목  
    body: 이메일 내용  
    attachments: 파일 경로 리스트  
      
    ---

    ### 예시 코드
      
    email_module.send_email("ordermind@gmail.com", "OrderMind",
                        "20221995@edu.hanbat.ac.kr", "\[OrderMind\] 주문 종합이 완료됐어요!",
                        "마지막 메일테스트를 해보겠습니다", "[PASSWORD](https://jimmy-ai.tistory.com/451)",
                        ["25XXXX_주문종합.csv"])
    
    '''

    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
    msg['To'] = receiver_email
    msg['Subject'] = Header(subject, 'utf-8')

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    for filepath in attachments:
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        filename = os.path.basename(filepath)
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=("utf-8", "", filename)
            # (encoding, language, filename)
        )
        msg.attach(part)


    smtp_server = "smtp.gmail.com"
    port = 587

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    server.send_message(msg)
    server.quit()

    print("메일 전송 완료")