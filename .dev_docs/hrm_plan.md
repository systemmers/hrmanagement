# Salary 모델 별칭 제거 - 완료

**상태**: 완료
**완료일**: 2026-01-01
**Phase**: 28 필드 통일화

---

## 작업 내역

### 수정 파일
- `app/models/salary.py`

### 제거 항목
1. `__dict_aliases__` dict 제거
2. `__dict_camel_mapping__`에서 `pay_type`, `transport_allowance` 폴백 제거
3. `@property transport_allowance` (getter/setter) 제거
4. `@property pay_type` (getter/setter) 제거

### 변경하지 않은 항목
- `corporate/settings.html`: `accordion_section('pay_type', ...)`는 ClassificationOption 카테고리 ID (Salary 모델과 무관)
- `ClassificationOption.CATEGORY_PAY_TYPE`: 분류 옵션 카테고리 상수 (별개 개념)

---

## 검증 결과

- 의존성 검증: 별칭 사용처 없음 확인
- 구문 검증: `python -m py_compile` 통과
- 테스트: 모든 관련 테스트 통과 (38개)

---

## 참고

### 기존 분석 내용

1. 템플릿
   - Detail 페이지: `salary.transportation_allowance`, `salary.salary_type` 직접 사용 (DB 컬럼명)
   - `corporate/settings.html`: `pay_type`는 ClassificationOption 카테고리 ID

2. 코드
   - `to_dict()`: `profile_adapter.py`에서 사용하지만 별칭 키는 소비자 없음
   - 템플릿: 이미 DB 컬럼명 사용 중

### 제거 근거
1. 개발 단계: 운영 환경/외부 API 클라이언트 없음
2. 템플릿은 이미 DB 컬럼명 사용 중
3. Phase 28 필드 통일 작업과 일치
4. 코드 단순화: 별칭 유지 비용 > 이점
