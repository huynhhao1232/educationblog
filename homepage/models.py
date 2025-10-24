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
    id_number = models.CharField(max_length=20)
    id_issued_date = models.DateField()
    id_issued_place = models.CharField(max_length=100, default="Cục trưởng cục cảnh sát QLHC về TTXH")

    # Trường THCS
    graduation_year = models.CharField(max_length=10)
    graduation_school = models.CharField(max_length=255)
    graduation_rank = models.CharField(max_length=50)
    exam_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(30)])
    conduct = models.CharField(max_length=50, null=True, blank=True)
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
    # Liên kết cơ sở - ca học - tổ hợp
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT)
    subject_group = models.ForeignKey(SubjectGroup, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

