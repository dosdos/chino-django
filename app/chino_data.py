import dateutil.parser
import string
import random

from django.utils import timezone
from datetime import date, datetime

#timezone.now()

# TODO: Dates prior 1900 will be soon supported..
DATE_NULL = date(1900, 01, 01)
DATETIME_NULL = datetime(1900, 01, 01, 1, 1, 1)

CHINO_DEBUG = False
CHINO_DEBUG_USER_ID = 3
CHINO_DEBUG_USER_TYPE = 0  # 0: patient, 1: therapist

def get_random_chino_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))

def field_to_json(t, v):
    if v is not None and v is not "null" and t in ('datetime', 'date', 'time'):
        return v.isoformat()
    return v

def field_from_json(t, v):
    if v is not None and t in ('datetime', 'date', 'time'):
        parsed = dateutil.parser.parse(v)
        if t == 'datetime':
            return parsed
        if t == 'date':
            return parsed.date()
        if t == 'time':
            return parsed.time()

    return v


USER_FIELDS = (
    # Field name, field type, field is indexed, field default value (lambda function)

    ('date_joined', 'datetime', False, lambda: datetime.now()),

    ('first_name', 'string', False, lambda: ""),
    ('last_name', 'string', False, lambda: ""),
    ('email', 'string', True, lambda: ""),
    ('sex', 'integer', False, lambda: 0),
    ('birth_date', 'date', False, lambda: DATE_NULL),
    ('fiscal_code', 'string', False, lambda: ""),

    ('scholarity', 'integer', False, lambda: 0),

    ('address_type_1', 'integer', False, lambda: 0),
    ('address_1', 'string', False, lambda: ""),
    ('address_type_2', 'integer', False, lambda: 1),
    ('address_2', 'string', False, lambda: ""),

    ('phone_type_1', 'integer', False, lambda: 0),
    ('phone_1', 'string', False, lambda: ""),
    ('phone_type_2', 'integer', False, lambda: 1),
    ('phone_2', 'string', False, lambda: ""),

    ('language', 'string', False, lambda: "it"),
)

RELATED_FIELDS = (

    ('first_name', 'string', False, lambda: ""),
    ('last_name', 'string', False, lambda: ""),
    ('email', 'string', False, lambda: ""),
    ('notes', 'string', False, lambda: ""),

    ('address_type_1', 'integer', False, lambda: 0),
    ('address_1', 'string', False, lambda: ""),
    ('address_type_2', 'integer', False, lambda: 1),
    ('address_2', 'string', False, lambda: ""),

    ('phone_type_1', 'integer', False, lambda: 0),
    ('phone_1', 'string', False, lambda: ""),
    ('phone_type_2', 'integer', False, lambda: 1),
    ('phone_2', 'string', False, lambda: ""),

    )
