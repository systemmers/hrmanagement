"""
Resignation Service

퇴사 처리 및 프로필 스냅샷 서비스
Phase 6: 스냅샷 기능 구현
"""
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
from app.database import db
from app.models import Employee, Profile


class ResignationService:
    """퇴사 처리 서비스"""

    # 기본 데이터 보관 기간 (년)
    DEFAULT_RETENTION_YEARS = 3

    def process_resignation(
        self,
        employee_id: int,
        resignation_date: date,
        retention_years: int = None
    ) -> Dict:
        """
        퇴사 처리 및 스냅샷 생성

        Args:
            employee_id: 직원 ID
            resignation_date: 퇴직일
            retention_years: 데이터 보관 기간 (년), 기본 3년

        Returns:
            처리 결과 딕셔너리
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return {'success': False, 'error': 'Employee not found'}

        if employee.status in ('resigned', 'terminated'):
            return {'success': False, 'error': 'Already resigned'}

        # 보관 기간 설정
        if retention_years is None:
            retention_years = self.DEFAULT_RETENTION_YEARS

        # 스냅샷 데이터 구성
        snapshot = self._build_snapshot(employee)

        # 직원 상태 업데이트
        employee.status = 'resigned'
        employee.resignation_date = resignation_date
        employee.profile_snapshot = snapshot
        employee.snapshot_at = datetime.utcnow()
        employee.data_retention_until = resignation_date + timedelta(days=retention_years * 365)

        db.session.commit()

        return {
            'success': True,
            'employee_id': employee_id,
            'resignation_date': resignation_date.isoformat(),
            'snapshot_at': employee.snapshot_at.isoformat(),
            'data_retention_until': employee.data_retention_until.isoformat()
        }

    def _build_snapshot(self, employee: Employee) -> Dict:
        """
        스냅샷 데이터 구성

        Args:
            employee: Employee 모델

        Returns:
            스냅샷 딕셔너리
        """
        snapshot = {
            'snapshot_version': '1.0',
            'snapshot_at': datetime.utcnow().isoformat(),
        }

        # 프로필 데이터 (연결된 경우)
        if employee.profile:
            snapshot['profile'] = employee.profile.to_dict()
        else:
            # 프로필 연결 없는 경우 employee 기본 정보 사용
            snapshot['profile'] = {
                'name': employee.name,
                'english_name': employee.english_name,
                'chinese_name': employee.chinese_name,
                'birth_date': employee.birth_date,
                'gender': employee.gender,
                'mobile_phone': employee.mobile_phone,
                'home_phone': employee.home_phone,
                'email': employee.email,
                'address': employee.address,
                'detailed_address': employee.detailed_address,
                'postal_code': employee.postal_code,
                'resident_number': employee.resident_number,
                'nationality': employee.nationality,
                'blood_type': employee.blood_type,
                'religion': employee.religion,
                'hobby': employee.hobby,
                'specialty': employee.specialty,
                'disability_info': employee.disability_info,
                'marital_status': employee.marital_status,
                'emergency_contact': employee.emergency_contact,
                'emergency_relation': employee.emergency_relation,
            }

        # 이력 데이터
        snapshot['educations'] = [e.to_dict() for e in employee.educations.all()]
        snapshot['careers'] = [c.to_dict() for c in employee.careers.all()]
        snapshot['certificates'] = [c.to_dict() for c in employee.certificates.all()]
        snapshot['languages'] = [l.to_dict() for l in employee.languages.all()]
        snapshot['families'] = [f.to_dict() for f in employee.family_members.all()]

        # 병역 정보
        if employee.military_service:
            snapshot['military'] = employee.military_service.to_dict()
        else:
            snapshot['military'] = None

        # 수상 내역
        snapshot['awards'] = [a.to_dict() for a in employee.awards.all()]

        # 조직 정보 (퇴사 시점 기준)
        snapshot['organization'] = {
            'department': employee.department,
            'position': employee.position,
            'job_grade': employee.job_grade,
            'job_title': employee.job_title,
            'job_role': employee.job_role,
            'team': employee.team,
            'hire_date': employee.hire_date,
            'employee_number': employee.employee_number,
        }

        return snapshot

    def get_profile_data(self, employee_id: int) -> Dict:
        """
        직원 프로필 데이터 조회 (재직자: 실시간, 퇴사자: 스냅샷)

        Args:
            employee_id: 직원 ID

        Returns:
            프로필 데이터 딕셔너리
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return {'error': 'Employee not found'}

        # 퇴사자: 스냅샷 반환
        if employee.status in ('resigned', 'terminated') and employee.profile_snapshot:
            return {
                'source': 'snapshot',
                'snapshot_at': employee.snapshot_at.isoformat() if employee.snapshot_at else None,
                'data': employee.profile_snapshot
            }

        # 재직자: 실시간 데이터
        return {
            'source': 'live',
            'data': self._build_snapshot(employee)
        }

    def cancel_resignation(self, employee_id: int) -> Dict:
        """
        퇴사 취소 (복직 처리)

        Args:
            employee_id: 직원 ID

        Returns:
            처리 결과 딕셔너리
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return {'success': False, 'error': 'Employee not found'}

        if employee.status not in ('resigned', 'terminated'):
            return {'success': False, 'error': 'Employee is not resigned'}

        # 상태 복원
        employee.status = '재직'
        employee.resignation_date = None
        employee.profile_snapshot = None
        employee.snapshot_at = None
        employee.data_retention_until = None

        db.session.commit()

        return {
            'success': True,
            'employee_id': employee_id,
            'message': 'Resignation cancelled, employee reinstated'
        }


class DataRetentionService:
    """데이터 보관 기간 관리 서비스"""

    def get_expired_employees(self) -> List[Employee]:
        """보관 기간 만료된 퇴사자 조회"""
        today = date.today()
        return Employee.query.filter(
            Employee.status.in_(['resigned', 'terminated']),
            Employee.data_retention_until < today
        ).all()

    def cleanup_expired_data(self, anonymize: bool = True) -> Dict:
        """
        보관 기간 만료 데이터 정리

        Args:
            anonymize: True면 익명화, False면 스냅샷만 삭제

        Returns:
            처리 결과 딕셔너리
        """
        expired = self.get_expired_employees()
        count = 0

        for emp in expired:
            if anonymize:
                # 개인정보 익명화
                emp.profile_snapshot = None
                emp.snapshot_at = None
                # 선택: 프로필 연결 해제
                # emp.profile_id = None
            else:
                # 스냅샷만 삭제
                emp.profile_snapshot = None
                emp.snapshot_at = None
            count += 1

        db.session.commit()

        return {
            'success': True,
            'processed_count': count,
            'anonymized': anonymize
        }

    def extend_retention(self, employee_id: int, additional_years: int) -> Dict:
        """
        데이터 보관 기간 연장

        Args:
            employee_id: 직원 ID
            additional_years: 추가 보관 기간 (년)

        Returns:
            처리 결과 딕셔너리
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return {'success': False, 'error': 'Employee not found'}

        if not employee.data_retention_until:
            return {'success': False, 'error': 'No retention date set'}

        new_date = employee.data_retention_until + timedelta(days=additional_years * 365)
        employee.data_retention_until = new_date
        db.session.commit()

        return {
            'success': True,
            'employee_id': employee_id,
            'new_retention_until': new_date.isoformat()
        }

    def get_retention_report(self) -> Dict:
        """데이터 보관 현황 리포트"""
        today = date.today()
        one_month = today + timedelta(days=30)
        three_months = today + timedelta(days=90)

        # 만료된 데이터
        expired = Employee.query.filter(
            Employee.status.in_(['resigned', 'terminated']),
            Employee.data_retention_until < today
        ).count()

        # 1개월 내 만료 예정
        expiring_soon = Employee.query.filter(
            Employee.status.in_(['resigned', 'terminated']),
            Employee.data_retention_until >= today,
            Employee.data_retention_until < one_month
        ).count()

        # 3개월 내 만료 예정
        expiring_3months = Employee.query.filter(
            Employee.status.in_(['resigned', 'terminated']),
            Employee.data_retention_until >= one_month,
            Employee.data_retention_until < three_months
        ).count()

        # 총 퇴사자 (스냅샷 있는)
        total_resigned = Employee.query.filter(
            Employee.status.in_(['resigned', 'terminated']),
            Employee.profile_snapshot.isnot(None)
        ).count()

        return {
            'report_date': today.isoformat(),
            'expired': expired,
            'expiring_within_1_month': expiring_soon,
            'expiring_within_3_months': expiring_3months,
            'total_resigned_with_snapshot': total_resigned
        }
