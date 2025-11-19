#!/bin/bash
# Flask 애플리케이션 시작 스크립트

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
source venv/bin/activate

# 환경변수 로드
export FLASK_APP=run.py
export FLASK_DEBUG=1

# Flask 애플리케이션 실행
echo "Flask 애플리케이션을 시작합니다..."
echo "접속 URL: http://localhost:5001"
echo "관리자 계정 - 아이디: admin, 비밀번호: admin123!"
echo ""

python3 run.py
