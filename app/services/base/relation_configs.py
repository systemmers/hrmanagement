"""
RelationDataConfigs

관계형 데이터 업데이트 설정을 정의합니다.
Phase 4.2: SOLID 원칙 적용 - 설정과 로직 분리

각 관계 타입별 설정을 정의하여 코드 중복을 제거합니다.
"""
from typing import Dict, Any
from dataclasses import dataclass, field
from .relation_updater import RelationDataConfig


def get_relation_config(relation_type: str, repositories: Dict[str, Any]) -> RelationDataConfig:
    """
    관계 타입에 대한 설정 반환

    Args:
        relation_type: 관계 타입 ('education', 'career', 'certificate' 등)
        repositories: Repository 인스턴스 딕셔너리

    Returns:
        RelationDataConfig 인스턴스
    """
    from app.models import (
        Education, Career, Certificate, Language,
        FamilyMember, Award, ProjectParticipation
    )

    configs = {
        'education': RelationDataConfig(
            model_class=Education,
            repository=repositories.get('education'),
            form_prefix='education_',
            required_field='school_name',
            field_mapping={
                'school_type': 'school_type',
                'school_name': 'school_name',
                'graduation_year': 'graduation_date',
                'major': 'major',
                'degree': 'degree',
                'graduation_status': 'graduation_status',
            }
        ),

        'career': RelationDataConfig(
            model_class=Career,
            repository=repositories.get('career'),
            form_prefix='career_',
            required_field='company_name',
            field_mapping={
                'company_name': 'company_name',
                'start_date': 'start_date',
                'end_date': 'end_date',
                'department': 'department',
                'position': 'position',
                'duties': 'job_description',
            }
        ),

        'certificate': RelationDataConfig(
            model_class=Certificate,
            repository=repositories.get('certificate'),
            form_prefix='certificate_',
            required_field='name',
            field_mapping={
                'name': 'certificate_name',
                'grade': 'grade',
                'issuer': 'issuing_organization',
                'number': 'certificate_number',
                'date': 'acquisition_date',
            }
        ),

        'language': RelationDataConfig(
            model_class=Language,
            repository=repositories.get('language'),
            form_prefix='language_',
            required_field='name',
            field_mapping={
                'name': 'language',
                'level': 'level',
                'test_name': 'test_name',
                'score': 'score',
                'test_date': 'test_date',
            }
        ),

        'family': RelationDataConfig(
            model_class=FamilyMember,
            repository=repositories.get('family'),
            form_prefix='family_',
            required_field='name',
            field_mapping={
                'relation': 'relation',
                'name': 'name',
                'birth_date': 'birth_date',
                'occupation': 'occupation',
                'phone': 'contact',
                'cohabiting': 'is_cohabitant',
            },
            converters={'is_cohabitant': bool}
        ),

        'award': RelationDataConfig(
            model_class=Award,
            repository=repositories.get('award'),
            form_prefix='award_',
            required_field='name',
            field_mapping={
                'date': 'award_date',
                'name': 'award_name',
                'issuer': 'issuer',
                'note': 'note',
            }
        ),

        'project_participation': RelationDataConfig(
            model_class=ProjectParticipation,
            repository=repositories.get('project_participation'),
            form_prefix='project_',
            required_field='name',
            field_mapping={
                'name': 'project_name',
                'start_date': 'start_date',
                'end_date': 'end_date',
                'duties': 'role',
                'role': 'role',
                'client': 'client',
            }
        ),
    }

    if relation_type not in configs:
        raise ValueError(f"Unknown relation type: {relation_type}")

    return configs[relation_type]


# 지원되는 관계 타입 목록
SUPPORTED_RELATION_TYPES = [
    'education',
    'career',
    'certificate',
    'language',
    'family',
    'award',
    'project_participation',
]
