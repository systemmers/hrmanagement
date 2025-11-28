"""
Flask-SQLAlchemy 데이터베이스 인스턴스

이 모듈은 SQLAlchemy 인스턴스를 생성하고 export합니다.
App Factory 패턴에서 db.init_app(app)으로 초기화됩니다.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
