# adminpage/models.py - Chấm công tự động
from django.db import models


# Cơ sở AT (AS và AT đều tính AT), BS, CS dùng homepage.Campus. Điểm liên kết (CN, ĐS, KT, HT, VH) dùng Location bên dưới.


class Location(models.Model):
    """Điểm liên kết: CN, ĐS, KT, HT, VH (cơ sở AT, BS, CS dùng homepage.Campus)."""
    code = models.CharField(max_length=10, unique=True, verbose_name='Mã')
    name = models.CharField(max_length=100, blank=True, verbose_name='Tên')

    class Meta:
        verbose_name = 'Điểm liên kết'
        verbose_name_plural = 'Điểm liên kết'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Teacher(models.Model):
    """Giáo viên: Họ tên, Mã giáo viên, Môn (từ DSGV)."""
    full_name = models.CharField(max_length=255, verbose_name='Họ và tên')
    teacher_code = models.CharField(max_length=50, unique=True, verbose_name='Mã giáo viên')
    display_subject = models.CharField(
        max_length=100, blank=True, verbose_name='Tên môn (từ DSGV)', help_text='Hiển thị ở cột Môn trong bảng chấm công'
    )

    class Meta:
        verbose_name = 'Giáo viên'
        verbose_name_plural = 'Giáo viên'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.teacher_code} - {self.full_name}"


class ClassRoom(models.Model):
    """Lớp học: Tên lớp, Khối, Sĩ số, Cơ sở quản lý (homepage.Campus, vd: lớp AT thuộc AS)."""
    GRADE_CHOICES = [(10, '10'), (11, '11'), (12, '12')]
    name = models.CharField(max_length=50, verbose_name='Tên lớp')
    grade = models.PositiveSmallIntegerField(
        choices=GRADE_CHOICES, null=True, blank=True, verbose_name='Khối'
    )
    class_size = models.PositiveIntegerField(default=0, verbose_name='Sĩ số')
    # Cơ sở quản lý (Campus AT/BS/CS): AS và AT trong tên lớp đều gắn Campus AT
    managing_campus = models.ForeignKey(
        'homepage.Campus',
        on_delete=models.PROTECT,
        related_name='admin_classrooms',
        null=True,
        blank=True,
        verbose_name='Cơ sở quản lý'
    )
    # Điểm liên kết (CN, ĐS, KT...) - dùng cho lọc Nhóm 2
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='classrooms_at_location',
        null=True,
        blank=True,
        verbose_name='Điểm liên kết'
    )

    class Meta:
        verbose_name = 'Lớp học'
        verbose_name_plural = 'Lớp học'
        ordering = ['grade', 'name']

    def __str__(self):
        return f"{self.name} (Khối {self.grade}, Sĩ số {self.class_size})"

    def get_display_location(self):
        """Location để phân loại: ưu tiên managing_campus (Campus AT/BS/CS)."""
        return self.managing_campus


class ScheduleVersion(models.Model):
    """Phiên bản TKB theo tuần trong tháng. Tuần 1=ngày 1-7, Tuần 2=8-14, Tuần 3=15-21, Tuần 4=22-hết tháng."""
    name = models.CharField(max_length=200, verbose_name='Tên phiên bản (vd: T2/2025 Tuần 1)')
    effective_from = models.DateField(null=True, blank=True, verbose_name='Áp dụng từ')
    effective_to = models.DateField(null=True, blank=True, verbose_name='Áp dụng đến')
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Năm')
    month = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Tháng (1-12)')
    week = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Tuần trong tháng (1-4)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Phiên bản TKB'
        verbose_name_plural = 'Phiên bản TKB'
        ordering = ['-year', '-month', '-week']

    def __str__(self):
        return self.name


class Schedule(models.Model):
    """TKB: Liên kết Teacher - ClassRoom, Thứ, Tiết, Môn, Buổi, Ngày áp dụng."""
    SESSION_CHOICES = [
        ('sang', 'Sáng'),
        ('chieu', 'Chiều'),
        ('toi', 'Tối'),
    ]
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='schedules', verbose_name='Giáo viên'
    )
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='schedules', verbose_name='Lớp'
    )
    day_of_week = models.PositiveSmallIntegerField(
        verbose_name='Thứ', help_text='2=Thứ 2, 3=Thứ 3, ... 8=Chủ nhật'
    )
    period = models.PositiveSmallIntegerField(verbose_name='Tiết')
    subject_name = models.CharField(max_length=50, verbose_name='Tên môn (vd: SH để lọc Sinh hoạt)')
    session = models.CharField(
        max_length=10, choices=SESSION_CHOICES, default='sang', verbose_name='Buổi'
    )
    effective_date = models.DateField(null=True, blank=True, verbose_name='Ngày áp dụng')
    version = models.ForeignKey(
        ScheduleVersion,
        on_delete=models.CASCADE,
        related_name='schedules',
        null=True,
        blank=True,
        verbose_name='Phiên bản TKB'
    )

    class Meta:
        verbose_name = 'Tiết TKB'
        verbose_name_plural = 'Tiết TKB'
        ordering = ['day_of_week', 'period']

    def __str__(self):
        return f"{self.teacher.teacher_code} - {self.classroom.name} - T{self.day_of_week} Tiết {self.period}"

    def get_converted_periods(self):
        """
        Tính tiết quy đổi:
        - Môn SH (Sinh hoạt): Cơ sở (AT, BS, CS) = 4 tiết; Điểm liên kết = 3 tiết.
        - Môn khác: 1 tiết.
        """
        from adminpage.services import get_converted_periods_for_schedule
        return get_converted_periods_for_schedule(self)


class AttendanceOverride(models.Model):
    """Ghi đè số tiết khi người dùng sửa trực tiếp ô trên bảng chấm công."""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendance_overrides')
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    day = models.PositiveSmallIntegerField()
    value = models.PositiveSmallIntegerField(default=0, verbose_name='Số tiết (đã sửa)')

    class Meta:
        verbose_name = 'Ghi đè tiết chấm công'
        verbose_name_plural = 'Ghi đè tiết chấm công'
        unique_together = ('teacher', 'year', 'month', 'day')

    def __str__(self):
        return f"{self.teacher.teacher_code} {self.year}-{self.month:02d}-{self.day:02d}: {self.value}"


# ---------- Sổ đầu bài số (theo nhóm bộ môn) ----------

# Map tên môn (từ DSGV) sang mã dùng trong SubjectJournal
SUBJECT_DISPLAY_TO_CODE = {
    'ngữ văn': 'nguvan', 'nguvan': 'nguvan',
    'toán': 'toan', 'toan': 'toan',
    'hoá': 'hoa', 'hóa': 'hoa', 'hoa': 'hoa', 'hóa học': 'hoa',
    'sinh': 'sinh', 'lý': 'ly', 'ly': 'ly',
    'sử': 'su', 'su': 'su', 'địa': 'dia', 'dia': 'dia',
    'ktpl': 'ktpl', 'kt-pl': 'ktpl',
    'tiếng anh': 'ta', 'ta': 'ta', 'tieng anh': 'ta',
}


def normalize_subject_code(raw):
    """Chuẩn hóa tên môn từ file thành mã (nguvan, toan, ...)."""
    s = str(raw).strip().lower()
    return SUBJECT_DISPLAY_TO_CODE.get(s, s[:20] if len(s) > 20 else s)


SUBJECT_CHOICES = [
    ('nguvan', 'Ngữ văn'),
    ('toan', 'Toán'),
    ('hoa', 'Hoá'),
    ('sinh', 'Sinh'),
    ('ly', 'Lý'),
    ('su', 'Sử'),
    ('dia', 'Địa'),
    ('ktpl', 'KTPL'),
    ('ta', 'Tiếng Anh'),
]


class JournalTeacher(models.Model):
    """Giáo viên: mã truy cập, tên, môn, số lớp (số hàng = số lớp × 2)."""
    full_name = models.CharField(max_length=255, verbose_name='Họ và tên')
    subject = models.CharField(max_length=50, verbose_name='Môn')  # Ngữ văn, Toán, ...
    access_code = models.CharField(
        max_length=50, unique=True, verbose_name='Mã số truy cập',
        help_text='Giáo viên nhập mã này để vào sổ đầu bài'
    )
    num_classes = models.PositiveSmallIntegerField(
        default=1, verbose_name='Số lớp',
        help_text='Số hàng trong sổ = Số lớp × 2'
    )

    class Meta:
        verbose_name = 'Giáo viên (Sổ đầu bài)'
        verbose_name_plural = 'Giáo viên (Sổ đầu bài)'
        ordering = ['full_name']

    def num_rows(self):
        return self.num_classes * 2

    def __str__(self):
        return f"{self.access_code} - {self.full_name} ({self.subject})"


class JournalClass(models.Model):
    """Lớp học (từ DSL): 10AS1, 11BS3..."""
    name = models.CharField(max_length=50, unique=True, verbose_name='Tên lớp')

    class Meta:
        verbose_name = 'Lớp (Sổ đầu bài)'
        verbose_name_plural = 'Lớp (Sổ đầu bài)'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubjectJournal(models.Model):
    """Sổ đầu bài theo nhóm bộ môn và năm."""
    subject = models.CharField(max_length=50, verbose_name='Môn')  # Ngữ văn, Toán, Hoá, ...
    year = models.PositiveIntegerField(verbose_name='Năm học')
    week1_start_date = models.DateField(
        null=True, blank=True, verbose_name='Ngày bắt đầu tuần 1',
        help_text='Khi set, tự động tạo 13 tuần liền kề'
    )

    class Meta:
        verbose_name = 'Sổ đầu bài (theo môn/năm)'
        verbose_name_plural = 'Sổ đầu bài (theo môn/năm)'
        unique_together = ('subject', 'year')
        ordering = ['-year', 'subject']

    def __str__(self):
        return f"{self.subject} {self.year}"

    def get_subject_display(self):
        """Trả về tên hiển thị môn từ SUBJECT_CHOICES."""
        for code, label in SUBJECT_CHOICES:
            if code == self.subject:
                return label
        return self.subject


class JournalWeek(models.Model):
    """Tuần trong sổ (1-13), có thể khóa."""
    subject_journal = models.ForeignKey(
        SubjectJournal, on_delete=models.CASCADE, related_name='weeks', verbose_name='Sổ đầu bài'
    )
    week_number = models.PositiveSmallIntegerField(verbose_name='Tuần', help_text='1-13')
    start_date = models.DateField(verbose_name='Từ ngày')
    end_date = models.DateField(verbose_name='Đến ngày')
    is_locked = models.BooleanField(default=False, verbose_name='Khóa')
    allow_late_edit = models.BooleanField(
        default=False,
        verbose_name='Cho phép nhập/sửa quá hạn',
        help_text='Bật khi quản trị viên mở lại tuần đã quá hạn.'
    )

    class Meta:
        verbose_name = 'Tuần sổ đầu bài'
        verbose_name_plural = 'Tuần sổ đầu bài'
        unique_together = ('subject_journal', 'week_number')
        ordering = ['week_number']

    def __str__(self):
        return f"{self.subject_journal} - Tuần {self.week_number}"


class JournalRow(models.Model):
    """Một hàng trong sổ đầu bài, gắn với giáo viên."""
    subject_journal = models.ForeignKey(
        SubjectJournal, on_delete=models.CASCADE, related_name='rows', verbose_name='Sổ đầu bài'
    )
    teacher = models.ForeignKey(
        JournalTeacher, on_delete=models.CASCADE, related_name='journal_rows', verbose_name='Giáo viên'
    )
    row_order = models.PositiveIntegerField(verbose_name='Thứ tự hàng', help_text='STT trong bảng')

    class Meta:
        verbose_name = 'Hàng sổ đầu bài'
        verbose_name_plural = 'Hàng sổ đầu bài'
        unique_together = ('subject_journal', 'row_order')
        ordering = ['row_order']

    def __str__(self):
        return f"{self.subject_journal} - Hàng {self.row_order} ({self.teacher.full_name})"


class JournalEntry(models.Model):
    """Một ô nhập liệu trong sổ: ngày dạy, lớp, tiết, tên bài, học viên vắng..."""
    journal_row = models.ForeignKey(
        JournalRow, on_delete=models.CASCADE, related_name='entries', verbose_name='Hàng'
    )
    week_number = models.PositiveSmallIntegerField(verbose_name='Tuần')
    lesson_date = models.DateField(verbose_name='Ngày dạy')
    period = models.PositiveSmallIntegerField(verbose_name='Tiết dạy', help_text='1-5')
    classes_taught = models.CharField(
        max_length=255, blank=True, verbose_name='Lớp dạy',
        help_text='Lớp hoặc nhiều lớp cách nhau bằng dấu phẩy'
    )
    student_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Sĩ số')
    absent_students = models.TextField(blank=True, verbose_name='Học viên vắng')
    lesson_title = models.CharField(max_length=500, blank=True, verbose_name='Tên bài giảng')
    comment = models.TextField(blank=True, verbose_name='Nhận xét của GV sau tiết dạy')

    class Meta:
        verbose_name = 'Ô sổ đầu bài'
        verbose_name_plural = 'Ô sổ đầu bài'
        ordering = ['-lesson_date', '-id']

    def __str__(self):
        return f"{self.journal_row} - {self.lesson_date} T{self.period}"


# --- Legacy (giữ tạm cho migration, sẽ xóa khi chuyển xong) ---
class SchoolConfig(models.Model):
    current_date = models.DateField(verbose_name='Ngày hiện tại')
    current_week = models.PositiveSmallIntegerField(verbose_name='Tuần học hiện tại')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cấu hình trường (Legacy)'
        verbose_name_plural = 'Cấu hình trường (Legacy)'


class ClassJournal(models.Model):
    """Legacy - dùng JournalEntry thay thế."""
    teacher = models.ForeignKey(JournalTeacher, on_delete=models.CASCADE, related_name='legacy_entries')
    lesson_date = models.DateField()
    week = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(default=1)
    subject = models.CharField(max_length=100, blank=True)
    lesson_title = models.CharField(max_length=500, blank=True)
    absent_students = models.TextField(blank=True)
    rating = models.CharField(max_length=20, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sổ đầu bài (Legacy)'
