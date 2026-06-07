import re

PHONE_PATTERN = re.compile(r'^0\d{9}$')
CCCD_PATTERN = re.compile(r'^0\d{11}$')


def validate_vn_phone(value, field_name='Số điện thoại'):
    phone = (value or '').strip()
    if not PHONE_PATTERN.fullmatch(phone):
        return f'{field_name} phải gồm đúng 10 chữ số và bắt đầu bằng số 0'
    return None


def validate_vn_cccd(value):
    cccd = (value or '').strip()
    if not CCCD_PATTERN.fullmatch(cccd):
        return 'Số CCCD phải gồm đúng 12 chữ số và bắt đầu bằng số 0'
    return None
