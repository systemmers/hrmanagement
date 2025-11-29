# HR Management System - Development Workflow

## Document Info
- Created: 2025-11-29
- Last Updated: 2025-11-29
- Status: Draft
- Branch: new

---

## 1. Project Analysis Summary

### 1.1 Current Implementation Status

| Category | Completion | Details |
|----------|------------|---------|
| Data Models | 95% | 21 models (Employee, Contract, Salary, etc.) |
| Employee Detail View | 90% | 14 sections complete |
| Employee Registration Form | 60% | 8 sections, some missing |
| Authentication System | 0% | Not implemented |
| Organization Management | 0% | Not implemented |
| E-Contract System | 0% | Not implemented |

### 1.2 Gap Analysis (note.md vs Current)

#### Implemented (Core)
- Employee CRUD operations
- Employee detail page (all 14 sections)
- Relational data models
- Repository pattern data access layer
- Attachment sidebar UI

#### Partial Implementation (Needs Improvement)
| Item | Current | Required (note.md) |
|------|---------|-------------------|
| Photo Upload | URL input | 10+ photos, selection feature |
| Address Input | Text input | Daum Address API modal |
| Resident Number | Masked input | Auto gender/birthdate extraction |
| Employee Form | 8 sections | Missing: Salary, Insurance, Language, Project |

#### Not Implemented (Major Gaps)
- User authentication and authorization
- Organization structure (tree hierarchy)
- Auto employee number generation
- Auto email setup
- E-contract system
- Excel import/export
- Payslip generation
- Business card generation

---

## 2. Development Phases

### Phase 0: Immediate Improvements (1-2 weeks)
**Goal**: Quick wins that can be implemented within current codebase

#### Tasks
- [ ] P0-1: Add missing form sections (Salary, Insurance, Language, Project)
- [ ] P0-2: Integrate Daum Address API
- [ ] P0-3: Implement employee number auto-generation
- [ ] P0-4: File upload functionality (photos, attachments)
- [ ] P0-5: Improve employee list sorting/filtering

#### Checklist
- [ ] No breaking changes to existing functionality
- [ ] Follow existing code patterns (Repository pattern)
- [ ] Code review before merge
- [ ] Update CHANGELOG

---

### Phase 1: Foundation System (3-4 weeks)
**Goal**: Build core infrastructure

#### 1.1 Authentication System
- [ ] P1-1: Create User model
  - Fields: id, username, email, password_hash, role, employee_id
  - Roles: admin, manager, employee
- [ ] P1-2: Implement login/logout endpoints
- [ ] P1-3: Add role-based access control (RBAC)
- [ ] P1-4: Create auth decorators (@login_required, @role_required)

#### 1.2 Organization Structure
- [ ] P1-5: Create Organization/Department models
  - Tree structure with parent_id
  - Types: company, division, department, team
- [ ] P1-6: Build organization management UI
- [ ] P1-7: Implement tree selector component
- [ ] P1-8: Create position/grade code management

#### 1.3 System Settings
- [ ] P1-9: Create SystemSetting model
- [ ] P1-10: Employee number generation rules
- [ ] P1-11: Email domain configuration
- [ ] P1-12: Company basic information

#### Checklist
- [ ] Security review (password hashing, session management)
- [ ] Database migrations created
- [ ] API documentation updated
- [ ] Unit tests for auth system

---

### Phase 2: Contract/Document Management (2-3 weeks)
**Goal**: Contract template and document generation

#### Tasks
- [ ] P2-1: Create contract template system
  - Employment contract
  - Salary contract
  - NDA and other documents
- [ ] P2-2: Implement PDF generation (ReportLab/WeasyPrint)
- [ ] P2-3: Contract preview functionality
- [ ] P2-4: Contract history management
- [ ] P2-5: Payslip generation

#### Checklist
- [ ] Template customization options
- [ ] Data merge validation
- [ ] PDF output quality check

---

### Phase 3: Bulk Processing (2 weeks)
**Goal**: Excel and batch operations

#### Tasks
- [ ] P3-1: Excel export (employee list, salary ledger)
- [ ] P3-2: Excel import (attendance, salary)
- [ ] P3-3: Batch personnel movement screen
- [ ] P3-4: Batch contract processing

#### Checklist
- [ ] Error handling for invalid data
- [ ] Progress indicator for large files
- [ ] Data validation rules

---

### Phase 4: Advanced Features (As needed)
**Goal**: Nice-to-have features

#### Tasks
- [ ] P4-1: Electronic signature
- [ ] P4-2: Business card generation
- [ ] P4-3: Resume templates
- [ ] P4-4: Dashboard and statistics
- [ ] P4-5: Notification system

---

## 3. Technical Specifications

### 3.1 Technology Stack
- Backend: Flask (Python)
- Database: SQLAlchemy ORM
- Frontend: Jinja2 templates + Vanilla JS
- Pattern: Repository pattern

### 3.2 Dependencies to Add
```
# Phase 0
# No new dependencies

# Phase 1
Flask-Login==0.6.3      # or session-based auth
Werkzeug>=3.0.0         # password hashing

# Phase 2
reportlab==4.0.0        # PDF generation
# or
weasyprint==60.0        # HTML to PDF

# Phase 3
openpyxl==3.1.0         # Excel read/write
pandas==2.0.0           # Data processing (optional)
```

### 3.3 File Structure (Planned)
```
app/
  models/
    user.py              # New: User model
    organization.py      # New: Organization model
    system_setting.py    # New: System settings
  blueprints/
    auth.py              # New: Authentication
    admin/
      organization.py    # New: Org management
      settings.py        # New: System settings
  services/
    auth_service.py      # New: Auth business logic
    document_service.py  # New: PDF generation
    excel_service.py     # New: Excel processing
  utils/
    decorators.py        # New: Auth decorators
    validators.py        # New: Input validation
  templates/
    auth/
      login.html         # New: Login page
    admin/
      organization.html  # New: Org management
      settings.html      # New: System settings
```

---

## 4. Code Standards (from CLAUDE.md)

### 4.1 Must Follow
- Korean communication
- No emojis in code/docs
- DRY principle
- snake_case for Python files
- Max 500-800 lines per file
- Docstring at file top
- No magic numbers (use constants)
- No unauthorized work

### 4.2 Process
- Ask questions when unclear
- Propose balanced alternatives
- Critical thinking before implementation
- Version control tracking
- CHANGELOG updates

---

## 5. Git Workflow

### 5.1 Branch Strategy
```
master          # Production
  |-- new       # Current development (current branch)
      |-- feature/phase0-form-sections
      |-- feature/phase1-auth
      |-- feature/phase1-organization
```

### 5.2 Commit Convention
```
feat: Add salary section to employee form
fix: Correct address validation logic
refactor: Extract file upload service
docs: Update API documentation
```

---

## 6. Progress Tracking

### Current Status
- [x] Project analysis complete
- [x] Gap analysis complete
- [x] Development plan created
- [ ] Phase 0 started
- [ ] Phase 1 started
- [ ] Phase 2 started
- [ ] Phase 3 started
- [ ] Phase 4 started

### Decision Points (Pending User Input)
1. **Priority**: Phase 0 (features) or Phase 1 (auth) first?
2. **Organization Complexity**: Simple (company-dept-team) or complex (multi-level)?
3. **E-contract Legal Requirements**: External service needed?

---

## 7. Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Auth system complexity | High | Medium | Use Flask-Login, proven patterns |
| PDF generation issues | Medium | Low | Test with sample data early |
| Excel large file handling | Medium | Medium | Streaming approach, chunked processing |
| Scope creep | High | High | Stick to phase boundaries |

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-29 | 0.1.0 | Initial workflow document | Claude |

