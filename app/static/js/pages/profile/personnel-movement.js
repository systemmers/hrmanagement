/**
 * 인사이동 및 고과 섹션 데이터 로더
 *
 * 기능:
 * - loadPromotions: 승진 이력 로드
 * - loadEvaluations: 인사평가 로드
 * - loadTrainings: 교육 이력 로드
 * - initPersonnelMovement: 전체 초기화
 */

/**
 * 승진 이력 로드
 * @param {string} apiUrl - API 엔드포인트 URL
 */
export function loadPromotions(apiUrl) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('promotionContainer');
            if (!container) return;

            if (data.success && data.data && data.data.length > 0) {
                let html = '<table class="data-table"><thead><tr>';
                html += '<th>승진일</th><th>이전 직급</th><th>승진 직급</th><th>비고</th>';
                html += '</tr></thead><tbody>';

                data.data.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + (item.promotion_date || '-') + '</td>';
                    html += '<td>' + (item.previous_position || '-') + '</td>';
                    html += '<td>' + (item.new_position || '-') + '</td>';
                    html += '<td>' + (item.notes || '-') + '</td>';
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state empty-state--small"><p>승진 이력이 없습니다.</p></div>';
            }
        })
        .catch(() => {
            const container = document.getElementById('promotionContainer');
            if (container) {
                container.innerHTML = '<div class="error-state"><p>데이터 로드 실패</p></div>';
            }
        });
}

/**
 * 인사평가 로드
 * @param {string} apiUrl - API 엔드포인트 URL
 */
export function loadEvaluations(apiUrl) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('evaluationContainer');
            if (!container) return;

            if (data.success && data.data && data.data.length > 0) {
                let html = '<table class="data-table"><thead><tr>';
                html += '<th>평가기간</th><th>평가등급</th><th>점수</th><th>비고</th>';
                html += '</tr></thead><tbody>';

                data.data.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + (item.evaluation_period || '-') + '</td>';
                    html += '<td>' + (item.grade || '-') + '</td>';
                    html += '<td>' + (item.score || '-') + '</td>';
                    html += '<td>' + (item.notes || '-') + '</td>';
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state empty-state--small"><p>평가 이력이 없습니다.</p></div>';
            }
        })
        .catch(() => {
            const container = document.getElementById('evaluationContainer');
            if (container) {
                container.innerHTML = '<div class="error-state"><p>데이터 로드 실패</p></div>';
            }
        });
}

/**
 * 교육 이력 로드
 * @param {string} apiUrl - API 엔드포인트 URL
 */
export function loadTrainings(apiUrl) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('trainingContainer');
            if (!container) return;

            if (data.success && data.data && data.data.length > 0) {
                let html = '<table class="data-table"><thead><tr>';
                html += '<th>교육명</th><th>교육기간</th><th>교육기관</th><th>수료여부</th>';
                html += '</tr></thead><tbody>';

                data.data.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + (item.training_name || '-') + '</td>';
                    html += '<td>' + (item.start_date || '-') + ' ~ ' + (item.end_date || '-') + '</td>';
                    html += '<td>' + (item.institution || '-') + '</td>';
                    html += '<td>' + (item.completion_status || '-') + '</td>';
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state empty-state--small"><p>교육 이력이 없습니다.</p></div>';
            }
        })
        .catch(() => {
            const container = document.getElementById('trainingContainer');
            if (container) {
                container.innerHTML = '<div class="error-state"><p>데이터 로드 실패</p></div>';
            }
        });
}

/**
 * 인사이동 섹션 전체 초기화
 * @param {Object} urls - API URL 객체
 * @param {string} urls.promotions - 승진 이력 API URL
 * @param {string} urls.evaluations - 인사평가 API URL
 * @param {string} urls.trainings - 교육 이력 API URL
 */
export function initPersonnelMovement(urls) {
    if (urls.promotions) loadPromotions(urls.promotions);
    if (urls.evaluations) loadEvaluations(urls.evaluations);
    if (urls.trainings) loadTrainings(urls.trainings);
}

// 전역 노출 (레거시 호환)
if (typeof window !== 'undefined') {
    window.PersonnelMovement = {
        loadPromotions,
        loadEvaluations,
        loadTrainings,
        initPersonnelMovement
    };
}
