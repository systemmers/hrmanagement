



  1. 직원목록 필터 조건

  조건: PCC.status="approved" AND PCC.employee_number = Employee.employee_number
        AND Employee.resignation_date IS NULL

  | No   | employee_number | 이름         | status       | 퇴사일 | PCC상태  | 직원목록   |
  |------|-----------------|--------------|--------------|--------|----------|------------|
  | 1    | EMP-2015-0003   | 서현우       | resigned     | -      | approved | O          |
  | 2    | EMP-2015-0004   | 류예린       | resigned     | O      | approved | X (퇴사)   |
  | 3    | EMP-2015-0005   | 이시연       | active       | -      | approved | O          |
  | 4    | EMP-2015-0007   | 최유리       | active       | -      | approved | O          |
  | 5    | EMP-2015-0008   | 정민영       | active       | -      | approved | O          |
  | 6    | EMP-2015-0010   | 박지현       | active       | -      | approved | O          |
  | 7~36 | EMP-2015-* ~    | (30명)       | active       | -      | -        | X (미계약) |
  | 37   | EMP-2019-0002   | 정우성       | active       | -      | approved | O          |
  | 38   | EMP-2019-0006   | 권지훈       | active       | -      | approved | O          |
  | 41   | EMP-2020-0009   | 송유진       | active       | -      | approved | O          |
  | 48   | EMP-2024-0001   | 임영호       | resigned     | -      | approved | O          |
  | 51   | EMP-2025-0052   | 테스트직원2  | pending_info | -      | approved | O          |
  | 52   | EMP-2025-0053   | 상진환       | active       | -      | approved | O          |
  | 53   | EMP-2025-0054   | 박지우       | resigned     | O      | -        | X (퇴사)   |
  | 54   | EMP-2025-0055   | 이서준       | resigned     | O      | approved | X (퇴사)   |
  | 55   | EMP-2025-0056   | 김준혁       | active       | -      | approved | O          |
  | 57   | EMP-2025-0058   | 테스트직원02 | pending_info | -      | approved | O          |
  | 58   | EMP-2025-0058-1 | 이종선       | pending_info | -      | approved | O          |
  | 60   | EMP-2025-0064   | 롤백테스트   | pending_info | -      | approved | O          |

  요약: 총 60명 중 15명 표시 (퇴사 4명 제외, 미계약 41명 제외)

직원목록 목 첫번째는 pcc가 approved 된 상태이며, pending_info 상태는 미계약 상태이기 때문에 해당되지 않는다. > 계약목록에 유지
resigned, approved 는 퇴사한 상태이며, 퇴사일이 있어야 정상이고 직원목록에서 제외된다.
직원목록 조건은 acvive, approved 이다. 
pcc 상태개 비워져 있는 것은 무엇인가? 계약이 되지 않은 상태 외에 미계약, 계약해지로 할 수 있으며, 
계약 해지의 경우 resigned, approved 조건에 해당되기 때문에 적합한 용어를 추가해야한다. > resigned + terminated
그리고 제일 처음 언급한 pending_info 와 approved는 공존할 수 없다. pending_info는 계약전이기 때문이다.

데이터 정합성 검증: pending_info + approved 조합 데이터 수정 필요
퇴사일 필수화: resigned 상태는 반드시 resignation_date 필요
계약 상태 명확화: NULL vs 'terminated' vs 'rejected' 구분 필요

pending_info는 Employee 상태이고, PCC 상태와는 별개입니다. pending_info + approved 조합은 "직원 정보는 미완성이지만 계약은 승인됨"을 의미하므로 데이터 정합성 검증이 필요
>> 계약 승인 시점(PersonCorporateContract.status → approved)에 자동으로 Employee.status를 pending_info → active로 변경 결론 active , approved 전환

requested → approved (승인)
         → rejected (거절)
         → terminated (종료)

   | resigned       | approved   | 있음             | X        | O        | 정상 퇴사 |
   | resigned       | terminated | 있음             | X        | O        | 계약 종료 후 퇴사 |
    공존 불가
         
resigned 시 apprved >> terminated 변경 



  ---
  2. 계약목록 필터 조건

  조건: PCC.company_id = 1

  | No  | PCC_ID | employee_number | status     | User Email                     | Employee         |
  |-----|--------|-----------------|------------|--------------------------------|------------------|
  | 1   | 38     | NULL            | terminated | jung518@testcorp.co.kr         | X                |
  | 2   | 39     | NULL            | terminated | seo623@testcorp.co.kr          | X                |
  | 3   | 40     | NULL            | terminated | shin49@testcorp.co.kr          | X                |
  | 4   | 41     | EMP-2015-0005   | approved   | lee597@testcorp.co.kr          | O (이시연)       |
  | 5   | 42     | EMP-2019-0006   | approved   | kwon413@testcorp.co.kr         | O (권지훈)       |
  | 6   | 43     | EMP-2015-0007   | approved   | choi996@testcorp.co.kr         | O (최유리)       |
  | 7   | 44     | EMP-2015-0008   | approved   | jung330@testcorp.co.kr         | O (정민영)       |
  | 8   | 45     | EMP-2020-0009   | approved   | song653@testcorp.co.kr         | O (송유진)       |
  | 9   | 46     | NULL            | terminated | park697@testcorp.co.kr         | X                |
  | 10  | 87     | NULL            | terminated | lim397@testcorp.co.kr          | X                |
  | 11  | 88     | EMP-2025-0054   | terminated | junhyuk.kim@gmail.com          | O (박지우)       |
  | 12  | 89     | EMP-2025-0055   | terminated | seojun.lee@gmail.com           | O (이서준)       |
  | 13  | 90     | NULL            | rejected   | jiwoo.lee@gmail.com            | X                |
  | 14  | 91     | NULL            | requested  | test_provision2@test.com       | X                |
  | 15  | 92     | NULL            | terminated | junhyuk.kim@gmail.com          | X                |
  | 16  | 94     | EMP-2025-0056   | approved   | junhyuk.kim@gmail.com          | O (김준혁)       |
  | 17  | 95     | EMP-2015-0003   | approved   | seo623@testcorp.co.kr          | O (서현우)       |
  | 18  | 96     | EMP-2015-0004   | approved   | shin49@testcorp.co.kr          | O (류예린)       |
  | 19  | 97     | EMP-2025-0058-1 | approved   | jongsun@naver.com              | O (이종선)       |
  | 20  | 99     | EMP-2019-0002   | approved   | jung518@testcorp.co.kr         | O (정우성)       |
  | 21  | 100    | EMP-2025-0052   | approved   | test_provision2@test.com       | O (테스트직원2)  |
  | 22  | 101    | EMP-2024-0001   | approved   | lim397@testcorp.co.kr          | O (임영호)       |
  | 23  | 102    | EMP-2025-0053   | approved   | sangjeans@gmail.com            | O (상진환)       |
  | 24  | 103    | EMP-2015-0010   | approved   | park697@testcorp.co.kr         | O (박지현)       |
  | 25  | 104    | EMP-2025-0055   | approved   | seojun.lee@gmail.com           | O (이서준)       |
  | 26  | 105    | NULL            | approved   | testuser456@test.com           | X (문제)         |
  | 27  | 106    | EMP-2025-0058   | approved   | testprovision02@testcorp.co.kr | O (테스트직원02) |
  | 28  | 107    | EMP-2025-0064   | approved   | rollbacktest@testcorp.co.kr    | O (롤백테스트)   |

  요약: 총 28건 (approved 18건, terminated 7건, rejected 1건, requested 1건)

  사원번호(employee_number) 관리 원칙:
  - 계약 승인(approved) 시점에 영구 부여
  - 한 번 부여된 사원번호는 재사용 불가 (terminated/rejected 후에도 유지)
  - NULL 상태는 requested 단계에서만 허용
  - approved 상태에서 NULL은 데이터 무결성 위반 (PCC#105 수정 필요)


네, 맞습니다. 계약 목록은 모든 계약 상태(approved, terminated, rejected, requested)를 포함해야 합니다.
이유:
계약 이력 관리: 종료(terminated)되거나 거절(rejected)된 계약도 이력으로 보관해야 합니다
현재 데이터 구조: 선택된 표에서 이미 28건 전체(approved 18건, terminated 7건, rejected 1건, requested 1건)를 보여주고 있습니다
직원 목록과의 차이: 직원 목록은 approved + active + 미퇴사 조건으로 필터링하지만, 계약 목록은 company_id만으로 필터링하여 모든 계약 이력을 표시합니다
다만, ContractFilterService의 ACTIVE_STATUSES = ['approved', 'terminated']는 활성 계약만 조회하는 용도이므로, 계약 목록 페이지에서는 이 필터를 사용하지 않고 전체 조회해야 합니다.



  요약: 총 28건 (approved 18건, terminated 7건, rejected 1건, requested 1건)

  ---
  3. 계정관리 필터 조건

  조건: User.account_type="employee_sub" AND User.company_id=1

  | No  | User_ID | Email                          | employee_id | Employee        | 계약상태 |
  |-----|---------|--------------------------------|-------------|-----------------|----------|
  | 1   | 6       | lim397@testcorp.co.kr          | 1           | O (임영호)      | approved |
  | 2   | 7       | jung518@testcorp.co.kr         | 2           | O (정우성)      | approved |
  | 3   | 8       | seo623@testcorp.co.kr          | 3           | O (서현우)      | approved |
  | 4   | 9       | shin49@testcorp.co.kr          | 4           | O (류예린)      | approved |
  | 5   | 10      | lee597@testcorp.co.kr          | 5           | O (이시연)      | approved |
  | 6   | 11      | kwon413@testcorp.co.kr         | 6           | O (권지훈)      | approved |
  | 7   | 12      | choi996@testcorp.co.kr         | 7           | O (최유리)      | approved |
  | 8   | 13      | jung330@testcorp.co.kr         | 8           | O (정민영)      | approved |
  | 9   | 14      | song653@testcorp.co.kr         | 9           | O (송유진)      | approved |
  | 10  | 15      | park697@testcorp.co.kr         | 10          | O (박지현)      | approved |
  | 11  | 66      | test_provision2@test.com       | 52          | O (테스트직원2) | approved |
  | 12  | 67      | sangjeans@gmail.com            | 53          | O (상진환)      | approved |
  | 13  | 68      | jongsun@naver.com              | 58          | O (이종선)      | approved |
  | 14  | 69      | testuser456@test.com           | NULL        | X               | approved |
  | 15  | 70      | testprovision02@testcorp.co.kr | NULL        | X               | approved |
  | 16  | 71      | rollbacktest@testcorp.co.kr    | 64          | O (롤백테스트)  | approved |

  요약: 총 16명 (Employee 연결 14명, 미연결 2명)


  해당 계약 상태는 계정 생성과는 별개이다. 계약이 승인된 이후에 계약 상태가 결정되어진다. 해당 조건을 다시 체크하여라.
 