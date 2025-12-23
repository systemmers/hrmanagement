"""
템플릿 유틸리티 모듈

Jinja2 템플릿에서 사용하는 컨텍스트 프로세서와 필터를 정의합니다.
SSOT 원칙: field_options.py를 단일 진실 공급원으로 사용합니다.

이 모듈은 Flask 등록만 담당하고, 모든 레이블 변환 로직은 FieldOptions에 위임합니다.
"""
from datetime import datetime, date
from app.constants.field_options import FieldOptions


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
            """상태 텍스트 (SSOT: FieldOptions.EMPLOYEE_STATUS)"""
            return FieldOptions.get_label_with_legacy(FieldOptions.EMPLOYEE_STATUS, status)

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

        # ========================================
        # 레이블 변환 함수 (SSOT: FieldOptions 위임)
        # ========================================

        def get_gender_label(gender):
            """성별 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.GENDER, gender)

        def get_marital_status_label(status):
            """결혼여부 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.MARITAL_STATUS, status)

        def get_nationality_label(nationality):
            """국적 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.NATIONALITY, nationality)

        def get_blood_type_label(blood_type):
            """혈액형 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.BLOOD_TYPE, blood_type)

        def get_employment_type_label(emp_type):
            """고용형태 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.EMPLOYMENT_TYPE, emp_type)

        def get_degree_label(degree):
            """학위 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.DEGREE, degree)

        def get_graduation_status_label(status):
            """졸업상태 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.GRADUATION_STATUS, status)

        def get_salary_type_label(salary_type):
            """급여유형 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.SALARY_TYPE, salary_type)

        def get_relation_label(relation):
            """가족 관계 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.FAMILY_RELATION, relation)

        def get_cohabit_label(cohabit):
            """동거여부 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.COHABIT, cohabit)

        def get_language_label(language):
            """언어 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.LANGUAGE, language)

        def get_level_label(level):
            """언어 수준 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.LANGUAGE_LEVEL, level)

        def get_military_status_label(status):
            """병역 상태 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.MILITARY_STATUS, status)

        def get_branch_label(branch):
            """군 구분 레이블 변환"""
            return FieldOptions.get_label_with_legacy(FieldOptions.MILITARY_BRANCH, branch)

        return {
            # 포맷팅 함수
            'format_phone': format_phone,
            'format_date': format_date,
            'format_currency': format_currency,
            # 상태 함수
            'get_status_badge_class': get_status_badge_class,
            'get_status_text': get_status_text,
            'calculate_tenure': calculate_tenure,
            # 레이블 변환 함수 (SSOT: FieldOptions 위임)
            'get_gender_label': get_gender_label,
            'get_marital_status_label': get_marital_status_label,
            'get_nationality_label': get_nationality_label,
            'get_blood_type_label': get_blood_type_label,
            'get_employment_type_label': get_employment_type_label,
            'get_degree_label': get_degree_label,
            'get_graduation_status_label': get_graduation_status_label,
            'get_salary_type_label': get_salary_type_label,
            'get_relation_label': get_relation_label,
            'get_cohabit_label': get_cohabit_label,
            'get_language_label': get_language_label,
            'get_level_label': get_level_label,
            'get_military_status_label': get_military_status_label,
            'get_branch_label': get_branch_label,
        }
