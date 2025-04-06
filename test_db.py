import psycopg2
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 DB URL 불러오기
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ 데이터베이스 연결 성공!")
    conn.close()
except Exception as e:
    print("❌ 연결 실패:", e)
