/**
 * ExcelExporter - 엑셀 내보내기 기능
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class ExcelExporter {
    /**
     * 데이터를 엑셀 파일로 내보내기
     * @param {Object} options - 내보내기 옵션
     * @param {Array} options.data - 내보낼 데이터
     * @param {Array} options.columns - 컬럼 설정
     * @param {string} options.filename - 파일명 (기본값: 'data_export')
     * @param {string} options.sheetName - 시트명 (기본값: '데이터')
     * @param {boolean} options.includeSum - 합계 행 포함 여부
     * @param {Function} options.onExport - 내보내기 완료 콜백
     * @returns {boolean} 성공 여부
     */
    export(options) {
        const {
            data,
            columns,
            filename = 'data_export',
            sheetName = '데이터',
            includeSum = true,
            onExport = null
        } = options;

        // SheetJS 라이브러리 확인
        if (typeof XLSX === 'undefined') {
            console.error('SheetJS (XLSX) 라이브러리가 로드되지 않았습니다.');
            alert('엑셀 내보내기 기능을 사용하려면 SheetJS 라이브러리가 필요합니다.');
            return false;
        }

        if (!data || data.length === 0) {
            alert('내보낼 데이터가 없습니다.');
            return false;
        }

        // 헤더 행 생성
        const headers = columns.map(col => col.label);

        // 데이터 행 생성
        const rows = data.map(row => {
            return columns.map(col => {
                const value = row[col.key];

                if (value === null || value === undefined) {
                    return '';
                }

                // 숫자 타입은 숫자로 유지
                if (col.type === 'number' || col.type === 'currency') {
                    return Number(value) || 0;
                }

                return String(value);
            });
        });

        // 합계 행 추가
        if (includeSum) {
            const sumColumns = columns.filter(c => c.sum);
            if (sumColumns.length > 0) {
                const sumRow = columns.map((col, idx) => {
                    if (col.sum) {
                        return data.reduce((acc, row) => {
                            return acc + (Number(row[col.key]) || 0);
                        }, 0);
                    }
                    return idx === 0 ? '합계' : '';
                });
                rows.push(sumRow);
            }
        }

        // 워크시트 데이터 구성
        const wsData = [headers, ...rows];

        // 워크시트 생성
        const ws = XLSX.utils.aoa_to_sheet(wsData);

        // 컬럼 너비 설정
        ws['!cols'] = columns.map(col => {
            const width = parseInt(col.width) || 100;
            return { wch: Math.max(10, Math.min(50, width / 8)) };
        });

        // 워크북 생성
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, sheetName);

        // 파일명 생성
        const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const fullFilename = `${filename}_${timestamp}.xlsx`;

        // 파일 다운로드
        XLSX.writeFile(wb, fullFilename);

        // 콜백 호출
        if (onExport) {
            onExport({
                filename: fullFilename,
                rowCount: data.length,
                columnCount: columns.length
            });
        }

        console.log(`엑셀 파일 내보내기 완료: ${fullFilename} (${data.length}행, ${columns.length}열)`);
        return true;
    }
}

export default ExcelExporter;
