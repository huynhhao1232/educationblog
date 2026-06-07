import json
import os
import re
from urllib.request import Request, urlopen

from django.conf import settings

EFFECTIVE_DATE = '2025-07-01'
ADDRESS_KIT_BASE = f'https://production.cas.so/address-kit/{EFFECTIVE_DATE}'
ADDRESS_DATA_DIR = os.path.join(
    settings.BASE_DIR, 'homepage', 'static', 'data', 'address'
)
PROVINCES_FILE = os.path.join(ADDRESS_DATA_DIR, 'provinces.json')
COMMUNES_DIR = os.path.join(ADDRESS_DATA_DIR, 'communes')

PROVINCE_CODE_RE = re.compile(r'^\d{1,3}$')


def is_valid_province_code(code):
    return bool(code and PROVINCE_CODE_RE.match(str(code)))


def data_is_available():
    return os.path.isfile(PROVINCES_FILE)


def load_provinces():
    with open(PROVINCES_FILE, encoding='utf-8') as f:
        return json.load(f)


def load_communes(province_code):
    if not is_valid_province_code(province_code):
        raise ValueError('Mã tỉnh/thành phố không hợp lệ')
    path = os.path.join(COMMUNES_DIR, f'{province_code}.json')
    if not os.path.isfile(path):
        raise FileNotFoundError(f'Không có dữ liệu xã/phường cho mã {province_code}')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def fetch_from_cas(path):
    url = f'{ADDRESS_KIT_BASE}/{path.lstrip("/")}'
    req = Request(url, headers={'User-Agent': 'education-blog/1.0'})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def save_provinces(data):
    os.makedirs(ADDRESS_DATA_DIR, exist_ok=True)
    with open(PROVINCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_communes(province_code, data):
    os.makedirs(COMMUNES_DIR, exist_ok=True)
    path = os.path.join(COMMUNES_DIR, f'{province_code}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
