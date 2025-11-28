"""
Flask 애플리케이션 진입점

App Factory 패턴으로 애플리케이션을 생성하고 실행합니다.
"""
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5200)
