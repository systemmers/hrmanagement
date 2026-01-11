/**
 * Attachment 도메인 진입점
 *
 * 첨부파일 관련 모듈을 통합 export합니다.
 */

// API 클라이언트 로드
import './services/attachment-api.js';

// 컴포넌트 로드
import './components/file-panel.js';

// 모듈 초기화 완료 로그
console.debug('[Attachment] 도메인 모듈 로드 완료');
