# backend_functions.py

from PIL import Image
import json
from gpt_caller import GptCaller
from db_writer import DatabaseManager
from notification_sender import NotificationSender
import os  # os 모듈 추가
from datetime import datetime

# 에러 처리 함수
def handle_error(message, exception=None):
    """에러 처리 함수."""
    if exception:
        print(f"세부 정보: {exception}")
    raise SystemExit  # Jupyter에서 프로세스를 중지

# Step 0: 파일 이름으로 파일 경로 완성
def complete_file_path(file_name, directory="image"):
    """파일 이름을 사용하여 파일 경로를 완성합니다."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(file_name):
                return os.path.join(root, file)
    handle_error(f"{file_name}에 해당하는 파일을 찾을 수 없습니다.")

# Step 1: 이미지 읽기 및 클래스 초기화
def initialize_processor_and_load_image(file_path):
    """이미지를 읽고 RiskAnalysisProcessor 클래스를 초기화합니다."""
    try:
        image = Image.open(file_path)
    except Exception as e:
        handle_error("이미지 파일을 열 수 없습니다.", e)

    try:
        processor = GptCaller()
    except ValueError as e:
        handle_error("환경 변수 설정 오류", e)

    return image, file_path, processor

# Step 2: 이미지 분석 실행
def analyze_image(processor, image_path, comment, location):
    """이미지 분석 실행."""
    try:
        analysis_response, image_base64 = processor.analyze_image_risks(image_path, comment, location)
        return analysis_response, image_base64
    except Exception as e:
        handle_error("이미지 분석 중 오류 발생", e)

# Step 3: 분석 결과를 JSON 변환
def convert_analysis_to_json(processor, analysis_response):
    """이미지 분석 결과를 JSON으로 변환."""
    try:
        analyzed_text = analysis_response.choices[0].message.content
        json_response = processor.format_risk_as_json(analyzed_text)
        return json_response
    except Exception as e:
        handle_error("JSON 변환 중 오류 발생", e)

# Step 4: 담당자 및 관련 문서 정보 탐색
def retrieve_information(processor, json_response):
    """JSON 데이터를 기반으로 관련 정보를 탐색."""
    def extract_data(choices, error_message):
        if choices and len(choices) > 0:
            tool_calls = choices[0].message.tool_calls
            if tool_calls and len(tool_calls) > 0:
                arguments = tool_calls[0].function.arguments
                return json.loads(arguments)
            else:
                handle_error(error_message)
        else:
            handle_error(error_message)

    try:
        json_data = extract_data(json_response.choices, "choices에 데이터가 없습니다.")["data"]
    except Exception as e:
        handle_error("정보 검색 중 오류 발생", e)

    doc_search_keyword = json_data['content']['potentialRisk']
    retrieve_response = processor.retrieve_information([json_data], doc_search_keyword)
    
    try:
        risk_data = extract_data(retrieve_response.choices, "retrieve_response의 choices에 데이터가 없습니다.")["risks"]
        # print("risk_data 출력")
        # print(risk_data)
        
    except Exception as e:
        handle_error("retrieve_response 처리 중 오류 발생", e)
    
    return risk_data

# Step 5: 사진 및 기타 정보 입력
def add_info_to_response(hazard_response, reporter, image_base64, image_compressed_base64):
    """잠재위험 응답에 이미지 정보를 추가합니다."""
    updated_response = hazard_response.copy()
    updated_response['reporter'] = reporter
    updated_response['image_base64'] = image_base64
    updated_response['image_compressed_base64'] = image_compressed_base64
    return updated_response

# Step 6: 데이터베이스에 저장
def save_to_database(response, id):
    """잠재위험 응답을 데이터베이스에 저장합니다."""
    db_manager = DatabaseManager()
    
    if id < 0:
        # 초기 데이터 저장
        return db_manager.save(response)
    else:
        # 기존 레코드 업데이트
        return db_manager.update(response, id)
def fetch_user_data(email):
    """주어진 email로 데이터베이스에서 데이터를 조회합니다."""
    db_manager = DatabaseManager()
    return db_manager.fetch_by_email_and_password(email)

def fetch_reporter_data(reporter):
    """주어진 reporter로 데이터베이스에서 데이터를 조회합니다."""
    db_manager = DatabaseManager()
    return db_manager.fetch_by_reporter(reporter)

def fetch_manager_data(manager):
    """주어진 manager로 데이터베이스에서 데이터를 조회합니다."""
    db_manager = DatabaseManager()
    return db_manager.fetch_by_manager(manager)

def update_report_status(report_id, reporter, new_status):
    """보고서의 상태를 업데이트합니다."""
    db_manager = DatabaseManager()
    return db_manager.update_status(report_id, reporter, new_status)

def get_current_status(report_id, reporter):
    """주어진 보고서 ID와 reporter의 현재 상태를 조회합니다."""
    db_manager = DatabaseManager()
    return db_manager.get_current_status(report_id, reporter)

# Step 7: 알림 전송 (이메일, 팀즈)
def send_notification(hazard_response, to_email, cc_email, id):
    """잠재위험 응답을 이메일로 전송합니다."""
    notification_sender = NotificationSender()
    notification_sender.send_email(data=hazard_response, to_email=to_email, cc_email=cc_email)
    notification_sender.send_teams(data=hazard_response, id=id)








if __name__ == "__main__":
    print("=== 잠재위험 신고 프로그램 ===")
    comment = "위험 신고합니다."
    location = "포스코 포항제철소"
    reporter = "report seok.jw@posco.com"

    notification_sender = NotificationSender()

    for i in range(1, 11):
        file_name = f"test{i}"  # file_name을 test1부터 test10까지 설정
        file_path = complete_file_path(file_name)  # file_path를 complete_file_path 함수로 설정

        # 초기 데이터베이스 저장
        initial_data = {
            "comment": comment,
            "location": location,
            "reporter": reporter
        }
        id = save_to_database(initial_data, id=-1)

        # Step 1: 이미지 읽기 및 클래스 초기화
        print(f"Step 1: 이미지 읽기 및 클래스 초기화 시작 - {file_name}")
        image, save_path, processor = initialize_processor_and_load_image(file_path)
        print("Step 1 완료: 이미지 및 프로세서 초기화 완료")

        # Step 2: 이미지 분석 실행
        print("Step 2: 이미지 분석 실행 시작")
        analysis_response, image_base64 = analyze_image(processor, save_path, comment, location)
        print("Step 2 완료: 이미지 분석 결과")
        print(analysis_response)

        # Step 3: 분석 결과를 JSON 변환
        print("Step 3: 분석 결과를 JSON 변환 시작")
        json_response = convert_analysis_to_json(processor, analysis_response)
        print("Step 3 완료: JSON 변환 결과")
        print(json_response)

        # Step 4: 담당자 및 관련 문서 탐색
        print("Step 4: 담당자 및 관련 문서 탐색 시작")
        hazard_response = retrieve_information(processor, json_response)
        print("Step 4 완료: 탐색 결과")
        print(hazard_response)

        # Step 5: 사진 및 기타 정보 입력
        print("Step 5: 신고자 정보 및 사진 정보 입력 시작")
        hazard_response = add_info_to_response(hazard_response, reporter, image_base64)
        print("Step 5 완료: 신고자 정보 및 사진 정보 입력 완료")

        # Step 6: 데이터베이스에 저장 (업데이트)
        print("Step 6: 데이터베이스에 저장 시작")
        save_to_database(hazard_response, id=id)
        print("Step 6 완료: 데이터베이스 저장 완료")

        # Step 7: 알림 전송
        print("Step 7: 알림 전송 시작")
        send_notification(hazard_response, to_email=["seok.jw@posco.com"], cc_email=[], id=id)
        print("Step 7 완료: 알림 전송 완료")

        # 결과 확인 (출력을 위해 base64 길이 줄임)
        print("\n=== 결과 확인 ===")
        hazard_response_copy = hazard_response.copy()
        hazard_response_copy["image_base64"] = hazard_response_copy["image_base64"][:20] + "..."
        print(json.dumps(hazard_response_copy, indent=4, ensure_ascii=False))

