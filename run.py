"""
Flask 애플리케이션 진입점
개발 서버 실행
"""
import os
from app import create_app, db
from app.models import User, Employee, Department, Position

# 환경변수에서 설정 이름 가져오기 (기본값: development)
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)


# Flask Shell 컨텍스트
@app.shell_context_processor
def make_shell_context():
    """Flask Shell에서 사용할 변수 등록"""
    return {
        'db': db,
        'User': User,
        'Employee': Employee,
        'Department': Department,
        'Position': Position
    }


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
