from .phone_model import get_or_create_phone_model
from .manufacturer import get_or_create_manufacturer
from .model import get_or_create_model
from .generic_operations import get_or_create

__all__ = [
    'get_or_create_phone_model',
    'get_or_create_manufacturer',
    'get_or_create_model',
    'get_or_create'
]
