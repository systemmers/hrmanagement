# 첨부파일 관리 체계 설계

## 요구사항 분석

| 항목 | 요구사항 | 현재 상태 |
|------|---------|----------|
| 필수 서류 지정 | 회사별 프리셋으로 필수 서류 지정 | X 미구현 |
| 중요도 정렬 | 중요 순서대로 나열 | X 미구현 |
| 현황 확인 | 첨부서류 현황 및 사이드바 확인 | 부분 구현 |
| 저장 규칙 | 체계적인 저장 경로 규칙 | FileStorageService 정의만 |
| 법인 자료 분류 | 근태기록 등 분류별 저장 | X 미구현 |
| 증명사진 복수 | 5개 업로드 후 선택 | X 미구현 (1개만) |

---

## 1. 데이터 모델 설계

### 1.1 DocumentCategory (서류 카테고리 마스터)

```sql
CREATE TABLE document_categories (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),  -- NULL이면 시스템 기본값
    code VARCHAR(50) NOT NULL,           -- 'contract', 'id_photo', 'certificate' 등
    name VARCHAR(100) NOT NULL,          -- '근로계약서', '증명사진', '자격증' 등
    description TEXT,
    is_required BOOLEAN DEFAULT FALSE,   -- 필수 서류 여부
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,        -- 중요도/정렬 순서
    max_files INTEGER DEFAULT 1,         -- 최대 업로드 수 (증명사진=5)
    allowed_extensions VARCHAR(200),     -- 'jpg,png,pdf' 허용 확장자
    max_file_size INTEGER DEFAULT 10485760,  -- 최대 파일 크기 (bytes)
    retention_days INTEGER,              -- 보관 기간 (일)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_doc_cat_company ON document_categories(company_id);
CREATE INDEX idx_doc_cat_code ON document_categories(code);
CREATE UNIQUE INDEX idx_doc_cat_unique ON document_categories(company_id, code);
```

### 1.2 시스템 기본 카테고리 (프리셋)

| code | name | is_required | sort_order | max_files | 설명 |
|------|------|-------------|------------|-----------|------|
| `id_photo` | 증명사진 | true | 1 | 5 | 제출용 선택 |
| `contract` | 근로계약서 | true | 2 | 1 | 필수 |
| `resume` | 이력서 | true | 3 | 1 | 필수 |
| `diploma` | 졸업증명서 | false | 10 | 5 | 학력별 |
| `certificate` | 자격증 | false | 11 | 10 | 다수 가능 |
| `id_card` | 신분증 사본 | false | 12 | 1 | |
| `bank_account` | 통장 사본 | false | 13 | 1 | |
| `health_check` | 건강검진결과 | false | 14 | 1 | |
| `nda` | 비밀유지서약서 | false | 20 | 1 | |
| `other` | 기타 | false | 99 | 10 | |

### 1.3 Attachment 모델 확장

```sql
-- 기존 attachments 테이블 확장
ALTER TABLE attachments ADD COLUMN category_id INTEGER REFERENCES document_categories(id);
ALTER TABLE attachments ADD COLUMN is_primary BOOLEAN DEFAULT FALSE;  -- 대표 파일 (증명사진 선택용)
ALTER TABLE attachments ADD COLUMN sort_order INTEGER DEFAULT 0;
ALTER TABLE attachments ADD COLUMN expires_at DATE;  -- 만료일 (자격증 등)
ALTER TABLE attachments ADD COLUMN verified_at TIMESTAMP;  -- 확인일
ALTER TABLE attachments ADD COLUMN verified_by INTEGER REFERENCES users(id);  -- 확인자

-- 인덱스
CREATE INDEX idx_attach_category ON attachments(category_id);
CREATE INDEX idx_attach_primary ON attachments(employee_id, category_id, is_primary);
```

### 1.4 CompanyDocumentPreset (회사별 필수서류 설정)

```sql
CREATE TABLE company_document_presets (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    category_id INTEGER NOT NULL REFERENCES document_categories(id),
    is_required BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    max_files INTEGER,  -- NULL이면 카테고리 기본값 사용
    note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_company_preset ON company_document_presets(company_id, category_id);
```

---

## 2. 저장 경로 규칙

### 2.1 디렉토리 구조

```
app/static/uploads/
├── corporate/{company_id}/
│   ├── employees/{employee_id}/
│   │   ├── id_photo/           # 증명사진 (복수)
│   │   │   ├── 1_photo_20241216_001.jpg
│   │   │   ├── 1_photo_20241216_002.jpg  (is_primary=true)
│   │   │   └── ...
│   │   ├── contract/           # 근로계약서
│   │   ├── resume/             # 이력서
│   │   ├── diploma/            # 졸업증명서
│   │   ├── certificate/        # 자격증
│   │   └── other/              # 기타
│   │
│   └── company_files/          # 회사 전체 자료
│       ├── attendance/         # 근태기록
│       │   └── 2024/
│       │       ├── 01_attendance.xlsx
│       │       └── 02_attendance.xlsx
│       ├── payroll/            # 급여자료
│       └── reports/            # 보고서
│
├── personal/{user_id}/
│   ├── id_photo/
│   ├── resume/
│   ├── certificate/
│   └── other/
│
└── temp/
```

### 2.2 파일명 규칙

```
{entity_id}_{category}_{timestamp}_{sequence}.{ext}

예시:
- 증명사진: 1_photo_20241216_001.jpg, 1_photo_20241216_002.jpg
- 계약서: 1_contract_20241216_001.pdf
- 자격증: 1_cert_20241216_001.pdf, 1_cert_20241216_002.pdf
```

---

## 3. API 설계

### 3.1 카테고리 관리

```
GET  /api/document-categories                    # 시스템 기본 카테고리 목록
GET  /api/companies/{id}/document-categories     # 회사별 카테고리 (프리셋 포함)
POST /api/companies/{id}/document-categories     # 회사 커스텀 카테고리 추가
PUT  /api/companies/{id}/document-presets        # 회사별 필수서류 설정
```

### 3.2 첨부파일 관리

```
GET  /api/employees/{id}/attachments                      # 전체 목록
GET  /api/employees/{id}/attachments/status               # 필수서류 제출 현황
GET  /api/employees/{id}/attachments/{category}           # 카테고리별 목록
POST /api/employees/{id}/attachments/{category}           # 업로드
PUT  /api/employees/{id}/attachments/{id}/primary         # 대표 지정 (증명사진)
DELETE /api/attachments/{id}                              # 삭제
```

### 3.3 회사 자료 관리

```
GET  /api/companies/{id}/files                    # 회사 자료 목록
GET  /api/companies/{id}/files/{category}         # 카테고리별 (attendance, payroll)
POST /api/companies/{id}/files/{category}         # 업로드
```

---

## 4. 증명사진 관리 (5개 업로드 + 선택)

### 4.1 흐름

```
1. 직원이 증명사진 최대 5개 업로드
   POST /api/employees/{id}/attachments/id_photo
   (max_files: 5 제한)

2. 업로드된 사진 목록 조회
   GET /api/employees/{id}/attachments/id_photo
   -> [{ id: 1, is_primary: false }, { id: 2, is_primary: true }, ...]

3. 제출용 사진 선택 (대표 지정)
   PUT /api/employees/{id}/attachments/2/primary
   -> is_primary = true (기존 primary 해제)

4. 증명서 발급 시 대표 사진 사용
   -> WHERE category='id_photo' AND is_primary=true
```

### 4.2 UI 컴포넌트

```html
<!-- 증명사진 업로드 영역 -->
<div class="id-photo-gallery">
    <div class="photo-grid">
        <!-- 업로드된 사진들 (최대 5개) -->
        <div class="photo-item" data-id="1">
            <img src="/uploads/.../photo1.jpg">
            <button class="btn-primary" onclick="setPrimary(1)">대표 지정</button>
            <span class="badge-primary" style="display:none">대표</span>
        </div>
        <!-- ... -->
    </div>
    <div class="upload-slot" v-if="photos.length < 5">
        <input type="file" accept="image/*" @change="uploadPhoto">
        <span>+ 사진 추가 ({photos.length}/5)</span>
    </div>
</div>
```

---

## 5. 첨부서류 현황 표시

### 5.1 사이드바 표시

```html
<!-- 사이드바 첨부서류 섹션 -->
<div class="sidebar-section attachments">
    <h4>첨부서류 현황</h4>
    <ul class="document-checklist">
        <li class="required completed">
            <i class="icon-check"></i> 증명사진 (2/5)
        </li>
        <li class="required completed">
            <i class="icon-check"></i> 근로계약서
        </li>
        <li class="required missing">
            <i class="icon-warning"></i> 이력서 (미제출)
        </li>
        <li class="optional completed">
            <i class="icon-check"></i> 자격증 (3)
        </li>
    </ul>
    <div class="summary">
        필수: 2/3 완료 | 선택: 1/5 완료
    </div>
</div>
```

### 5.2 현황 API 응답

```json
{
  "required": {
    "total": 3,
    "completed": 2,
    "items": [
      { "category": "id_photo", "name": "증명사진", "count": 2, "max": 5, "status": "completed" },
      { "category": "contract", "name": "근로계약서", "count": 1, "max": 1, "status": "completed" },
      { "category": "resume", "name": "이력서", "count": 0, "max": 1, "status": "missing" }
    ]
  },
  "optional": {
    "total": 5,
    "completed": 1,
    "items": [
      { "category": "certificate", "name": "자격증", "count": 3, "max": 10, "status": "completed" },
      { "category": "diploma", "name": "졸업증명서", "count": 0, "max": 5, "status": "pending" }
    ]
  }
}
```

---

## 6. 법인 자료 분류 저장

### 6.1 CompanyFile 모델 (신규)

```sql
CREATE TABLE company_files (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    category VARCHAR(50) NOT NULL,       -- 'attendance', 'payroll', 'report'
    file_name VARCHAR(500),
    file_path VARCHAR(1000),
    file_type VARCHAR(50),
    file_size INTEGER,
    year INTEGER,                        -- 연도
    month INTEGER,                       -- 월 (선택)
    description TEXT,
    uploaded_by INTEGER REFERENCES users(id),
    upload_date TIMESTAMP DEFAULT NOW(),
    note TEXT
);

CREATE INDEX idx_company_file ON company_files(company_id, category, year, month);
```

### 6.2 법인 자료 카테고리

| category | name | 설명 | 파일명 패턴 |
|----------|------|------|------------|
| `attendance` | 근태기록 | 월별 근태 엑셀 | `{year}{month}_attendance.xlsx` |
| `payroll` | 급여대장 | 월별 급여 | `{year}{month}_payroll.xlsx` |
| `tax` | 세무자료 | 원천징수 등 | `{year}{month}_tax.pdf` |
| `insurance` | 4대보험 | 신고내역 | `{year}{month}_insurance.pdf` |
| `report` | 보고서 | 기타 보고서 | 자유형식 |

---

## 7. 구현 우선순위

### Phase 1: 기본 구조 (필수)
1. DocumentCategory 모델 생성
2. 시스템 기본 카테고리 시드 데이터
3. Attachment 모델 확장 (category_id, is_primary)
4. 기존 데이터 마이그레이션 (category → category_id)

### Phase 2: 회사별 설정
1. CompanyDocumentPreset 모델
2. 회사별 필수서류 설정 UI
3. 카테고리 관리 API

### Phase 3: 증명사진 다중 업로드
1. 다중 파일 업로드 API
2. 대표 사진 선택 기능
3. 갤러리 UI 컴포넌트

### Phase 4: 현황 표시
1. 첨부서류 현황 API
2. 사이드바 현황 컴포넌트
3. 필수서류 알림

### Phase 5: 법인 자료
1. CompanyFile 모델
2. 법인 자료 업로드/조회 API
3. 자료실 UI

---

## 8. 마이그레이션 계획

### 기존 Attachment.category 값 매핑

| 기존 category | 신규 category_id (code) |
|--------------|------------------------|
| `profile_photo` | `id_photo` |
| `business_card_front` | `id_photo` (또는 별도 카테고리) |
| `business_card_back` | `id_photo` |
| `계약서` | `contract` |
| `기타` | `other` |

---

## 문서 정보

- **생성일**: 2025-12-16
- **버전**: 1.0
- **관련 파일**:
  - `app/models/attachment.py`
  - `app/services/file_storage_service.py`
  - `app/blueprints/employees/files.py`
