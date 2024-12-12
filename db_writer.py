# db_writer.py

import psycopg2
import pandas as pd
import tkinter as tk
from tkinter import ttk
from datetime import datetime  # datetime 모듈 추가
import os
import subprocess
import platform
import json
import random  # 파일 상단에 추가

class DatabaseManager:
    def __init__(self, db_config=None):
        # db_config가 주어지지 않으면 기본값 사용
        self.db_config = db_config or {
            "host": os.getenv("DB_HOST"),
            "database": os.getenv("DB_DATABASE"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "port": os.getenv("DB_PORT")
        }
        self.connection = None
        self.locations = [
            (37.378401, 126.667191),
            (37.379578, 126.667706),
            (37.378469, 126.669262),
            (37.377975, 126.670378)
        ]

    def connect(self):
        """데이터베이스에 연결합니다."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"데이터베이스 연결 중 오류 발생: {e}")

    def disconnect(self):
        """데이터베이스 연결을 종료합니다."""
        if self.connection:
            self.connection.close()

    def save(self, data):
        """report 테이블에 초기 데이터를 저장하고 새로 삽입된 행의 id를 반환합니다."""
        try:
            self.connect()
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO report (
                comment, location, created_at, created_by
            ) VALUES (%s, %s, %s, %s) RETURNING id
            """
            # JSON 데이터에서 필요한 값 추출
            comment = data.get("comment", None)
            location = data.get("location", None)
            created_at = datetime.now()
            created_by = data.get("reporter", None)
            
            # 데이터베이스에 삽입 및 id 반환
            cursor.execute(insert_query, (
                comment, location, created_at, created_by
            ))
            new_id = cursor.fetchone()[0]

            self.connection.commit()
            # print("초기 데이터 저장 완료")
            return new_id

        except Exception as e:
            print(f"초기 데이터 저장 중 오류 발생: {e}")
            return 0
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()

    def update(self, data, id):
        """기존 레코드를 업데이트합니다."""
        # print("기존 레코드 업데이트 시작 update함수")
        try:
            self.connect()
            cursor = self.connection.cursor()
            update_query = """
            UPDATE report
            SET risk_level = %s, potential_risk = %s, mitigation_plan = %s, simulation = %s, keywords = %s,
                manager_name = %s, manager_department = %s, manager_phone = %s, manager_email = %s,
                document_title = %s, document_summary = %s, image_base64 = %s, updated_at = %s, updated_by = %s, 
                action_taken = %s, image_compressed_base64 = %s, location_x = %s, location_y = %s
            WHERE id = %s AND comment = %s AND location = %s AND created_by = %s
            """
            # JSON 데이터에서 필요한 값 추출
            comment = data.get("comment", None)
            location = data.get("location", None)
            created_by = data.get("reporter", None)
            
            risk_level = data.get("riskLevel", None)
            potential_risk = data.get("content", {}).get("potentialRisk", None)
            mitigation_plan = data.get("content", {}).get("mitigationPlan", None)
            simulation = data.get("content", {}).get("simulation", None)
            keywords = data.get("keywords", None)
            manager_name = data.get("manager", {}).get("name", None)
            manager_department = data.get("manager", {}).get("department", None)
            manager_phone = data.get("manager", {}).get("phonenumber", None)
            manager_email = data.get("manager", {}).get("email", None)
            document_title = data.get("documents", {}).get("title", None)
            document_summary = data.get("documents", {}).get("document_summary", None)
            image_base64 = 'data:image/jpeg;base64,'+ data.get("image_base64", None)
            updated_at = datetime.now()
            updated_by = data.get("reporter", None)
            action_taken = False
            image_compressed_base64 = 'data:image/jpeg;base64,'+ data.get("image_compressed_base64", None)
            
            # 랜덤 위치 선택
            random_location = random.choice(self.locations)
            location_x, location_y = random_location
            
            # 데이터베이스 업데이트
            cursor.execute(update_query, (
                risk_level, potential_risk, mitigation_plan, simulation, keywords,
                manager_name, manager_department, manager_phone, manager_email,
                document_title, document_summary, image_base64, updated_at, updated_by, 
                action_taken, image_compressed_base64, location_x, location_y,
                id, comment, location, created_by
            ))

            self.connection.commit()
            # print("데이터 업데이트 완료")

        except Exception as e:
            print(f"데이터 업데이트 중 오류 발생: {e}")
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()

    def fetch_by_email_and_password(self, email):
        """주어진 email로 데이터베이스에서 사용자 타입을 조회합니다."""
        try:
            self.connect()
            cursor = self.connection.cursor()
            select_query = """
            SELECT usertype
            FROM "user"
            WHERE email = %s
            """
            cursor.execute(select_query, (email,))
            results = cursor.fetchall()  # fetchone() 대신 fetchall() 사용
            return results[0][0]  # usertype 직접 반환

        except Exception as e:
            print(f"사용자 조회 중 오류 발생: {e}")
            return None  # 오류 발생 시 None 반환
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()

    def fetch_by_reporter(self, reporter, limit=3):
        """주어진 reporter로 데이터베이스에서 comment, created_at, status, id를 조회하고 JSON으로 반환합니다."""
        try:
            self.connect()
            cursor = self.connection.cursor()
            select_query = """
            SELECT id, comment, created_at, status
            FROM report
            WHERE created_by = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            cursor.execute(select_query, (reporter, limit))
            results = cursor.fetchall()

            # 결과를 JSON 형식으로 변환 (ensure_ascii=False 추가)
            results_json = json.dumps([
                {
                    "id": id,
                    "comment": comment,
                    "created_at": created_at.isoformat(),
                    "status": status
                }
                for id, comment, created_at, status in results
            ], ensure_ascii=False)  # ensure_ascii=False 추가
            #print(results_json)
            
            return results_json

        except Exception as e:
            print(f"데이터 조회 중 오류 발생: {e}")
            return json.dumps([], ensure_ascii=False)  # ensure_ascii=False 추가
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()

    def fetch_by_manager(self, manager, limit=3):
        """주어진 manager로 데이터베이스에서 image_compressed_base64, comment, created_at, status, id를 조회하고 JSON으로 반환합니다."""
        try:
            self.connect()
            cursor = self.connection.cursor()
            select_query = """
            SELECT id, comment, created_at, status, image_compressed_base64
            FROM report
            WHERE manager_email = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            cursor.execute(select_query, (manager, limit))
            results = cursor.fetchall()

            # 결과를 JSON 형식으로 변환 (ensure_ascii=False 추가)
            results_json = json.dumps([
                {
                    "id": id,
                    "comment": comment,
                    "created_at": created_at.isoformat(),
                    "status": status,
                    "image_compressed_base64": image_compressed_base64
                }
                for id, comment, created_at, status, image_compressed_base64 in results
            ], ensure_ascii=False)  # ensure_ascii=False 추가
            #print(results_json)
            
            return results_json

        except Exception as e:
            print(f"데이터 조회 중 오류 발생: {e}")
            return json.dumps([], ensure_ascii=False)  # ensure_ascii=False 추가
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()

    def update_status(self, report_id, reporter, new_status):
        """주어진 보고서 ID와 reporter의 상태를 업데이트합니다."""
        try:
            self.connect()
            cursor = self.connection.cursor()
            update_query = """
            UPDATE report
            SET status = %s, updated_at = %s
            WHERE id = %s AND created_by = %s
            """
            updated_at = datetime.now()
            
            # 데이터베이스 업데이트
            cursor.execute(update_query, (new_status, updated_at, report_id, reporter))
            self.connection.commit()
            # print("상태 업데이트 완료", report_id, reporter, new_status)
            return cursor.rowcount > 0  # 업데이트된 행이 있는지 확인

        except Exception as e:
            print(f"상태 업데이트 중 오류 발생: {e}")
            return False
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()

    def get_current_status(self, report_id, reporter):
        """주어진 보고서 ID와 reporter의 현재 상태를 조회합니다."""
        try:
            self.connect()
            cursor = self.connection.cursor()
            select_query = """
            SELECT status
            FROM report
            WHERE id = %s AND created_by = %s
            """
            cursor.execute(select_query, (report_id, reporter))
            result = cursor.fetchone()
            return result[0] if result else None

        except Exception as e:
            print(f"현재 상태 조회 중 오류 발생: {e}")
            return None
        finally:
            if self.connection:
                cursor.close()
                self.disconnect()
