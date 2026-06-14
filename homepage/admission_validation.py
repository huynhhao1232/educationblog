import os
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .validators import validate_vn_cccd, validate_vn_phone

VALID_GENDERS = {'Nam', 'Nữ'}
VALID_CONDUCT = {'Tốt', 'Khá', 'Đạt', 'Chưa Đạt'}
VALID_ADMISSION_METHODS = {'transcript', 'exam'}
LEGACY_GRADUATION_YEARS = {'current', 'before'}
GRADUATION_YEAR_MIN = 1985
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_IMAGE_CONTENT_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/gif',
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def validate_admission_email(email):
    email = (email or '').strip()
    if not email:
        return 'Email là bắt buộc'
    try:
        validate_email(email)
    except ValidationError:
        return 'Email không hợp lệ'
    return None


def validate_admission_image(uploaded_file, field_label='Ảnh'):
    if not uploaded_file:
        return None
    if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
        return f'{field_label} không được vượt quá 5MB'
    content_type = (getattr(uploaded_file, 'content_type', '') or '').lower()
    ext = os.path.splitext(uploaded_file.name or '')[1].lower()
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES and ext not in ALLOWED_IMAGE_EXTENSIONS:
        return f'{field_label} phải là file ảnh (JPG, PNG, WEBP, GIF)'
    return None


def validate_admission_conduct(conduct_6, conduct_7, conduct_8, conduct_9):
    for label, value in [
        ('lớp 6', conduct_6),
        ('lớp 7', conduct_7),
        ('lớp 8', conduct_8),
        ('lớp 9', conduct_9),
    ]:
        if value not in VALID_CONDUCT:
            return f'KQRL {label} không hợp lệ'
    return None


def _parse_decimal(raw, min_val, max_val, max_label=None, required=True):
    if not raw or not str(raw).strip():
        if required:
            return None, 'Thiếu thông tin điểm'
        return None, None
    try:
        value = Decimal(str(raw).strip().replace(',', '.'))
    except (ValueError, InvalidOperation):
        return None, 'Điểm không hợp lệ'
    max_display = max_label if max_label is not None else max_val
    if value < Decimal(str(min_val)):
        return None, f'Điểm phải lớn hơn hoặc bằng {min_val}'
    if value > Decimal(str(max_val)):
        return None, f'Điểm phải nhỏ hơn hoặc bằng {max_display}'
    return value, None


def infer_admission_method_from_admission(admission):
    """Suy ra phương thức xét tuyển từ hồ sơ đã lưu."""
    if admission.exam_score is not None:
        return 'exam'
    grade_fields = (
        'avg_score', 'math_score_6', 'literature_score_6',
        'math_score_7', 'literature_score_7',
        'math_score_8', 'literature_score_8',
        'math_score_9', 'literature_score_9',
    )
    if any(getattr(admission, f) is not None for f in grade_fields):
        return 'transcript'
    if admission.graduation_year == 'before':
        return 'transcript'
    if admission.graduation_year == 'current':
        return 'exam'
    return 'exam'


def graduation_year_label(raw):
    if raw == 'current':
        return 'Tốt nghiệp năm nay (dữ liệu cũ)'
    if raw == 'before':
        return 'Tốt nghiệp những năm trước (dữ liệu cũ)'
    return str(raw)


def _resolve_admission_method(data, graduation_year=None):
    """Xác định phương thức xét tuyển từ form hoặc dữ liệu cũ."""
    method = (data.get('admission_method') or '').strip()
    if method in VALID_ADMISSION_METHODS:
        return method
    if graduation_year == 'current':
        return 'exam'
    if graduation_year == 'before':
        return 'transcript'
    if data.get('graduation_total_score') or data.get('exam_score'):
        return 'exam'
    if data.get('math_score_6') or data.get('avg_score'):
        return 'transcript'
    return ''


def validate_graduation_year(raw):
    raw = (raw or '').strip()
    if not raw:
        return None, 'Năm tốt nghiệp THCS không được để trống'
    if raw in LEGACY_GRADUATION_YEARS:
        return raw, None
    try:
        year = int(raw)
    except (ValueError, TypeError):
        return None, 'Năm tốt nghiệp THCS không hợp lệ'
    from django.utils import timezone
    current = timezone.now().year
    if year < GRADUATION_YEAR_MIN or year > current:
        return None, 'Năm tốt nghiệp THCS không hợp lệ'
    return str(year), None


def parse_graduation_scores(data, graduation_year=None):
    """Trả về dict điểm hoặc (None, error_message)."""
    result = {
        'exam_score': None,
        'avg_score': None,
        'math_score_6': None,
        'literature_score_6': None,
        'math_score_7': None,
        'literature_score_7': None,
        'math_score_8': None,
        'literature_score_8': None,
        'math_score_9': None,
        'literature_score_9': None,
    }

    admission_method = _resolve_admission_method(data, graduation_year)
    if not admission_method:
        return None, 'Vui lòng chọn phương thức xét tuyển'

    if admission_method == 'exam':
        value, err = _parse_decimal(
            data.get('graduation_total_score') or data.get('exam_score'),
            0, 30, max_label='30.0',
        )
        if err:
            return None, err
        result['exam_score'] = value
        return result, None

    if admission_method == 'transcript':
        score_map = [
            ('Điểm Toán lớp 6', 'math_score_6'),
            ('Điểm Văn lớp 6', 'literature_score_6'),
            ('Điểm Toán lớp 7', 'math_score_7'),
            ('Điểm Văn lớp 7', 'literature_score_7'),
            ('Điểm Toán lớp 8', 'math_score_8'),
            ('Điểm Văn lớp 8', 'literature_score_8'),
            ('Điểm Toán lớp 9', 'math_score_9'),
            ('Điểm Văn lớp 9', 'literature_score_9'),
        ]
        for label, key in score_map:
            value, err = _parse_decimal(data.get(key), 0, 10, max_label='10.0')
            if err:
                return None, f'{label}: {err}'
            result[key] = value
        avg, err = _parse_decimal(data.get('avg_score'), 0, 10, max_label='10.0')
        if err:
            return None, 'Điểm trung bình không hợp lệ'
        result['avg_score'] = avg
        return result, None

    return None, 'Phương thức xét tuyển không hợp lệ'


def validate_study_vocational(data):
    study_vocational = data.get('study_vocational', 'no')
    if study_vocational == 'yes':
        if not data.get('vocational_campus_id') or not data.get('vocational_trade_id'):
            return 'Vui lòng chọn cơ sở và nghề dạy nghề'
    elif study_vocational != 'no':
        return 'Lựa chọn học nghề không hợp lệ'
    return None


def validate_admission_post(data):
    """
    Validate toàn bộ POST đăng ký tuyển sinh.
    Trả về (error_message, parsed_scores_dict).
    """
    email_err = validate_admission_email(data.get('email'))
    if email_err:
        return email_err, None

    phone = (data.get('phone') or '').strip()
    phone_err = validate_vn_phone(phone)
    if phone_err:
        return phone_err, None

    id_number = (data.get('id_number') or '').strip()
    cccd_err = validate_vn_cccd(id_number)
    if cccd_err:
        return cccd_err, None

    father_phone = (data.get('father_phone') or '').strip()
    father_phone_err = validate_vn_phone(father_phone, 'Số điện thoại của cha')
    if father_phone_err:
        return father_phone_err, None

    mother_phone = (data.get('mother_phone') or '').strip()
    mother_phone_err = validate_vn_phone(mother_phone, 'Số điện thoại của mẹ')
    if mother_phone_err:
        return mother_phone_err, None

    full_name = (data.get('full_name') or '').strip()
    if not full_name:
        return 'Họ và tên không được để trống', None

    gender = (data.get('gender') or '').strip()
    if gender not in VALID_GENDERS:
        return 'Giới tính không hợp lệ', None

    if not (data.get('birthday') or '').strip():
        return 'Ngày sinh không được để trống', None

    if not (data.get('ethnicity') or '').strip():
        return 'Dân tộc không được để trống', None

    if not (data.get('birth_place') or data.get('birth_place_facility') or '').strip():
        return 'Nơi sinh không được để trống', None

    if not (data.get('graduation_school') or '').strip():
        return 'Trường THCS không được để trống', None

    if not (data.get('id_issued_date') or '').strip():
        return 'Ngày cấp CCCD không được để trống', None

    for field, label in [
        ('permanent_house_number', 'Số nhà thường trú'),
        ('permanent_street', 'Đường thường trú'),
        ('permanent_ward', 'Phường/xã thường trú'),
        ('permanent_province', 'Tỉnh/thành phố thường trú'),
        ('current_house_number', 'Số nhà hiện tại'),
        ('current_street', 'Đường hiện tại'),
        ('current_ward', 'Phường/xã hiện tại'),
        ('current_province', 'Tỉnh/thành phố hiện tại'),
    ]:
        if not (data.get(field) or '').strip():
            return f'{label} không được để trống', None

    for field, label in [
        ('father_name', 'Họ tên cha'),
        ('father_job', 'Nghề nghiệp cha'),
        ('father_birth', 'Năm sinh cha'),
        ('mother_name', 'Họ tên mẹ'),
        ('mother_job', 'Nghề nghiệp mẹ'),
        ('mother_birth', 'Năm sinh mẹ'),
    ]:
        if not (data.get(field) or '').strip():
            return f'{label} không được để trống', None

    graduation_year, year_err = validate_graduation_year(data.get('graduation_year'))
    if year_err:
        return year_err, None

    admission_method = _resolve_admission_method(data, graduation_year)
    if admission_method not in VALID_ADMISSION_METHODS:
        return 'Vui lòng chọn phương thức xét tuyển', None

    conduct_err = validate_admission_conduct(
        data.get('conduct_6', ''),
        data.get('conduct_7', ''),
        data.get('conduct_8', ''),
        data.get('conduct_9', ''),
    )
    if conduct_err:
        return conduct_err, None

    vocational_err = validate_study_vocational(data)
    if vocational_err:
        return vocational_err, None

    scores, score_err = parse_graduation_scores(data, graduation_year)
    if score_err:
        return score_err, None

    return None, scores
