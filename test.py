import psycopg2
import os

def check_user_table_structure():
    # 데이터베이스 연결 설정
    db_config = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_DATABASE"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT")
    }

    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # user 테이블의 컬럼 정보 조회
        query = """
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position;
        """
        
        cursor.execute(query)
        columns = cursor.fetchall()

        print("\n=== user 테이블 구조 ===")
        print("컬럼명\t\t데이터타입\t\t최대길이")
        print("-" * 50)
        
        for column in columns:
            column_name, data_type, max_length = column
            max_length = str(max_length) if max_length is not None else "N/A"
            print(f"{column_name}\t\t{data_type}\t\t{max_length}")

    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    check_user_table_structure()