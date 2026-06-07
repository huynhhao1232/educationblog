# adminpage/services.py - Logic chấm công tự động
"""
Rule mới:
- Mọi tiết lên lớp (kể cả SH) trên cột ngày đều tính 1 tiết.
- Nếu là SH:
  - Cơ sở AT/BS/CS: cộng thêm 3 tiết vào "Số tiết làm hồ sơ"
  - Điểm liên kết: cộng thêm 2 tiết vào "Số tiết làm hồ sơ"
- Tổng quy đổi cho 1 tiết SH vì vậy vẫn là 4 (AT/BS/CS) hoặc 3 (liên kết).
"""


def _is_sh_subject(subject_name):
    subject = (subject_name or '').strip().upper()
    return subject == 'SH' or 'HDTN' in subject


def _is_primary_campus_code(campus_code):
    return (campus_code or '').strip().upper() in ('AT', 'BS', 'CS')


def get_daily_periods_for_schedule(schedule):
    """Số tiết hiển thị tại cột ngày cho 1 tiết TKB."""
    if not schedule:
        return 0
    return 1


def get_hoso_extra_for_schedule(schedule):
    """Số tiết cộng thêm vào cột 'Số tiết làm hồ sơ' cho 1 tiết TKB."""
    if not schedule:
        return 0
    if not _is_sh_subject(getattr(schedule, 'subject_name', '')):
        return 0
    campus = getattr(schedule, 'classroom', None) and getattr(schedule.classroom, 'managing_campus', None)
    campus_code = getattr(campus, 'code', None)
    return 4 if _is_primary_campus_code(campus_code) else 2


def get_converted_periods_for_schedule(schedule):
    """
    Tổng tiết quy đổi cho 1 tiết TKB (giữ API cũ để tương thích).
    = tiết cột ngày + tiết hồ sơ.
    """
    return get_daily_periods_for_schedule(schedule) + get_hoso_extra_for_schedule(schedule)


def get_converted_periods_for_row(subject_name, is_campus_location):
    """
    Hàm thuần theo API cũ: trả về tổng tiết quy đổi.
    - Môn thường: 1
    - SH: 4 (AT/BS/CS) hoặc 3 (liên kết)
    """
    if not _is_sh_subject(subject_name):
        return 1
    return 5 if is_campus_location else 3
