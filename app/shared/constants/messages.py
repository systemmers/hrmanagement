"""
Messages 상수 정의

플래시 메시지 및 에러 메시지 상수화
"""


class FlashMessages:
    """플래시 메시지 상수"""
    # 로그인/인증
    LOGIN_REQUIRED = '로그인이 필요합니다.'
    ACCESS_DENIED = '접근 권한이 없습니다.'
    ADMIN_REQUIRED = '관리자만 접근 가능합니다.'
    ADMIN_OR_MANAGER_REQUIRED = '관리자 또는 매니저만 접근 가능합니다.'
    ADMIN_PERMISSION_REQUIRED = '관리자 권한이 필요합니다.'

    # 로그인 폼 검증
    ENTER_USERNAME_PASSWORD = '사용자명과 비밀번호를 입력해주세요.'
    INVALID_CREDENTIALS = '사용자명 또는 비밀번호가 올바르지 않습니다.'
    INVALID_CURRENT_PASSWORD = '현재 비밀번호가 올바르지 않습니다.'

    # 비밀번호 변경
    FILL_ALL_FIELDS = '모든 필드를 입력해주세요.'
    PASSWORD_MISMATCH = '새 비밀번호가 일치하지 않습니다.'
    PASSWORD_TOO_SHORT = '비밀번호는 최소 8자 이상이어야 합니다.'
    PASSWORD_CHANGED = '비밀번호가 변경되었습니다.'
    PASSWORD_CHANGE_FAILED = '비밀번호 변경에 실패했습니다.'

    # 계정 타입
    PERSONAL_ACCOUNT_REQUIRED = '개인 계정으로 로그인해주세요.'
    CORPORATE_ACCOUNT_REQUIRED = '법인 계정으로 로그인해주세요.'
    PERSONAL_ONLY_ACCESS = '개인 계정으로만 접근할 수 있습니다.'
    CORPORATE_ONLY_ACCESS = '법인 계정으로만 접근할 수 있습니다.'
    PERSONAL_OR_EMPLOYEE_ONLY = '개인 또는 직원 계정으로만 접근할 수 있습니다.'
    SUPERADMIN_REQUIRED = '플랫폼 관리자 권한이 필요합니다.'

    # 로그아웃
    LOGGED_OUT_TEMPLATE = '{}님이 로그아웃되었습니다.'
    WELCOME_TEMPLATE = '{}님, 환영합니다!'


class ErrorMessages:
    """API 에러 메시지 상수"""
    # 인증
    LOGIN_REQUIRED = '로그인이 필요합니다.'
    ACCESS_DENIED = '접근 권한이 없습니다.'
    ADMIN_PERMISSION_REQUIRED = '관리자 권한이 필요합니다.'

    # 계정 타입
    PERSONAL_ONLY = '개인 계정으로만 접근할 수 있습니다.'
    CORPORATE_ONLY = '법인 계정으로만 접근할 수 있습니다.'
    SUPERADMIN_REQUIRED = '플랫폼 관리자 권한이 필요합니다.'

    # 리소스
    NOT_FOUND = '리소스를 찾을 수 없습니다.'
    CONTRACT_NOT_FOUND = '계약을 찾을 수 없습니다.'
    EMPLOYEE_NOT_FOUND = '직원 정보를 찾을 수 없습니다.'

    # 파일 관련
    FILE_NOT_FOUND = '파일을 찾을 수 없습니다.'
    FILE_TOO_LARGE = '파일 크기는 {size}MB를 초과할 수 없습니다.'
    INVALID_EXTENSION = '허용되지 않는 파일 형식입니다.'
    UPLOAD_FAILED = '파일 업로드에 실패했습니다.'

    # 일반
    SERVER_ERROR = '서버 오류가 발생했습니다.'
    INVALID_ACCOUNT_TYPE = '잘못된 계정 유형입니다.'
    INVALID_REQUEST = '잘못된 요청입니다.'
