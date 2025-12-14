/**
 * AI Test Compare Page JavaScript
 * AI Provider 비교 분석 페이지
 *
 * Used by:
 * - ai_test/compare.html
 */

// Global variable to store providers - set from template
window.aiTestProviders = window.aiTestProviders || [];

document.addEventListener('DOMContentLoaded', function() {
    initFileSelection();
    initCompareForm();
});

/**
 * Initialize file selection mutual exclusion
 */
function initFileSelection() {
    const fileInput = document.getElementById('fileInput');
    const sampleSelect = document.getElementById('sampleSelect');

    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0 && sampleSelect) {
                sampleSelect.value = '';
            }
        });
    }

    if (sampleSelect) {
        sampleSelect.addEventListener('change', function() {
            if (this.value && fileInput) {
                fileInput.value = '';
            }
        });
    }
}

/**
 * Initialize compare form submission
 */
function initCompareForm() {
    const form = document.getElementById('compareForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const btn = document.getElementById('compareBtn');
        const resultArea = document.getElementById('resultArea');

        const fileInput = document.getElementById('fileInput');
        const sampleSelect = document.getElementById('sampleSelect');
        const file = fileInput?.files[0];
        const sampleFile = sampleSelect?.value;

        if (!file && !sampleFile) {
            alert('파일을 선택해주세요');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 분석 중...';

        // Initialize provider cards
        const providers = window.aiTestProviders || [];
        resultArea.innerHTML = `
            <div class="compare-grid">
                ${providers.map(p => `
                    <div class="provider-card" id="card-${p}">
                        <div class="provider-header">
                            <span class="provider-name">${getProviderName(p)}</span>
                            <span class="provider-status status-pending">대기중</span>
                        </div>
                        <div class="provider-body">
                            <div class="loading-overlay">
                                <div class="spinner"></div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        try {
            const response = await fetch('/ai-test/compare/run', {
                method: 'POST',
                body: formData
            });

            const results = await response.json();

            // Display each provider result
            for (const [provider, result] of Object.entries(results)) {
                updateProviderCard(provider, result);
            }
        } catch (error) {
            resultArea.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i> 오류: ${error.message}
                </div>
            `;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-play"></i> 비교 분석 시작';
        }
    });
}

/**
 * Update provider card with result
 * @param {string} provider - Provider name
 * @param {Object} result - Analysis result
 */
function updateProviderCard(provider, result) {
    const card = document.getElementById(`card-${provider}`);
    if (!card) return;

    const header = card.querySelector('.provider-status');
    const body = card.querySelector('.provider-body');

    if (result.success) {
        const data = result.data;
        const confidence = data.confidence || 0;
        const confClass = confidence > 0.8 ? 'high' : confidence > 0.6 ? 'medium' : 'low';

        header.className = 'provider-status status-success';
        header.textContent = '성공';

        body.innerHTML = `
            <div class="provider-meta">
                <div class="meta-item">
                    <div class="label">신뢰도</div>
                    <div class="value">
                        <span class="confidence-badge confidence-${confClass}">
                            ${(confidence * 100).toFixed(0)}%
                        </span>
                    </div>
                </div>
                <div class="meta-item">
                    <div class="label">처리시간</div>
                    <div class="value">${data.processing_time?.toFixed(2) || '-'}초</div>
                </div>
            </div>
            <div class="meta-item mb-3">
                <div class="label">문서 유형</div>
                <div class="value text-sm">${data.document_type || '-'}</div>
            </div>
            <pre class="result-preview">${JSON.stringify(data.extracted_fields || data, null, 2)}</pre>
        `;
    } else {
        header.className = 'provider-status status-error';
        header.textContent = '실패';

        body.innerHTML = `
            <div class="error-message">
                ${result.error || '알 수 없는 오류'}
            </div>
        `;
    }
}

/**
 * Get provider display name
 * @param {string} provider - Provider key
 * @returns {string} Display name
 */
function getProviderName(provider) {
    const names = {
        'gemini': 'Gemini (AI Studio)',
        'vertex_ai': 'Vertex AI',
        'document_ai': 'Document AI'
    };
    return names[provider] || provider;
}

// Expose functions for non-module environments
window.updateProviderCard = updateProviderCard;
window.getProviderName = getProviderName;
