# InsaCard 구현 체크리스트 및 추적 문서

> 생성일: 2025-11-25
> 최종 업데이트: 2025-11-25
> 버전: 1.0

---

## 1. 전체 진행률 대시보드

```
전체 진행률: [          ] 0% (0/35 완료)

Phase 1: [          ] 0% (0/7)   기존 필드 보완
Phase 2: [          ] 0% (0/12)  핵심 기능
Phase 3: [          ] 0% (0/8)   인사평가
Phase 4: [          ] 0% (0/8)   부가 기능
```

---

## 2. Phase 1: 기존 JSON 필드 보완

### 상태: 대기중

| 완료 | Task ID | 작업명 | 담당 | 시작일 | 완료일 | 비고 |
|:----:|---------|--------|------|--------|--------|------|
| [ ] | P1-T01 | education.json 필드 추가 | - | - | - | gpa, note |
| [ ] | P1-T02 | careers.json 필드 추가 | - | - | - | department, salary |
| [ ] | P1-T03 | military.json 필드 추가 | - | - | - | duty, specialty |
| [ ] | P1-T04 | Education 모델 수정 | - | - | - | P1-T01 필요 |
| [ ] | P1-T05 | Career 모델 수정 | - | - | - | P1-T02 필요 |
| [ ] | P1-T06 | Military 모델 수정 | - | - | - | P1-T03 필요 |
| [ ] | P1-T07 | 템플릿 검증 | - | - | - | P1-T04~06 필요 |

### 검증 체크리스트
- [ ] education.json 파싱 성공
- [ ] careers.json 파싱 성공
- [ ] military.json 파싱 성공
- [ ] Flask 서버 정상 기동
- [ ] 직원 상세 페이지 오류 없음
- [ ] 추가 필드 표시 확인

---

## 3. Phase 2: 핵심 기능 JSON 생성

### 상태: 대기중

| 완료 | Task ID | 작업명 | 담당 | 시작일 | 완료일 | 비고 |
|:----:|---------|--------|------|--------|--------|------|
| [ ] | P2-T01 | salaries.json 생성 | - | - | - | 25 레코드 |
| [ ] | P2-T02 | benefits.json 생성 | - | - | - | 25 레코드 |
| [ ] | P2-T03 | contracts.json 생성 | - | - | - | 샘플 데이터 |
| [ ] | P2-T04 | salary_history.json 생성 | - | - | - | 샘플 데이터 |
| [ ] | P2-T05 | Salary 모델 생성 | - | - | - | P2-T01 필요 |
| [ ] | P2-T06 | Benefit 모델 생성 | - | - | - | P2-T02 필요 |
| [ ] | P2-T07 | Contract 모델 생성 | - | - | - | P2-T03 필요 |
| [ ] | P2-T08 | SalaryHistory 모델 생성 | - | - | - | P2-T04 필요 |
| [ ] | P2-T09 | Repository 4개 생성 | - | - | - | P2-T05~08 필요 |
| [ ] | P2-T10 | config.py 경로 추가 | - | - | - | P2-T01~04 필요 |
| [ ] | P2-T11 | app.py 라우트 수정 | - | - | - | P2-T09,10 필요 |
| [ ] | P2-T12 | 템플릿 바인딩 | - | - | - | P2-T11 필요 |

### 검증 체크리스트
- [ ] 4개 JSON 파일 생성 완료
- [ ] employee_id 1~25 매핑 확인
- [ ] 모든 Repository get_by_employee_id() 동작
- [ ] 급여정보 섹션 표시
- [ ] 연차/복리후생 섹션 표시
- [ ] 근로계약이력 섹션 표시
- [ ] 연봉계약이력 섹션 표시

---

## 4. Phase 3: 인사평가 기능

### 상태: 대기중

| 완료 | Task ID | 작업명 | 담당 | 시작일 | 완료일 | 비고 |
|:----:|---------|--------|------|--------|--------|------|
| [ ] | P3-T01 | promotions.json 생성 | - | - | - | 인사이동/승진 |
| [ ] | P3-T02 | evaluations.json 생성 | - | - | - | 인사고과 |
| [ ] | P3-T03 | trainings.json 생성 | - | - | - | 교육훈련 |
| [ ] | P3-T04 | attendance.json 생성 | - | - | - | 근태현황 |
| [ ] | P3-T05 | 모델/Repository 생성 | - | - | - | 4개 클래스 |
| [ ] | P3-T06 | config.py 경로 추가 | - | - | - | 4개 경로 |
| [ ] | P3-T07 | app.py 라우트 수정 | - | - | - | - |
| [ ] | P3-T08 | 템플릿 바인딩 | - | - | - | 4개 섹션 |

### 검증 체크리스트
- [ ] 4개 JSON 파일 생성 완료
- [ ] 인사이동/승진 섹션 표시
- [ ] 인사고과 섹션 표시
- [ ] 교육훈련 섹션 표시
- [ ] 근태현황 섹션 표시

---

## 5. Phase 4: 부가 기능

### 상태: 대기중

| 완료 | Task ID | 작업명 | 담당 | 시작일 | 완료일 | 비고 |
|:----:|---------|--------|------|--------|--------|------|
| [ ] | P4-T01 | insurances.json 생성 | - | - | - | 4대보험 |
| [ ] | P4-T02 | projects.json 생성 | - | - | - | 유사사업참여 |
| [ ] | P4-T03 | awards.json 생성 | - | - | - | 수상내역 |
| [ ] | P4-T04 | assets.json 생성 | - | - | - | 비품지급 |
| [ ] | P4-T05 | 모델/Repository 생성 | - | - | - | 4개 클래스 |
| [ ] | P4-T06 | config.py 경로 추가 | - | - | - | 4개 경로 |
| [ ] | P4-T07 | app.py 라우트 수정 | - | - | - | - |
| [ ] | P4-T08 | 템플릿 바인딩 | - | - | - | 4개 섹션 |

### 검증 체크리스트
- [ ] 4개 JSON 파일 생성 완료
- [ ] 4대보험 섹션 표시
- [ ] 유사사업참여경력 섹션 표시
- [ ] 수상내역 섹션 표시
- [ ] 비품지급 섹션 표시

---

## 6. 파일 변경 추적

### 수정 예정 파일

| 파일 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | 총 변경 |
|------|:-------:|:-------:|:-------:|:-------:|:-------:|
| data/education.json | O | - | - | - | 1 |
| data/careers.json | O | - | - | - | 1 |
| data/military.json | O | - | - | - | 1 |
| models.py | O | O | O | O | 4 |
| config.py | - | O | O | O | 3 |
| app.py | - | O | O | O | 3 |
| employee_detail.html | O | O | O | O | 4 |

### 신규 생성 파일

| 파일 | Phase | 레코드 수 | 스키마 정의 |
|------|-------|----------|------------|
| data/salaries.json | 2 | 25 | WORKFLOW.md |
| data/benefits.json | 2 | 25 | WORKFLOW.md |
| data/contracts.json | 2 | 다수 | WORKFLOW.md |
| data/salary_history.json | 2 | 다수 | WORKFLOW.md |
| data/promotions.json | 3 | 다수 | WORKFLOW.md |
| data/evaluations.json | 3 | 다수 | WORKFLOW.md |
| data/trainings.json | 3 | 다수 | WORKFLOW.md |
| data/attendance.json | 3 | 다수 | WORKFLOW.md |
| data/insurances.json | 4 | 25 | WORKFLOW.md |
| data/projects.json | 4 | 다수 | WORKFLOW.md |
| data/awards.json | 4 | 다수 | WORKFLOW.md |
| data/assets.json | 4 | 다수 | WORKFLOW.md |

---

## 7. 이슈 트래커

### 열린 이슈

| ID | 제목 | Phase | 우선순위 | 상태 | 담당 | 생성일 |
|----|------|-------|---------|------|------|--------|
| - | - | - | - | - | - | - |

### 해결된 이슈

| ID | 제목 | Phase | 해결일 | 해결 방법 |
|----|------|-------|--------|----------|
| - | - | - | - | - |

---

## 8. Git 커밋 로그

### 예정 커밋

| 순서 | 커밋 메시지 | 포함 Task | 상태 |
|------|------------|----------|------|
| 1 | refactor: 단일 파일 구조로 전환 | 초기화 | 대기 |
| 2 | feat(P1): 기존 JSON 필드 보완 | P1-T01~07 | 대기 |
| 3 | feat(P2): 핵심 기능 JSON 생성 | P2-T01~04 | 대기 |
| 4 | feat(P2): 핵심 기능 모델/설정 | P2-T05~10 | 대기 |
| 5 | feat(P2): 핵심 기능 통합 | P2-T11~12 | 대기 |
| 6 | feat(P3): 인사평가 기능 | P3-T01~08 | 대기 |
| 7 | feat(P4): 부가 기능 | P4-T01~08 | 대기 |

### 실제 커밋 내역

| 날짜 | 커밋 해시 | 메시지 | 변경 파일 수 |
|------|----------|--------|-------------|
| - | - | - | - |

---

## 9. 변경 로그

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-11-25 | 1.0 | 초기 문서 생성 | Claude |

---

## 10. 관련 문서

- [WORKFLOW.md](./WORKFLOW.md) - 구현 워크플로우 전체 계획
- [TASK_BREAKDOWN.md](./TASK_BREAKDOWN.md) - Task 분해 및 의존성 상세
- [HTML vs DB 분석](../../.claude/plans/silly-sparking-nygaard.md) - 필드 비교 분석 결과
