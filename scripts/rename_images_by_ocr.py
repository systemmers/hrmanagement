"""
이미지 OCR 텍스트 기반 파일명 변경 스크립트

businesscard50과 pic50 폴더의 이미지에서 OCR로 텍스트를 추출하여
파일명을 변경합니다.

실행 방법:
    python scripts/rename_images_by_ocr.py
    python scripts/rename_images_by_ocr.py --dry-run    # 미리보기만
"""
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.shared.services.ai.vision_ocr import VisionOCR


def sanitize_filename(text: str) -> str:
    """파일명으로 사용 가능하도록 텍스트 정리
    
    Args:
        text: 원본 텍스트
        
    Returns:
        정리된 파일명 (확장자 제외)
    """
    if not text:
        return ""
    
    # 공백을 언더스코어로 변환
    text = text.replace(' ', '_')
    
    # Windows 파일명 제한 문자 제거: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    text = re.sub(invalid_chars, '', text)
    
    # 연속된 언더스코어를 하나로 정리
    text = re.sub(r'_+', '_', text)
    
    # 앞뒤 언더스코어 제거
    text = text.strip('_')
    
    # 빈 문자열이면 기본값 반환
    if not text:
        return "unnamed"
    
    return text


def get_unique_filename(base_name: str, extension: str, existing_files: List[str]) -> str:
    """중복되지 않는 고유한 파일명 생성
    
    Args:
        base_name: 기본 파일명 (확장자 제외)
        extension: 확장자 (예: '.png')
        existing_files: 이미 존재하는 파일명 리스트
        
    Returns:
        고유한 파일명
    """
    filename = f"{base_name}{extension}"
    
    # 중복이 없으면 그대로 반환
    if filename not in existing_files:
        return filename
    
    # 중복이 있으면 번호 추가
    counter = 1
    while True:
        filename = f"{base_name}_{counter}{extension}"
        if filename not in existing_files:
            return filename
        counter += 1


def process_folder(folder_path: Path, ocr: VisionOCR, dry_run: bool = False) -> Dict[str, str]:
    """폴더 내 모든 이미지 파일 처리
    
    Args:
        folder_path: 처리할 폴더 경로
        ocr: VisionOCR 인스턴스
        dry_run: True면 실제 변경하지 않고 미리보기만
        
    Returns:
        변경 전/후 파일명 매핑 딕셔너리
    """
    if not folder_path.exists():
        print(f"오류: 폴더를 찾을 수 없습니다: {folder_path}")
        return {}
    
    # 이미지 파일만 필터링
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    image_files = [
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"경고: {folder_path}에 이미지 파일이 없습니다.")
        return {}
    
    print(f"\n{'='*60}")
    print(f"폴더 처리 시작: {folder_path.name}")
    print(f"총 {len(image_files)}개 파일")
    print(f"{'='*60}")
    
    # 파일명 변경 매핑 저장
    rename_map: Dict[str, str] = {}
    
    # 기존 파일명 목록 (중복 체크용)
    existing_filenames = [f.name for f in image_files]
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for idx, image_file in enumerate(sorted(image_files), 1):
        print(f"\n[{idx}/{len(image_files)}] 처리 중: {image_file.name}")
        
        # OCR로 텍스트 추출
        ocr_result = ocr.extract_text(str(image_file))
        
        if not ocr_result.success:
            print(f"  OCR 실패: {ocr_result.error}")
            error_count += 1
            continue
        
        extracted_text = ocr_result.text.strip()
        
        if not extracted_text:
            print(f"  텍스트 추출 실패: 이미지에서 텍스트를 찾을 수 없습니다.")
            skip_count += 1
            continue
        
        print(f"  추출된 텍스트: '{extracted_text}' (신뢰도: {ocr_result.confidence:.2f})")
        
        # 파일명 정리
        sanitized_name = sanitize_filename(extracted_text)
        extension = image_file.suffix
        
        # 고유한 파일명 생성
        new_filename = get_unique_filename(sanitized_name, extension, existing_filenames)
        
        # 이미 같은 이름이면 스킵
        if new_filename == image_file.name:
            print(f"  파일명 변경 불필요: 이미 '{new_filename}'입니다.")
            skip_count += 1
            continue
        
        print(f"  새 파일명: '{new_filename}'")
        
        rename_map[image_file.name] = new_filename
        
        if not dry_run:
            # 파일명 변경
            try:
                new_path = image_file.parent / new_filename
                image_file.rename(new_path)
                print(f"  변경 완료: {image_file.name} -> {new_filename}")
                # 기존 파일명 목록 업데이트
                existing_filenames.remove(image_file.name)
                existing_filenames.append(new_filename)
                success_count += 1
            except Exception as e:
                print(f"  파일명 변경 실패: {str(e)}")
                error_count += 1
        else:
            print(f"  [DRY-RUN] 변경 예정: {image_file.name} -> {new_filename}")
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"처리 완료: {folder_path.name}")
    print(f"  성공: {success_count}개")
    print(f"  스킵: {skip_count}개")
    print(f"  오류: {error_count}개")
    print(f"{'='*60}")
    
    return rename_map


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='이미지 OCR 텍스트 기반 파일명 변경')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 변경하지 않고 미리보기만 실행'
    )
    args = parser.parse_args()
    
    # 프로젝트 루트 경로
    project_root = Path(__file__).parent.parent
    base_folder = project_root / '.dev_docs' / 'img'
    sample_folder = project_root / '.dev_docs' / 'sample' / 'img'
    
    # 처리할 폴더들
    folders = [
        base_folder / 'businesscard50',
        base_folder / 'pic50',
        sample_folder / 'logo'
    ]
    
    # Vision OCR 초기화
    print("Vision OCR 초기화 중...")
    ocr = VisionOCR()
    
    if not ocr.is_available:
        print("오류: Vision OCR을 사용할 수 없습니다.")
        print("GCP 인증 설정을 확인해주세요.")
        sys.exit(1)
    
    print("Vision OCR 준비 완료\n")
    
    if args.dry_run:
        print("=" * 60)
        print("DRY-RUN 모드: 실제 파일명은 변경되지 않습니다.")
        print("=" * 60)
    
    # 각 폴더 처리
    all_rename_maps = {}
    
    for folder in folders:
        rename_map = process_folder(folder, ocr, dry_run=args.dry_run)
        if rename_map:
            all_rename_maps[folder.name] = rename_map
    
    # 전체 요약
    print(f"\n{'='*60}")
    print("전체 처리 요약")
    print(f"{'='*60}")
    
    total_changes = sum(len(m) for m in all_rename_maps.values())
    print(f"총 변경된 파일: {total_changes}개")
    
    for folder_name, rename_map in all_rename_maps.items():
        print(f"\n{folder_name}:")
        for old_name, new_name in rename_map.items():
            print(f"  {old_name} -> {new_name}")
    
    if args.dry_run:
        print("\n실제 변경을 실행하려면 --dry-run 옵션을 제거하세요.")


if __name__ == '__main__':
    main()

