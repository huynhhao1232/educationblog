# adminpage/services.py - Logic chấm công tự động
"""
Tính tiết quy đổi:
- Môn SH (Sinh hoạt): Cơ sở (AT, BS, CS) = 4 tiết; Điểm liên kết = 3 tiết.
- Môn khác: 1 tiết.
"""


def get_converted_periods_for_schedule(schedule):
    """
    Trả về số tiết quy đổi cho một tiết TKB.
    schedule: object có .subject_name, .classroom (có .managing_campus là Location).
    """
    if not schedule:
        return 0
    subject = (schedule.subject_name or '').strip().upper()
    # Lọc môn Sinh hoạt: mã SH hoặc tên chứa "Sinh hoạt"
    is_sh = subject == 'SH' or 'SINH HOẠT' in (schedule.subject_name or '').upper()
    if not is_sh:
        return 1
    # SH: Cơ sở (AT, BS, CS) = 4 tiết; Điểm liên kết (CN, ĐS, KT, HT, VH) = 3 tiết
    campus = getattr(schedule, 'classroom', None) and getattr(schedule.classroom, 'managing_campus', None)
    if campus and getattr(campus, 'code', None) in ('AT', 'BS', 'CS'):
        return 4
    return 3


def get_converted_periods_for_row(subject_name, is_campus_location):
    """
    Hàm thuần: cho môn học và loại địa điểm (campus=True/False), trả về tiết quy đổi.
    Dùng khi không có instance Schedule (vd khi aggregate).
    """
    subject = (subject_name or '').strip().upper()
    is_sh = subject == 'SH' or 'SINH HOẠT' in (subject_name or '').upper()
    if not is_sh:
        return 1
    return 4 if is_campus_location else 3
