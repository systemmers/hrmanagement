---
description: "웹사이트 디자인을 체계적으로 분석하여 JSON 형식으로 변환"
argument-hint: "URL 또는 파일경로 [--output-json] [--screenshot] [--detailed]"
allowed-tools: [mcp_sequential_thinking_sequentialthinking, mcp_playwright_playwright, mcp_filesystem_read_file, mcp_filesystem_write_file, mcp_filesystem_list_dir]
---


# 웹사이트 디자인 분석 명령어

요청사항: $ARGUMENTS

## 작업 계획 (Sequential Thinking)

### 1단계: 요구사항 분석
- 입력 타입 확인 (URL vs 파일경로)
- 플래그 파싱 (--output, --screenshot, --detailed)
- 분석 범위 결정

### 2단계: 웹사이트 접근
- URL인 경우: Playwright로 페이지 로드
- 파일인 경우: 로컬 파일 읽기
- 스크린샷 옵션 처리

### 3단계: 디자인 요소 추출
- 레이아웃 구조 분석
- 색상 팔레트 추출
- 타이포그래피 분석
- 컴포넌트 스타일 분석

### 4단계: JSON 구조화
- 디자인 시스템 JSON 생성
- 컴포넌트 라이브러리 JSON 생성
- 레이아웃 구조 JSON 생성

### 5단계: 결과 출력
- 지정된 형식으로 출력
- 파일 저장 (필요시)

## 지원 플래그

- `--output-json`: JSON 형식으로 출력 및 json 파일로 저장 (기본값)
- `--output-md`: 마크다운 형식으로 출력
- `--screenshot`: 페이지 스크린샷 캡처
- `--detailed`: 상세 분석 모드 (더 많은 정보 포함)
- `--layout` : 레이아웃 분석
- `--interface` : 인터페이스 분석
- `--style` : 스타일 분석
- `--structure` : 구조 분석
- `--tree` : 트리형태로 출력
- `--demo` : `styleguide`에 따른 html 샘플, 데모페이지 구현, 가능한 모든 요소를 가용하여 구현하며, 주제는 임의로 선정. 
- `--styleguide` : html, css, js의 코드로 일반화 및 중앙화된 html 기반의 스타일 가이드 작성 및 구현.
- `--seq` : sequential thinking mcp 를 활용해서 단계적사고 
- `--c7` : context7 mcp 활용
- `--think` : 충분한 사고로 답변
- `--loop` : 충분히 분석할 때까지 반복
- `--iterator#` : 반복횟수
- `--list-tree` : 리스트화하여 트리형식으로 출력
- `--architecture` : 아키텍쳐구조, 생성할 디렉토리, 파일, 코드의 리스트와 구조 출력

## Context7 적용

### 컨텍스트 1: 프로젝트 목적
- 자산관리시스템 디자인 분석
- 미니멀 디자인 시스템 v2 기준
- 일관성 있는 디자인 패턴 추출

### 컨텍스트 2: 타겟 사용자
- 디자이너: 디자인 시스템 구축
- 개발자: 컴포넌트 라이브러리 개발
- 기획자: UI/UX 가이드라인 수립

### 컨텍스트 3: 기술적 요구사항
- 반응형 디자인 분석
- 접근성 기준 준수 확인
- 성능 최적화 요소 파악

### 컨텍스트 4: 디자인 철학
- 미니멀리즘 원칙
- 일관성 있는 사용자 경험
- 확장 가능한 시스템 구조

### 컨텍스트 5: 구현 환경
- 웹 브라우저 호환성
- 모바일/데스크톱 대응
- 크로스 플랫폼 지원

### 컨텍스트 6: 품질 기준
- WCAG 2.1 AA 접근성
- 성능 최적화
- 유지보수성

### 컨텍스트 7: 확장성
- 새로운 컴포넌트 추가
- 테마 시스템 지원
- 다국어 대응

## ToDo List

### Phase 1: 초기 설정
- [ ] 입력 파라미터 파싱
- [ ] 플래그 옵션 확인
- [ ] 작업 환경 준비

### Phase 2: 웹사이트 접근
- [ ] URL/파일 경로 확인
- [ ] Playwright 브라우저 실행 (URL인 경우)
- [ ] 페이지 로드 및 대기
- [ ] 스크린샷 캡처 (옵션)

### Phase 3: 레이아웃 분석
- [ ] 전체 페이지 구조 파악
- [ ] CSS Grid/Flexbox 시스템 분석
- [ ] 반응형 브레이크포인트 확인
- [ ] 컴포넌트 계층 구조 매핑

### Phase 4: 시각적 요소 분석
- [ ] 색상 팔레트 추출
- [ ] 타이포그래피 시스템 분석
- [ ] 간격 및 여백 시스템 파악
- [ ] 그림자 및 효과 분석

### Phase 5: 컴포넌트 분석
- [ ] 버튼 스타일 분석
- [ ] 입력 필드 스타일 분석
- [ ] 카드 컴포넌트 분석
- [ ] 네비게이션 분석
- [ ] 테이블 스타일 분석

### Phase 6: 인터랙션 분석
- [ ] 호버 효과 분석
- [ ] 포커스 상태 분석
- [ ] 애니메이션/트랜지션 분석
- [ ] 상태 표시 분석

### Phase 7: JSON 생성
- [ ] 디자인 시스템 JSON 구조화
- [ ] 컴포넌트 라이브러리 JSON 생성
- [ ] 레이아웃 구조 JSON 생성
- [ ] 메타데이터 추가

### Phase 8: 결과 출력
- [ ] 지정된 형식으로 출력
- [ ] 파일 저장 (필요시)
- [ ] 분석 리포트 생성

## Checklist

### 입력 검증
- [ ] URL 또는 파일 경로 유효성 확인
- [ ] 플래그 옵션 파싱 완료
- [ ] 작업 환경 준비 완료

### 웹사이트 접근
- [ ] 페이지 로드 성공
- [ ] JavaScript 실행 완료 대기
- [ ] 스크린샷 캡처 완료 (옵션)
- [ ] 페이지 구조 파악 완료

### 레이아웃 분석
- [ ] 전체 구조 매핑 완료
- [ ] 그리드 시스템 분석 완료
- [ ] 반응형 브레이크포인트 확인 완료
- [ ] 컴포넌트 계층 구조 완료

### 시각적 요소
- [ ] 색상 팔레트 추출 완료
- [ ] 타이포그래피 분석 완료
- [ ] 간격 시스템 분석 완료
- [ ] 그림자/효과 분석 완료

### 컴포넌트 분석
- [ ] 버튼 스타일 분석 완료
- [ ] 입력 필드 분석 완료
- [ ] 카드 컴포넌트 분석 완료
- [ ] 네비게이션 분석 완료
- [ ] 테이블 스타일 분석 완료

### 인터랙션 분석
- [ ] 호버 효과 분석 완료
- [ ] 포커스 상태 분석 완료
- [ ] 애니메이션 분석 완료
- [ ] 상태 표시 분석 완료

### JSON 생성
- [ ] 디자인 시스템 JSON 완성
- [ ] 컴포넌트 라이브러리 JSON 완성
- [ ] 레이아웃 구조 JSON 완성
- [ ] 메타데이터 추가 완료

### 결과 출력
- [ ] 지정 형식으로 출력 완료
- [ ] 파일 저장 완료 (필요시)
- [ ] 분석 리포트 생성 완료

## Playwright 활용

### 브라우저 설정
```javascript
const browser = await playwright.chromium.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});
```

### 페이지 로드
```javascript
const page = await browser.newPage();
await page.goto(url, { waitUntil: 'networkidle' });
```

### 스크린샷 캡처
```javascript
if (screenshotFlag) {
  await page.screenshot({ 
    path: 'design-analysis-screenshot.png',
    fullPage: true 
  });
}
```

### CSS 분석
```javascript
const styles = await page.evaluate(() => {
  // CSS 변수 추출
  const cssVars = getComputedStyle(document.documentElement);
  // 컴포넌트 스타일 분석
  const components = document.querySelectorAll('[class*="btn"], [class*="card"], [class*="input"]');
  // 레이아웃 구조 분석
  const layout = analyzeLayout();
  
  return { cssVars, components, layout };
});
```

## JSON 출력 형식

### 디자인 시스템 JSON
```json
{
  "designSystem": {
    "colors": {
      "primary": "#색상코드",
      "secondary": "#색상코드",
      "background": "#색상코드",
      "text": "#색상코드",
      "border": "#색상코드",
      "grayScale": {
        "50": "#fafafa",
        "100": "#f5f5f5",
        "200": "#e5e7eb",
        "300": "#9ca3af",
        "400": "#6b7280",
        "500": "#4b5563",
        "600": "#374151",
        "700": "#1f2937"
      }
    },
    "typography": {
      "fontFamily": "Inter, system-ui, sans-serif",
      "sizes": {
        "xs": "12px",
        "sm": "14px",
        "base": "16px",
        "lg": "18px",
        "xl": "20px",
        "2xl": "24px",
        "3xl": "30px"
      },
      "weights": {
        "normal": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700
      },
      "lineHeights": {
        "tight": 1.25,
        "normal": 1.5,
        "relaxed": 1.625
      }
    },
    "spacing": {
      "1": "4px",
      "2": "8px",
      "3": "12px",
      "4": "16px",
      "5": "20px",
      "6": "24px",
      "8": "32px",
      "10": "40px",
      "12": "48px"
    },
    "shadows": {
      "sm": "0 1px 2px rgba(0,0,0,0.05)",
      "md": "0 4px 6px rgba(0,0,0,0.1)",
      "lg": "0 10px 15px rgba(0,0,0,0.1)"
    },
    "borderRadius": {
      "sm": "4px",
      "md": "8px",
      "lg": "12px",
      "xl": "16px"
    }
  }
}
```

### 컴포넌트 라이브러리 JSON
```json
{
  "components": {
    "button": {
      "primary": {
        "background": "#1f2937",
        "color": "#ffffff",
        "padding": "12px 24px",
        "borderRadius": "8px",
        "fontWeight": 500,
        "hover": {
          "transform": "translateY(-2px)",
          "boxShadow": "0 4px 12px rgba(0,0,0,0.15)"
        }
      },
      "secondary": {
        "background": "#f5f5f5",
        "color": "#1f2937",
        "border": "1px solid #d1d5db",
        "padding": "12px 24px",
        "borderRadius": "8px"
      }
    },
    "card": {
      "background": "#ffffff",
      "borderRadius": "12px",
      "padding": "24px",
      "boxShadow": "0 2px 10px rgba(0,0,0,0.1)",
      "hover": {
        "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
        "transform": "translateY(-2px)"
      }
    },
    "input": {
      "padding": "12px 16px",
      "border": "1px solid #d1d5db",
      "borderRadius": "8px",
      "fontSize": "14px",
      "focus": {
        "borderColor": "#6b7280",
        "boxShadow": "0 0 0 3px rgba(107, 114, 128, 0.1)"
      }
    }
  }
}
```

### 레이아웃 구조 JSON
```json
{
  "layout": {
    "grid": {
      "columns": 12,
      "gap": "24px",
      "breakpoints": {
        "mobile": "768px",
        "tablet": "1024px",
        "desktop": "1200px"
      }
    },
    "sidebar": {
      "width": "280px",
      "position": "left",
      "background": "#ffffff",
      "border": "1px solid #e5e7eb"
    },
    "header": {
      "height": "64px",
      "background": "#ffffff",
      "borderBottom": "1px solid #e5e7eb"
    },
    "mainContent": {
      "padding": "32px",
      "maxWidth": "1200px",
      "margin": "0 auto"
    }
  }
}
```

## 사용법 예시

```bash
# URL 분석 (기본 JSON 출력)
analyze-design https://example.com

# 상세 분석 + 스크린샷
analyze-design https://example.com --detailed --screenshot

# 로컬 파일 분석
analyze-design ./index.html --output=json

# 마크다운 형식 출력
analyze-design https://example.com --output=markdown
```

## 설치 방법

1. `.claude/commands/` 디렉토리에 `analyze-design.md` 파일 생성
2. 위 내용을 복사하여 붙여넣기
3. Claude Code에서 `analyze-design` 명령어 사용 가능

이 명령어는 Sequential Thinking, Context7, ToDo List, Checklist, Playwright를 모두 활용하여 웹사이트 디자인을 체계적으로 분석하고 JSON 형식으로 변환합니다.
<｜tool▁call▁end｜><｜tool▁calls▁end｜>