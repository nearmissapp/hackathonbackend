# notification_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import base64
from email.mime.image import MIMEImage
import requests
import json

class NotificationSender:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = os.getenv("EMAIL_APP_MAIL")    # 환경 변수에서 이메일 주소 가져오기
        self.password = os.getenv("EMAIL_APP_PASSWORD")  # 환경 변수에서 앱 비밀번호 가져오기
        self.teams_url = os.getenv("TEAMS_WEBHOOK_URL")  # 환경 변수에서 Teams 웹훅 URL 가져오기
        
    def send_email(self, data, to_email, cc_email):
        """이메일을 전송합니다."""
        msg = MIMEMultipart()
        msg['From'] = "잠재위험 신고앱"
        msg['To'] = ", ".join(to_email)
        msg['Cc'] = ", ".join(cc_email)
        msg['Subject'] = "잠재위험 신고 알림 " + datetime.now().strftime('%Y%m%d%H%M%S')

        # HTML 템플릿
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-family: Arial, sans-serif;
                    background-color: #ffffff;
                }}
                th, td {{
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #ffffff;
                }}
                .header {{
                    font-size: 18px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 10px;
                }}
                td:first-child, th:first-child {{
                    width: 30%;
                }}
            </style>
            
        </head>
        <body>
            <div class="header">잠재위험 신고 알림</div>
            <table>
                <tr><th>항목</th><th>내용</th></tr>
                <tr><td>이미지</td><td><img src="cid:image1"></td></tr>
                <tr><td>코멘트</td><td>{data.get("comment", "None")}</td></tr>
                <tr><td>위치</td><td>{data.get("location", "None")}</td></tr>
                <tr><td>생성일시</td><td>{datetime.now()}</td></tr>
                <tr><td>작성자</td><td>{data.get("reporter", "None")}</td></tr>
                <tr><td>위험 수준</td><td>{data.get("riskLevel", "None")}</td></tr>
                <tr><td>위험 종류</td><td>{data.get("content", {}).get("potentialRisk", "None")}</td></tr>
                <tr><td>위험 상황</td><td>{data.get("content", {}).get("simulation", "None")}</td></tr>
                <tr><td>조치 방법</td><td>{data.get("content", {}).get("mitigationPlan", "None")}</td></tr>
                <tr><td>키워드</td><td>{data.get("keywords", "None")}</td></tr>
                <tr><td>조치자 이름</td><td>{data.get("manager", {}).get("name", "None")}</td></tr>
                <tr><td>조치자 부서</td><td>{data.get("manager", {}).get("department", "None")}</td></tr>
                <tr><td>조치자 전화번호</td><td>{data.get("manager", {}).get("phonenumber", "None")}</td></tr>
                <tr><td>조치자 이메일</td><td>{data.get("manager", {}).get("email", "None")}</td></tr>
                <tr><td>문서 제목</td><td>{data.get("documents", {}).get("title", "None")}</td></tr>
                <tr><td>문서 요약</td><td>{data.get("documents", {}).get("document_summary", "None")}</td></tr>
            </table>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        # 이미지 첨부
        if 'image_base64' in data:
            image_base64 = data['image_base64']
            image_data = base64.b64decode(image_base64)
            image = MIMEImage(image_data)
            image.add_header('Content-ID', '<image1>')
            msg.attach(image)

        try:
            # SMTP 연결 시도 시 타임아웃 설정 추가
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                
                # 연결 상태 확인
                server.ehlo()
                
                server.login(self.from_email, self.password)

                all_recipients = to_email + cc_email
                server.sendmail(self.from_email, all_recipients, msg.as_string())
                
        except smtplib.SMTPServerDisconnected as e:
            print(f"SMTP 서버 연결 끊김: {e}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"인증 오류: {e}")
        except Exception as e:
            print(f"이메일 전송 중 오류 발생: {e}")

    def send_teams(self, data, id):
        """Teams로 데이터를 전송합니다."""
        headers = {
            "Content-Type": "application/json"
        }

        # Teams로 전송할 데이터 구성
        teams_data = {
            "id": id,
            "comment": data.get("comment", "None"),
            "location": data.get("location", "None"),
            "reporter": data.get("reporter", "None"),
            "riskLevel": data.get("riskLevel", "None"),
            "potentialRisk": data.get("content", {}).get("potentialRisk", "None"),
            "simulation": data.get("content", {}).get("simulation", "None"),
            "mitigationPlan": data.get("content", {}).get("mitigationPlan", "None"),
            "keywords": data.get("keywords", "None"),
            "manager_name": data.get("manager", {}).get("name", "None"),
            "manager_department": data.get("manager", {}).get("department", "None"),
            "manager_phonenumber": data.get("manager", {}).get("phonenumber", "None"),
            "manager_email": data.get("manager", {}).get("email", "None"),
            "document_title": data.get("documents", {}).get("title", "None"),
            "document_summary": data.get("documents", {}).get("document_summary", "None"),
            "image_base64": data.get("image_base64", "None")
        }
        
        try:
            response = requests.post(self.teams_url, headers=headers, data=json.dumps(teams_data))
            return
        
        except Exception as e:
            print(f"Teams 전송 중 오류 발생: {e}")

