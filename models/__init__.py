"""Package containing SQLAlchemy models for the Real Property Tax Assessment System.

This package includes models for:
- Owner Details
- Approval Sections
"""

from .ownerDetails_model import OwnerDetailsModel
from .approvalSection_model import ApprovalSectionModel

__all__ = ['OwnerDetailsModel', 'ApprovalSectionModel']
