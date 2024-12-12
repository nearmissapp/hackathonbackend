# flask_server.py

import base64
from PIL import Image
import io

from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import json
from backend_functions import (
    complete_file_path,
    initialize_processor_and_load_image,
    analyze_image,
    convert_analysis_to_json,
    retrieve_information,
    add_info_to_response,
    save_to_database,
    send_notification,
    update_report_status,
    fetch_reporter_data,
    fetch_manager_data,
    fetch_user_data,
    get_current_status
)
import os
import logging
from logging import FileHandler
from datetime import datetime
import threading

app = Flask(__name__)
# CORS 설정 수정
CORS(app, resources={r"*": {"origins": "*"}})

# 로그 설정
file_handler = FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# 루트 로거에 핸들러 추가
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # 로그 레벨 설정
logger.addHandler(file_handler)

def background_task(file_path, caller_ip, reporter, comment, location, id):
    try:
        # Step 1: 이미지 읽기 및 클래스 초기화
        print("API_call-gpt | Step 1: 이미지 읽기 및 클래스 초기화")
        image, save_path, processor = initialize_processor_and_load_image(file_path)
        logger.info(f"Image and processor initialization complete - Caller IP: {caller_ip}")

        # Step 2: 이미지 분석 실행
        print("API_call-gpt | Step 2: 이미지 분석 실행")
        analysis_response, image_base64 = analyze_image(processor, save_path, comment, location)
        logger.info(f"Image analysis complete - Caller IP: {caller_ip}")

        # Step 3: 분석 결과를 JSON 변환
        print("API_call-gpt | Step 3: 분석 결과를 JSON 변환")
        json_response = convert_analysis_to_json(processor, analysis_response)
        logger.info(f"Analysis result converted to JSON - Caller IP: {caller_ip}")

        # Step 4: 담당자 및 관련 문서 탐색
        print("API_call-gpt | Step 4: 담당자 및 관련 문서 탐색")
        hazard_response = retrieve_information(processor, json_response)
        print(hazard_response)
        logger.info(f"Responsible person and related documents retrieved - Caller IP: {caller_ip}")
        
         # **여기에서 "기타" 분류 확인**
        if hazard_response.get("content", {}).get("potentialRisk") == "기타":
            print("skip")
            logger.info("Classification is '기타'; skipping Step 5 to Step 7.")
            return
        
        # Step 5: 사진 및 기타 정보 입력
        def encode_image_to_base64(image_path, max_size=1024):
            """
            이미지를 리사이즈하고 Base64로 인코딩하는 메서드.
            :param image_path: 인코딩할 이미지 파일 경로
            :param max_size: 이미지의 최대 크기 (픽셀 단위, 기본값: 1024)
            :return: Base64 인코딩된 이미지 문자열
            """
            with open(image_path, "rb") as image_file:
                image = Image.open(image_file)
                width, height = image.size

                if width > max_size or height > max_size:
                    if width > height:
                        new_width = max_size
                        new_height = int((max_size / width) * height)
                    else:
                        new_height = max_size
                        new_width = int((max_size / height) * width)
                    image = image.resize((new_width, new_height), Image.LANCZOS)
                    print(f"조정된 이미지 크기: {new_width} x {new_height} 픽셀")  # 조정된 이미지의 픽셀 크기 출력

                # RGBA 모드를 RGB 모드로 변환
                if image.mode == 'RGBA':
                    image = image.convert('RGB')

                # 이미지 파일을 메모리에 저장하고 Base64로 인코딩
                with io.BytesIO() as output:
                    image.save(output, format="JPEG")
                    return base64.b64encode(output.getvalue()).decode("utf-8")
            
        print("API_call-gpt | Step 5: 사진 및 기타 정보 입력")
        image_compressed_base64 = encode_image_to_base64(save_path, 400)
        hazard_response = add_info_to_response(hazard_response, reporter, image_base64, image_compressed_base64)
        logger.info(f"Image and other information added - Caller IP: {caller_ip}")

        # Step 6: 데이터베이스에 저장
        print("API_call-gpt | Step 6: 데이터베이스에 저장")
        save_to_database(hazard_response, id=id)
        logger.info(f"Data saved to database - Caller IP: {caller_ip}")

        # Step 7: 알림 전송 (이메일, 팀즈)
        print("API_call-gpt | Step 7: 알림 전송")
        manager = [hazard_response.get("manager", {}).get("email", "None")]
        hackathon_members = ["seok.jw@posco.com", "ebazy@posco.com", "seongjuhong@posco.com","ysm2691@posco.com","mhcoc@poscosteeleon.com"]
        send_notification(hazard_response, to_email=["pyramid629@gmail.com"], cc_email=hackathon_members, id=id)
        logger.info(f"Notification sent - Caller IP: {caller_ip}")

        # 종료
        print("API_call-gpt | 종료")

    except Exception as e:
        logger.error(f"Unexpected error in background task: {str(e)} - Caller IP: {caller_ip}")

@app.route('/call-gpt', methods=['POST'])
def analyze_image_api():
    try:
        print("API_call-gpt | Step 0: call-gpt api 응답")
        print(request.form)
        print(request.files)
        caller_ip = request.remote_addr
        logger.info(f"API_call-gpt | API call received - Caller IP: {caller_ip}")

        # 이미지 파일 받기
        image_file = request.files.get('image')
        if not image_file:
            logger.warning(f"API_call-gpt | No image file provided - Caller IP: {caller_ip}")
            return jsonify({"error": "Image file is required."}), 400

        # reporter 받기
        reporter = request.form.get('reporter')
        if not reporter:
            logger.warning(f"API_call-gpt | No reporter provided - Caller IP: {caller_ip}")
            return jsonify({"error": "Reporter is required."}), 401

        # comment 받기
        comment = request.form.get('comment')
        if not comment:
            logger.warning(f"API_call-gpt | No comment provided - Caller IP: {caller_ip}")
            return jsonify({"error": "Comment is required."}), 402

        # location 받기
        location = request.form.get('location')
        if not location:
            logger.warning(f"API_call-gpt | No location provided - Caller IP: {caller_ip}")
            return jsonify({"error": "Location is required."}), 403

        # 이미지 저장
        original_file_name = image_file.filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        sanitized_file_name = original_file_name.replace(" ", "_").replace("|", "_")
        new_file_name = f"{timestamp}_{caller_ip}_{sanitized_file_name}"
        file_path = os.path.join("image", new_file_name)
        logger.info(f"API_call-gpt | Image saved: {new_file_name}")
        image_file.save(file_path)

        # 초기 데이터베이스 저장
        initial_data = {
            "comment": comment,
            "location": location,
            "reporter": reporter
        }
        id = save_to_database(initial_data, id=-1)  # id=-1은 초기 데이터를 의미합니다.

        # 백그라운드 작업 시작
        print("API_call-gpt | 백그라운드 작업 시작")
        threading.Thread(target=background_task, args=(file_path, caller_ip, reporter, comment, location, id)).start()

        return jsonify({"message": "Image received and processing started."}), 200

    except Exception as e:
        logger.error(f"API_call-gpt | Unexpected error occurred: {str(e)} - Caller IP: {caller_ip}")
        print("API_call-gpt | 종료")
        return jsonify({"error": str(e)}), 500

@app.route('/list-reporter', methods=['POST'])
def list_reporter():
    try:
        print("API_list-reporter | Step 0: list-reporter api 응답")
        # 요청에서 reporter(email) 가져오기
        reporter = request.form.get('reporter')

        if not reporter:
            logger.warning("API_list-reporter | No reporter provided for login")
            print("API_list-reporter | 종료")
            return jsonify({"error": "Reporter (email) is required."}), 400

        # fetch_reporter_data 함수 호출
        results_json = fetch_reporter_data(reporter)

        # 결과 반환
        print("API_list-reporter | 종료")
        return jsonify({"data": json.loads(results_json)}), 200

    except Exception as e:
        logger.error(f"API_list-reporter | Unexpected error in login API: {str(e)}")
        print("API_update-status | 종료")
        return jsonify({"error": str(e)}), 500

@app.route('/list-manager', methods=['POST'])
def list_manager():
    try:
        print("API_list-manager | Step 0: list-manager api 응답")

        manager = request.form.get('manager')
        if not manager:
            logger.warning("API_list-manager | No manager provided for login")
            print("API_list-manager | 종료")
            return jsonify({"error": "Manager (email) is required."}), 400

        # fetch_manager_data 함수 호출
        results_json = fetch_manager_data(manager)
        # 결과 반환
        print("API_list-manager | 종료")
        return jsonify({"data": json.loads(results_json)}), 200

    except Exception as e:
        logger.error(f"API_list-manager | Unexpected error in login API: {str(e)}")
        print("API_list-manager | 종료")
        return jsonify({"error": str(e)}), 500
    
@app.route('/update-status', methods=['PATCH'])
def update_status():
    try:
        print("API_update-status | Step 0: update-status api 응답")
        # 요청에서 id와 manager 가져오기

        report_id = request.get_json().get('id')
        manager = request.get_json().get('manager')
        print(report_id, manager)
        if not report_id or not manager:
            print("API_update-status | 종료")
            logger.warning("API_update-status | Report ID and manager are required for status update")
            return jsonify({"error": "Report ID and manager are required."}), 400

        # 현재 상태 확인
        current_status = get_current_status(report_id, manager)

        if current_status == "completed":
            print("API_update-status | 이미 completed 상태이므로 종료")
            return jsonify({"message": "Status is already completed."}), 300
        
        if current_status == None:
            print("API_update-status | id와 manager가 일치하지 않아 종료")
            return jsonify({"error": "id and manager are not matched."}), 300

        # 상태 업데이트 수행
        update_success = update_report_status(report_id, manager, "completed")
        
        if update_success:
            print("API_update-status | 종료")
            return jsonify({"message": "Status updated to completed."}), 200
        else:
            print("API_update-status | 종료")
            return jsonify({"error": "Failed to update status."}), 500

    except Exception as e:
        logger.error(f"API_update-status | Unexpected error in update status API: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            logger.warning("API_login | 이메일 또는 비밀번호가 제공되지 않았습니다")
            return jsonify({"error": "이메일과 비밀번호가 필요합니다."}), 400

        ###### 비밀번호 체크는 구현하지 않음 ######
        type = fetch_user_data(email)
        
        if type:
            return jsonify({"type": type}), 200
        else:
            return jsonify({"error": "로그인 실패"}), 401

    except Exception as e:
        logger.error(f"API_login | Unexpected error in login API: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 서버의 IP 주소 확인
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)

    print(f"Server is running on IP: {hostname} - {server_ip}")
    logger.info(f"Server is running on IP: {server_ip}")

    app.run(host='0.0.0.0', port=5000, debug=True)