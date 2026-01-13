"""
Relation Data Update Functions (Personal Blueprint)

Uses ProfileRelationService for transaction safety.

Phase 1 Migration: domains/user/blueprints/personal/relation_updaters.py
- DRY: atomic_transaction() for transaction pattern
- SSOT: transaction.py's atomic_transaction() as single source
- Consistent with employees/relation_updaters.py pattern
"""
from app.types import FormData, OwnerType
from app.shared.utils.transaction import atomic_transaction
from app.domains.employee.services import profile_relation_service
from .form_extractors import (
    extract_education_list,
    extract_career_list,
    extract_certificate_list,
    extract_language_list,
    extract_military_data,
)


class ProfileRelationUpdater:
    """Profile relation data update class

    Uses atomic_transaction() for transaction safety
    Follows DRY principle
    """

    def __init__(self, owner_type: OwnerType = 'profile') -> None:
        """
        Args:
            owner_type: 'profile' (personal account) or 'employee' (corporate employee)
        """
        self.owner_type: OwnerType = owner_type
        self.service = profile_relation_service

    def update_educations(self, owner_id: int, form_data: FormData) -> bool:
        """Batch update education info (transaction safe)"""
        with atomic_transaction():
            items = extract_education_list(form_data)
            self.service.delete_all_educations(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('school_name'):
                    self.service.add_education(owner_id, item, self.owner_type, commit=False)
        return True

    def update_careers(self, owner_id: int, form_data: FormData) -> bool:
        """Batch update career info (transaction safe)"""
        with atomic_transaction():
            items = extract_career_list(form_data)
            self.service.delete_all_careers(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('company_name'):
                    self.service.add_career(owner_id, item, self.owner_type, commit=False)
        return True

    def update_certificates(self, owner_id: int, form_data: FormData) -> bool:
        """Batch update certificate info (transaction safe)"""
        with atomic_transaction():
            items = extract_certificate_list(form_data)
            self.service.delete_all_certificates(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('certificate_name'):  # Model field name
                    self.service.add_certificate(owner_id, item, self.owner_type, commit=False)
        return True

    def update_languages(self, owner_id: int, form_data: FormData) -> bool:
        """Batch update language proficiency info (transaction safe)"""
        with atomic_transaction():
            items = extract_language_list(form_data)
            self.service.delete_all_languages(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('language_name'):  # Model field name
                    self.service.add_language(owner_id, item, self.owner_type, commit=False)
        return True

    def update_military(self, owner_id: int, form_data: FormData) -> bool:
        """Update military service info (1:1 relation, transaction safe)"""
        with atomic_transaction():
            data = extract_military_data(form_data)
            if data:
                self.service.update_or_create_military(owner_id, data, self.owner_type, commit=False)
        return True

    def update_all_relations(self, owner_id: int, form_data) -> bool:
        """Batch update all relation data (single transaction)

        Transaction safety: Rollback all if any fails
        """
        with atomic_transaction():
            # Education
            items = extract_education_list(form_data)
            self.service.delete_all_educations(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('school_name'):
                    self.service.add_education(owner_id, item, self.owner_type, commit=False)

            # Career
            items = extract_career_list(form_data)
            self.service.delete_all_careers(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('company_name'):
                    self.service.add_career(owner_id, item, self.owner_type, commit=False)

            # Certificates
            items = extract_certificate_list(form_data)
            self.service.delete_all_certificates(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('certificate_name'):  # Model field name
                    self.service.add_certificate(owner_id, item, self.owner_type, commit=False)

            # Languages
            items = extract_language_list(form_data)
            self.service.delete_all_languages(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('language_name'):  # Model field name
                    self.service.add_language(owner_id, item, self.owner_type, commit=False)

            # Military
            military_data = extract_military_data(form_data)
            if military_data:
                self.service.update_or_create_military(owner_id, military_data, self.owner_type, commit=False)

        return True


# Singleton instance (for personal accounts)
profile_relation_updater = ProfileRelationUpdater(owner_type='profile')


# ========================================
# Wrapper functions (existing API compatibility)
# ========================================

def update_profile_relations(profile_id: int, form_data) -> bool:
    """Batch update profile relation data (transaction safe)

    Args:
        profile_id: Profile ID
        form_data: request.form data

    Returns:
        bool: Success status

    Raises:
        Exception: On update failure
    """
    return profile_relation_updater.update_all_relations(profile_id, form_data)
