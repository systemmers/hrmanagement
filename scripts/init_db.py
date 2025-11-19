"""
데이터베이스 초기화 스크립트
관리자 계정, 부서, 직급 마스터 데이터 생성
"""
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Department, Position

def init_database():
    """데이터베이스 초기화"""
    app = create_app('development')

    with app.app_context():
        # 기존 데이터 삭제
        db.drop_all()
        print('기존 데이터베이스 삭제 완료')

        # 테이블 생성
        db.create_all()
        print('데이터베이스 테이블 생성 완료')

        # 관리자 계정 생성
        admin = User(username='admin', name='관리자')
        admin.set_password('admin123!')
        db.session.add(admin)
        print('관리자 계정 생성: admin / admin123!')

        # 부서 마스터 데이터 생성
        departments = [
            Department(name='개발팀', code='DEV'),
            Department(name='디자인팀', code='DESIGN'),
            Department(name='마케팅팀', code='MARKETING'),
            Department(name='영업팀', code='SALES'),
            Department(name='관리팀', code='ADMIN')
        ]
        for dept in departments:
            db.session.add(dept)
        print(f'부서 마스터 데이터 생성: {len(departments)}개')

        # 직급 마스터 데이터 생성
        positions = [
            Position(name='사원', level=1),
            Position(name='대리', level=2),
            Position(name='과장', level=3),
            Position(name='차장', level=4),
            Position(name='부장', level=5)
        ]
        for pos in positions:
            db.session.add(pos)
        print(f'직급 마스터 데이터 생성: {len(positions)}개')

        # 커밋
        db.session.commit()
        print('\n데이터베이스 초기화 완료!')
        print('-' * 50)
        print('로그인 정보:')
        print('  아이디: admin')
        print('  비밀번호: admin123!')
        print('-' * 50)


if __name__ == '__main__':
    init_database()
