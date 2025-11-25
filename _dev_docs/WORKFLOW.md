# InsaCard 구현 워크플로우

> 생성일: 2025-11-25
> 상태: 활성
> 버전: 1.0

---

## 1. 프로젝트 현황 요약

### 1.1 Git 상태
- **Branch**: master
- **상태**: 대규모 구조 변경 중 (기존 app/ 구조 삭제, 단일 파일 구조로 전환)
- **미추적 파일**: app.py, models.py, forms.py, config.py, data/, templates/, static/
- **삭제된 파일**: app/ 디렉토리 전체 (Blueprint 구조)

### 1.2 현재 파일 구조
```
C:/workspace/insacard/
├── app.py              # Flask 메인 애플리케이션 (20KB)
├── config.py           # 설정 파일 (1.6KB)
├── forms.py            # WTForms 폼 정의 (2KB)
├── models.py           # 데이터 모델 및 Repository (25KB)
├── data/               # JSON 데이터베이스 (9개 파일)
│   ├── employees.json
│   ├── employees_extended.json
│   ├── education.json
│   ├── careers.json
│   ├── certificates.json
│   ├── family_members.json
│   ├── languages.json
│   ├── military.json
│   └── classification_options.json
├── templates/          # Jinja2 템플릿
└── static/             # 정적 파일 (CSS, JS, images)
```

### 1.3 DB 연결 현황
| 구분 | 개수 | 비율 |
|------|------|------|
| 연결된 섹션 | 8개 | 40% |
| 미연결 섹션 | 12개 | 60% |
| 누락 필드 있는 JSON | 3개 | - |

---

## 2. 구현 Phase 정의

### Phase 1: 기존 JSON 필드 보완 (우선순위: 긴급)
**목표**: 기존 8개 섹션의 완전한 데이터 바인딩

| Task ID | 작업 | 대상 파일 | 추가 필드 | 의존성 |
|---------|------|----------|----------|--------|
| P1-T01 | education.json 필드 추가 | data/education.json | gpa, note | 없음 |
| P1-T02 | careers.json 필드 추가 | data/careers.json | department, salary | 없음 |
| P1-T03 | military.json 필드 추가 | data/military.json | duty, specialty | 없음 |
| P1-T04 | Education 모델 수정 | models.py | gpa, note | P1-T01 |
| P1-T05 | Career 모델 수정 | models.py | department, salary | P1-T02 |
| P1-T06 | Military 모델 수정 | models.py | duty, specialty | P1-T03 |
| P1-T07 | 템플릿 데이터 바인딩 검증 | employee_detail.html | - | P1-T04~06 |

### Phase 2: 핵심 기능 JSON 생성 (우선순위: 높음)
**목표**: 인사관리 핵심 기능 데이터 구축

| Task ID | 작업 | 대상 파일 | 관련 섹션 | 의존성 |
|---------|------|----------|----------|--------|
| P2-T01 | salaries.json 생성 | data/salaries.json | 급여정보 | 없음 |
| P2-T02 | benefits.json 생성 | data/benefits.json | 연차/복리후생 | 없음 |
| P2-T03 | contracts.json 생성 | data/contracts.json | 근로계약이력 | 없음 |
| P2-T04 | salary_history.json 생성 | data/salary_history.json | 연봉계약이력 | 없음 |
| P2-T05 | Salary 모델 생성 | models.py | - | P2-T01 |
| P2-T06 | Benefit 모델 생성 | models.py | - | P2-T02 |
| P2-T07 | Contract 모델 생성 | models.py | - | P2-T03 |
| P2-T08 | SalaryHistory 모델 생성 | models.py | - | P2-T04 |
| P2-T09 | Repository 클래스 생성 (4개) | models.py | - | P2-T05~08 |
| P2-T10 | config.py 경로 추가 | config.py | - | P2-T01~04 |
| P2-T11 | app.py 라우트 수정 | app.py | - | P2-T09~10 |
| P2-T12 | 템플릿 데이터 바인딩 (4섹션) | employee_detail.html | - | P2-T11 |

### Phase 3: 인사평가 기능 (우선순위: 중간)
**목표**: 인사이동, 승진, 고과 기능

| Task ID | 작업 | 대상 파일 | 관련 섹션 | 의존성 |
|---------|------|----------|----------|--------|
| P3-T01 | promotions.json 생성 | data/promotions.json | 인사이동/승진 | 없음 |
| P3-T02 | evaluations.json 생성 | data/evaluations.json | 인사고과 | 없음 |
| P3-T03 | trainings.json 생성 | data/trainings.json | 교육훈련 | 없음 |
| P3-T04 | attendance.json 생성 | data/attendance.json | 근태현황 | 없음 |
| P3-T05 | 모델 및 Repository 생성 (4개) | models.py | - | P3-T01~04 |
| P3-T06 | config.py 경로 추가 | config.py | - | P3-T01~04 |
| P3-T07 | app.py 라우트 수정 | app.py | - | P3-T05~06 |
| P3-T08 | 템플릿 데이터 바인딩 (4섹션) | employee_detail.html | - | P3-T07 |

### Phase 4: 부가 기능 (우선순위: 낮음)
**목표**: 보험, 프로젝트, 수상, 비품 관리

| Task ID | 작업 | 대상 파일 | 관련 섹션 | 의존성 |
|---------|------|----------|----------|--------|
| P4-T01 | insurances.json 생성 | data/insurances.json | 4대보험 | 없음 |
| P4-T02 | projects.json 생성 | data/projects.json | 유사사업참여경력 | 없음 |
| P4-T03 | awards.json 생성 | data/awards.json | 수상내역 | 없음 |
| P4-T04 | assets.json 생성 | data/assets.json | 비품지급 | 없음 |
| P4-T05 | 모델 및 Repository 생성 (4개) | models.py | - | P4-T01~04 |
| P4-T06 | config.py 경로 추가 | config.py | - | P4-T01~04 |
| P4-T07 | app.py 라우트 수정 | app.py | - | P4-T05~06 |
| P4-T08 | 템플릿 데이터 바인딩 (4섹션) | employee_detail.html | - | P4-T07 |

---

## 3. 의존성 다이어그램

```
Phase 1 (기존 필드 보완)
========================
[P1-T01] ─┬─> [P1-T04] ─┐
[P1-T02] ─┼─> [P1-T05] ─┼─> [P1-T07]
[P1-T03] ─┴─> [P1-T06] ─┘

Phase 2 (핵심 기능)
==================
[P2-T01] ─> [P2-T05] ─┐
[P2-T02] ─> [P2-T06] ─┼─> [P2-T09] ─┬─> [P2-T11] ─> [P2-T12]
[P2-T03] ─> [P2-T07] ─┤            │
[P2-T04] ─> [P2-T08] ─┘            │
                                    │
[P2-T01~04] ──────────> [P2-T10] ───┘

Phase 3, 4 (동일 패턴)
=====================
[JSON 생성] ─> [모델 생성] ─> [config] ─> [app.py] ─> [템플릿]
```

---

## 4. 작업별 상세 스펙

### 4.1 JSON 스키마 정의

#### salaries.json
```json
{
  "id": 1,
  "employee_id": 1,
  "salary_type": "월급",
  "base_salary": 3500000,
  "position_allowance": 300000,
  "meal_allowance": 200000,
  "transportation_allowance": 100000,
  "total_salary": 4100000,
  "payment_day": 25,
  "payment_method": "계좌이체",
  "bank_account": "국민은행 123-456-789012"
}
```

#### benefits.json
```json
{
  "id": 1,
  "employee_id": 1,
  "year": 2025,
  "annual_leave_granted": 15,
  "annual_leave_used": 5,
  "annual_leave_remaining": 10,
  "severance_type": "DC형",
  "severance_method": "퇴직연금"
}
```

#### insurances.json
```json
{
  "id": 1,
  "employee_id": 1,
  "national_pension": true,
  "health_insurance": true,
  "employment_insurance": true,
  "industrial_accident": true,
  "national_pension_rate": 4.5,
  "health_insurance_rate": 3.545
}
```

#### contracts.json
```json
{
  "id": 1,
  "employee_id": 1,
  "contract_date": "2024-01-01",
  "contract_type": "정규직",
  "contract_period": "무기계약",
  "employee_type": "일반직",
  "work_type": "주5일"
}
```

#### salary_history.json
```json
{
  "id": 1,
  "employee_id": 1,
  "contract_year": 2025,
  "annual_salary": 50000000,
  "bonus": 5000000,
  "total_amount": 55000000,
  "contract_period": "2025-01-01 ~ 2025-12-31"
}
```

#### promotions.json
```json
{
  "id": 1,
  "employee_id": 1,
  "order_date": "2024-03-01",
  "order_type": "승진",
  "before_position": "대리",
  "after_position": "과장",
  "before_department": "개발1팀",
  "after_department": "개발1팀",
  "reason": "정기 승진"
}
```

#### evaluations.json
```json
{
  "id": 1,
  "employee_id": 1,
  "year": 2024,
  "q1_grade": "A",
  "q2_grade": "B+",
  "q3_grade": "A",
  "q4_grade": "A",
  "final_grade": "A",
  "salary_negotiation": "5% 인상"
}
```

#### trainings.json
```json
{
  "id": 1,
  "employee_id": 1,
  "training_date": "2024-05-15",
  "training_name": "정보보안 교육",
  "institution": "한국정보보호진흥원",
  "hours": 8,
  "completed": true
}
```

#### attendance.json
```json
{
  "id": 1,
  "employee_id": 1,
  "year": 2024,
  "month": 11,
  "work_days": 20,
  "absent_days": 0,
  "late_count": 1,
  "early_leave_count": 0,
  "annual_leave_used": 2
}
```

#### projects.json
```json
{
  "id": 1,
  "employee_id": 1,
  "project_name": "스마트시티 플랫폼 구축",
  "period": "2023-01 ~ 2023-12",
  "role": "PM",
  "duty": "프로젝트 총괄",
  "client": "서울특별시"
}
```

#### awards.json
```json
{
  "id": 1,
  "employee_id": 1,
  "award_date": "2024-06-01",
  "award_name": "우수사원상",
  "institution": "주식회사 테스트",
  "note": "상반기 실적 우수"
}
```

#### assets.json
```json
{
  "id": 1,
  "employee_id": 1,
  "issue_date": "2024-01-15",
  "item_name": "노트북",
  "model": "MacBook Pro 14",
  "serial_number": "ABC123456",
  "status": "사용중"
}
```

---

## 5. 체크리스트

### Phase 1 체크리스트
- [ ] P1-T01: education.json에 gpa, note 필드 추가
- [ ] P1-T02: careers.json에 department, salary 필드 추가
- [ ] P1-T03: military.json에 duty, specialty 필드 추가
- [ ] P1-T04: Education 모델에 gpa, note 파라미터 추가
- [ ] P1-T05: Career 모델에 department, salary 파라미터 추가
- [ ] P1-T06: Military 모델에 duty, specialty 파라미터 추가
- [ ] P1-T07: employee_detail.html 해당 섹션 데이터 바인딩 검증

### Phase 2 체크리스트
- [ ] P2-T01: salaries.json 생성 (25개 샘플 데이터)
- [ ] P2-T02: benefits.json 생성 (25개 샘플 데이터)
- [ ] P2-T03: contracts.json 생성 (25개 샘플 데이터)
- [ ] P2-T04: salary_history.json 생성 (샘플 데이터)
- [ ] P2-T05: Salary 모델 클래스 생성
- [ ] P2-T06: Benefit 모델 클래스 생성
- [ ] P2-T07: Contract 모델 클래스 생성
- [ ] P2-T08: SalaryHistory 모델 클래스 생성
- [ ] P2-T09: Repository 클래스 4개 생성
- [ ] P2-T10: config.py에 JSON 경로 4개 추가
- [ ] P2-T11: app.py employee_detail 라우트에 데이터 로드 추가
- [ ] P2-T12: employee_detail.html 4개 섹션 데이터 바인딩

### Phase 3 체크리스트
- [ ] P3-T01: promotions.json 생성
- [ ] P3-T02: evaluations.json 생성
- [ ] P3-T03: trainings.json 생성
- [ ] P3-T04: attendance.json 생성
- [ ] P3-T05: 4개 모델 및 Repository 생성
- [ ] P3-T06: config.py 경로 추가
- [ ] P3-T07: app.py 라우트 수정
- [ ] P3-T08: 템플릿 4개 섹션 바인딩

### Phase 4 체크리스트
- [ ] P4-T01: insurances.json 생성
- [ ] P4-T02: projects.json 생성
- [ ] P4-T03: awards.json 생성
- [ ] P4-T04: assets.json 생성
- [ ] P4-T05: 4개 모델 및 Repository 생성
- [ ] P4-T06: config.py 경로 추가
- [ ] P4-T07: app.py 라우트 수정
- [ ] P4-T08: 템플릿 4개 섹션 바인딩

---

## 6. Git 커밋 전략

### 커밋 메시지 형식
```
[Phase X] Task ID: 작업 설명

- 변경 사항 1
- 변경 사항 2
```

### 권장 커밋 단위
1. Phase 1 완료 후 커밋
2. Phase 2-T01~T04 (JSON 생성) 커밋
3. Phase 2-T05~T10 (모델/설정) 커밋
4. Phase 2-T11~T12 (통합) 커밋
5. Phase 3, 4 동일 패턴

### 초기 커밋 (현재 상태 정리)
```bash
# 현재 변경사항 정리
git add app.py config.py forms.py models.py
git add data/ templates/ static/
git add _dev_docs/

# 삭제된 파일 정리
git add -u

git commit -m "refactor: 단일 파일 구조로 전환

- Blueprint 구조 제거, 단일 app.py로 통합
- JSON 기반 데이터 저장소 구현
- Repository 패턴 적용
- 8개 데이터 섹션 구현 완료"
```

---

## 7. 진행 추적

### 진행률 현황
| Phase | 전체 Task | 완료 | 진행률 |
|-------|----------|------|--------|
| Phase 1 | 7 | 0 | 0% |
| Phase 2 | 12 | 0 | 0% |
| Phase 3 | 8 | 0 | 0% |
| Phase 4 | 8 | 0 | 0% |
| **합계** | **35** | **0** | **0%** |

### 변경 로그
| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-11-25 | 1.0 | 초기 워크플로우 문서 생성 |

---

## 8. 리스크 및 이슈

### 잠재적 리스크
1. **models.py 크기 증가**: 12개 모델 추가 시 파일 크기 50KB+ 예상
   - 대응: 필요시 models/ 디렉토리로 분리

2. **JSON 파일 동기화**: 여러 JSON 파일 간 employee_id 일관성 유지
   - 대응: 데이터 생성 시 검증 스크립트 활용

3. **템플릿 복잡도**: employee_detail.html 크기 증가
   - 대응: include/partial 템플릿 분리 검토

### 현재 이슈
- 없음

---

## 9. 다음 단계

1. **즉시**: Git 현재 상태 커밋 (구조 변경 기록)
2. **Phase 1 시작**: 기존 JSON 필드 보완 작업
3. **Phase 2 계획**: 핵심 기능 JSON 스키마 검토 및 확정
