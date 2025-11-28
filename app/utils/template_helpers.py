"""
템플릿 유틸리티 모듈

Jinja2 템플릿에서 사용하는 컨텍스트 프로세서와 필터를 정의합니다.
"""
from datetime import datetime, date


def register_template_utils(app):
    """템플릿 유틸리티 함수 등록"""

    @app.context_processor
    def utility_processor():
        """템플릿 유틸리티 함수"""

        def format_phone(phone):
            """전화번호 포맷팅"""
            return phone

        def get_status_badge_class(status):
            """상태 배지 CSS 클래스"""
            status_classes = {
                'active': 'badge-success',
                'warning': 'badge-warning',
                'expired': 'badge-danger'
            }
            return status_classes.get(status, 'badge-secondary')

        def get_status_text(status):
            """상태 텍스트"""
            status_texts = {
                'active': '정상',
                'warning': '대기',
                'expired': '만료'
            }
            return status_texts.get(status, status)

        def calculate_tenure(hire_date):
            """근속연수 계산 (입사일 기준)"""
            if not hire_date:
                return '정보 없음'

            try:
                if isinstance(hire_date, str):
                    hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
                elif isinstance(hire_date, datetime):
                    hire_date = hire_date.date()

                today = date.today()
                years = today.year - hire_date.year
                months = today.month - hire_date.month

                if today.day < hire_date.day:
                    months -= 1

                if months < 0:
                    years -= 1
                    months += 12

                if years > 0 and months > 0:
                    return f'{years}년 {months}개월'
                elif years > 0:
                    return f'{years}년'
                elif months > 0:
                    return f'{months}개월'
                else:
                    return '1개월 미만'
            except (ValueError, TypeError):
                return '정보 없음'

        def format_date(date_value, format_str='%Y-%m-%d'):
            """날짜 포맷팅"""
            if not date_value:
                return '정보 없음'

            try:
                if isinstance(date_value, str):
                    date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                elif isinstance(date_value, (datetime, date)):
                    date_obj = date_value
                else:
                    return str(date_value)

                return date_obj.strftime(format_str)
            except (ValueError, TypeError):
                return str(date_value)

        def format_currency(amount):
            """금액 포맷팅 (천 단위 콤마)"""
            if amount is None:
                return '정보 없음'

            try:
                return f'{int(amount):,}원'
            except (ValueError, TypeError):
                return str(amount)

        def get_degree_label(degree):
            """학위 레이블 변환"""
            labels = {
                'bachelor': '학사',
                'master': '석사',
                'doctor': '박사',
                'associate': '전문학사',
                'high_school': '고졸'
            }
            return labels.get(degree, degree or '정보 없음')

        def get_level_label(level):
            """언어 수준 레이블 변환"""
            labels = {
                'advanced': '상급',
                'intermediate': '중급',
                'beginner': '초급',
                'native': '원어민'
            }
            return labels.get(level, level or '정보 없음')

        def get_relation_label(relation):
            """가족 관계 레이블 변환"""
            labels = {
                'spouse': '배우자',
                'child': '자녀',
                'parent': '부모',
                'sibling': '형제자매',
                'grandparent': '조부모',
                'other': '기타'
            }
            return labels.get(relation, relation or '정보 없음')

        def get_military_status_label(status):
            """병역 상태 레이블 변환"""
            labels = {
                'completed': '군필',
                'exempted': '면제',
                'serving': '복무중',
                'not_applicable': '해당없음'
            }
            return labels.get(status, status or '정보 없음')

        def get_branch_label(branch):
            """군 구분 레이블 변환"""
            labels = {
                'army': '육군',
                'navy': '해군',
                'airforce': '공군',
                'marine': '해병대',
                'auxiliary': '보충역'
            }
            return labels.get(branch, branch or '정보 없음')

        def get_gender_label(gender):
            """성별 레이블 변환"""
            labels = {
                'male': '남성',
                'female': '여성'
            }
            return labels.get(gender, gender or '정보 없음')

        def get_employment_type_label(emp_type):
            """고용형태 레이블 변환"""
            labels = {
                'regular': '정규직',
                'contract': '계약직',
                'parttime': '파트타임',
                'intern': '인턴'
            }
            return labels.get(emp_type, emp_type or '정보 없음')

        return {
            'format_phone': format_phone,
            'get_status_badge_class': get_status_badge_class,
            'get_status_text': get_status_text,
            'calculate_tenure': calculate_tenure,
            'format_date': format_date,
            'format_currency': format_currency,
            'get_degree_label': get_degree_label,
            'get_level_label': get_level_label,
            'get_relation_label': get_relation_label,
            'get_military_status_label': get_military_status_label,
            'get_branch_label': get_branch_label,
            'get_gender_label': get_gender_label,
            'get_employment_type_label': get_employment_type_label
        }
