● 버그 원인을 분석한 피드백입니다.

  직원 목록 페이지네이션 버그 분석

  문제점

  list_routes.py의 86-100 라인에서 페이지네이션 이후 추가 필터링이 발생합니다:

  # 1. 페이지네이션으로 10명 조회 (정상)
  pagination = employee_service.filter_employees(**filter_params)
  employees = [emp.to_dict() for emp in pagination.items]

  # 2. 여기서 추가 필터링 발생! (문제)
  employees_with_contract = employee_service.get_employees_with_contracts(
      employees, company_id
  )  # 10명 → 4명으로 줄어듦

  근본 원인

  1. filter_employees(): 페이지네이션 적용하여 35건 중 1-10번째 직원 10명 반환
  2. get_employees_with_contracts(): "21번 원칙: 계약 approved인 직원만 표시" 로직 수행
  3. 결과: 10명 중 계약 승인된 4명만 남음

  불일치 현상
  ┌──────────────────┬─────┬──────────────────────────┐
  │       항목       │ 값  │           기준           │
  ├──────────────────┼─────┼──────────────────────────┤
  │ pagination.total │ 35  │ 전체 직원 수 (필터링 전) │
  ├──────────────────┼─────┼──────────────────────────┤
  │ per_page         │ 10  │ 요청된 페이지당 항목 수  │
  ├──────────────────┼─────┼──────────────────────────┤
  │ 표시 건수        │ 4   │ 계약 승인 필터링 후      │
  └──────────────────┴─────┴──────────────────────────┘
  해결 방향 (구현 전 확인 필요)

  Option A: Repository 레벨에서 계약 승인 필터 적용
  - filter_employees()에 contract_status='approved' 조건 추가
  - JOIN 쿼리로 PersonCorporateContract 테이블 연결 필요

  Option B: 비즈니스 로직 재검토
  - "21번 원칙"이 목록 페이지에도 적용되어야 하는지 확인
  - 현재 로직이 의도된 것인지 명확화 필요

  추가 검토 필요 파일

  - app/domains/employee/services/employee_service.py - get_employees_with_contracts() 메서드 확인
  - app/domains/employee/services/employee_core_service.py - filter_employees() 메서드 확인

  피드백 완료. 수정을 원하시면 말씀해 주세요.

● 알겠습니다. 수정하지 않겠습니다.

  이미 제공한 피드백을 요약하면:

  버그 요약

  현상: 직원 목록에서 per_page=10 설정 시 "35건 중 1-10 표시"라고 표시되지만 실제 테이블에는 4행만 표시됨

  원인: list_routes.py 98-100라인에서 페이지네이션 이후에 get_employees_with_contracts() 함수가 "계약 승인된 직원만" 추가 필터링하여 10명 → 4명으로 줄어듦

  결론: 페이지네이션 카운트(35건)와 실제 표시 데이터(4건) 간 불일치 발생