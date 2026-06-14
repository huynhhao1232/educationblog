import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class AccountType(models.Model):
    accounttype_id = models.AutoField(primary_key=True)
    accounttype_role = models.CharField(max_length=50, blank = False, null = True)

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_phone = models.CharField(max_length=20, blank=True, null = True)
    account_CCCD = models.CharField(max_length=20, blank=True, null = True)
    account_address = models.CharField(max_length=100, blank = True, null = True)
    account_createdate = models.DateTimeField(auto_now_add=True, null = True, blank = False)
    account_editdate = models.DateTimeField(auto_now_add=True, null = True, blank = False)
    account_enable = models.BooleanField(default=True, null = False, blank = False)
    account_picture = models.CharField(max_length=100, null = True, blank = True)
    forget_password_token = models.CharField(max_length=100, null = True, blank = True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank = True, null = True)
    accounttype = models.ForeignKey(AccountType, on_delete=models.DO_NOTHING, blank = True, null = True)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    enable = models.BooleanField(default=True, blank= False, null = False)

    def post_count(self):
        return Post.objects.filter(category=self).count()

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    content = models.TextField(max_length=100, blank=True, null=False)
    image_file = models.ImageField(upload_to='image', blank=True, null= False)
    createdate = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enable = models.BooleanField(default=True, blank= False, null = False)
    views = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null = True, blank = False)
    def save(self, *args, **kwargs):
        if self.pk:  # Kiểm tra nếu bài viết đã tồn tại
            old_post = Post.objects.filter(pk=self.pk).first()
            if old_post:
                # Xóa ảnh cũ nếu ảnh mới được tải lên
                if old_post.image_file and self.image_file != old_post.image_file:
                    if os.path.isfile(old_post.image_file.path):
                        os.remove(old_post.image_file.path)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Xóa ảnh khi bài viết bị xóa
        if self.image_file and os.path.isfile(self.image_file.path):
            os.remove(self.image_file.path)
        super().delete(*args, **kwargs)
class UploadedFile(models.Model):
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING, null = True, blank = False)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)


class NamhHoc(models.Model):
    id = models.AutoField(primary_key=True)
    namhoc = models.CharField(max_length=50, blank=True, null=True)
    enable = models.BooleanField(default=True, blank= False, null = False)

class LichCongTac(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    createdate = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enable = models.BooleanField(default=True, blank= False, null = False)
    namhoc = models.ForeignKey(NamhHoc, on_delete=models.DO_NOTHING, null = True, blank = False)

class PhongBan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    enable = models.BooleanField(default=True, blank= False, null = False)
    createdate = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def num_teachers(self):
        return self.pb_gv_set.count()

class GV(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    role1 = models.CharField(max_length=50, blank=True, null=True)
    role2 = models.CharField(max_length=50, blank=True, null=True)
    sex = models.BooleanField(default=True, blank= False, null = False) #True la Nam, False la Nu
    chuyenmon = models.CharField(max_length=50, blank=True, null=True)
    namsinh =models.CharField(max_length=50, blank=True, null=True)
    image_file = models.ImageField(upload_to='image', blank=True, null= False)
    bac = models.IntegerField(null = True, blank = True)
    enable = models.BooleanField(default=True, blank= False, null = False)

class PB_GV(models.Model):
    id = models.AutoField(primary_key=True)
    phongban = models.ForeignKey(PhongBan, on_delete=models.DO_NOTHING, null = True, blank = False)
    gv = models.ForeignKey(GV, on_delete=models.DO_NOTHING, null = True, blank = False)


class PostAnswer(models.Model):
    post_id = models.AutoField(primary_key=True)
    post_title = models.CharField(max_length=100, null = True, blank = False)
    post_content = models.TextField(max_length=100, null = True, blank = False)
    post_approved = models.BooleanField(default=False, null = False, blank = False)
    post_enable = models.BooleanField(default=False, null = False, blank = False)
    post_createdate = models.DateTimeField(auto_now_add=True, null = True, blank = False)
    post_editdate = models.DateTimeField(auto_now_add=True, null = True, blank = False)
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING, null = True, blank = False)

class PostForum(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null = True, blank = False)
    content = models.TextField(max_length=100, null = True, blank = False)
    enable = models.BooleanField(default=False, null = False, blank = False)
    createdate = models.DateTimeField(auto_now_add=True, null = True, blank = False)
    name =  models.CharField(max_length=100, null = True, blank = False)


class PostForumComment(models.Model):
    """Bình luận / trả lời (cây lồng nhau) trên bài PostForum."""
    post = models.ForeignKey(PostForum, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    author_name = models.CharField(max_length=100)
    body = models.TextField(max_length=2000)
    createdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['createdate']

    def __str__(self):
        return f'{self.author_name}: {self.body[:40]}'


class Campus(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)  # Thêm dòng này

    def __str__(self):
        return self.name



class Shift(models.Model):
    code = models.CharField(max_length=10, unique=True)  # 'sang', 'toi'
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SubjectGroup(models.Model):
    code = models.CharField(max_length=10, unique=True)  # '1', '2', '3', etc.
    description = models.TextField(blank=True)
    subjects = models.TextField(help_text="Danh sách môn học, cách nhau bởi dấu phẩy")

    def __str__(self):
        return f"Tổ hợp {self.code}"


class ExamRoom(models.Model):
    """Phòng thi: thuộc một cơ sở, có số hàng/cột để tính sức chứa."""
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, verbose_name="Cơ sở")
    name = models.CharField(max_length=100, verbose_name="Tên phòng (vd: P101)")
    row_count = models.PositiveIntegerField(verbose_name="Số hàng")
    col_count = models.PositiveIntegerField(verbose_name="Số cột (số ghế mỗi hàng)")
    capacity = models.PositiveIntegerField(editable=False, default=0)

    class Meta:
        verbose_name = "Phòng thi"
        verbose_name_plural = "Phòng thi"
        unique_together = ('campus', 'name')

    def save(self, *args, **kwargs):
        self.capacity = self.row_count * self.col_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campus.name} - {self.name}"


class ExamRoomShiftConfig(models.Model):
    """Kích thước phòng theo từng ca thi."""
    SHIFT_CHOICES = [
        ('sang', 'Sáng'),
        ('chieu', 'Chiều'),
        ('toi', 'Tối'),
    ]
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, related_name='shift_configs')
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, default='sang')
    row_count = models.PositiveIntegerField(verbose_name="Số hàng")
    col_count = models.PositiveIntegerField(verbose_name="Số cột (số ghế mỗi hàng)")
    capacity = models.PositiveIntegerField(editable=False, default=0)

    class Meta:
        unique_together = ('exam_room', 'shift')
        verbose_name = "Cấu hình phòng theo ca"
        verbose_name_plural = "Cấu hình phòng theo ca"

    def save(self, *args, **kwargs):
        self.capacity = self.row_count * self.col_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.exam_room} - {self.get_shift_display()} ({self.row_count}x{self.col_count})"


class CampusShiftGroup(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    subject_group = models.ForeignKey(SubjectGroup, on_delete=models.CASCADE)
    registration_count = models.PositiveIntegerField(default=0)
    number_of_classes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('campus', 'shift', 'subject_group')

    def __str__(self):
        return f"{self.campus.name} - {self.shift.name} - Tổ hợp {self.subject_group.code}"


class VocationalCampus(models.Model):
    """Cơ sở dạy nghề (GDNN)"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Cơ sở dạy nghề'
        verbose_name_plural = 'Cơ sở dạy nghề'

    def __str__(self):
        return self.name


class CampusVocationalLink(models.Model):
    """Liên kết cơ sở tuyển sinh GDTX với cơ sở dạy nghề"""
    admission_campus = models.ForeignKey(
        Campus, on_delete=models.CASCADE, related_name='vocational_links'
    )
    vocational_campus = models.ForeignKey(
        VocationalCampus, on_delete=models.CASCADE, related_name='admission_links'
    )

    class Meta:
        unique_together = ('admission_campus', 'vocational_campus')
        verbose_name = 'Liên kết cơ sở dạy nghề'
        verbose_name_plural = 'Liên kết cơ sở dạy nghề'

    def __str__(self):
        return f'{self.admission_campus.name} → {self.vocational_campus.name}'


class VocationalTrade(models.Model):
    """Nghề đào tạo tại cơ sở dạy nghề"""
    vocational_campus = models.ForeignKey(
        VocationalCampus, on_delete=models.CASCADE, related_name='trades'
    )
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('vocational_campus', 'name')
        verbose_name = 'Nghề'
        verbose_name_plural = 'Nghề'

    def __str__(self):
        return f'{self.vocational_campus.name} - {self.name}'


class AdmissionForm(models.Model):
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    ethnicity = models.CharField(max_length=50)
    birthday = models.DateField()
    religion = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # CCCD Image
    cccd_image = models.ImageField(upload_to='image', verbose_name='Ảnh CCCD', null=True, blank=True)

    # School Record Image
    school_record_image = models.ImageField(upload_to='image', verbose_name='Ảnh học bạ', null=True, blank=True)

    # Địa chỉ thường trú
    cccd_province = models.CharField(max_length=100)
    cccd_district = models.CharField(max_length=100)
    cccd_ward = models.CharField(max_length=100)
    cccd_town = models.CharField(max_length=255)

    # Quê quán
    hometown_province = models.CharField(max_length=100)

    # Nơi khai sinh
    birth_reg_province = models.CharField(max_length=100)
    birth_reg_district = models.CharField(max_length=100)
    birth_reg_ward = models.CharField(max_length=100)
    birth_reg_town = models.CharField(max_length=255)

    # Nơi sinh
    birth_place_province = models.CharField(max_length=100)
    birth_place_district = models.CharField(max_length=100)
    birth_place_ward = models.CharField(max_length=100)
    birth_place_facility = models.CharField(max_length=255)

    # Nơi ở hiện tại
    current_province = models.CharField(max_length=100)
    current_district = models.CharField(max_length=100)
    current_ward = models.CharField(max_length=100)

    # CCCD
    id_number = models.CharField(max_length=20, unique=True)
    id_issued_date = models.DateField()
    id_issued_place = models.CharField(max_length=100, default="Cục trưởng cục cảnh sát QLHC về TTXH")

    # Trường THCS
    graduation_year = models.CharField(max_length=10)
    graduation_school = models.CharField(max_length=255)
    graduation_rank = models.CharField(max_length=50)
    exam_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(30)])
    conduct = models.CharField(max_length=50, null=True, blank=True)
    conduct_6 = models.CharField(max_length=20, null=True, blank=True, verbose_name="KQRL lớp 6")
    conduct_7 = models.CharField(max_length=20, null=True, blank=True, verbose_name="KQRL lớp 7")
    conduct_8 = models.CharField(max_length=20, null=True, blank=True, verbose_name="KQRL lớp 8")
    conduct_9 = models.CharField(max_length=20, null=True, blank=True, verbose_name="KQRL lớp 9")
    avg_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    math_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])  # Thêm điểm toán
    literature_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])


    math_score_6 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Toán lớp 6")
    literature_score_6 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Văn lớp 6")
    math_score_7 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Toán lớp 7")
    literature_score_7 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Văn lớp 7")
    math_score_8 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Toán lớp 8")
    literature_score_8 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Văn lớp 8")
    math_score_9 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Toán lớp 9")
    literature_score_9 = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Điểm Văn lớp 9")
    # Nghề nghiệp
    current_job = models.CharField(max_length=255, blank=True)

    # Thông tin phụ huynh
    father_name = models.CharField(max_length=255)
    father_job = models.CharField(max_length=100)
    father_birth = models.CharField(max_length=10)
    father_phone = models.CharField(max_length=20)

    mother_name = models.CharField(max_length=255)
    mother_job = models.CharField(max_length=100)
    mother_birth = models.CharField(max_length=10)
    mother_phone = models.CharField(max_length=20)
    enable = models.BooleanField(default=False, null=False, blank=False)

    study_vocational = models.CharField(
        max_length=3, default='no',
        choices=[('no', 'Không học nghề'), ('yes', 'Học nghề')]
    )
    vocational_campus = models.ForeignKey(
        VocationalCampus, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='admissions'
    )
    vocational_trade = models.ForeignKey(
        VocationalTrade, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='admissions'
    )

    # Liên kết cơ sở - ca học - tổ hợp
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT)
    subject_group = models.ForeignKey(SubjectGroup, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def student_type_label(self):
        from django.utils import timezone
        year = timezone.now().year
        gy = self.graduation_year
        if gy == 'before':
            return 'Tự do'
        if gy == 'current':
            return f'Thi chuyển cấp {year}'
        try:
            if int(gy) < year:
                return 'Tự do'
        except (ValueError, TypeError):
            pass
        return f'Thi chuyển cấp {year}'

    def __str__(self):
        return self.full_name


class Student(models.Model):
    """Model lưu thông tin học viên từ hệ thống"""
    student_code = models.CharField(max_length=7, unique=True, primary_key=True, verbose_name="Mã học viên")
    # Mã học viên: 7 số (2 số đầu: cơ sở, 2 số tiếp: tổ hợp môn, 3 số cuối: số thứ tự)
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, verbose_name="Cơ sở")
    subject_group = models.ForeignKey(SubjectGroup, on_delete=models.PROTECT, verbose_name="Tổ hợp môn")
    class_name = models.CharField(max_length=50, verbose_name="Lớp")
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    birthday = models.DateField(verbose_name="Ngày sinh")
    id_number = models.CharField(max_length=20, verbose_name="Số CCCD")
    birth_place = models.CharField(max_length=255, verbose_name="Nơi sinh")
    ethnicity = models.CharField(max_length=50, verbose_name="Dân tộc")
    gender = models.CharField(max_length=10, verbose_name="Giới tính")

    # Thông tin bổ sung học viên có thể điền
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ thường trú")
    parent_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Họ tên phụ huynh")
    parent_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại phụ huynh")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Học viên"
        verbose_name_plural = "Học viên"

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"

    def get_campus_name(self):
        """Lấy tên cơ sở từ mã học viên"""
        return self.campus.name if self.campus else ""


class ExamRoomStudent(models.Model):
    """Học viên dùng riêng cho chức năng xếp phòng thi (không liên quan đăng ký tốt nghiệp)."""
    student_code = models.CharField(max_length=7, unique=True, primary_key=True, verbose_name="Mã học viên")
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, verbose_name="Cơ sở")
    subject_group = models.ForeignKey(SubjectGroup, on_delete=models.PROTECT, verbose_name="Tổ hợp môn")
    class_name = models.CharField(max_length=50, verbose_name="Lớp")
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    exam_number = models.CharField(max_length=6, unique=True, null=True, blank=True, verbose_name="Số báo danh")
    is_integration = models.BooleanField(default=False, verbose_name="Học viên hoà nhập")

    class Meta:
        verbose_name = "Học viên (xếp phòng thi)"
        verbose_name_plural = "Học viên (xếp phòng thi)"

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"


class StudentExamAssignment(models.Model):
    """Xếp phòng thi theo ca (mỗi ca 1 phòng duy nhất cho 1 học viên)."""
    SHIFT_CHOICES = [
        ('sang', 'Sáng'),
        ('chieu', 'Chiều'),
        ('toi', 'Tối'),
    ]
    student = models.ForeignKey(ExamRoomStudent, on_delete=models.CASCADE, verbose_name="Học viên (xếp phòng)")
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phòng thi")
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, default='sang', verbose_name="Ca thi")
    seat_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Số ghế")

    class Meta:
        unique_together = ('student', 'shift')
        verbose_name = "Xếp phòng thi"
        verbose_name_plural = "Xếp phòng thi"

    def __str__(self):
        return f"{self.student.student_code} - {self.exam_room} ({self.get_shift_display()})"


class ExamSubjectSeat(models.Model):
    """
    Lưu sơ đồ chỗ ngồi riêng cho từng môn thi trong cùng phòng/ca.
    Mỗi (phòng, ca, môn) có một layout độc lập, hỗ trợ kéo thả.
    """
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, verbose_name="Phòng thi")
    shift = models.CharField(
        max_length=10,
        choices=StudentExamAssignment.SHIFT_CHOICES,
        default='sang',
        verbose_name="Ca thi",
    )
    subject_name = models.CharField(max_length=100, verbose_name="Môn thi")
    student = models.ForeignKey(ExamRoomStudent, on_delete=models.CASCADE, verbose_name="Học viên")
    seat_number = models.PositiveIntegerField(verbose_name="Số ghế")

    class Meta:
        unique_together = (
            ('exam_room', 'shift', 'subject_name', 'seat_number'),
            ('exam_room', 'shift', 'subject_name', 'student'),
        )
        verbose_name = "Sơ đồ ghế theo môn"
        verbose_name_plural = "Sơ đồ ghế theo môn"

    def __str__(self):
        return f"{self.exam_room} - {self.shift} - {self.subject_name} - ghế {self.seat_number}"


class ExamRoomSubject(models.Model):
    """Lưu danh sách môn thi đã gán cho từng phòng + ca."""
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, verbose_name="Phòng thi")
    shift = models.CharField(
        max_length=10,
        choices=StudentExamAssignment.SHIFT_CHOICES,
        default='sang',
        verbose_name="Ca thi",
    )
    subject_name = models.CharField(max_length=100, verbose_name="Môn thi")

    class Meta:
        unique_together = ('exam_room', 'shift', 'subject_name')
        verbose_name = "Môn thi phòng thi"
        verbose_name_plural = "Môn thi phòng thi"

    def __str__(self):
        return f"{self.exam_room} - {self.get_shift_display()} - {self.subject_name}"


class StudentExamRegistration(models.Model):
    """Model lưu thông tin đăng ký thi tốt nghiệp của học viên"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, verbose_name="Học viên")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email", help_text="Học viên có thể điền sau")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại", help_text="Học viên có thể điền sau")
    exam_subjects = models.JSONField(default=list, blank=True, verbose_name="Môn thi tốt nghiệp", help_text="Danh sách các môn học viên đã chọn")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    registration_date = models.DateTimeField(null=True, blank=True, verbose_name="Ngày đăng ký", help_text="Ngày đăng ký cuối cùng")
    update_count = models.PositiveIntegerField(default=0, verbose_name="Số lần cập nhật", help_text="Số lần học viên đã cập nhật thông tin đăng ký")

    class Meta:
        verbose_name = "Đăng ký thi tốt nghiệp"
        verbose_name_plural = "Đăng ký thi tốt nghiệp"

    def __str__(self):
        return f"{self.student.student_code} - {self.student.full_name}"

    def can_update(self):
        """Kiểm tra xem học viên có thể cập nhật thông tin không (tối đa 2 lần)"""
        return self.update_count < 2


class RegistrationHistory(models.Model):
    """Model lưu lịch sử cập nhật đăng ký thi tốt nghiệp"""
    registration = models.ForeignKey(StudentExamRegistration, on_delete=models.CASCADE, related_name='history', verbose_name="Đăng ký")

    # Thông tin trước khi cập nhật
    old_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email cũ")
    old_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại cũ")
    old_exam_subjects = models.JSONField(default=list, blank=True, verbose_name="Môn thi tốt nghiệp cũ")

    # Thông tin sau khi cập nhật
    new_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email mới")
    new_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại mới")
    new_exam_subjects = models.JSONField(default=list, blank=True, verbose_name="Môn thi tốt nghiệp mới")

    # Thông tin cập nhật
    action_type = models.CharField(max_length=20, choices=[
        ('created', 'Đăng ký lần đầu'),
        ('updated', 'Cập nhật thông tin'),
    ], default='updated', verbose_name="Loại hành động")
    update_count = models.PositiveIntegerField(verbose_name="Số lần cập nhật tại thời điểm này")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian cập nhật")

    class Meta:
        verbose_name = "Lịch sử đăng ký"
        verbose_name_plural = "Lịch sử đăng ký"
        ordering = ['-created_at']  # Sắp xếp theo thời gian mới nhất

    def __str__(self):
        return f"{self.registration.student.student_code} - {self.get_action_type_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class StudentInfoRecord(models.Model):
    """Thông tin học viên dùng cho chức năng kiểm tra thông tin trước kỳ thi THPT."""

    student_code = models.CharField(max_length=30, unique=True, verbose_name="Mã học viên")
    stt = models.PositiveIntegerField(null=True, blank=True, verbose_name="STT gốc từ Excel")
    class_name = models.CharField(max_length=50, blank=True, default="", verbose_name="Lớp")
    full_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Họ và tên")
    birthday = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    birth_place = models.CharField(max_length=255, blank=True, default="", verbose_name="Nơi sinh")
    gender = models.CharField(max_length=20, blank=True, default="", verbose_name="Giới tính")
    ethnicity = models.CharField(max_length=50, blank=True, default="", verbose_name="Dân tộc")
    id_number = models.CharField(max_length=20, blank=True, default="", verbose_name="Số CCCD")
    contact_address = models.TextField(blank=True, default="", verbose_name="Địa chỉ liên hệ")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Gmail")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="Số điện thoại")
    highschool_10 = models.CharField(max_length=255, blank=True, default="", verbose_name="Nơi học THPT lớp 10")
    highschool_11 = models.CharField(max_length=255, blank=True, default="", verbose_name="Nơi học THPT lớp 11")
    exam_subjects = models.JSONField(default=list, blank=True, verbose_name="Môn thi TN THPT")
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thông tin học viên kiểm tra"
        verbose_name_plural = "Thông tin học viên kiểm tra"
        ordering = ["class_name", "full_name"]

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"


class StudentInfoVerification(models.Model):
    """Lưu kết quả xác nhận: mỗi trường Đúng (D) hoặc Sai (S); giao diện gộp thành xác nhận tổng thể + tick mục sai."""

    STATUS_CHOICES = (
        ("", "Chưa chọn"),
        ("D", "Đúng"),
        ("S", "Sai"),
    )

    student = models.OneToOneField(
        StudentInfoRecord,
        on_delete=models.CASCADE,
        related_name="verification",
        verbose_name="Học viên",
    )
    class_name_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    full_name_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    birthday_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    birth_place_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    gender_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    ethnicity_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    id_number_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    contact_address_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    email_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    phone_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    highschool_10_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    highschool_11_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    exam_subjects_status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, default="")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú của học viên")
    submit_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Số lần đã gửi xác nhận",
        help_text="Tối đa 2 lần; sau đó chỉ xem, không chỉnh sửa.",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Xác nhận thông tin học viên"
        verbose_name_plural = "Xác nhận thông tin học viên"

    def __str__(self):
        return f"Xác nhận - {self.student.student_code}"

    def can_submit_again(self) -> bool:
        return self.submit_count < 2


class StudentInfoVerificationHistory(models.Model):
    """Mỗi lần học viên gửi xác nhận thành công (tối đa 2) lưu một bản ghi."""

    verification = models.ForeignKey(
        StudentInfoVerification,
        on_delete=models.CASCADE,
        related_name="history_entries",
        verbose_name="Bản xác nhận",
    )
    submit_index = models.PositiveSmallIntegerField(verbose_name="Lần gửi thứ")
    created_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict, verbose_name="Dữ liệu đã gửi")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lịch sử gửi xác nhận"
        verbose_name_plural = "Lịch sử gửi xác nhận"

    def __str__(self):
        return f"{self.verification.student.student_code} — lần {self.submit_index} @ {self.created_at}"


# --- Sắp xếp phòng thi II (phân hệ thí sinh + điểm thi, trộn cơ sở) ---

EXAM_SORT2_CAMPUS_CODE_BY_INT = {
    1: 'AS',
    2: 'AT',
    3: 'BS',
    4: 'CS',
    5: 'VH',
    6: 'KT',
    7: 'CN',
    8: 'HT',
    9: 'ĐS',
}


class ExamSort2Candidate(models.Model):
    """Thí sinh gốc (phân hệ 1) — danh sách master để lấy về điểm thi."""
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, verbose_name="Thuộc cơ sở")
    class_name = models.CharField(max_length=50, verbose_name="Lớp")
    elective_subject_1 = models.CharField(
        max_length=50, blank=True, default='', verbose_name="Môn tự chọn 1",
    )
    elective_subject_2 = models.CharField(
        max_length=50, blank=True, default='', verbose_name="Môn tự chọn 2",
    )
    exam_number = models.CharField(
        max_length=12, blank=True, default='', verbose_name="Số báo danh",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Thí sinh (SXPT II)"
        verbose_name_plural = "Thí sinh (SXPT II)"
        ordering = ['campus__code', 'class_name', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.campus.code} — {self.class_name})"

    def get_exam_subjects_display(self) -> str:
        """4 môn thi: Văn + Toán (bắt buộc) + 2 môn tự chọn."""
        parts = ['Văn', 'Toán']
        for subj in (self.elective_subject_1, self.elective_subject_2):
            if subj:
                parts.append(subj)
        return ', '.join(parts)


class ExamSort2Venue(models.Model):
    """Điểm thi — mỗi cơ sở trung tâm có thể là một điểm thi."""
    code = models.CharField(max_length=20, unique=True, verbose_name="Mã điểm thi")
    name = models.CharField(max_length=255, verbose_name="Tên điểm thi")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="STT")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Điểm thi (SXPT II)"
        verbose_name_plural = "Điểm thi (SXPT II)"
        ordering = ['sort_order', 'code']

    def __str__(self):
        return f"{self.code} — {self.name}"


class ExamSort2VenueCandidate(models.Model):
    """Thí sinh đã mang về một điểm thi cụ thể."""
    venue = models.ForeignKey(ExamSort2Venue, on_delete=models.CASCADE, related_name='venue_candidates')
    candidate = models.ForeignKey(ExamSort2Candidate, on_delete=models.CASCADE, related_name='venue_links')

    class Meta:
        unique_together = ('venue', 'candidate')
        verbose_name = "Thí sinh tại điểm thi"
        verbose_name_plural = "Thí sinh tại điểm thi"

    def __str__(self):
        return f"{self.venue.code}: {self.candidate.full_name}"


class ExamSort2Room(models.Model):
    """Phòng thi thuộc một điểm thi."""
    venue = models.ForeignKey(ExamSort2Venue, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100, verbose_name="Tên phòng thi")
    col_count = models.PositiveIntegerField(verbose_name="Số cột")
    row_count = models.PositiveIntegerField(verbose_name="Số hàng")
    target_campus = models.ForeignKey(
        Campus, on_delete=models.PROTECT, verbose_name="Đối tượng cơ sở",
        related_name='exam_sort2_target_rooms',
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name="STT")
    capacity = models.PositiveIntegerField(editable=False, default=0)

    class Meta:
        verbose_name = "Phòng thi (SXPT II)"
        verbose_name_plural = "Phòng thi (SXPT II)"
        unique_together = ('venue', 'name')
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        self.capacity = self.col_count * self.row_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.venue.code} / {self.name}"


class ExamSort2SeatAssignment(models.Model):
    """Gán thí sinh vào ghế trong phòng (số ghế 1..capacity, theo ma trận cột×hàng)."""
    room = models.ForeignKey(ExamSort2Room, on_delete=models.CASCADE, related_name='seat_assignments')
    venue_candidate = models.ForeignKey(
        ExamSort2VenueCandidate, on_delete=models.CASCADE, related_name='seat_assignments',
    )
    seat_number = models.PositiveIntegerField(verbose_name="Số ghế")

    class Meta:
        unique_together = (
            ('room', 'seat_number'),
            ('room', 'venue_candidate'),
        )
        verbose_name = "Xếp ghế (SXPT II)"
        verbose_name_plural = "Xếp ghế (SXPT II)"
        ordering = ['seat_number']

    def __str__(self):
        return f"{self.room.name} — ghế {self.seat_number}"


# --- Xếp lớp theo năm học ---

CLASS_ASSIGNMENT_CAMPUS_CODES = ('AS', 'AT', 'CN', 'KT', 'VH', 'ĐS', 'BS', 'CS')


class ClassAssignmentOldClassConfig(models.Model):
    """Cấu hình lớp cũ → tổ hợp môn (import từ CHIA LỚP)."""
    year = models.ForeignKey(
        NamhHoc, on_delete=models.CASCADE, related_name='class_assignment_old_configs',
        verbose_name="Năm học",
    )
    class_name = models.CharField(max_length=50, verbose_name="Tên lớp cũ")
    old_grade = models.PositiveSmallIntegerField(verbose_name="Khối cũ")
    campus_code = models.CharField(max_length=10, verbose_name="Mã cơ sở")
    subject_group = models.ForeignKey(
        SubjectGroup, on_delete=models.PROTECT, verbose_name="Tổ hợp môn",
    )
    female_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Sĩ số nữ (tham khảo)")

    class Meta:
        verbose_name = "Cấu hình lớp cũ (xếp lớp)"
        verbose_name_plural = "Cấu hình lớp cũ (xếp lớp)"
        unique_together = ('year', 'class_name')
        ordering = ['campus_code', 'old_grade', 'class_name']

    def __str__(self):
        return f"{self.class_name} → TH {self.subject_group.code}"


class ClassAssignmentClass(models.Model):
    """Lớp mới sau xếp lớp."""
    year = models.ForeignKey(
        NamhHoc, on_delete=models.CASCADE, related_name='class_assignment_classes',
        verbose_name="Năm học",
    )
    name = models.CharField(max_length=50, verbose_name="Tên lớp mới")
    new_grade = models.PositiveSmallIntegerField(verbose_name="Khối mới")
    old_grade = models.PositiveSmallIntegerField(verbose_name="Khối cũ")
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, verbose_name="Cơ sở")
    subject_group = models.ForeignKey(SubjectGroup, on_delete=models.PROTECT, verbose_name="Tổ hợp môn")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lớp (xếp lớp)"
        verbose_name_plural = "Lớp (xếp lớp)"
        unique_together = ('year', 'name')
        ordering = ['campus__code', 'new_grade', 'name']

    def __str__(self):
        return self.name


class ClassAssignmentStudent(models.Model):
    """Học viên chờ / đã xếp lớp trong một năm học."""
    year = models.ForeignKey(
        NamhHoc, on_delete=models.CASCADE, related_name='class_assignment_students',
        verbose_name="Năm học",
    )
    id_number = models.CharField(max_length=20, verbose_name="Số định danh")
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    old_class_name = models.CharField(max_length=50, verbose_name="Lớp cũ")
    old_grade = models.PositiveSmallIntegerField(verbose_name="Khối cũ")
    campus_code = models.CharField(max_length=10, verbose_name="Mã cơ sở")
    subject_group = models.ForeignKey(
        SubjectGroup, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="Tổ hợp môn",
    )
    gender = models.CharField(max_length=10, verbose_name="Giới tính")
    ethnicity = models.CharField(max_length=50, blank=True, default="", verbose_name="Dân tộc")
    birthday = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    academic_result = models.CharField(max_length=50, blank=True, default="", verbose_name="KQ học tập HK CN")
    promoted = models.CharField(max_length=20, blank=True, default="", verbose_name="Lên lớp")
    assigned_class = models.ForeignKey(
        ClassAssignmentClass, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students', verbose_name="Lớp đã xếp",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Học viên (xếp lớp)"
        verbose_name_plural = "Học viên (xếp lớp)"
        unique_together = ('year', 'id_number')
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.old_class_name})"

    @property
    def is_assigned(self):
        return self.assigned_class_id is not None

