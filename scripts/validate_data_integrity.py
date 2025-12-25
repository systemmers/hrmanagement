"""
Phase 23 데이터 정합성 검증 스크립트

PersonCorporateContract, Employee, User 간 비즈니스 규칙 검증

실행:
    python scripts/validate_data_integrity.py [--company-id N] [--fix] [--dry-run]

옵션:
    --company-id N  특정 회사 ID로 제한
    --fix           자동 수정 가능한 항목 수정
    --dry-run       수정 미리보기 (--fix와 함께 사용)

체크 항목:
1. pending_info + approved: 계약 승인 시 Employee.status = 'active' 필요
2. resigned + approved: 퇴사 시 PCC.status = 'terminated' 필요
3. resigned + 퇴사일 없음: resignation_date 필수
4. PCC.employee_number NULL: approved 계약은 employee_number 필요
5. approved + Employee 없음: 승인된 계약은 Employee 연결 필요
6. User.employee_id NULL: employee_sub 계정은 employee_id 필요
"""
import os
import sys
import argparse

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.utils.data_validator import get_validator


def print_header(title: str):
    """섹션 헤더 출력"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_issue(issue, index: int):
    """이슈 상세 출력"""
    severity_icon = {
        'critical': '[CRITICAL]',
        'warning': '[WARNING]',
        'info': '[INFO]'
    }
    icon = severity_icon.get(issue.severity, '[UNKNOWN]')

    print(f"\n  {index}. {icon} {issue.issue_type}")
    print(f"     Entity: {issue.entity_type}#{issue.entity_id}")
    print(f"     {issue.description}")
    if issue.current_value:
        print(f"     Current: {issue.current_value}")
    if issue.expected_value:
        print(f"     Expected: {issue.expected_value}")
    if issue.fix_action:
        print(f"     Fix: {issue.fix_action}")


def main():
    parser = argparse.ArgumentParser(description='Phase 23 데이터 정합성 검증')
    parser.add_argument('--company-id', type=int, help='특정 회사 ID로 제한')
    parser.add_argument('--fix', action='store_true', help='자동 수정 가능한 항목 수정')
    parser.add_argument('--dry-run', action='store_true', help='수정 미리보기 (--fix와 함께)')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        print_header("Phase 23 데이터 정합성 검증")

        if args.company_id:
            print(f"  대상 회사: company_id={args.company_id}")

        validator = get_validator(company_id=args.company_id)
        issues = validator.validate_all()
        summary = validator.get_summary()

        # 요약 출력
        print_header("검증 결과 요약")
        print(f"  총 이슈: {summary['total_issues']}건")
        print(f"  - Critical: {summary['critical']}건")
        print(f"  - Warning: {summary['warning']}건")
        print(f"  - Info: {summary['info']}건")

        if summary['by_type']:
            print("\n  유형별:")
            for issue_type, count in summary['by_type'].items():
                print(f"    - {issue_type}: {count}건")

        # 상세 이슈 출력
        if issues:
            print_header("상세 이슈 목록")
            for i, issue in enumerate(issues, 1):
                print_issue(issue, i)

        # 자동 수정
        if args.fix:
            print_header("자동 수정")
            dry_run = args.dry_run
            if dry_run:
                print("  [DRY-RUN 모드] 실제 수정 없이 미리보기만 실행")

            result = validator.auto_fix(dry_run=dry_run)

            if result['fixes']:
                print(f"\n  수정됨 ({result['total_fixes']}건):")
                for fix in result['fixes']:
                    print(f"    - [{fix['issue']}] {fix['entity']}: {fix['action']}")

            if result['errors']:
                print(f"\n  수동 처리 필요 ({result['total_errors']}건):")
                for error in result['errors']:
                    print(f"    - [{error['issue']}] {error['entity']}: {error['reason']}")

            if not dry_run and result['total_fixes'] > 0:
                print(f"\n  총 {result['total_fixes']}건 수정 완료")

        # 최종 결과
        print_header("검증 완료")
        if summary['total_issues'] == 0:
            print("  모든 데이터 정합성 검증 통과")
            return 0
        else:
            print(f"  {summary['total_issues']}건의 이슈 발견")
            if summary['critical'] > 0:
                print(f"  !! {summary['critical']}건의 CRITICAL 이슈가 있습니다")
            return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
