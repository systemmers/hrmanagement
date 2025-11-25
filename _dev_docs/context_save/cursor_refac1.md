# 세션 만료 후 연결 방법
_Exported on 11/24/2025 at 17:51:11 GMT+9 from Cursor (2.1.25)_

---

**User**

세션이 만료되면 프로젝트를 새로운 세션으로 해야한다 어떻게 이전 세션과 연결하는가

---

**Cursor**


프로젝트의 세션 관리 방식을 확인 중입니다.



프로젝트 구조와 메인 애플리케이션 파일 확인 중입니다.



프로젝트의 컨텍스트 저장 관련 파일 확인 중입니다.



Cursor에서 세션이 만료되면 AI의 대화 컨텍스트는 초기화되지만, 프로젝트 파일과 코드는 그대로 유지됩니다. 새로운 세션에서 이전 작업을 이어가려면 다음을 활용하세요:

## 1. 프로젝트 문서 활용

프로젝트에 이미 문서화된 정보가 있습니다:
- `_dev_docs/info_list.md` - 프로젝트 요구사항 및 구조
- `_dev_docs/` 폴더의 기타 문서들
- `claude.md` - 프로젝트 기본 정보

새 세션 시작 시 이 문서들을 참고하도록 요청하세요.

## 2. 컨텍스트 복원 방법

새 세션에서 다음과 같이 요청하세요:

```
"이전 세션에서 작업하던 insacard 프로젝트를 이어서 진행합니다.
프로젝트 구조와 현재 상태를 파악해주세요."
```

또는 구체적으로:

```
"insacard Flask 프로젝트의 현재 상태를 분석하고,
app.py, models.py, forms.py를 읽어서 프로젝트 구조를 파악해주세요."
```

## 3. 컨텍스트 저장 폴더 활용

프로젝트에 `_dev_docs/context_save/` 폴더가 있습니다. 이 폴더에 다음을 저장하세요:

- 현재 작업 중인 기능/작업 목록
- 주요 결정 사항 및 아키텍처 결정
- 다음 단계 작업 계획
- 중요한 코드 스니펫이나 패턴

## 4. 권장 워크플로우

세션 전환 시:

1. 현재 작업 상태를 `_dev_docs/`에 문서화
2. 새 세션에서 프로젝트 루트의 주요 파일들을 읽도록 요청
3. 문서화된 정보를 참고하도록 안내
4. 이전 세션의 작업 내용을 요약해서 제공

현재 프로젝트 상태를 문서화하거나, 새 세션에서 복원할 정보가 있으면 알려주세요.

```plaintext
"이전 세션에서 작업하던 insacard 프로젝트를 이어서 진행합니다.
프로젝트 구조와 현재 상태를 파악해주세요."
```

```plaintext
"insacard Flask 프로젝트의 현재 상태를 분석하고,
app.py, models.py, forms.py를 읽어서 프로젝트 구조를 파악해주세요."
```

---

**User**

이전 내용을 가져올수 없는가

---

**Cursor**


이전 세션 내용을 가져오는 방법을 확인 중입니다.



프로젝트 관리 문서에서 세션 관리 방법을 확인했습니다. 이전 세션 내용을 가져오는 방법은 다음과 같습니다:



이전 세션 내용을 가져오는 방법:

## 1. SuperClaude 세션 관리 명령어 사용 (설정된 경우)

프로젝트에 SuperClaude 세션 관리가 설정되어 있다면:

```bash
# 이전 세션 컨텍스트 로드
/sc:load insacard

# 또는 프로젝트 경로 지정
/sc:load C:\workspace\insacard
```

이 명령어는:
- 이전 세션의 저장된 메모리를 읽어옵니다
- 프로젝트 컨텍스트와 결정 사항을 복원합니다
- 진행 상황과 패턴을 불러옵니다

## 2. Cursor 기본 기능 활용

### 방법 A: 프로젝트 파일 기반 복원
새 세션에서 다음을 요청하세요:

```
"insacard 프로젝트의 현재 상태를 파악해주세요.
app.py, models.py, forms.py, 그리고 _dev_docs 폴더의 문서들을 읽어서
이전에 작업하던 내용을 이해하고 이어서 진행하겠습니다."
```

### 방법 B: 최근 파일 정보 활용
Cursor는 최근에 열었던 파일 정보를 유지합니다. 새 세션에서:
- 열려있는 파일들을 확인
- 최근 수정된 파일들을 읽도록 요청
- 변경 이력을 통해 작업 내용 파악

## 3. 수동 컨텍스트 저장/복원

### 저장 (세션 종료 전)
`_dev_docs/context_save/` 폴더에 다음을 저장:

```markdown
# session_context_YYYYMMDD.md
## 현재 작업 중인 기능
- [작업 내용]

## 주요 결정 사항
- [결정 내용]

## 다음 단계
- [할 일]

## 중요 코드 스니펫
- [코드 위치 및 설명]
```

### 복원 (새 세션 시작 시)
```
"_dev_docs/context_save/ 폴더의 최근 세션 문서를 읽어서
이전 작업 내용을 복원해주세요."
```

## 4. 즉시 시도할 수 있는 방법

현재 세션에서 다음을 요청하세요:

```
"이전 세션에서 작업하던 insacard 프로젝트의 컨텍스트를 복원해주세요.
프로젝트의 주요 파일들과 문서를 읽어서 현재 상태를 파악하고,
이전에 논의했던 내용이나 진행 중이던 작업이 있다면 알려주세요."
```

또는 SuperClaude가 설정되어 있다면:

```
/sc:load insacard
```

어떤 방법을 사용할지 알려주시면 더 구체적으로 안내하겠습니다.

```shellscript
# 이전 세션 컨텍스트 로드
/sc:load insacard

# 또는 프로젝트 경로 지정
/sc:load C:\workspace\insacard
```

```plaintext
"insacard 프로젝트의 현재 상태를 파악해주세요.
app.py, models.py, forms.py, 그리고 _dev_docs 폴더의 문서들을 읽어서
이전에 작업하던 내용을 이해하고 이어서 진행하겠습니다."
```

```markdown
# session_context_YYYYMMDD.md
## 현재 작업 중인 기능
- [작업 내용]

## 주요 결정 사항
- [결정 내용]

## 다음 단계
- [할 일]

## 중요 코드 스니펫
- [코드 위치 및 설명]
```

```plaintext
"_dev_docs/context_save/ 폴더의 최근 세션 문서를 읽어서
이전 작업 내용을 복원해주세요."
```

```plaintext
"이전 세션에서 작업하던 insacard 프로젝트의 컨텍스트를 복원해주세요.
프로젝트의 주요 파일들과 문서를 읽어서 현재 상태를 파악하고,
이전에 논의했던 내용이나 진행 중이던 작업이 있다면 알려주세요."
```

```plaintext
/sc:load insacard
```

---

**User**

/sc/improve @insacard  "리팩토링" --soc --modular-phy --sql --preview --seq --depth deep

--- Cursor Command: sc/improve.md ---

# /sc:improve - Code Improvement

## Triggers
- Code quality enhancement and refactoring requests
- Performance optimization and bottleneck resolution needs
- Maintainability improvements and technical debt reduction
- Best practices application and coding standards enforcement

## Usage
```
/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```

## Behavioral Flow
1. **Analyze**: Examine codebase for improvement opportunities and quality issues
2. **Plan**: Choose improvement approach and activate relevant personas for expertise
3. **Execute**: Apply systematic improvements with domain-specific best practices
4. **Validate**: Ensure improvements preserve functionality and meet quality standards
5. **Document**: Generate improvement summary and recommendations for future work

Key behaviors:
- Multi-persona coordination (architect, performance, quality, security) based on improvement type
- Framework-specific optimization via Context7 integration for best practices
- Systematic analysis via Sequential MCP for complex multi-component improvements
- Safe refactoring with comprehensive validation and rollback capabilities

## MCP Integration
- **Sequential MCP**: Auto-activated for complex multi-step improvement analysis and planning
- **Context7 MCP**: Framework-specific best practices and optimization patterns
- **Persona Coordination**: Architect (structure), Performance (speed), Quality (maintainability), Security (safety)

## Tool Coordination
- **Read/Grep/Glob**: Code analysis and improvement opportunity identification
- **Edit/MultiEdit**: Safe code modification and systematic refactoring
- **TodoWrite**: Progress tracking for complex multi-file improvement operations
- **Task**: Delegation for large-scale improvement workflows requiring systematic coordination

## Key Patterns
- **Quality Improvement**: Code analysis → technical debt identification → refactoring application
- **Performance Optimization**: Profiling analysis → bottleneck identification → optimization implementation
- **Maintainability Enhancement**: Structure analysis → complexity reduction → documentation improvement
- **Security Hardening**: Vulnerability analysis → security pattern application → validation verification

## Examples

### Code Quality Enhancement
```
/sc:improve src/ --type quality --safe
# Systematic quality analysis with safe refactoring application
# Improves code structure, reduces technical debt, enhances readability
```

### Performance Optimization
```
/sc:improve api-endpoints --type performance --interactive
# Performance persona analyzes bottlenecks and optimization opportunities
# Interactive guidance for complex performance improvement decisions
```

### Maintainability Improvements
```
/sc:improve legacy-modules --type maintainability --preview
# Architect persona analyzes structure and suggests maintainability improvements
# Preview mode shows changes before application for review
```

### Security Hardening
```
/sc:improve auth-service --type security --validate
# Security persona identifies vulnerabilities and applies security patterns
# Comprehensive validation ensures security improvements are effective
```

## Boundaries

**Will:**
- Apply systematic improvements with domain-specific expertise and validation
- Provide comprehensive analysis with multi-persona coordination and best practices
- Execute safe refactoring with rollback capabilities and quality preservation

**Will Not:**
- Apply risky improvements without proper analysis and user confirmation
- Make architectural changes without understanding full system impact
- Override established coding standards or project-specific conventions


--- End Command ---

---

**Cursor**


프로젝트 구조와 코드를 분석해 리팩토링 계획을 수립 중입니다.



프로젝트 구조와 코드를 분석해 리팩토링 계획을 수립 중입니다.



리팩토링 계획 수립 중입니다. 확인이 필요한 사항이 있습니다.



리팩토링 계획 수립 중입니다.


---

**User**

정적 파일도 구조화하여라.

---

**Cursor**


정적 파일 구조화를 계획에 추가합니다. 현재 정적 파일 구조를 확인 중입니다.



정적 파일 구조화를 계획에 추가 중입니다.


---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**


첫 번째 TODO부터 진행합니다. 현재 파일을 확인하고 단계별로 리팩토링을 진행합니다.



Phase 1부터 진행합니다. 디렉토리 구조를 생성하고 파일을 분리합니다.



PowerShell에 맞게 명령을 수정합니다.



모델 파일 생성 중입니다.


```python
"""
데이터 모델 패키지
"""
from app.models.employee import Employee

__all__ = ['Employee']

```

```python
"""
직원 데이터 모델
"""
from typing import Dict


class Employee:
    """직원 모델"""
    
    def __init__(self, id: int, name: str, photo: str, department: str, 
                 position: str, status: str, hireDate: str, phone: str, email: str):
        self.id = id
        self.name = name
        self.photo = photo
        self.department = department
        self.position = position
        self.status = status
        self.hireDate = hireDate
        self.phone = phone
        self.email = email
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
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
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Employee':
        """딕셔너리에서 생성"""
        return cls(**data)

```

```python
"""
분류 옵션 모델 (향후 SQLAlchemy 마이그레이션용)
"""
from typing import Dict, List, Optional


class ClassificationOptions:
    """분류 옵션 모델 (향후 SQLAlchemy로 전환 예정)"""
    
    def __init__(self, departments: List[str], positions: List[str], statuses: List[Dict]):
        self.departments = departments
        self.positions = positions
        self.statuses = statuses
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'departments': self.departments,
            'positions': self.positions,
            'statuses': self.statuses
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClassificationOptions':
        """딕셔너리에서 생성"""
        return cls(
            departments=data.get('departments', []),
            positions=data.get('positions', []),
            statuses=data.get('statuses', [])
        )

```


리포지토리 파일 생성 중입니다.


```python
"""
데이터 접근 레이어 패키지
"""
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.classification_repository import ClassificationOptionsRepository

__all__ = ['EmployeeRepository', 'ClassificationOptionsRepository']

```

```python
"""
기본 리포지토리 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """기본 리포지토리 인터페이스"""
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """모든 엔티티 조회"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """ID로 엔티티 조회"""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """엔티티 생성"""
        pass
    
    @abstractmethod
    def update(self, entity_id: int, entity: T) -> Optional[T]:
        """엔티티 수정"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """엔티티 삭제"""
        pass

```

```python
"""
직원 데이터 저장소 (JSON 파일 기반)
"""
import json
import os
from typing import List, Optional, Dict
from app.models.employee import Employee


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
        
        return {
            'total': total,
            'active': active,
            'warning': warning,
            'expired': expired,
            'active_rate': round((active / total * 100) if total > 0 else 0, 1),
            'warning_rate': round((warning / total * 100) if total > 0 else 0, 1),
            'expired_rate': round((expired / total * 100) if total > 0 else 0, 1)
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

```

```python
"""
분류 옵션 데이터 저장소 (JSON 파일 기반)
"""
import json
import os
from typing import List, Dict


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

```


폼과 유틸리티 파일 생성 중입니다.


```python
"""
WTForms 폼 패키지
"""
from app.forms.employee_form import EmployeeForm

__all__ = ['EmployeeForm']

```

```python
"""
WTForms 폼 정의
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length


class EmployeeForm(FlaskForm):
    """직원 정보 입력 폼"""
    
    name = StringField('이름', validators=[
        DataRequired(message='이름은 필수 항목입니다.'),
        Length(min=2, max=50, message='이름은 2-50자 이내여야 합니다.')
    ])
    
    photo = StringField('사진 URL', validators=[
        Length(max=500, message='URL은 500자 이내여야 합니다.')
    ])
    
    department = StringField('부서', validators=[
        DataRequired(message='부서는 필수 항목입니다.'),
        Length(max=100, message='부서명은 100자 이내여야 합니다.')
    ])
    
    position = SelectField('직급', choices=[
        ('사원', '사원'),
        ('대리', '대리'),
        ('과장', '과장'),
        ('차장', '차장'),
        ('부장', '부장'),
        ('이사', '이사'),
        ('상무', '상무'),
        ('전무', '전무'),
        ('대표', '대표')
    ], validators=[DataRequired(message='직급은 필수 항목입니다.')])
    
    status = SelectField('재직 상태', choices=[
        ('active', '정상'),
        ('warning', '대기'),
        ('expired', '만료')
    ], validators=[DataRequired(message='재직 상태는 필수 항목입니다.')])
    
    hireDate = DateField('입사일', validators=[
        DataRequired(message='입사일은 필수 항목입니다.')
    ])
    
    phone = StringField('전화번호', validators=[
        DataRequired(message='전화번호는 필수 항목입니다.'),
        Length(min=10, max=20, message='전화번호 형식이 올바르지 않습니다.')
    ])
    
    email = StringField('이메일', validators=[
        DataRequired(message='이메일은 필수 항목입니다.'),
        Email(message='올바른 이메일 형식이 아닙니다.'),
        Length(max=100, message='이메일은 100자 이내여야 합니다.')
    ])

```

```python
"""
유틸리티 패키지
"""

```

```python
"""
템플릿 유틸리티 함수
"""


def format_phone(phone: str) -> str:
    """전화번호 포맷팅"""
    return phone


def get_status_badge_class(status: str) -> str:
    """상태 배지 CSS 클래스"""
    status_classes = {
        'active': 'badge-success',
        'warning': 'badge-warning',
        'expired': 'badge-danger'
    }
    return status_classes.get(status, 'badge-secondary')


def get_status_text(status: str) -> str:
    """상태 텍스트"""
    status_texts = {
        'active': '정상',
        'warning': '대기',
        'expired': '만료'
    }
    return status_texts.get(status, status)


def register_template_helpers(app):
    """템플릿 헬퍼 함수 등록"""
    @app.context_processor
    def utility_processor():
        """템플릿 유틸리티 함수"""
        return {
            'format_phone': format_phone,
            'get_status_badge_class': get_status_badge_class,
            'get_status_text': get_status_text
        }

```

```python
"""
커스텀 검증기
"""
from typing import Any, Callable


def validate_required(value: Any) -> bool:
    """필수 값 검증"""
    return value is not None and str(value).strip() != ''


def validate_email_format(email: str) -> bool:
    """이메일 형식 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_format(phone: str) -> bool:
    """전화번호 형식 검증"""
    import re
    # 숫자, 하이픈, 공백 제거 후 길이 확인
    cleaned = re.sub(r'[\s-]', '', phone)
    return cleaned.isdigit() and 10 <= len(cleaned) <= 11

```


config.py를 app/로 이동하고 서비스 레이어 생성 중입니다.


```python
"""
Flask 애플리케이션 설정 파일
"""
import os


class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 데이터 파일 경로
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    EMPLOYEES_JSON = os.path.join(DATA_DIR, 'employees.json')
    CLASSIFICATION_OPTIONS_JSON = os.path.join(DATA_DIR, 'classification_options.json')
    
    # Flask 설정
    DEBUG = True
    TESTING = False
    
    # WTForms 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True


class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    WTF_CSRF_ENABLED = False


# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

```

```python
"""
비즈니스 로직 레이어 패키지
"""
from app.services.employee_service import EmployeeService
from app.services.classification_service import ClassificationService

__all__ = ['EmployeeService', 'ClassificationService']

```

```python
"""
직원 비즈니스 로직 서비스
"""
from typing import List, Optional, Dict
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository


class EmployeeService:
    """직원 비즈니스 로직 서비스"""
    
    def __init__(self, employee_repo: EmployeeRepository):
        self.repo = employee_repo
    
    def get_all_employees(self) -> List[Employee]:
        """모든 직원 조회"""
        return self.repo.get_all()
    
    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """ID로 직원 조회"""
        return self.repo.get_by_id(employee_id)
    
    def create_employee(self, form_data: Dict) -> Employee:
        """직원 생성 (폼 데이터에서)"""
        employee = Employee(
            id=0,  # 자동 생성
            name=form_data.get('name', '').strip(),
            photo=form_data.get('photo', 'https://i.pravatar.cc/150').strip(),
            department=form_data.get('department', '').strip(),
            position=form_data.get('position', '').strip(),
            status=form_data.get('status', 'active').strip(),
            hireDate=form_data.get('hireDate', '').strip(),
            phone=form_data.get('phone', '').strip(),
            email=form_data.get('email', '').strip()
        )
        return self.repo.create(employee)
    
    def update_employee(self, employee_id: int, form_data: Dict) -> Optional[Employee]:
        """직원 수정 (폼 데이터에서)"""
        employee = Employee(
            id=employee_id,
            name=form_data.get('name', '').strip(),
            photo=form_data.get('photo', 'https://i.pravatar.cc/150').strip(),
            department=form_data.get('department', '').strip(),
            position=form_data.get('position', '').strip(),
            status=form_data.get('status', 'active').strip(),
            hireDate=form_data.get('hireDate', '').strip(),
            phone=form_data.get('phone', '').strip(),
            email=form_data.get('email', '').strip()
        )
        return self.repo.update(employee_id, employee)
    
    def delete_employee(self, employee_id: int) -> bool:
        """직원 삭제"""
        return self.repo.delete(employee_id)
    
    def search_employees(self, query: str) -> List[Employee]:
        """직원 검색"""
        return self.repo.search(query)
    
    def filter_employees(self, department: Optional[str] = None,
                        position: Optional[str] = None,
                        status: Optional[str] = None,
                        departments: Optional[List[str]] = None,
                        positions: Optional[List[str]] = None,
                        statuses: Optional[List[str]] = None) -> List[Employee]:
        """직원 필터링"""
        return self.repo.filter_employees(
            department=department,
            position=position,
            status=status,
            departments=departments,
            positions=positions,
            statuses=statuses
        )
    
    def get_statistics(self) -> Dict:
        """통계 정보 조회"""
        return self.repo.get_statistics()
    
    def get_department_statistics(self) -> Dict[str, int]:
        """부서별 통계 조회"""
        return self.repo.get_department_statistics()
    
    def get_recent_employees(self, limit: int = 5) -> List[Employee]:
        """최근 등록 직원 조회"""
        return self.repo.get_recent_employees(limit)

```

```python
"""
분류 옵션 비즈니스 로직 서비스
"""
from typing import List, Dict
from app.repositories.classification_repository import ClassificationOptionsRepository


class ClassificationService:
    """분류 옵션 비즈니스 로직 서비스"""
    
    def __init__(self, classification_repo: ClassificationOptionsRepository):
        self.repo = classification_repo
    
    def get_all_options(self) -> Dict:
        """모든 옵션 조회"""
        return self.repo.get_all()
    
    def get_departments(self) -> List[str]:
        """부서 목록 조회"""
        return self.repo.get_departments()
    
    def get_positions(self) -> List[str]:
        """직급 목록 조회"""
        return self.repo.get_positions()
    
    def get_statuses(self) -> List[Dict]:
        """상태 목록 조회"""
        return self.repo.get_statuses()
    
    def add_department(self, department: str) -> bool:
        """부서 추가"""
        return self.repo.add_department(department.strip())
    
    def update_department(self, old_department: str, new_department: str) -> bool:
        """부서 수정"""
        return self.repo.update_department(old_department.strip(), new_department.strip())
    
    def delete_department(self, department: str) -> bool:
        """부서 삭제"""
        return self.repo.delete_department(department)
    
    def add_position(self, position: str) -> bool:
        """직급 추가"""
        return self.repo.add_position(position.strip())
    
    def update_position(self, old_position: str, new_position: str) -> bool:
        """직급 수정"""
        return self.repo.update_position(old_position.strip(), new_position.strip())
    
    def delete_position(self, position: str) -> bool:
        """직급 삭제"""
        return self.repo.delete_position(position)
    
    def add_status(self, value: str, label: str) -> bool:
        """상태 추가"""
        return self.repo.add_status(value.strip(), label.strip())
    
    def update_status(self, old_value: str, new_value: str, new_label: str) -> bool:
        """상태 수정"""
        return self.repo.update_status(old_value.strip(), new_value.strip(), new_label.strip())
    
    def delete_status(self, value: str) -> bool:
        """상태 삭제"""
        return self.repo.delete_status(value)

```


Blueprint로 라우트 분리 중입니다.


```python
"""
라우트 패키지 - Blueprint 등록
"""
from flask import Flask
from app.services.employee_service import EmployeeService
from app.repositories.classification_repository import ClassificationOptionsRepository


def register_blueprints(app: Flask, employee_service: EmployeeService, 
                       classification_repo: ClassificationOptionsRepository):
    """Blueprint 등록"""
    from app.routes.dashboard import dashboard_bp
    from app.routes.employees import employees_bp
    from app.routes.classification import classification_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(classification_bp)

```

```python
"""
대시보드 라우트
"""
from flask import Blueprint, render_template, request, jsonify
from app.services.employee_service import EmployeeService
from app.repositories.classification_repository import ClassificationOptionsRepository

dashboard_bp = Blueprint('dashboard', __name__)


def init_dashboard_routes(employee_service: EmployeeService, 
                         classification_repo: ClassificationOptionsRepository):
    """대시보드 라우트 초기화"""
    
    @dashboard_bp.route('/')
    def index():
        """대시보드 - 통계 및 정보"""
        stats = employee_service.get_statistics()
        dept_stats = employee_service.get_department_statistics()
        recent_employees = employee_service.get_recent_employees(limit=5)
        classification_options = classification_repo.get_all()
        return render_template('index.html', 
                             stats=stats, 
                             dept_stats=dept_stats, 
                             recent_employees=recent_employees,
                             classification_options=classification_options)
    
    @dashboard_bp.route('/search')
    def search():
        """직원 검색"""
        query = request.args.get('q', '')
        status_filter = request.args.get('status', '')
        department_filter = request.args.get('department', '')
        position_filter = request.args.get('position', '')
        
        # 필터 적용
        if status_filter or department_filter or position_filter:
            employees = employee_service.filter_employees(
                department=department_filter if department_filter else None,
                position=position_filter if position_filter else None,
                status=status_filter if status_filter else None
            )
        elif query:
            employees = employee_service.search_employees(query)
        else:
            employees = employee_service.get_all_employees()
        
        stats = employee_service.get_statistics()
        
        # AJAX 요청인 경우 JSON 반환
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'employees': [emp.to_dict() for emp in employees],
                'stats': stats
            })
        
        dept_stats = employee_service.get_department_statistics()
        recent_employees = employee_service.get_recent_employees(limit=5)
        classification_options = classification_repo.get_all()
        return render_template('index.html', 
                             employees=employees, 
                             stats=stats, 
                             dept_stats=dept_stats, 
                             recent_employees=recent_employees, 
                             search_query=query,
                             classification_options=classification_options)

```

```python
"""
직원 관리 라우트
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.employee_service import EmployeeService

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')


def init_employee_routes(employee_service: EmployeeService):
    """직원 라우트 초기화"""
    
    @employees_bp.route('/')
    def employee_list():
        """직원 목록"""
        # 필터 파라미터 추출
        departments = request.args.getlist('department')
        positions = request.args.getlist('position')
        statuses = request.args.getlist('status')
        
        # 단일 값도 지원 (하위 호환성)
        department = request.args.get('department', None)
        position = request.args.get('position', None)
        status = request.args.get('status', None)
        
        # 다중 필터 적용
        if departments or positions or statuses:
            employees = employee_service.filter_employees(
                departments=departments if departments else None,
                positions=positions if positions else None,
                statuses=statuses if statuses else None
            )
        elif department or position or status:
            employees = employee_service.filter_employees(
                department=department,
                position=position,
                status=status
            )
        else:
            employees = employee_service.get_all_employees()
        
        # 분류 옵션은 classification_repo에서 가져와야 하지만,
        # 여기서는 일단 빈 딕셔너리로 처리 (나중에 수정)
        from app.repositories.classification_repository import ClassificationOptionsRepository
        from app import create_app
        app = create_app()
        classification_repo = ClassificationOptionsRepository(app.config['CLASSIFICATION_OPTIONS_JSON'])
        classification_options = classification_repo.get_all()
        
        return render_template('employee_list.html', 
                             employees=employees, 
                             classification_options=classification_options)
    
    @employees_bp.route('/<int:employee_id>')
    def employee_detail(employee_id):
        """직원 상세 정보"""
        employee = employee_service.get_employee_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('dashboard.index'))
        return render_template('employee_detail.html', employee=employee)
    
    @employees_bp.route('/new', methods=['GET'])
    def employee_new():
        """직원 등록 폼"""
        return render_template('employee_form.html', employee=None, action='create')
    
    @employees_bp.route('', methods=['POST'])
    def employee_create():
        """직원 등록 처리"""
        try:
            created_employee = employee_service.create_employee(request.form)
            flash(f'{created_employee.name} 직원이 등록되었습니다.', 'success')
            return redirect(url_for('employees.employee_detail', employee_id=created_employee.id))
        except Exception as e:
            flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_new'))
    
    @employees_bp.route('/<int:employee_id>/edit', methods=['GET'])
    def employee_edit(employee_id):
        """직원 수정 폼"""
        employee = employee_service.get_employee_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('dashboard.index'))
        return render_template('employee_form.html', employee=employee, action='update')
    
    @employees_bp.route('/<int:employee_id>/update', methods=['POST'])
    def employee_update(employee_id):
        """직원 수정 처리"""
        try:
            updated_employee = employee_service.update_employee(employee_id, request.form)
            if updated_employee:
                flash(f'{updated_employee.name} 직원 정보가 수정되었습니다.', 'success')
                return redirect(url_for('employees.employee_detail', employee_id=employee_id))
            else:
                flash('직원을 찾을 수 없습니다.', 'error')
                return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(f'직원 수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))
    
    @employees_bp.route('/<int:employee_id>/delete', methods=['POST'])
    def employee_delete(employee_id):
        """직원 삭제 처리"""
        try:
            employee = employee_service.get_employee_by_id(employee_id)
            if employee:
                if employee_service.delete_employee(employee_id):
                    flash(f'{employee.name} 직원이 삭제되었습니다.', 'success')
                else:
                    flash('직원 삭제에 실패했습니다.', 'error')
            else:
                flash('직원을 찾을 수 없습니다.', 'error')
        except Exception as e:
            flash(f'직원 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
        
        return redirect(url_for('dashboard.index'))

```

```python
"""
분류 옵션 관리 라우트
"""
from flask import Blueprint, render_template, request, jsonify
from app.services.classification_service import ClassificationService

classification_bp = Blueprint('classification', __name__, url_prefix='/api/classification-options')


def init_classification_routes(classification_service: ClassificationService):
    """분류 옵션 라우트 초기화"""
    
    @classification_bp.route('', methods=['GET'])
    def get_classification_options():
        """분류 옵션 조회"""
        options = classification_service.get_all_options()
        return jsonify(options)
    
    @classification_bp.route('/departments', methods=['POST'])
    def add_department():
        """부서 추가"""
        data = request.get_json()
        department = data.get('department', '').strip()
        
        if not department:
            return jsonify({'error': '부서명이 필요합니다.'}), 400
        
        if classification_service.add_department(department):
            return jsonify({'success': True, 'message': f'{department} 부서가 추가되었습니다.'}), 201
        else:
            return jsonify({'error': '이미 존재하는 부서입니다.'}), 400
    
    @classification_bp.route('/departments/<old_department>', methods=['PUT'])
    def update_department(old_department):
        """부서 수정"""
        data = request.get_json()
        new_department = data.get('department', '').strip()
        
        if not new_department:
            return jsonify({'error': '새 부서명이 필요합니다.'}), 400
        
        if classification_service.update_department(old_department, new_department):
            return jsonify({'success': True, 'message': f'부서가 {new_department}로 변경되었습니다.'}), 200
        else:
            return jsonify({'error': '부서를 찾을 수 없습니다.'}), 404
    
    @classification_bp.route('/departments/<department>', methods=['DELETE'])
    def delete_department(department):
        """부서 삭제"""
        if classification_service.delete_department(department):
            return jsonify({'success': True, 'message': f'{department} 부서가 삭제되었습니다.'}), 200
        else:
            return jsonify({'error': '부서를 찾을 수 없습니다.'}), 404
    
    @classification_bp.route('/positions', methods=['POST'])
    def add_position():
        """직급 추가"""
        data = request.get_json()
        position = data.get('position', '').strip()
        
        if not position:
            return jsonify({'error': '직급명이 필요합니다.'}), 400
        
        if classification_service.add_position(position):
            return jsonify({'success': True, 'message': f'{position} 직급이 추가되었습니다.'}), 201
        else:
            return jsonify({'error': '이미 존재하는 직급입니다.'}), 400
    
    @classification_bp.route('/positions/<old_position>', methods=['PUT'])
    def update_position(old_position):
        """직급 수정"""
        data = request.get_json()
        new_position = data.get('position', '').strip()
        
        if not new_position:
            return jsonify({'error': '새 직급명이 필요합니다.'}), 400
        
        if classification_service.update_position(old_position, new_position):
            return jsonify({'success': True, 'message': f'직급이 {new_position}로 변경되었습니다.'}), 200
        else:
            return jsonify({'error': '직급을 찾을 수 없습니다.'}), 404
    
    @classification_bp.route('/positions/<position>', methods=['DELETE'])
    def delete_position(position):
        """직급 삭제"""
        if classification_service.delete_position(position):
            return jsonify({'success': True, 'message': f'{position} 직급이 삭제되었습니다.'}), 200
        else:
            return jsonify({'error': '직급을 찾을 수 없습니다.'}), 404
    
    @classification_bp.route('/statuses', methods=['POST'])
    def add_status():
        """상태 추가"""
        data = request.get_json()
        value = data.get('value', '').strip()
        label = data.get('label', '').strip()
        
        if not value or not label:
            return jsonify({'error': '상태 값과 라벨이 필요합니다.'}), 400
        
        if classification_service.add_status(value, label):
            return jsonify({'success': True, 'message': f'{label} 상태가 추가되었습니다.'}), 201
        else:
            return jsonify({'error': '이미 존재하는 상태입니다.'}), 400
    
    @classification_bp.route('/statuses/<old_value>', methods=['PUT'])
    def update_status(old_value):
        """상태 수정"""
        data = request.get_json()
        new_value = data.get('value', '').strip()
        new_label = data.get('label', '').strip()
        
        if not new_value or not new_label:
            return jsonify({'error': '새 상태 값과 라벨이 필요합니다.'}), 400
        
        if classification_service.update_status(old_value, new_value, new_label):
            return jsonify({'success': True, 'message': f'상태가 {new_label}로 변경되었습니다.'}), 200
        else:
            return jsonify({'error': '상태를 찾을 수 없습니다.'}), 404
    
    @classification_bp.route('/statuses/<value>', methods=['DELETE'])
    def delete_status(value):
        """상태 삭제"""
        if classification_service.delete_status(value):
            return jsonify({'success': True, 'message': '상태가 삭제되었습니다.'}), 200
        else:
            return jsonify({'error': '상태를 찾을 수 없습니다.'}), 404


# 페이지 라우트 (별도 Blueprint)
classification_page_bp = Blueprint('classification_page', __name__)


def init_classification_page_routes(classification_service: ClassificationService):
    """분류 옵션 페이지 라우트 초기화"""
    
    @classification_page_bp.route('/classification-options')
    def classification_options_page():
        """분류 옵션 관리 페이지"""
        options = classification_service.get_all_options()
        return render_template('classification_options.html', classification_options=options)

```


Flask 앱 팩토리 생성 중입니다. 라우트 초기화 방식을 수정합니다.


```python
"""
Flask 애플리케이션 팩토리
"""
from flask import Flask
from app.config import config
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.classification_repository import ClassificationOptionsRepository
from app.services.employee_service import EmployeeService
from app.services.classification_service import ClassificationService
from app.utils.template_helpers import register_template_helpers


def create_app(config_name: str = 'development') -> Flask:
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 리포지토리 초기화
    employee_repo = EmployeeRepository(app.config['EMPLOYEES_JSON'])
    classification_repo = ClassificationOptionsRepository(app.config['CLASSIFICATION_OPTIONS_JSON'])
    
    # 서비스 초기화
    employee_service = EmployeeService(employee_repo)
    classification_service = ClassificationService(classification_repo)
    
    # Blueprint 등록
    from app.routes import register_blueprints
    register_blueprints(app, employee_service, classification_repo)
    
    # 분류 옵션 페이지 라우트 등록
    from app.routes.classification import classification_page_bp, init_classification_page_routes
    init_classification_page_routes(classification_service)
    app.register_blueprint(classification_page_bp)
    
    # 라우트 초기화 (서비스 주입)
    from app.routes.dashboard import init_dashboard_routes
    from app.routes.employees import init_employee_routes
    from app.routes.classification import init_classification_routes
    
    init_dashboard_routes(employee_service, classification_repo)
    init_employee_routes(employee_service)
    init_classification_routes(classification_service)
    
    # 에러 핸들러 등록
    register_error_handlers(app)
    
    # 템플릿 헬퍼 등록
    register_template_helpers(app)
    
    return app


def register_error_handlers(app: Flask):
    """에러 핸들러 등록"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """404 에러 핸들러"""
        return app.send_static_file('404.html') if app.has_static_folder else ('Not Found', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        return app.send_static_file('500.html') if app.has_static_folder else ('Internal Server Error', 500)

```

```python
"""
직원 관리 라우트
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.employee_service import EmployeeService

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')


def init_employee_routes(employee_service: EmployeeService):
    """직원 라우트 초기화"""
    
    @employees_bp.route('/')
    def employee_list():
        """직원 목록"""
        # 필터 파라미터 추출
        departments = request.args.getlist('department')
        positions = request.args.getlist('position')
        statuses = request.args.getlist('status')
        
        # 단일 값도 지원 (하위 호환성)
        department = request.args.get('department', None)
        position = request.args.get('position', None)
        status = request.args.get('status', None)
        
        # 다중 필터 적용
        if departments or positions or statuses:
            employees = employee_service.filter_employees(
                departments=departments if departments else None,
                positions=positions if positions else None,
                statuses=statuses if statuses else None
            )
        elif department or position or status:
            employees = employee_service.filter_employees(
                department=department,
                position=position,
                status=status
            )
        else:
            employees = employee_service.get_all_employees()
        
        # 분류 옵션은 전역에서 가져옴 (임시)
        from flask import current_app
        from app.repositories.classification_repository import ClassificationOptionsRepository
        classification_repo = ClassificationOptionsRepository(current_app.config['CLASSIFICATION_OPTIONS_JSON'])
        classification_options = classification_repo.get_all()
        
        return render_template('employee_list.html', 
                             employees=employees, 
                             classification_options=classification_options)
    
    @employees_bp.route('/<int:employee_id>')
    def employee_detail(employee_id):
        """직원 상세 정보"""
        employee = employee_service.get_employee_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('dashboard.index'))
        return render_template('employee_detail.html', employee=employee)
    
    @employees_bp.route('/new', methods=['GET'])
    def employee_new():
        """직원 등록 폼"""
        return render_template('employee_form.html', employee=None, action='create')
    
    @employees_bp.route('', methods=['POST'])
    def employee_create():
        """직원 등록 처리"""
        try:
            created_employee = employee_service.create_employee(request.form)
            flash(f'{created_employee.name} 직원이 등록되었습니다.', 'success')
            return redirect(url_for('employees.employee_detail', employee_id=created_employee.id))
        except Exception as e:
            flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_new'))
    
    @employees_bp.route('/<int:employee_id>/edit', methods=['GET'])
    def employee_edit(employee_id):
        """직원 수정 폼"""
        employee = employee_service.get_employee_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('dashboard.index'))
        return render_template('employee_form.html', employee=employee, action='update')
    
    @employees_bp.route('/<int:employee_id>/update', methods=['POST'])
    def employee_update(employee_id):
        """직원 수정 처리"""
        try:
            updated_employee = employee_service.update_employee(employee_id, request.form)
            if updated_employee:
                flash(f'{updated_employee.name} 직원 정보가 수정되었습니다.', 'success')
                return redirect(url_for('employees.employee_detail', employee_id=employee_id))
            else:
                flash('직원을 찾을 수 없습니다.', 'error')
                return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(f'직원 수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))
    
    @employees_bp.route('/<int:employee_id>/delete', methods=['POST'])
    def employee_delete(employee_id):
        """직원 삭제 처리"""
        try:
            employee = employee_service.get_employee_by_id(employee_id)
            if employee:
                if employee_service.delete_employee(employee_id):
                    flash(f'{employee.name} 직원이 삭제되었습니다.', 'success')
                else:
                    flash('직원 삭제에 실패했습니다.', 'error')
            else:
                flash('직원을 찾을 수 없습니다.', 'error')
        except Exception as e:
            flash(f'직원 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
        
        return redirect(url_for('dashboard.index'))


```

```python
"""
라우트 패키지 - Blueprint 등록
"""
from flask import Flask
from app.services.employee_service import EmployeeService
from app.repositories.classification_repository import ClassificationOptionsRepository


def register_blueprints(app: Flask, employee_service: EmployeeService, 
                       classification_repo: ClassificationOptionsRepository):
    """Blueprint 등록"""
    from app.routes.dashboard import dashboard_bp
    from app.routes.employees import employees_bp
    from app.routes.classification import classification_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(classification_bp)
    
    # 라우트 초기화 (서비스 주입)
    from app.routes.dashboard import init_dashboard_routes
    from app.routes.employees import init_employee_routes
    from app.routes.classification import init_classification_routes
    from app.services.classification_service import ClassificationService
    
    classification_service = ClassificationService(classification_repo)
    
    init_dashboard_routes(employee_service, classification_repo)
    init_employee_routes(employee_service)
    init_classification_routes(classification_service)


```

```python
"""
Flask 애플리케이션 팩토리
"""
from flask import Flask
from app.config import config
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.classification_repository import ClassificationOptionsRepository
from app.services.employee_service import EmployeeService
from app.services.classification_service import ClassificationService
from app.utils.template_helpers import register_template_helpers


def create_app(config_name: str = 'development') -> Flask:
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 리포지토리 초기화
    employee_repo = EmployeeRepository(app.config['EMPLOYEES_JSON'])
    classification_repo = ClassificationOptionsRepository(app.config['CLASSIFICATION_OPTIONS_JSON'])
    
    # 서비스 초기화
    employee_service = EmployeeService(employee_repo)
    classification_service = ClassificationService(classification_repo)
    
    # Blueprint 등록 및 라우트 초기화
    from app.routes import register_blueprints
    register_blueprints(app, employee_service, classification_repo)
    
    # 분류 옵션 페이지 라우트 등록
    from app.routes.classification import classification_page_bp, init_classification_page_routes
    init_classification_page_routes(classification_service)
    app.register_blueprint(classification_page_bp)
    
    # 에러 핸들러 등록
    register_error_handlers(app)
    
    # 템플릿 헬퍼 등록
    register_template_helpers(app)
    
    return app


def register_error_handlers(app: Flask):
    """에러 핸들러 등록"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """404 에러 핸들러"""
        return app.send_static_file('404.html') if app.has_static_folder else ('Not Found', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        return app.send_static_file('500.html') if app.has_static_folder else ('Internal Server Error', 500)


```

```python
"""
애플리케이션 실행 진입점
"""
from app import create_app
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

```


정적 파일 구조화 진행 중입니다. CSS부터 분리합니다.



CSS 파일을 모듈별로 분리 중입니다. 전체 파일을 읽어 구조를 파악합니다.



CSS를 모듈별로 분리 중입니다. 주요 파일부터 생성합니다.


```css
/* ========================================
   디자인 시스템 CSS 변수
   ======================================== */
:root {
    /* 색상 팔레트 - 15단계 따뜻한 그레이 톤 */
    --color-pure-black: #000000;
    --color-pure-white: #ffffff;
    --color-gray-25: #fcfcfc;
    --color-gray-50: #f9f9f9;
    --color-gray-75: #f6f6f6;
    --color-gray-100: #f1f1f1;
    --color-gray-200: #e4e4e4;
    --color-gray-300: #d1d1d1;
    --color-gray-400: #b4b4b4;
    --color-gray-500: #888888;
    --color-gray-600: #6b6b6b;
    --color-gray-700: #515151;
    --color-gray-800: #343434;
    --color-gray-900: #1a1a1a;

    /* 타이포그래피 */
    --font-family: 'Inter', system-ui, -apple-system, sans-serif;
    --text-2xs: 0.6875rem;   /* 11px */
    --text-xs: 0.75rem;      /* 12px */
    --text-sm: 0.8125rem;    /* 13px */
    --text-base: 0.875rem;   /* 14px */
    --text-md: 0.9375rem;    /* 15px */
    --text-lg: 1rem;         /* 16px */
    --text-xl: 1.125rem;     /* 18px */
    --text-2xl: 1.25rem;     /* 20px */
    --text-3xl: 1.5rem;      /* 24px */
    --text-4xl: 2rem;        /* 32px */

    /* 간격 - 13단계 정밀 시스템 */
    --space-0-5: 0.125rem;  /* 2px */
    --space-1: 0.25rem;     /* 4px */
    --space-1-5: 0.375rem;  /* 6px */
    --space-2: 0.5rem;      /* 8px */
    --space-2-5: 0.625rem;  /* 10px */
    --space-3: 0.75rem;     /* 12px */
    --space-4: 1rem;        /* 16px */
    --space-5: 1.25rem;     /* 20px */
    --space-6: 1.5rem;      /* 24px */
    --space-8: 2rem;        /* 32px */
    --space-10: 2.5rem;     /* 40px */
    --space-12: 3rem;       /* 48px */
    --space-16: 4rem;       /* 64px */

    /* 모서리 */
    --radius-xs: 0.1875rem;  /* 3px */
    --radius-sm: 0.25rem;    /* 4px */
    --radius-md: 0.375rem;   /* 6px */
    --radius-lg: 0.5rem;     /* 8px */
    --radius-xl: 0.75rem;    /* 12px */
    --radius-2xl: 1rem;      /* 16px */

    /* 그림자 */
    --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow-md: 0 2px 4px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 8px 25px rgba(0, 0, 0, 0.15);

    /* 전환 */
    --transition-fast: 120ms cubic-bezier(0.4, 0.0, 0.2, 1);
    --transition-normal: 200ms cubic-bezier(0.4, 0.0, 0.2, 1);
    --transition-slow: 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}

```

```css
/* ========================================
   기본 리셋 및 스타일
   ======================================== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-family);
    font-size: var(--text-base);
    line-height: 1.6;
    color: var(--color-gray-900);
    background-color: var(--color-gray-25);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow: hidden;
}

```

```css
/* ========================================
   타이포그래피
   ======================================== */
/* 기본 타이포그래피는 variables.css의 CSS 변수로 관리됨 */

```

```css
/* ========================================
   상단 헤더
   ======================================== */
.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background-color: var(--color-pure-white);
    border-bottom: 1px solid var(--color-gray-200);
    display: flex;
    align-items: center;
    padding: 0 var(--space-6);
    z-index: 100;
}

.header-brand {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-right: var(--space-8);
}

.header-logo {
    width: 36px;
    height: 36px;
    background-color: var(--color-gray-900);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-pure-white);
    font-weight: 700;
    font-size: var(--text-lg);
}

.header-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-gray-900);
}

.header-search {
    flex: 1;
    max-width: 500px;
    position: relative;
}

.header-search-input {
    width: 100%;
    padding: var(--space-2-5) var(--space-4);
    padding-left: var(--space-10);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    transition: all var(--transition-fast);
}

.header-search-input:focus {
    outline: none;
    border-color: var(--color-gray-900);
    box-shadow: var(--shadow-sm);
}

.header-search-icon {
    position: absolute;
    left: var(--space-3);
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-gray-500);
    pointer-events: none;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-left: auto;
}

.header-user {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.header-user:hover {
    background-color: var(--color-gray-50);
}

.header-user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--color-gray-900);
    color: var(--color-pure-white);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: var(--text-sm);
}

.header-user-name {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-gray-900);
}

.btn-logout {
    padding: var(--space-2) var(--space-4);
    border: 1px solid var(--color-gray-300);
    background-color: var(--color-pure-white);
    color: var(--color-gray-700);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.btn-logout:hover {
    background-color: var(--color-gray-50);
    border-color: var(--color-gray-400);
}

```

```css
/* ========================================
   좌측 사이드바
   ======================================== */
.sidebar {
    width: 280px;
    background-color: var(--color-pure-white);
    border-right: 1px solid var(--color-gray-200);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    height: 100%;
    overflow-y: auto;
}

.sidebar-header {
    padding: var(--space-6);
    border-bottom: 1px solid var(--color-gray-200);
}

.sidebar-title {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-gray-900);
    margin-bottom: var(--space-1);
}

.sidebar-subtitle {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
}

.sidebar-nav {
    flex: 1;
    padding: var(--space-4);
}

.nav-section {
    margin-bottom: var(--space-6);
}

.nav-section-title {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--color-gray-600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-3);
    padding: 0 var(--space-2);
}

.nav-item {
    display: flex;
    align-items: center;
    padding: var(--space-2-5) var(--space-3);
    color: var(--color-gray-700);
    text-decoration: none;
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    cursor: pointer;
    margin-bottom: var(--space-1);
}

.nav-item:hover {
    background-color: var(--color-gray-50);
    color: var(--color-gray-900);
}

.nav-item.active {
    background-color: var(--color-gray-900);
    color: var(--color-pure-white);
}

.nav-item i {
    width: 20px;
    margin-right: var(--space-3);
    font-size: var(--text-sm);
}

.search-input {
    width: 100%;
    padding: var(--space-2-5) var(--space-3);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    margin-bottom: var(--space-3);
    transition: all var(--transition-fast);
}

.search-input:focus {
    outline: none;
    border-color: var(--color-gray-900);
    box-shadow: var(--shadow-sm);
}

.sidebar-footer {
    padding: var(--space-4);
    border-top: 1px solid var(--color-gray-200);
}

.user-info {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--color-gray-900);
    color: var(--color-pure-white);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.user-details {
    flex: 1;
}

.user-name {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-gray-900);
}

.user-role {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
}

```

```css
/* ========================================
   레이아웃 - 3컬럼
   ======================================== */
.app-container {
    display: flex;
    position: fixed;
    top: 64px;
    left: 0;
    right: 0;
    bottom: 0;
}

.app-layout {
    display: flex;
    width: 100%;
    height: 100%;
}

/* 메인 컨텐츠 */
.main-content {
    flex: 1;
    padding: var(--space-8);
    overflow-y: auto;
    background-color: var(--color-gray-25);
    height: 100%;
}

.page-header {
    margin-bottom: var(--space-6);
}

.page-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-2);
}

.page-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--color-gray-900);
}

.page-actions {
    display: flex;
    gap: var(--space-3);
    align-items: center;
}

.view-toggle-group {
    display: flex;
    gap: var(--space-1);
    background-color: var(--color-gray-100);
    border-radius: var(--radius-md);
    padding: var(--space-1);
}

.view-toggle-btn {
    padding: var(--space-2) var(--space-3);
    border: none;
    background-color: transparent;
    color: var(--color-gray-600);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
}

.view-toggle-btn:hover {
    background-color: var(--color-gray-200);
    color: var(--color-gray-900);
}

.view-toggle-btn.active {
    background-color: var(--color-pure-white);
    color: var(--color-gray-900);
    box-shadow: var(--shadow-xs);
}

.page-description {
    font-size: var(--text-sm);
    color: var(--color-gray-600);
}

/* 우측 사이드바 */
.right-sidebar {
    width: 320px;
    background-color: var(--color-pure-white);
    border-left: 1px solid var(--color-gray-200);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    height: 100%;
    overflow-y: auto;
}

.right-sidebar-header {
    padding: var(--space-6);
    border-bottom: 1px solid var(--color-gray-200);
}

.right-sidebar-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-gray-900);
}

.right-sidebar-content {
    flex: 1;
    padding: var(--space-4);
}

.file-card {
    background-color: var(--color-gray-50);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-md);
    padding: var(--space-3);
    margin-bottom: var(--space-3);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.file-card:hover {
    background-color: var(--color-gray-100);
    border-color: var(--color-gray-300);
}

.file-icon {
    width: 40px;
    height: 40px;
    background-color: var(--color-pure-white);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--text-xl);
    color: var(--color-gray-600);
}

.file-info {
    flex: 1;
}

.file-name {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-gray-900);
    margin-bottom: var(--space-0-5);
}

.file-meta {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
}

.file-viewer {
    margin-top: var(--space-4);
    padding: var(--space-4);
    background-color: var(--color-gray-50);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-md);
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-gray-400);
}

```

```css
/* ========================================
   그리드 시스템
   ======================================== */
/* 그리드 관련 스타일은 각 컴포넌트에서 정의됨 */

```


컴포넌트 CSS 파일 생성 중입니다.


```css
/* ========================================
   버튼 컴포넌트
   ======================================== */
.btn {
    padding: var(--space-2-5) var(--space-4);
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
}

.btn-primary {
    background-color: var(--color-gray-900);
    color: var(--color-pure-white);
}

.btn-primary:hover {
    background-color: var(--color-gray-800);
    box-shadow: var(--shadow-md);
}

.btn-secondary {
    background-color: var(--color-pure-white);
    color: var(--color-gray-700);
    border: 1px solid var(--color-gray-300);
}

.btn-secondary:hover {
    background-color: var(--color-gray-50);
    border-color: var(--color-gray-400);
}

.btn-danger {
    background-color: #ef4444;
    color: var(--color-pure-white);
    border: 1px solid #ef4444;
}

.btn-danger:hover {
    background-color: #dc2626;
    border-color: #dc2626;
    box-shadow: var(--shadow-md);
}

.btn-small {
    padding: var(--space-1-5) var(--space-3);
    font-size: var(--text-xs);
    flex: 1;
}

.btn-icon {
    width: 32px;
    height: 32px;
    border: none;
    background-color: transparent;
    color: var(--color-gray-600);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-icon:hover {
    background-color: var(--color-gray-100);
    color: var(--color-gray-900);
}

a.btn {
    text-decoration: none;
}

```

```css
/* ========================================
   카드 컴포넌트
   ======================================== */
.stat-card {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    transition: all var(--transition-fast);
}

.stat-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--color-gray-300);
}

.stat-label {
    font-size: var(--text-xs);
    color: var(--color-gray-600);
    margin-bottom: var(--space-2);
}

.stat-value {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--color-gray-900);
    margin-bottom: var(--space-1);
}

.stat-change {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
}

.employee-card {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    transition: all var(--transition-fast);
    cursor: pointer;
    position: relative;
}

.employee-card:hover {
    box-shadow: var(--shadow-lg);
    border-color: var(--color-gray-300);
    transform: translateY(-2px);
}

.employee-status {
    position: absolute;
    top: var(--space-4);
    right: var(--space-4);
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.employee-status.active {
    background-color: #10b981;
}

.employee-status.warning {
    background-color: #f59e0b;
}

.employee-status.expired {
    background-color: #ef4444;
}

.employee-photo {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin: 0 auto var(--space-4);
    object-fit: cover;
}

.employee-name {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-gray-900);
    text-align: center;
    margin-bottom: var(--space-1);
}

.employee-position {
    font-size: var(--text-sm);
    color: var(--color-gray-600);
    text-align: center;
    margin-bottom: var(--space-3);
}

.employee-meta {
    border-top: 1px solid var(--color-gray-200);
    padding-top: var(--space-3);
    font-size: var(--text-xs);
    color: var(--color-gray-500);
}

.employee-meta-item {
    display: flex;
    align-items: center;
    margin-bottom: var(--space-2);
}

.employee-meta-item i {
    width: 16px;
    margin-right: var(--space-2);
}

.employee-actions {
    display: flex;
    gap: var(--space-2);
    margin-top: var(--space-3);
}

.info-card {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: all var(--transition-fast);
}

.info-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--color-gray-300);
}

.info-card-header {
    padding: var(--space-5);
    border-bottom: 1px solid var(--color-gray-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-card-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-gray-900);
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.info-card-title i {
    color: var(--color-gray-500);
}

.info-card-link {
    font-size: var(--text-xs);
    color: var(--color-gray-600);
    text-decoration: none;
    transition: color var(--transition-fast);
}

.info-card-link:hover {
    color: var(--color-gray-900);
}

.info-card-content {
    padding: var(--space-5);
}

.empty-state {
    text-align: center;
    padding: var(--space-16) var(--space-8);
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
}

.empty-message {
    text-align: center;
    color: var(--color-gray-500);
    font-size: var(--text-sm);
    padding: var(--space-4);
}

```

```css
/* ========================================
   폼 컴포넌트
   ======================================== */
.form-container {
    max-width: 800px;
}

.employee-form {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-8);
}

.form-section {
    margin-bottom: var(--space-8);
}

.form-section:last-of-type {
    margin-bottom: 0;
}

.form-section-title {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-gray-900);
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-3);
    border-bottom: 2px solid var(--color-gray-200);
}

.form-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-4);
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.form-label {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-gray-700);
}

.required {
    color: #ef4444;
}

.form-input {
    padding: var(--space-3);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    transition: all var(--transition-fast);
    font-family: var(--font-family);
}

.form-input:focus {
    outline: none;
    border-color: var(--color-gray-900);
    box-shadow: var(--shadow-sm);
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3);
    margin-top: var(--space-6);
    padding-top: var(--space-6);
    border-top: 1px solid var(--color-gray-200);
}

```

```css
/* ========================================
   모달 컴포넌트
   ======================================== */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background-color: var(--color-pure-white);
    border-radius: var(--radius-lg);
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-5);
    border-bottom: 1px solid var(--color-gray-200);
}

.modal-title {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-gray-900);
}

.modal-close {
    background: none;
    border: none;
    font-size: var(--text-2xl);
    color: var(--color-gray-500);
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color var(--transition-fast);
}

.modal-close:hover {
    color: var(--color-gray-900);
}

.modal-body {
    padding: var(--space-5);
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3);
    padding: var(--space-5);
    border-top: 1px solid var(--color-gray-200);
}

```

```css
/* ========================================
   알림 컴포넌트
   ======================================== */
.flash-messages {
    margin-bottom: var(--space-6);
}

.alert {
    padding: var(--space-4);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-3);
    font-size: var(--text-sm);
}

.alert-success {
    background-color: #d1fae5;
    border: 1px solid #10b981;
    color: #065f46;
}

.alert-error {
    background-color: #fee2e2;
    border: 1px solid #ef4444;
    color: #991b1b;
}

.alert-info {
    background-color: #dbeafe;
    border: 1px solid #3b82f6;
    color: #1e3a8a;
}

/* 토스트 알림 */
.toast-container {
    position: fixed;
    top: var(--space-4);
    right: var(--space-4);
    z-index: 1000;
}

.toast {
    background-color: var(--color-gray-900);
    color: var(--color-pure-white);
    padding: var(--space-4) var(--space-5);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-xl);
    margin-bottom: var(--space-3);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast-icon {
    font-size: var(--text-lg);
}

.toast-message {
    font-size: var(--text-sm);
}

```

```css
/* ========================================
   필터 컴포넌트
   ======================================== */
.filter-bar {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    margin-bottom: var(--space-6);
    display: flex;
    gap: var(--space-4);
    align-items: flex-start;
    flex-wrap: wrap;
}

.filter-bar-collapsible {
    flex-direction: column;
}

.filter-toggle-btn {
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--color-gray-300);
    background-color: var(--color-gray-50);
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--color-gray-700);
    transition: all var(--transition-fast);
}

.filter-toggle-btn:hover {
    background-color: var(--color-gray-100);
    border-color: var(--color-gray-400);
}

.filter-content {
    display: flex;
    gap: var(--space-4);
    align-items: flex-start;
    flex-wrap: wrap;
    margin-top: var(--space-4);
    width: 100%;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    min-width: 150px;
}

.filter-label {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--color-gray-700);
}

.filter-select {
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    background-color: var(--color-pure-white);
    color: var(--color-gray-900);
    min-height: 100px;
    max-height: 150px;
    overflow-y: auto;
}

.filter-select:focus {
    outline: none;
    border-color: var(--color-gray-500);
    box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.05);
}

.filter-checkboxes {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.filter-checkbox-label {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--color-gray-700);
    cursor: pointer;
}

.filter-checkbox {
    width: 16px;
    height: 16px;
    cursor: pointer;
}

.filter-reset {
    align-self: flex-end;
}

/* 활성 필터 표시 */
.active-filters {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
}

.filter-tag {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1-5) var(--space-3);
    background-color: var(--color-gray-100);
    border: 1px solid var(--color-gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    color: var(--color-gray-700);
}

.filter-tag button {
    background: none;
    border: none;
    color: var(--color-gray-500);
    cursor: pointer;
    font-size: var(--text-sm);
    padding: 0;
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color var(--transition-fast);
}

.filter-tag button:hover {
    color: var(--color-gray-900);
}

```

```css
/* ========================================
   대시보드 페이지
   ======================================== */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-8);
}

.dashboard-info-section {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-6);
    margin-bottom: var(--space-8);
}

.dept-stats-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.dept-stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3);
    background-color: var(--color-gray-50);
    border-radius: var(--radius-md);
}

.dept-name {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-gray-900);
}

.dept-count {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-gray-700);
}

.recent-employees-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.recent-employee-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.recent-employee-item:hover {
    background-color: var(--color-gray-50);
}

.recent-employee-photo {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
}

.recent-employee-info {
    flex: 1;
}

.recent-employee-name {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-gray-900);
    margin-bottom: var(--space-0-5);
}

.recent-employee-meta {
    font-size: var(--text-xs);
    color: var(--color-gray-600);
}

.recent-employee-date {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
}

```

```css
/* ========================================
   직원 목록 페이지
   ======================================== */
.employee-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
}

```

```css
/* ========================================
   직원 상세 페이지
   ======================================== */
.detail-container {
    max-width: 1000px;
}

.detail-card {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.detail-header {
    display: flex;
    align-items: center;
    gap: var(--space-6);
    padding: var(--space-8);
    background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-pure-white) 100%);
    border-bottom: 1px solid var(--color-gray-200);
}

.detail-photo {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid var(--color-pure-white);
    box-shadow: var(--shadow-md);
}

.detail-info {
    flex: 1;
}

.detail-name {
    font-size: var(--text-3xl);
    font-weight: 700;
    color: var(--color-gray-900);
    margin-bottom: var(--space-2);
}

.detail-position {
    font-size: var(--text-lg);
    color: var(--color-gray-600);
    margin-bottom: var(--space-3);
}

.detail-body {
    padding: var(--space-8);
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-6);
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.info-label {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--color-gray-600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.info-value {
    font-size: var(--text-base);
    color: var(--color-gray-900);
    font-weight: 500;
}

```

```css
/* ========================================
   직원 폼 페이지
   ======================================== */
/* 폼 스타일은 components/forms.css에 정의됨 */

```

```css
/* ========================================
   간격 유틸리티 클래스
   ======================================== */
/* 간격은 CSS 변수로 관리되며, 필요시 유틸리티 클래스 추가 가능 */

```

```css
/* ========================================
   헬퍼 클래스
   ======================================== */
/* 배지 */
.badge {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    font-weight: 600;
}

.badge-success {
    background-color: #d1fae5;
    color: #065f46;
}

.badge-warning {
    background-color: #fef3c7;
    color: #92400e;
}

.badge-danger {
    background-color: #fee2e2;
    color: #991b1b;
}

.badge-secondary {
    background-color: var(--color-gray-200);
    color: var(--color-gray-700);
}

/* 테이블 스타일 */
.table-container {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table thead {
    background-color: var(--color-gray-50);
}

.data-table th {
    padding: var(--space-4);
    text-align: left;
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--color-gray-700);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--color-gray-200);
}

.data-table td {
    padding: var(--space-4);
    font-size: var(--text-sm);
    color: var(--color-gray-900);
    border-bottom: 1px solid var(--color-gray-100);
}

.data-table tbody tr:hover {
    background-color: var(--color-gray-25);
}

.table-actions {
    display: flex;
    gap: var(--space-2);
}

/* 옵션 관리 페이지 */
.options-section {
    background-color: var(--color-pure-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    margin-bottom: var(--space-6);
}

.options-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-4);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--color-gray-200);
}

.options-title {
    font-size: var(--text-xl);
    font-weight: 600;
    color: var(--color-gray-900);
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.options-title i {
    color: var(--color-gray-500);
}

.options-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.options-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3) var(--space-4);
    background-color: var(--color-gray-50);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
}

.options-item:hover {
    background-color: var(--color-gray-100);
}

.options-item-name {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--color-gray-900);
}

.status-label {
    font-weight: 600;
}

.status-value {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
    margin-left: var(--space-1);
}

.options-item-actions {
    display: flex;
    gap: var(--space-2);
}

```

```css
/* ========================================
   메인 CSS 파일 - 모든 스타일 임포트
   ======================================== */

/* Base */
@import url('base/variables.css');
@import url('base/reset.css');
@import url('base/typography.css');

/* Layout */
@import url('layout/header.css');
@import url('layout/sidebar.css');
@import url('layout/main-content.css');
@import url('layout/grid.css');

/* Components */
@import url('components/buttons.css');
@import url('components/cards.css');
@import url('components/forms.css');
@import url('components/modals.css');
@import url('components/alerts.css');
@import url('components/filters.css');

/* Pages */
@import url('pages/dashboard.css');
@import url('pages/employee-list.css');
@import url('pages/employee-detail.css');
@import url('pages/employee-form.css');

/* Utilities */
@import url('utilities/spacing.css');
@import url('utilities/helpers.css');

/* ========================================
   반응형 Breakpoints
   ======================================== */

/* Mobile: 320px ~ 767px */
@media (max-width: 767px) {
    .app-header {
        padding: 0 var(--space-4);
    }

    .header-brand {
        margin-right: var(--space-4);
    }

    .header-title {
        display: none;
    }

    .header-search {
        max-width: 200px;
    }

    .header-user-name {
        display: none;
    }

    .app-container {
        flex-direction: column;
    }

    .app-layout {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--color-gray-200);
        height: auto;
    }

    .main-content {
        padding: var(--space-4);
        height: auto;
    }

    .right-sidebar {
        width: 100%;
        border-left: none;
        border-top: 1px solid var(--color-gray-200);
        height: auto;
    }

    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .dashboard-info-section {
        grid-template-columns: 1fr;
    }

    .employee-grid {
        grid-template-columns: 1fr;
    }

    .page-title-row {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--space-3);
    }

    .page-actions {
        width: 100%;
    }

    .btn {
        flex: 1;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }

    .detail-header {
        flex-direction: column;
        text-align: center;
    }

    .table-container {
        overflow-x: auto;
    }

    .data-table {
        min-width: 800px;
    }
}

/* Tablet: 768px ~ 1023px */
@media (min-width: 768px) and (max-width: 1023px) {
    .sidebar {
        width: 240px;
    }

    .right-sidebar {
        width: 280px;
    }

    .dashboard-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .dashboard-info-section {
        grid-template-columns: 1fr;
    }

    .employee-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .main-content {
        padding: var(--space-6);
    }
}

/* Desktop: 1024px ~ */
@media (min-width: 1024px) {
    /* 기본 스타일 유지 */
}

```

