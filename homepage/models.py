import os
from django.db import models
from django.contrib.auth.models import User
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
    def save(self, *args, **kwargs):
        if self.pk:  # Kiểm tra nếu file PDF đã tồn tại
            old_file = UploadedFile.objects.filter(pk=self.pk).first()
            if old_file and old_file.pdf_file != self.pdf_file:
                if old_file.pdf_file and os.path.isfile(old_file.pdf_file.path):
                    os.remove(old_file.pdf_file.path)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Xóa file PDF khi đối tượng bị xóa
        if self.pdf_file and os.path.isfile(self.pdf_file.path):
            os.remove(self.pdf_file.path)
        super().delete(*args, **kwargs)


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

