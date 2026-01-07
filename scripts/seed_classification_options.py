"""
분류 옵션 기본 데이터 시드 스크립트

실행 방법:
    python scripts/seed_classification_options.py
    python scripts/seed_classification_options.py --dry-run
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database import db
from app.domains.company.models import ClassificationOption

# 기본 데이터 정의
DEFAULT_OPTIONS = {
    # 조직 구조
    'department': ['경영지원', '인사', '재무', '영업', '마케팅', '개발', '기획'],
    'position': ['사원', '주임', '대리', '과장', '차장', '부장', '이사', '상무', '전무', '대표이사'],
    'rank': ['사원', '주임', '대리', '과장', '차장', '부장', '이사', '상무', '전무', '대표'],
    'job_title': ['팀원', '파트장', '팀장', '실장', '본부장', '대표'],
    'team': ['경영지원팀', '인사팀', '재무팀', '영업팀', '마케팅팀', '개발팀', '기획팀'],
    'work_location': ['본사', '지사', '재택', '파견'],
    'job_role': ['경영관리', '인사관리', '재무회계', '영업', '마케팅', '개발', '기획', '디자인'],
    'job_grade': [f'{i}호봉' for i in range(1, 31)],
    'org_unit': ['본부', '사업부', '센터', '실', '파트', '그룹'],

    # 고용 정책
    'employment_type': ['정규직', '계약직', '인턴', '파트타임', '프리랜서'],
    'status': ['재직', '휴직', '퇴직', '대기'],
    'pay_type': ['월급', '연봉', '시급', '일급'],
    'contract_type': ['정규', '계약', '파견', '용역'],
    'language': ['한국어', '영어', '일본어', '중국어'],
    'language_level': ['원어민', '비즈니스', '일상회화', '초급'],
    'family_relation': ['배우자', '자녀', '부모', '형제자매'],

    # 기본
    'bank': ['국민은행', '신한은행', '우리은행', '하나은행', '농협', '기업은행', '카카오뱅크', '토스뱅크'],
    'asset_type': ['노트북', '데스크탑', '모니터', '키보드', '마우스', '전화기', '기타'],
}


def seed_classification_options(dry_run=False):
    """분류 옵션 기본 데이터 삽입"""
    created = 0
    skipped = 0

    for category, values in DEFAULT_OPTIONS.items():
        category_label = ClassificationOption.CATEGORY_LABELS.get(category, category)
        print(f"\n[{category_label}]")

        for order, value in enumerate(values):
            # unique constraint: (category, value) - company_id 무관
            existing = ClassificationOption.query.filter_by(
                category=category,
                value=value
            ).first()

            if existing:
                # 시스템 옵션으로 업데이트 (이미 존재하면)
                if not existing.is_system:
                    existing.is_system = True
                    existing.sort_order = order
                    print(f"  * {value} (시스템 옵션으로 업데이트)")
                else:
                    print(f"  - {value} (이미 존재)")
                skipped += 1
                continue

            option = ClassificationOption(
                category=category,
                value=value,
                label=value,
                sort_order=order,
                company_id=None,
                is_active=True,
                is_system=True,
            )

            if not dry_run:
                db.session.add(option)

            created += 1
            print(f"  + {value}")

        # 각 카테고리 후 커밋 (중간 오류 방지)
        if not dry_run:
            db.session.commit()

    return created, skipped


def main():
    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("분류 옵션 기본 데이터 시드")
    print("=" * 60)

    if dry_run:
        print("[DRY RUN 모드 - 실제 데이터 변경 없음]")

    app = create_app()

    with app.app_context():
        created, skipped = seed_classification_options(dry_run)

        print("\n" + "-" * 60)
        print(f"결과: 생성 {created}개, 스킵(이미 존재) {skipped}개")

        if dry_run:
            print("\nDRY RUN 모드였습니다.")
            print("실제 실행: python scripts/seed_classification_options.py")
        else:
            print("\n기본 데이터 삽입 완료!")


if __name__ == '__main__':
    main()
