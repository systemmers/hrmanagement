"""
시스템 초기 설정 데이터 생성 유틸리티

P1-10: 사번 생성 규칙
P1-11: 이메일 도메인 설정
P1-12: 회사 정보 관리
"""


def init_system_settings():
    """
    시스템 초기 설정 데이터 삽입 (중복 시 무시)
    """
    from app.extensions import system_setting_repo

    if not system_setting_repo:
        print("system_setting_repo not initialized")
        return

    # P1-10: 사번 생성 규칙
    employee_number_settings = {
        'employee_number.prefix': {
            'value': 'EMP',
            'type': 'string',
            'description': '사번 접두어',
            'category': 'employee_number',
        },
        'employee_number.separator': {
            'value': '-',
            'type': 'string',
            'description': '사번 구분자',
            'category': 'employee_number',
        },
        'employee_number.include_year': {
            'value': True,
            'type': 'boolean',
            'description': '사번에 연도 포함 여부',
            'category': 'employee_number',
        },
        'employee_number.sequence_digits': {
            'value': 4,
            'type': 'integer',
            'description': '순번 자릿수',
            'category': 'employee_number',
        },
        'employee_number.auto_generate': {
            'value': True,
            'type': 'boolean',
            'description': '사번 자동 생성 여부',
            'category': 'employee_number',
        },
    }

    # P1-11: 이메일 도메인 설정
    email_settings = {
        'email.domain': {
            'value': 'company.co.kr',
            'type': 'string',
            'description': '회사 이메일 도메인',
            'category': 'email',
        },
        'email.auto_generate': {
            'value': False,
            'type': 'boolean',
            'description': '이메일 자동 생성 여부',
            'category': 'email',
        },
        'email.format': {
            'value': '{first_name}.{last_name}',
            'type': 'string',
            'description': '이메일 생성 포맷',
            'category': 'email',
        },
    }

    # P1-12: 회사 정보
    company_settings = {
        'company.name': {
            'value': '주식회사 예시기업',
            'type': 'string',
            'description': '회사명',
            'category': 'company',
        },
        'company.name_en': {
            'value': 'Example Corp.',
            'type': 'string',
            'description': '회사명 (영문)',
            'category': 'company',
        },
        'company.ceo_name': {
            'value': '',
            'type': 'string',
            'description': '대표이사명',
            'category': 'company',
        },
        'company.business_number': {
            'value': '',
            'type': 'string',
            'description': '사업자등록번호',
            'category': 'company',
        },
        'company.corporate_number': {
            'value': '',
            'type': 'string',
            'description': '법인등록번호',
            'category': 'company',
        },
        'company.address': {
            'value': '',
            'type': 'string',
            'description': '회사 주소',
            'category': 'company',
        },
        'company.phone': {
            'value': '',
            'type': 'string',
            'description': '대표 전화번호',
            'category': 'company',
        },
        'company.fax': {
            'value': '',
            'type': 'string',
            'description': '팩스 번호',
            'category': 'company',
        },
        'company.website': {
            'value': '',
            'type': 'string',
            'description': '회사 웹사이트',
            'category': 'company',
        },
        'company.established_date': {
            'value': '',
            'type': 'string',
            'description': '설립일',
            'category': 'company',
        },
        'company.logo_url': {
            'value': '',
            'type': 'string',
            'description': '회사 로고 URL',
            'category': 'company',
        },
    }

    # 설정 삽입 (이미 존재하면 업데이트하지 않음)
    all_settings = {**employee_number_settings, **email_settings, **company_settings}

    inserted_count = 0
    for key, config in all_settings.items():
        existing = system_setting_repo.get_by_key(key)
        if not existing:
            system_setting_repo.set_value(
                key=key,
                value=config['value'],
                value_type=config['type'],
                description=config['description'],
                category=config['category'],
            )
            inserted_count += 1

    return inserted_count


def reset_system_settings():
    """
    시스템 설정 강제 재설정 (기존 설정 덮어쓰기)
    """
    from app.extensions import system_setting_repo
    from app.models import SystemSetting
    from app.database import db

    if not system_setting_repo:
        print("system_setting_repo not initialized")
        return

    # 기존 설정 모두 삭제
    SystemSetting.query.delete()
    db.session.commit()

    # 초기 설정 재삽입
    return init_system_settings()


if __name__ == '__main__':
    # CLI 실행용
    from app import create_app
    app = create_app()
    with app.app_context():
        count = init_system_settings()
        print(f"Inserted {count} system settings")
