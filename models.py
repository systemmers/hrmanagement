"""
데이터 모델 및 JSON 파일 CRUD 유틸리티
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Dict

class Employee:
    """직원 모델"""

    def __init__(self, id: int, name: str, photo: str, department: str,
                 position: str, status: str, hireDate: str, phone: str, email: str,
                 # 확장 필드 - 개인정보
                 name_en: Optional[str] = None, birth_date: Optional[str] = None,
                 gender: Optional[str] = None, address: Optional[str] = None,
                 emergency_contact: Optional[str] = None, emergency_relation: Optional[str] = None,
                 # 확장 필드 - 소속정보
                 employee_number: Optional[str] = None, team: Optional[str] = None,
                 job_title: Optional[str] = None, work_location: Optional[str] = None,
                 internal_phone: Optional[str] = None, company_email: Optional[str] = None,
                 # 확장 필드 - 계약정보
                 employment_type: Optional[str] = None, contract_period: Optional[str] = None,
                 probation_end: Optional[str] = None, resignation_date: Optional[str] = None):
        # 기본 필드
        self.id = id
        self.name = name
        self.photo = photo
        self.department = department
        self.position = position
        self.status = status
        self.hireDate = hireDate
        self.phone = phone
        self.email = email
        # 확장 필드 - 개인정보
        self.name_en = name_en
        self.birth_date = birth_date
        self.gender = gender
        self.address = address
        self.emergency_contact = emergency_contact
        self.emergency_relation = emergency_relation
        # 확장 필드 - 소속정보
        self.employee_number = employee_number
        self.team = team
        self.job_title = job_title
        self.work_location = work_location
        self.internal_phone = internal_phone
        self.company_email = company_email
        # 확장 필드 - 계약정보
        self.employment_type = employment_type
        self.contract_period = contract_period
        self.probation_end = probation_end
        self.resignation_date = resignation_date

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        result = {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'department': self.department,
            'position': self.position,
            'status': self.status,
            'hireDate': self.hireDate,
            'phone': self.phone,
            'email': self.email
        }
        # 확장 필드가 있으면 추가
        extended_fields = [
            'name_en', 'birth_date', 'gender', 'address', 'emergency_contact', 'emergency_relation',
            'employee_number', 'team', 'job_title', 'work_location', 'internal_phone', 'company_email',
            'employment_type', 'contract_period', 'probation_end', 'resignation_date'
        ]
        for field in extended_fields:
            value = getattr(self, field, None)
            if value is not None:
                result[field] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'Employee':
        """딕셔너리에서 생성"""
        # 기본 필드
        base_fields = ['id', 'name', 'photo', 'department', 'position', 'status', 'hireDate', 'phone', 'email']
        # 확장 필드
        extended_fields = [
            'name_en', 'birth_date', 'gender', 'address', 'emergency_contact', 'emergency_relation',
            'employee_number', 'team', 'job_title', 'work_location', 'internal_phone', 'company_email',
            'employment_type', 'contract_period', 'probation_end', 'resignation_date'
        ]
        # 유효한 필드만 추출
        valid_data = {k: v for k, v in data.items() if k in base_fields + extended_fields}
        return cls(**valid_data)


class Education:
    """학력 모델"""

    def __init__(self, id: int, employee_id: int, school: str, degree: str,
                 major: str, graduation_year: str, graduation_status: str = None,
                 gpa: Optional[str] = None, note: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.school = school
        self.degree = degree
        self.major = major
        self.graduation_year = graduation_year
        self.graduation_status = graduation_status
        self.gpa = gpa
        self.note = note

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'school': self.school,
            'degree': self.degree,
            'major': self.major,
            'graduation_year': self.graduation_year,
            'graduation_status': self.graduation_status,
            'gpa': self.gpa,
            'note': self.note
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Education':
        return cls(**data)


class Career:
    """경력 모델"""

    def __init__(self, id: int, employee_id: int, company: str, position: str,
                 duty: str, start_date: str, end_date: str, is_current: bool = False,
                 department: Optional[str] = None, salary: Optional[int] = None):
        self.id = id
        self.employee_id = employee_id
        self.company = company
        self.position = position
        self.duty = duty
        self.start_date = start_date
        self.end_date = end_date
        self.is_current = is_current
        self.department = department
        self.salary = salary

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'company': self.company,
            'position': self.position,
            'duty': self.duty,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_current': self.is_current,
            'department': self.department,
            'salary': self.salary
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Career':
        return cls(**data)


class Certificate:
    """자격증 모델"""

    def __init__(self, id: int, employee_id: int, name: str, issuer: str,
                 acquired_date: str, expiry_date: Optional[str] = None,
                 certificate_number: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.name = name
        self.issuer = issuer
        self.acquired_date = acquired_date
        self.expiry_date = expiry_date
        self.certificate_number = certificate_number

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'issuer': self.issuer,
            'acquired_date': self.acquired_date,
            'expiry_date': self.expiry_date,
            'certificate_number': self.certificate_number
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Certificate':
        return cls(**data)


class FamilyMember:
    """가족 모델"""

    def __init__(self, id: int, employee_id: int, relation: str, name: str,
                 birth_date: str, occupation: Optional[str] = None,
                 is_dependent: bool = False):
        self.id = id
        self.employee_id = employee_id
        self.relation = relation
        self.name = name
        self.birth_date = birth_date
        self.occupation = occupation
        self.is_dependent = is_dependent

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'relation': self.relation,
            'name': self.name,
            'birth_date': self.birth_date,
            'occupation': self.occupation,
            'is_dependent': self.is_dependent
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FamilyMember':
        return cls(**data)


class Language:
    """언어능력 모델"""

    def __init__(self, id: int, employee_id: int, language: str, level: str,
                 test_name: Optional[str] = None, score: Optional[str] = None,
                 acquired_date: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.language = language
        self.level = level
        self.test_name = test_name
        self.score = score
        self.acquired_date = acquired_date

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'language': self.language,
            'level': self.level,
            'test_name': self.test_name,
            'score': self.score,
            'acquired_date': self.acquired_date
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Language':
        return cls(**data)


class MilitaryService:
    """병역 모델"""

    def __init__(self, id: int, employee_id: int, status: str,
                 branch: Optional[str] = None, rank: Optional[str] = None,
                 start_date: Optional[str] = None, end_date: Optional[str] = None,
                 exemption_reason: Optional[str] = None,
                 duty: Optional[str] = None, specialty: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.status = status
        self.branch = branch
        self.rank = rank
        self.start_date = start_date
        self.end_date = end_date
        self.exemption_reason = exemption_reason
        self.duty = duty
        self.specialty = specialty

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'status': self.status,
            'branch': self.branch,
            'rank': self.rank,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'exemption_reason': self.exemption_reason,
            'duty': self.duty,
            'specialty': self.specialty
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MilitaryService':
        return cls(**data)


class Salary:
    """급여 정보 모델"""

    def __init__(self, id: int, employee_id: int, salary_type: str,
                 base_salary: int, position_allowance: int, meal_allowance: int,
                 transportation_allowance: int, total_salary: int,
                 payment_day: int, payment_method: str, bank_account: str):
        self.id = id
        self.employee_id = employee_id
        self.salary_type = salary_type
        self.base_salary = base_salary
        self.position_allowance = position_allowance
        self.meal_allowance = meal_allowance
        self.transportation_allowance = transportation_allowance
        self.total_salary = total_salary
        self.payment_day = payment_day
        self.payment_method = payment_method
        self.bank_account = bank_account

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'salary_type': self.salary_type,
            'base_salary': self.base_salary,
            'position_allowance': self.position_allowance,
            'meal_allowance': self.meal_allowance,
            'transportation_allowance': self.transportation_allowance,
            'total_salary': self.total_salary,
            'payment_day': self.payment_day,
            'payment_method': self.payment_method,
            'bank_account': self.bank_account
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Salary':
        return cls(**data)


class Benefit:
    """복리후생/연차 정보 모델"""

    def __init__(self, id: int, employee_id: int, year: int,
                 annual_leave_granted: int, annual_leave_used: int,
                 annual_leave_remaining: int, severance_type: str,
                 severance_method: str):
        self.id = id
        self.employee_id = employee_id
        self.year = year
        self.annual_leave_granted = annual_leave_granted
        self.annual_leave_used = annual_leave_used
        self.annual_leave_remaining = annual_leave_remaining
        self.severance_type = severance_type
        self.severance_method = severance_method

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'year': self.year,
            'annual_leave_granted': self.annual_leave_granted,
            'annual_leave_used': self.annual_leave_used,
            'annual_leave_remaining': self.annual_leave_remaining,
            'severance_type': self.severance_type,
            'severance_method': self.severance_method
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Benefit':
        return cls(**data)


class Contract:
    """근로계약 정보 모델"""

    def __init__(self, id: int, employee_id: int, contract_date: str,
                 contract_type: str, contract_period: str,
                 employee_type: str, work_type: str):
        self.id = id
        self.employee_id = employee_id
        self.contract_date = contract_date
        self.contract_type = contract_type
        self.contract_period = contract_period
        self.employee_type = employee_type
        self.work_type = work_type

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'contract_date': self.contract_date,
            'contract_type': self.contract_type,
            'contract_period': self.contract_period,
            'employee_type': self.employee_type,
            'work_type': self.work_type
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Contract':
        return cls(**data)


class SalaryHistory:
    """연봉계약 이력 모델"""

    def __init__(self, id: int, employee_id: int, contract_year: int,
                 annual_salary: int, bonus: int, total_amount: int,
                 contract_period: str):
        self.id = id
        self.employee_id = employee_id
        self.contract_year = contract_year
        self.annual_salary = annual_salary
        self.bonus = bonus
        self.total_amount = total_amount
        self.contract_period = contract_period

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'contract_year': self.contract_year,
            'annual_salary': self.annual_salary,
            'bonus': self.bonus,
            'total_amount': self.total_amount,
            'contract_period': self.contract_period
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SalaryHistory':
        return cls(**data)


class EmployeeRepository:
    """직원 데이터 저장소 (JSON 파일 기반)"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """데이터 파일이 없으면 생성"""
        if not os.path.exists(self.json_file_path):
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
            self._save_data([])
    
    def _load_data(self) -> List[Dict]:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data: List[Dict]):
        """JSON 파일에 데이터 저장"""
        with open(self.json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all(self) -> List[Employee]:
        """모든 직원 조회"""
        data = self._load_data()
        return [Employee.from_dict(item) for item in data]
    
    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """ID로 직원 조회"""
        data = self._load_data()
        for item in data:
            if item['id'] == employee_id:
                return Employee.from_dict(item)
        return None
    
    def create(self, employee: Employee) -> Employee:
        """직원 생성"""
        data = self._load_data()
        
        # 새 ID 생성
        if data:
            employee.id = max(item['id'] for item in data) + 1
        else:
            employee.id = 1
        
        data.append(employee.to_dict())
        self._save_data(data)
        return employee
    
    def update(self, employee_id: int, employee: Employee) -> Optional[Employee]:
        """직원 수정"""
        data = self._load_data()
        
        for i, item in enumerate(data):
            if item['id'] == employee_id:
                employee.id = employee_id
                data[i] = employee.to_dict()
                self._save_data(data)
                return employee
        
        return None
    
    def delete(self, employee_id: int) -> bool:
        """직원 삭제"""
        data = self._load_data()
        original_length = len(data)
        
        data = [item for item in data if item['id'] != employee_id]
        
        if len(data) < original_length:
            self._save_data(data)
            return True
        return False
    
    def search(self, query: str) -> List[Employee]:
        """직원 검색 (이름, 부서, 직급)"""
        all_employees = self.get_all()
        query = query.lower()
        
        return [
            emp for emp in all_employees
            if query in emp.name.lower() or
               query in emp.department.lower() or
               query in emp.position.lower()
        ]
    
    def filter_by_status(self, status: str) -> List[Employee]:
        """상태별 필터링"""
        all_employees = self.get_all()
        return [emp for emp in all_employees if emp.status == status]
    
    def get_statistics(self) -> Dict:
        """통계 정보 조회"""
        employees = self.get_all()
        total = len(employees)
        active = len([e for e in employees if e.status == 'active'])
        warning = len([e for e in employees if e.status == 'warning'])
        expired = len([e for e in employees if e.status == 'expired'])
        
        # 기존 통계
        active_rate = round((active / total * 100) if total > 0 else 0, 1)
        warning_rate = round((warning / total * 100) if total > 0 else 0, 1)
        expired_rate = round((expired / total * 100) if total > 0 else 0, 1)
        
        # 개발예정 항목 (임시 목 데이터)
        retirement = 0  # 퇴직 예정 직원 수
        retirement_rate = 0.0  # 퇴직 예정률
        turnover_rate = 5.0  # 입퇴사율 (임시 고정값)
        working = active  # 근무 중 = 활성 직원
        working_rate = active_rate  # 근무 중 비율
        vacation = 0  # 휴가 중
        vacation_rate = 0.0  # 휴가 비율
        half_day = 0  # 반차 사용
        half_day_rate = 0.0  # 반차 비율
        sick_leave = 0  # 병가 사용
        sick_leave_rate = 0.0  # 병가 비율
        
        return {
            # 기존 통계
            'total': total,
            'active': active,
            'warning': warning,
            'expired': expired,
            'active_rate': active_rate,
            'warning_rate': warning_rate,
            'expired_rate': expired_rate,
            # 개발예정 항목
            'retirement': retirement,
            'retirement_rate': retirement_rate,
            'turnover_rate': turnover_rate,
            'working': working,
            'working_rate': working_rate,
            'vacation': vacation,
            'vacation_rate': vacation_rate,
            'half_day': half_day,
            'half_day_rate': half_day_rate,
            'sick_leave': sick_leave,
            'sick_leave_rate': sick_leave_rate
        }
    
    def get_department_statistics(self) -> Dict[str, int]:
        """부서별 통계 조회"""
        employees = self.get_all()
        dept_stats = {}
        
        for emp in employees:
            dept = emp.department
            dept_stats[dept] = dept_stats.get(dept, 0) + 1
        
        return dept_stats
    
    def get_recent_employees(self, limit: int = 5) -> List[Employee]:
        """최근 등록 직원 조회 (ID 기준 내림차순)"""
        employees = self.get_all()
        sorted_employees = sorted(employees, key=lambda e: e.id, reverse=True)
        return sorted_employees[:limit]
    
    def filter_by_department(self, department: str) -> List[Employee]:
        """부서별 필터링"""
        all_employees = self.get_all()
        return [emp for emp in all_employees if emp.department == department]
    
    def filter_by_position(self, position: str) -> List[Employee]:
        """직급별 필터링"""
        all_employees = self.get_all()
        return [emp for emp in all_employees if emp.position == position]
    
    def filter_employees(self, department: Optional[str] = None, 
                        position: Optional[str] = None, 
                        status: Optional[str] = None,
                        departments: Optional[List[str]] = None,
                        positions: Optional[List[str]] = None,
                        statuses: Optional[List[str]] = None) -> List[Employee]:
        """다중 필터 조합 지원"""
        all_employees = self.get_all()
        filtered = all_employees
        
        # 단일 부서 필터
        if department:
            filtered = [emp for emp in filtered if emp.department == department]
        
        # 다중 부서 필터
        if departments:
            filtered = [emp for emp in filtered if emp.department in departments]
        
        # 단일 직급 필터
        if position:
            filtered = [emp for emp in filtered if emp.position == position]
        
        # 다중 직급 필터
        if positions:
            filtered = [emp for emp in filtered if emp.position in positions]
        
        # 단일 상태 필터
        if status:
            filtered = [emp for emp in filtered if emp.status == status]
        
        # 다중 상태 필터
        if statuses:
            filtered = [emp for emp in filtered if emp.status in statuses]
        
        return filtered


class BaseRelationRepository:
    """관계형 데이터 레포지토리 기본 클래스"""

    def __init__(self, json_file_path: str, model_class):
        self.json_file_path = json_file_path
        self.model_class = model_class

    def _load_data(self) -> List[Dict]:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_all(self) -> List:
        """모든 데이터 조회"""
        data = self._load_data()
        return [self.model_class.from_dict(item) for item in data]

    def get_by_employee_id(self, employee_id: int) -> List:
        """직원 ID로 데이터 조회"""
        data = self._load_data()
        return [self.model_class.from_dict(item) for item in data
                if item.get('employee_id') == employee_id]


class EducationRepository(BaseRelationRepository):
    """학력 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Education)


class CareerRepository(BaseRelationRepository):
    """경력 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Career)


class CertificateRepository(BaseRelationRepository):
    """자격증 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Certificate)


class FamilyMemberRepository(BaseRelationRepository):
    """가족 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, FamilyMember)


class LanguageRepository(BaseRelationRepository):
    """언어능력 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Language)


class MilitaryServiceRepository(BaseRelationRepository):
    """병역 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, MilitaryService)

    def get_by_employee_id(self, employee_id: int) -> Optional[MilitaryService]:
        """직원 ID로 병역 정보 조회 (단일 객체 반환)"""
        data = self._load_data()
        for item in data:
            if item.get('employee_id') == employee_id:
                return self.model_class.from_dict(item)
        return None


class SalaryRepository(BaseRelationRepository):
    """급여 정보 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Salary)

    def get_by_employee_id(self, employee_id: int) -> Optional[Salary]:
        """직원 ID로 급여 정보 조회 (단일 객체 반환)"""
        data = self._load_data()
        for item in data:
            if item.get('employee_id') == employee_id:
                return self.model_class.from_dict(item)
        return None


class BenefitRepository(BaseRelationRepository):
    """복리후생/연차 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Benefit)

    def get_by_employee_id(self, employee_id: int) -> Optional[Benefit]:
        """직원 ID로 복리후생 정보 조회 (단일 객체 반환)"""
        data = self._load_data()
        for item in data:
            if item.get('employee_id') == employee_id:
                return self.model_class.from_dict(item)
        return None


class ContractRepository(BaseRelationRepository):
    """근로계약 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Contract)

    def get_by_employee_id(self, employee_id: int) -> Optional[Contract]:
        """직원 ID로 근로계약 정보 조회 (단일 객체 반환)"""
        data = self._load_data()
        for item in data:
            if item.get('employee_id') == employee_id:
                return self.model_class.from_dict(item)
        return None


class SalaryHistoryRepository(BaseRelationRepository):
    """연봉계약 이력 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, SalaryHistory)


class ClassificationOptionsRepository:
    """분류 옵션 데이터 저장소 (JSON 파일 기반)"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """데이터 파일이 없으면 기본값으로 생성"""
        if not os.path.exists(self.json_file_path):
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
            default_data = {
                "departments": ["개발팀", "디자인팀", "마케팅팀", "영업팀", "관리팀"],
                "positions": ["사원", "대리", "과장", "차장", "부장", "이사", "상무", "전무", "대표"],
                "statuses": [
                    {"value": "active", "label": "정상"},
                    {"value": "warning", "label": "대기"},
                    {"value": "expired", "label": "만료"}
                ]
            }
            self._save_data(default_data)
    
    def _load_data(self) -> Dict:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "departments": [],
                "positions": [],
                "statuses": []
            }
    
    def _save_data(self, data: Dict):
        """JSON 파일에 데이터 저장"""
        with open(self.json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all(self) -> Dict:
        """모든 옵션 조회"""
        return self._load_data()
    
    def get_departments(self) -> List[str]:
        """부서 목록 조회"""
        data = self._load_data()
        return data.get('departments', [])
    
    def get_positions(self) -> List[str]:
        """직급 목록 조회"""
        data = self._load_data()
        return data.get('positions', [])
    
    def get_statuses(self) -> List[Dict]:
        """상태 목록 조회"""
        data = self._load_data()
        return data.get('statuses', [])
    
    def add_department(self, department: str) -> bool:
        """부서 추가"""
        data = self._load_data()
        departments = data.get('departments', [])
        if department not in departments:
            departments.append(department)
            data['departments'] = departments
            self._save_data(data)
            return True
        return False
    
    def update_department(self, old_department: str, new_department: str) -> bool:
        """부서 수정"""
        data = self._load_data()
        departments = data.get('departments', [])
        if old_department in departments:
            index = departments.index(old_department)
            departments[index] = new_department
            data['departments'] = departments
            self._save_data(data)
            return True
        return False
    
    def delete_department(self, department: str) -> bool:
        """부서 삭제"""
        data = self._load_data()
        departments = data.get('departments', [])
        if department in departments:
            departments.remove(department)
            data['departments'] = departments
            self._save_data(data)
            return True
        return False
    
    def add_position(self, position: str) -> bool:
        """직급 추가"""
        data = self._load_data()
        positions = data.get('positions', [])
        if position not in positions:
            positions.append(position)
            data['positions'] = positions
            self._save_data(data)
            return True
        return False
    
    def update_position(self, old_position: str, new_position: str) -> bool:
        """직급 수정"""
        data = self._load_data()
        positions = data.get('positions', [])
        if old_position in positions:
            index = positions.index(old_position)
            positions[index] = new_position
            data['positions'] = positions
            self._save_data(data)
            return True
        return False
    
    def delete_position(self, position: str) -> bool:
        """직급 삭제"""
        data = self._load_data()
        positions = data.get('positions', [])
        if position in positions:
            positions.remove(position)
            data['positions'] = positions
            self._save_data(data)
            return True
        return False
    
    def add_status(self, value: str, label: str) -> bool:
        """상태 추가"""
        data = self._load_data()
        statuses = data.get('statuses', [])
        if not any(s['value'] == value for s in statuses):
            statuses.append({"value": value, "label": label})
            data['statuses'] = statuses
            self._save_data(data)
            return True
        return False
    
    def update_status(self, old_value: str, new_value: str, new_label: str) -> bool:
        """상태 수정"""
        data = self._load_data()
        statuses = data.get('statuses', [])
        for status in statuses:
            if status['value'] == old_value:
                status['value'] = new_value
                status['label'] = new_label
                data['statuses'] = statuses
                self._save_data(data)
                return True
        return False
    
    def delete_status(self, value: str) -> bool:
        """상태 삭제"""
        data = self._load_data()
        statuses = data.get('statuses', [])
        statuses = [s for s in statuses if s['value'] != value]
        if len(statuses) < len(data.get('statuses', [])):
            data['statuses'] = statuses
            self._save_data(data)
            return True
        return False


# ========================================
# Phase 3: 인사평가 기능 모델 및 Repository
# ========================================

class Promotion:
    """인사이동/승진 모델"""

    def __init__(self, id: int, employee_id: int, effective_date: str,
                 promotion_type: str, from_department: Optional[str],
                 to_department: str, from_position: Optional[str],
                 to_position: str, job_role: Optional[str] = None,
                 reason: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.effective_date = effective_date
        self.promotion_type = promotion_type
        self.from_department = from_department
        self.to_department = to_department
        self.from_position = from_position
        self.to_position = to_position
        self.job_role = job_role
        self.reason = reason

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'effective_date': self.effective_date,
            'promotion_type': self.promotion_type,
            'from_department': self.from_department,
            'to_department': self.to_department,
            'from_position': self.from_position,
            'to_position': self.to_position,
            'job_role': self.job_role,
            'reason': self.reason
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Promotion':
        return cls(**data)


class Evaluation:
    """인사고과 모델"""

    def __init__(self, id: int, employee_id: int, year: int,
                 q1_grade: Optional[str] = None, q2_grade: Optional[str] = None,
                 q3_grade: Optional[str] = None, q4_grade: Optional[str] = None,
                 overall_grade: Optional[str] = None,
                 salary_negotiation: Optional[str] = None,
                 note: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.year = year
        self.q1_grade = q1_grade
        self.q2_grade = q2_grade
        self.q3_grade = q3_grade
        self.q4_grade = q4_grade
        self.overall_grade = overall_grade
        self.salary_negotiation = salary_negotiation
        self.note = note

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'year': self.year,
            'q1_grade': self.q1_grade,
            'q2_grade': self.q2_grade,
            'q3_grade': self.q3_grade,
            'q4_grade': self.q4_grade,
            'overall_grade': self.overall_grade,
            'salary_negotiation': self.salary_negotiation,
            'note': self.note
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Evaluation':
        return cls(**data)


class Training:
    """교육훈련 모델"""

    def __init__(self, id: int, employee_id: int, training_date: str,
                 training_name: str, institution: str, hours: int,
                 completion_status: str, note: Optional[str] = None):
        self.id = id
        self.employee_id = employee_id
        self.training_date = training_date
        self.training_name = training_name
        self.institution = institution
        self.hours = hours
        self.completion_status = completion_status
        self.note = note

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'training_date': self.training_date,
            'training_name': self.training_name,
            'institution': self.institution,
            'hours': self.hours,
            'completion_status': self.completion_status,
            'note': self.note
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Training':
        return cls(**data)


class Attendance:
    """근태현황 모델"""

    def __init__(self, id: int, employee_id: int, year: int, month: int,
                 work_days: int, absent_days: int, late_count: int,
                 early_leave_count: int, annual_leave_used: int):
        self.id = id
        self.employee_id = employee_id
        self.year = year
        self.month = month
        self.work_days = work_days
        self.absent_days = absent_days
        self.late_count = late_count
        self.early_leave_count = early_leave_count
        self.annual_leave_used = annual_leave_used

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'year': self.year,
            'month': self.month,
            'work_days': self.work_days,
            'absent_days': self.absent_days,
            'late_count': self.late_count,
            'early_leave_count': self.early_leave_count,
            'annual_leave_used': self.annual_leave_used
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Attendance':
        return cls(**data)


class PromotionRepository(BaseRelationRepository):
    """인사이동/승진 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Promotion)


class EvaluationRepository(BaseRelationRepository):
    """인사고과 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Evaluation)


class TrainingRepository(BaseRelationRepository):
    """교육훈련 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Training)


class AttendanceRepository(BaseRelationRepository):
    """근태현황 데이터 저장소"""

    def __init__(self, json_file_path: str):
        super().__init__(json_file_path, Attendance)

    def get_by_employee_year(self, employee_id: int, year: int) -> List[Attendance]:
        """직원 ID와 연도로 근태 정보 조회"""
        data = self._load_data()
        return [self.model_class.from_dict(item) for item in data
                if item.get('employee_id') == employee_id and item.get('year') == year]

    def get_summary_by_employee(self, employee_id: int, year: int) -> Dict:
        """직원의 연간 근태 요약"""
        records = self.get_by_employee_year(employee_id, year)
        if not records:
            return {
                'total_work_days': 0,
                'total_absent_days': 0,
                'total_late_count': 0,
                'total_early_leave': 0,
                'total_annual_used': 0
            }
        return {
            'total_work_days': sum(r.work_days for r in records),
            'total_absent_days': sum(r.absent_days for r in records),
            'total_late_count': sum(r.late_count for r in records),
            'total_early_leave': sum(r.early_leave_count for r in records),
            'total_annual_used': sum(r.annual_leave_used for r in records)
        }

