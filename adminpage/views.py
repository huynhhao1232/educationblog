import os
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from homepage.models import *
import json
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import Decimal, InvalidOperation
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from copy import copy as shallow_copy
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import calendar
from collections import defaultdict
from django.db import models as django_models
from adminpage.models import *
from adminpage.services import get_converted_periods_for_schedule

from django.contrib import messages
# Create your views here.

def natural_sort_key(text):
    """Hàm helper để sắp xếp tự nhiên (natural sort) cho tên lớp"""
    if not text:
        return (0, '')
    # Tách chuỗi thành các phần số và chữ
    def convert(text_part):
        return int(text_part) if text_part.isdigit() else text_part.lower()

    return [convert(c) for c in re.split(r'(\d+)', str(text))]


def adminpage(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            users = User.objects.all()
            context = {'users': users}
            return render(request, 'adminpageSIMCODE/user.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:Login')

def getCategory(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            if request.method == 'POST':
                action = int(request.POST.get('action'))
                category_name = request.POST.get('category_name')
                category_enable = int(request.POST.get('enableHidden'))
                category_id = request.POST.get('category_id', None)
                if category_enable == 1:
                    category_enable = True
                else:
                    category_enable = False
                if action == 0:
                    category = Category.objects.create(name = category_name, enable = category_enable)
                category.save()
                return redirect('adminpage:category')
            categories = Category.objects.all()
            context = {'categories': categories}
            return render(request, 'adminpageSIMCODE/category.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:Login')

def get_post_data(request, post_id):
    post = get_object_or_404(Post, id = post_id)
    uploadedfiles = UploadedFile.objects.filter(post = post)
    data = {'files': [{'name': f.pdf_file.name, 'url': f.pdf_file.url} for f in uploadedfiles],'id': post.id,'name': post.title,'image': post.image_file.url, 'enable': post.enable, 'content': post.content}
    return JsonResponse(data)

def getCategoryDetail(request, category_id):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            if request.method == 'POST':
                action = int(request.POST.get('action'))
                if action == 1:
                    category_name = request.POST.get('category_name')
                    category_enable = int(request.POST.get('enableHidden'))
                    category_id = request.POST.get('category_id', None)
                    if category_enable == 1:
                        category_enable = True
                    else:
                        category_enable = False
                    category = Category.objects.get(id = category_id)
                    category.name = category_name
                    category.enable = category_enable
                    category.save()
                elif action == 0:
                    chapter_name = request.POST.get('chapter_name')
                    content = request.POST.get('ckeditor1', None)
                    image = request.FILES.get('topic-image', None)
                    files = request.FILES.getlist('topic-files', None)
                    category = Category.objects.get(id = category_id)
                    post = Post.objects.create(title = chapter_name, content = content, image_file = image, category = category)
                    post.save()
                    for file in files:
                        f = UploadedFile.objects.create(post=post, pdf_file=file)
                        f.save()
                elif action == 2:
                    post_id = request.POST.get('post-id')
                    post = get_object_or_404(Post, id=post_id)
                    category_enable = int(request.POST.get('enableHidden'))
                    if category_enable == 1:
                        category_enable = True
                    else:
                        category_enable = False
                    post.title = request.POST.get('chapter_name', post.title)
                    post.content = request.POST.get('ckeditor1', post.content)
                    post.enable = category_enable

        # Upload ảnh mới
                    if 'image_file' in request.FILES:
                        post.image_file = request.FILES['topic-image']

        # Xóa các tệp PDF cũ và thêm tệp PDF mới
                    existing_files = request.POST.get('existing-files', '[]')
     # Chuyển từ JSON string sang list
                    try:
                        existing_files = json.loads(existing_files)
                    except json.JSONDecodeError:
                        existing_files = []

# Lấy các file mới từ input file
                    new_files = request.FILES.getlist('topic-files')

# Nếu có file mới, xóa các file cũ không còn được chọn
                    if new_files:
                        for uploaded_file in post.uploadedfile_set.all():
        # Nếu file cũ không có trong danh sách file hiện tại, xóa nó
                            if uploaded_file.pdf_file.name not in existing_files:
                                uploaded_file.delete()

    # Thêm file mới vào cơ sở dữ liệu
                        for new_file in new_files:
                            UploadedFile.objects.create(post=post, pdf_file=new_file)
                    else:
    # Nếu không có file mới, không làm gì với các file cũ
                        pass
                    post.save()
                elif action == 3:
                    post_id = request.POST.get('post-id')
                    post = get_object_or_404(Post, id=post_id)
                    # Xóa các file đính kèm trước để tránh lỗi ràng buộc khóa ngoại
                    UploadedFile.objects.filter(post=post).delete()
                    post.delete()



                return redirect('adminpage:categorydetail', category_id = category_id )
            category = Category.objects.get(id = category_id)
            posts = Post.objects.filter(category__id = category_id)
            context = {'category': category, 'posts':posts}
            return render(request, 'adminpageSIMCODE/categorydetail.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:Login')

def get_PB(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            if request.method == 'POST':
                action = int(request.POST.get('action'))
                category_name = request.POST.get('category_name')
                category_enable = int(request.POST.get('enableHidden'))
                category_id = request.POST.get('category_id', None)
                if category_enable == 1:
                    category_enable = True
                else:
                    category_enable = False
                if action == 0:
                    pb = PhongBan.objects.create(name = category_name, enable = category_enable)
                else:
                    pb = PhongBan.objects.get(id = category_id)
                    pb.name = category_name
                    pb.enable = category_enable
                pb.save()
                return redirect('adminpage:phongban')
            pbs = PhongBan.objects.all()
            context = {'pbs': pbs}
            return render(request, 'adminpageSIMCODE/phongban.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:Login')
def get_CCTC(request, pb_id):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            if request.method == 'POST':
                action = int(request.POST.get('action'))
                chapter_name = request.POST.get('chapter_name')
                role1 = request.POST.get('role1', None)
                role2 = request.POST.get('role2')
                chuyenmon = request.POST.get('chuyenmon', None)
                namsinh = request.POST.get('namsinh')
                sex = int(request.POST.get('sex'))
                bac = request.POST.get('bac')
                image_file = request.FILES.get('topic-image', None)
                enable = int(request.POST.get('enableHidden'))
                if enable == 1:
                    enable = True
                else:
                    enable = False
                if sex == 1:
                    sex = True
                else:
                    sex = False
                if action == 0:
                    gv = GV.objects.create(name = chapter_name, role1 = role1, role2 = role2, sex = sex, chuyenmon = chuyenmon, namsinh = namsinh, bac = bac, image_file = image_file, enable = enable)
                    gv.save()
                    phongban = PhongBan.objects.get(id = pb_id)
                    pb_gv = PB_GV.objects.create(phongban = phongban, gv = gv)
                    pb_gv.save()
                else:
                    gv_id = int(request.POST.get('post-id'))
                    gv = get_object_or_404(GV, id = gv_id)
                    gv.name = chapter_name
                    gv.role1 = role1
                    gv.role2 = role2
                    gv.chuyenmon = chuyenmon
                    gv.namsinh = namsinh
                    gv.sex = sex
                    gv.enable = enable
                    gv.bac = bac
                    if 'image_file' in request.FILES:
                        gv.image_file = request.FILES['topic-image']
                    gv.save()
                return redirect('adminpage:CCTC', pb_id = pb_id)
            gvs = PB_GV.objects.filter(phongban__id = pb_id)
            context = {'gvs': gvs}
            return render(request, 'adminpageSIMCODE/cctc.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:Login')
def get_Admission(request):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            # Get all admission records
            admission_list = AdmissionForm.objects.all()

            # Apply filters
            name_filter = request.GET.get('name', '')
            gender_filter = request.GET.get('gender', '')
            status_filter = request.GET.get('status', '')
            campus_filter = request.GET.get('campus', '')
            shift_filter = request.GET.get('shift', '')
            subject_group_filter = request.GET.get('subject_group', '')
            exam_score_order = request.GET.get('exam_score', '')
            avg_score_order = request.GET.get('avg_score', '')
            graduation_year_filter = request.GET.get('graduation_year', '')
            conduct_filter = request.GET.get('conduct', '')
            from_date_filter = request.GET.get('from_date', '')
            to_date_filter = request.GET.get('to_date', '')

            if name_filter:
                admission_list = admission_list.filter(full_name__icontains=name_filter)

            if gender_filter:
                admission_list = admission_list.filter(gender=gender_filter)

            if status_filter:
                status_bool = status_filter == '1'
                admission_list = admission_list.filter(enable=status_bool)

            if campus_filter:
                admission_list = admission_list.filter(campus_id=campus_filter)

            if shift_filter:
                admission_list = admission_list.filter(shift_id=shift_filter)

            if subject_group_filter:
                admission_list = admission_list.filter(subject_group_id=subject_group_filter)

            if exam_score_order:
                order_by = '-exam_score' if exam_score_order == 'desc' else 'exam_score'
                admission_list = admission_list.order_by(order_by)

            if avg_score_order:
                order_by = '-avg_score' if avg_score_order == 'desc' else 'avg_score'
                admission_list = admission_list.order_by(order_by)

            if graduation_year_filter:
                admission_list = admission_list.filter(graduation_year=graduation_year_filter)

            if conduct_filter:
                admission_list = admission_list.filter(conduct=conduct_filter)
            if from_date_filter:
                admission_list = admission_list.filter(created_at__date__gte=from_date_filter)
            if to_date_filter:
                admission_list = admission_list.filter(created_at__date__lte=to_date_filter)

            # Set up pagination
            paginator = Paginator(admission_list, 10)  # Show 10 records per page
            page = request.GET.get('page', 1)

            try:
                ad = paginator.page(page)
            except PageNotAnInteger:
                ad = paginator.page(1)
            except EmptyPage:
                ad = paginator.page(paginator.num_pages)

            # Get data for filter dropdowns
            from homepage.models import Campus, Shift, SubjectGroup
            campuses = Campus.objects.all()
            shifts = Shift.objects.all()
            subject_groups = SubjectGroup.objects.all()
            # Graduation years for dropdown
            graduation_years = AdmissionForm.objects.order_by('graduation_year').values_list('graduation_year', flat=True).distinct()

            # Lấy thông báo từ session nếu có
            conduct_update_result = request.session.pop('conduct_update_result', None)

            context = {
                'ad': ad,
                'new_users': admission_list.count(),
                # Pass filter values back to template
                'name_filter': name_filter,
                'graduation_year_filter': graduation_year_filter,
                'status_filter': status_filter,
                'campus_filter': campus_filter,
                'shift_filter': shift_filter,
                'subject_group_filter': subject_group_filter,
                'exam_score_order': exam_score_order,
                'avg_score_order': avg_score_order,
                # Pass data for filter dropdowns
                'campuses': campuses,
                'shifts': shifts,
                'subject_groups': subject_groups,
                'graduation_years': graduation_years,
                'conduct_filter': conduct_filter,
                'from_date_filter': from_date_filter,
                'to_date_filter': to_date_filter,
                'conduct_update_result': conduct_update_result,
            }
            return render(request, 'adminpageSIMCODE/admission.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:Login')
def get_Letter(request, admission_id):
    if request.user.is_authenticated:
        account = Account.objects.get(user = request.user)
        accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            # Get admission record
            admission = get_object_or_404(AdmissionForm, id=admission_id)

            if request.method == 'POST':
                action = request.POST.get('action', 'update')
                if action == 'delete':
                    admission.delete()
                    return redirect('adminpage:admission')
                try:
                    # Kiểm tra trạng thái trước khi cập nhật
                    old_status = admission.enable
                    new_status = request.POST.get('enable') == '1'

                    # Nếu đã duyệt rồi thì không cho phép thay đổi trạng thái
                    if old_status:
                        new_status = True

                    # Update admission record
                    admission.full_name = request.POST.get('full_name')
                    admission.gender = request.POST.get('gender')
                    admission.birthday = request.POST.get('birthday')
                    admission.ethnicity = request.POST.get('ethnicity')
                    admission.religion = request.POST.get('religion')
                    admission.email = request.POST.get('email')
                    admission.id_number = request.POST.get('id_number')
                    admission.id_issued_date = request.POST.get('id_issued_date')
                    admission.id_issued_place = request.POST.get('id_issued_place')

                    # Handle phone number
                    admission.phone = request.POST.get('phone')

                    # Handle CCCD image
                    cccd_image = request.FILES.get('cccd_image')
                    if cccd_image:
                        # Delete old image if exists
                        if admission.cccd_image:
                            try:
                                os.remove(os.path.join(settings.MEDIA_ROOT, str(admission.cccd_image)))
                            except:
                                pass
                        admission.cccd_image = cccd_image

                    # Handle School Record image
                    school_record_image = request.FILES.get('school_record_image')
                    if school_record_image:
                        # Delete old image if exists
                        if admission.school_record_image:
                            try:
                                os.remove(os.path.join(settings.MEDIA_ROOT, str(admission.school_record_image)))
                            except:
                                pass
                        admission.school_record_image = school_record_image

                    # Các trường địa chỉ
                    admission.cccd_province = request.POST.get('cccd_province')
                    admission.cccd_district = request.POST.get('cccd_district')
                    admission.cccd_ward = request.POST.get('cccd_ward')
                    admission.cccd_town = request.POST.get('cccd_town')

                    admission.hometown_province = request.POST.get('hometown_province')

                    admission.birth_reg_province = request.POST.get('birth_reg_province')
                    admission.birth_reg_district = request.POST.get('birth_reg_district')
                    admission.birth_reg_ward = request.POST.get('birth_reg_ward')
                    admission.birth_reg_town = request.POST.get('birth_reg_town')

                    admission.birth_place_province = request.POST.get('birth_place_province')
                    admission.birth_place_district = request.POST.get('birth_place_district')
                    admission.birth_place_ward = request.POST.get('birth_place_ward')
                    admission.birth_place_facility = request.POST.get('birth_place_facility')

                    admission.current_province = request.POST.get('current_province')
                    admission.current_district = request.POST.get('current_district')
                    admission.current_ward = request.POST.get('current_ward')

                    # Thông tin học vấn
                    admission.graduation_school = request.POST.get('graduation_school')
                    admission.graduation_rank = request.POST.get('graduation_rank')
                    admission.conduct = request.POST.get('conduct')
                    admission.current_job = request.POST.get('current_job')

                    # Thông tin phụ huynh
                    admission.father_name = request.POST.get('father_name')
                    admission.father_job = request.POST.get('father_job')
                    admission.father_birth = request.POST.get('father_birth')
                    admission.father_phone = request.POST.get('father_phone')

                    admission.mother_name = request.POST.get('mother_name')
                    admission.mother_job = request.POST.get('mother_job')
                    admission.mother_birth = request.POST.get('mother_birth')
                    admission.mother_phone = request.POST.get('mother_phone')

                    # Xử lý điểm dựa vào năm tốt nghiệp
                    graduation_year = request.POST.get('graduation_year')

                    # Process exam_score and avg_score - only update if field is present in form
                    if 'exam_score' in request.POST:  # Only update if field is present in form
                        exam_score_str = request.POST.get('exam_score')
                        try:
                            admission.exam_score = Decimal(exam_score_str.strip()) if exam_score_str and exam_score_str.strip() else None
                        except InvalidOperation:
                            admission.exam_score = None

                    if 'avg_score' in request.POST:  # Only update if field is present in form
                        avg_score_str = request.POST.get('avg_score')
                        try:
                            admission.avg_score = Decimal(avg_score_str.strip()) if avg_score_str and avg_score_str.strip() else None
                        except InvalidOperation:
                            admission.avg_score = None

                    # Handle math_score and literature_score (always applicable)
                    math_score_str = request.POST.get('math_score')
                    try:
                        admission.math_score = Decimal(math_score_str.strip()) if math_score_str and math_score_str.strip() else None
                    except InvalidOperation:
                        admission.math_score = None

                    literature_score_str = request.POST.get('literature_score')
                    try:
                        admission.literature_score = Decimal(literature_score_str.strip()) if literature_score_str and literature_score_str.strip() else None
                    except InvalidOperation:
                        admission.literature_score = None

                    # Handle THCS scores (lớp 6, 7, 8, 9)
                    # Lớp 6
                    math_score_6_str = request.POST.get('math_score_6')
                    try:
                        admission.math_score_6 = Decimal(math_score_6_str.strip()) if math_score_6_str and math_score_6_str.strip() else None
                    except InvalidOperation:
                        admission.math_score_6 = None

                    literature_score_6_str = request.POST.get('literature_score_6')
                    try:
                        admission.literature_score_6 = Decimal(literature_score_6_str.strip()) if literature_score_6_str and literature_score_6_str.strip() else None
                    except InvalidOperation:
                        admission.literature_score_6 = None

                    # Lớp 7
                    math_score_7_str = request.POST.get('math_score_7')
                    try:
                        admission.math_score_7 = Decimal(math_score_7_str.strip()) if math_score_7_str and math_score_7_str.strip() else None
                    except InvalidOperation:
                        admission.math_score_7 = None

                    literature_score_7_str = request.POST.get('literature_score_7')
                    try:
                        admission.literature_score_7 = Decimal(literature_score_7_str.strip()) if literature_score_7_str and literature_score_7_str.strip() else None
                    except InvalidOperation:
                        admission.literature_score_7 = None

                    # Lớp 8
                    math_score_8_str = request.POST.get('math_score_8')
                    try:
                        admission.math_score_8 = Decimal(math_score_8_str.strip()) if math_score_8_str and math_score_8_str.strip() else None
                    except InvalidOperation:
                        admission.math_score_8 = None

                    literature_score_8_str = request.POST.get('literature_score_8')
                    try:
                        admission.literature_score_8 = Decimal(literature_score_8_str.strip()) if literature_score_8_str and literature_score_8_str.strip() else None
                    except InvalidOperation:
                        admission.literature_score_8 = None

                    # Lớp 9
                    math_score_9_str = request.POST.get('math_score_9')
                    try:
                        admission.math_score_9 = Decimal(math_score_9_str.strip()) if math_score_9_str and math_score_9_str.strip() else None
                    except InvalidOperation:
                        admission.math_score_9 = None

                    literature_score_9_str = request.POST.get('literature_score_9')
                    try:
                        admission.literature_score_9 = Decimal(literature_score_9_str.strip()) if literature_score_9_str and literature_score_9_str.strip() else None
                    except InvalidOperation:
                        admission.literature_score_9 = None

                    # Cập nhật trạng thái
                    admission.enable = new_status

                    # Cập nhật ca học (shift)
                    shift_id = request.POST.get('shift')
                    if shift_id:
                        admission.shift_id = shift_id

                    # Lưu thay đổi
                    admission.save()

                    # Nếu trạng thái thay đổi từ chưa duyệt sang đã duyệt và có email
                    if not old_status and new_status and admission.email:
                        try:
                            # Chuẩn bị nội dung email
                            html_message = render_to_string('adminpageSIMCODE/email_template.html', {
                                'full_name': admission.full_name,
                                'graduation_year': admission.graduation_year,
                                'campus': admission.campus.name,
                                'shift': admission.shift.name,
                                'subject_group': admission.subject_group.code
                            })
                            plain_message = strip_tags(html_message)

                            # Gửi email
                            send_mail(
                                subject='Thông báo xét duyệt hồ sơ nhập học',
                                message=plain_message,
                                from_email=settings.EMAIL_HOST_USER,
                                recipient_list=[admission.email],
                                html_message=html_message,
                                fail_silently=False,
                            )
                        except Exception as e:
                            print(f"Error sending email: {e}")
                            # Continue with success response even if email fails

                    return JsonResponse({'status': 'success'})
                except Exception as e:
                    print(f"Error updating admission: {e}")
                    return JsonResponse({'status': 'error', 'message': str(e)})

            context = {
                'admission': admission,
                'subject_groups': SubjectGroup.objects.all(),
                'shifts': Shift.objects.all()
            }
            return render(request, 'adminpageSIMCODE/letter.html', context)
    return redirect('adminpage:login')
# def Phaser(request):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             if request.method == "POST":
#                 phaser_name = request.POST.get('phaser_name')
#                 phaser_type = request.POST.get('phaser_type')
#                 phaser_path = request.POST.get('phaser_path')
#                 phaser_content = request.POST.get('ckeditor1')
#                 if phaser_type == "1":
#                     imgRoot = os.path.join(settings.MEDIA_ROOT, 'game_pic/')
#                     imgUrl = os.path.join(settings.MEDIA_URL, 'game_pic/')
#                     gameUrl = os.path.join(settings.MEDIA_URL,'game/')
#                     imgRoot=imgRoot.replace("\\","/")
#                     fileimage = request.FILES['file-image']
#                     fss = FileSystemStorage(location=imgRoot)
#                     saveimg = fss.save(fileimage.name,fileimage)
#                     game= Game.objects.create(game_name = phaser_name, game_picture = imgUrl+saveimg,game_hyperlink=gameUrl+phaser_path,game_content = phaser_content)
#                     game.save()
#                     return redirect('Phaser')
#                 else:
#                     imgRoot = os.path.join(settings.MEDIA_ROOT, 'simulation_pic/')
#                     imgUrl = os.path.join(settings.MEDIA_URL, 'simulation_pic/')
#                     simUrl = os.path.join(settings.MEDIA_URL,'simulation/')
#                     imgRoot=imgRoot.replace("\\","/")
#                     fileimage = request.FILES['file-image']
#                     fss = FileSystemStorage(location=imgRoot)
#                     saveimg = fss.save(fileimage.name,fileimage)
#                     simulation= Simulation.objects.create(simulation_name = phaser_name, simulation_picture = imgUrl+saveimg,simulation_hyperlink=simUrl+phaser_path,simulation_content = phaser_content)
#                     simulation.save()
#                     return redirect('Phaser')

#             else:
#                 # courses = Course.objects.all()
#                 # grades = Grade.objects.all()
#                 # subjects = Subject.objects.all()
#                 # context = {'courses': courses, 'grades': grades, 'subjects': subjects}
#                 return render(request, 'adminpageSIMCODE/Phaser.html')
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')
# def course(request):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             if request.method == "POST":
#                 action = int(request.POST.get('action'))
#                 course_name = request.POST.get('course_name')
#                 grade_id = request.POST.get('grade')
#                 subject_id = request.POST.get('subject')
#                 course_desc = request.POST.get('ckeditor1')
#                 course_enable = request.POST.get('enableHidden')
#                 file = request.FILES.get('topic-file', None)
#                 grade = Grade.objects.get(grade_id = grade_id)
#                 subject = Subject.objects.get(subject_id = subject_id)
#                 print(action)
#                 if file is not None:
#                     folder_name = 'course_pic'
#                     fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_name))
#                     filename = fs.save(file.name, file)
#                     saved_file_path = os.path.join(settings.MEDIA_URL, folder_name, filename)
#                 else:
#                     saved_file_path = None
#                 if action == 0:
#                     if saved_file_path is not None:
#                         course = Course.objects.create(course_name = course_name, course_desc = course_desc, course_enable = course_enable, grade = grade, subject = subject, course_picture = saved_file_path)
#                         course.save()
#                     else:
#                         course = Course.objects.create(course_name = course_name, course_desc = course_desc, course_enable = course_enable, grade = grade, subject = subject)
#                         course.save()

#                 else:
#                     course_id = request.POST.get('courseHidden')
#                     course = Course.objects.get(course_id = course_id)
#                     if saved_file_path is not None:
#                         print('a')

#                         course.course_name = course_name
#                         course.course_desc = course_desc
#                         course.course_picture = saved_file_path
#                         course.course_enable = course_enable
#                         course.grade = grade
#                         course.subject = subject
#                     else:
#                         course.course_name = course_name
#                         course.course_desc = course_desc
#                         course.course_picture = saved_file_path
#                         course.course_enable = course_enable
#                         course.grade = grade
#                         course.subject = subject
#                     course.save()

#                 return redirect('course')
#             else:
#                 courses = Course.objects.all()
#                 grades = Grade.objects.all()
#                 subjects = Subject.objects.all()
#                 context = {'courses': courses, 'grades': grades, 'subjects': subjects}
#                 return render(request, 'adminpageSIMCODE/course.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')

# def activity(request, course_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             course = Course.objects.get(course_id = course_id)
#             if request.method == 'POST':
#                 course_name = request.POST.get('course_name', None)
#                 if course_name is not None:
#                     gradeUpdate = request.POST.get('gradeUpdate')
#                     subjectUpdate = request.POST.get('subjectUpdate')
#                     enableHidden = int(request.POST.get('enableHidden'))

#                     grade = Grade.objects.get(grade_id = gradeUpdate)
#                     subject = Subject.objects.get(subject_id = subjectUpdate)
#                     course.course_name = course_name
#                     course.grade = grade
#                     course.subject = subject
#                     course.course_enable = (True if enableHidden == 1 else False)
#                     course.save()
#                 else:
#                     activity_name = request.POST.get('activityName')
#                     activity_order = request.POST.get('activityOrder')
#                     activity_type = request.POST.get('activityType')
#                     activityType = ActivityType.objects.get(activitytype_id = activity_type)
#                     activity = Activity.objects.create(activity_name = activity_name, activity_order = activity_order,  activity_enable = False, activitytype = activityType, course = course)
#                     activity.save()

#                 return redirect('activity', course_id=course_id)

#             else:
#                 grades = Grade.objects.all()
#                 subjects = Subject.objects.all()
#                 types = ActivityType.objects.all()
#                 activities = Activity.objects.filter(course = course)
#                 context = {'course': course, 'activities': activities, 'grades': grades, 'subjects': subjects, 'types': types}
#                 return render(request, 'adminpageSIMCODE/activity.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     else:
#         return redirect('homepage:Register')

# def activitydetail(request, activity_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':

#             activity = Activity.objects.get(activity_id = activity_id)
#             if request.method == "POST":
#                 activity_name = request.POST.get('activityName', None)

#                 if activity_name is not None:
#                     activity_order = request.POST.get('activityOrder')
#                     activity_type = request.POST.get('activityType')
#                     enableHidden = int(request.POST.get('enableHidden'))
#                     activityType = ActivityType.objects.get(activitytype_id = activity_type)
#                     activity.activity_name = activity_name
#                     activity.activity_order = activity_order
#                     activity.activitytype = activityType
#                     activity.activity_enable = (True if enableHidden == 1 else False)
#                     activity.save()
#                 else:
#                     name = request.POST.get('Name')
#                     text = request.POST.get('ckeditor1')
#                     id = request.POST.get('dataHidden', None)
#                     link = request.POST.get('link')
#                     if id is '':

#                         if activity.activitytype.activitytype_id == 1:
#                             order = request.POST.get('order')
#                             theoryUrl = os.path.join(settings.MEDIA_URL,'theory/')
#                             theory = Theory.objects.create(theory_name = name, theory_hyperlink = theoryUrl + link,  theory_order = order, activity = activity)
#                             theory.save()
#                         else:

#                             file = request.FILES.get('topic-file')
#                             folder_name = 'activity_pic'
#                             fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_name))
#                             filename = fs.save(file.name, file)
#                             saved_file_path = os.path.join(settings.MEDIA_URL, folder_name, filename)

#                             if activity.activitytype.activitytype_id == 2:
#                                 gameUrl = os.path.join(settings.MEDIA_URL,'game/')
#                                 game = Game.objects.create(game_name = name, game_content = text, game_picture = saved_file_path, game_hyperlink = gameUrl + link, activity = activity)
#                                 game.save()
#                             elif activity.activitytype.activitytype_id == 3:
#                                 simUrl = os.path.join(settings.MEDIA_URL,'simulation/')
#                                 simulation = Simulation.objects.create(simulation_name = name, simulation_content = text, simulation_picture = saved_file_path, simulation_hyperlink = simUrl + link, activity = activity)
#                                 simulation.save()

#                     else:
#                         enableHidden = int(request.POST.get('enableHidden'))
#                         if activity.activitytype.activitytype_id == 1:
#                             order = request.POST.get('order')
#                             theoryUrl = os.path.join(settings.MEDIA_URL,'theory/')
#                             theory = Theory.objects.get(theory_id = id)
#                             theory.theory_name = name
#                             theory.theory_hyperlink = theoryUrl + link
#                             theory.theory_order = order
#                             theory.theory_enable = enableHidden
#                             theory.save()
#                         else:
#                             # link = request.POST.get('link')
#                             file = request.FILES.get('topic-file', None)
#                             if file is not None:
#                                 folder_name = 'activity_pic'
#                                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_name))
#                                 filename = fs.save(file.name, file)
#                                 saved_file_path = os.path.join(settings.MEDIA_URL, folder_name, filename)
#                             else:
#                                 saved_file_path = None
#                             if activity.activitytype.activitytype_id == 2:
#                                 gameUrl = os.path.join(settings.MEDIA_URL,'game/')
#                                 game = Game.objects.get(game_id = id)
#                                 game.game_name = name
#                                 game.game_content = text
#                                 game.game_hyperlink = gameUrl + link
#                                 game.game_enable = enableHidden
#                                 if saved_file_path != game.game_picture and saved_file_path is not None:
#                                     game.game_picture = saved_file_path
#                                 game.save()
#                             elif activity.activitytype.activitytype_id == 3:
#                                 simUrl = os.path.join(settings.MEDIA_URL,'simulation/')
#                                 simulation = Simulation.objects.get(simulation_id = id)
#                                 simulation.simulation_name = name
#                                 simulation.simulation_content = text
#                                 simulation.simulation_hyperlink = simUrl + link
#                                 simulation.simulation_enable = enableHidden
#                                 if saved_file_path != simulation.simulation_picture and saved_file_path is not None:
#                                     simulation.simulation_picture = saved_file_path
#                                 simulation.save()


#                 return redirect('activitydetail', activity_id=activity_id)

#             else:
#                 types = ActivityType.objects.all()
#                 if activity.activitytype.activitytype_id == 1:
#                     ts = Theory.objects.filter(activity = activity).order_by('theory_order')
#                 elif activity.activitytype.activitytype_id == 2:
#                     ts = Game.objects.filter(activity = activity)
#                 elif activity.activitytype.activitytype_id == 3:
#                     ts = Simulation.objects.filter(activity = activity)
#                 context = {'activity':activity,  'types': types, 'ts': ts}
#                 return render(request, 'adminpageSIMCODE/activitydetail.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     else:
#         return redirect('homepage:Register')



# # def coursedetail(request, course_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             course = Course.objects.get(course_id = course_id)
#             if request.method == 'POST':
#                 chapter_name = request.POST.get('chapter_name', None)
#                 if chapter_name is not None:
#                     chapter_order = request.POST.get('chapterOrder')
#                     chapter = Chapter.objects.create(chapter_name = chapter_name, chapter_order = chapter_order, chapter_enable=False, course = course)
#                     chapter.save()
#                     return redirect('coursedetail', course_id=course.course_id)
#                 else:
#                     courseNameUpdate = request.POST.get('course_name')
#                     gradeUpdate = request.POST.get('gradeUpdate')
#                     subjectUpdate = request.POST.get('subjectUpdate')
#                     enableHidden = int(request.POST.get('enableHidden'))
#                     if(enableHidden == 0):
#                         course.course_name = courseNameUpdate
#                         grade = Grade.objects.get(grade_id = gradeUpdate)
#                         subject = Subject.objects.get(subject_id = subjectUpdate)
#                         course.grade = grade
#                         course.subject = subject
#                         course.course_enable = False

#                     else:
#                         course.course_name = courseNameUpdate
#                         grade = Grade.objects.get(grade_id = gradeUpdate)
#                         subject = Subject.objects.get(subject_id = subjectUpdate)
#                         course.grade = grade
#                         course.subject = subject
#                         course.course_enable = True
#                     course.save()
#                     return redirect('coursedetail', course_id=course.course_id)
#             else:
#                 course = Course.objects.get(course_id = course_id)
#                 chapters = course.chapter_set.all().order_by('chapter_order')
#                 grades = Grade.objects.all()
#                 subjects = Subject.objects.all()
#                 context = {'course': course, 'chapters':chapters, 'grades': grades, 'subjects':subjects}
#                 return render(request, 'adminpageSIMCODE/coursedetail.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')

# def chapterdetail(request, chapter_id, course_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             chapter = Chapter.objects.get(chapter_id = chapter_id)
#             course = Course.objects.get(course_id = course_id)
#             if request.method == "POST":
#                 chapter_name = request.POST.get('chapterName', None)
#                 if chapter_name is not None:
#                     chapter_order = request.POST.get('chapterOrder')
#                     chapter_enable = request.POST.get('enableHidden')
#                     chapter.chapter_name = chapter_name
#                     chapter.chapter_order = chapter_order
#                     chapter.chapter_enable = chapter_enable
#                     chapter.save()
#                     return redirect('chapterdetail', chapter_id=chapter_id, course_id=course_id)
#                 else:
#                     lesson_name = request.POST.get('lessonName')
#                     lesson_order = request.POST.get('lessonOrder')
#                     lesson = Lesson.objects.create(lesson_name = lesson_name, lesson_order = lesson_order, lesson_enable = False, chapter = chapter)
#                     lesson.save()
#                     return redirect('chapterdetail', chapter_id=chapter_id, course_id=course_id)
#             else:
#                 lessons = chapter.lesson_set.all().order_by('lesson_order')
#                 context = {'chapter' : chapter, 'course':course, 'lessons': lessons}
#                 return render(request, 'adminpageSIMCODE/chapterdetail.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')

# # def lessondetail(request, chapter_id, lesson_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             chapter = Chapter.objects.get(chapter_id = chapter_id)
#             lesson = Lesson.objects.get(lesson_id = lesson_id)
#             types = ActivityType.objects.all()
#             if request.method == "POST":
#                 lesson_name = request.POST.get('lessonName', None)
#                 if lesson_name is not None:
#                     lesson_order = request.POST.get('lessonOrder')
#                     lesson_enable = request.POST.get('enableHidden')
#                     lesson.lesson_name = lesson_name
#                     lesson.lesson_order = lesson_order
#                     lesson.lesson_enable = lesson_enable
#                     lesson.save()
#                     return redirect('lessondetail', chapter_id=chapter_id, lesson_id=lesson_id)
#                 else:
#                     activity_name = request.POST.get('activityName')
#                     activity_order = request.POST.get('activityOrder')
#                     activity_type = request.POST.get('activityType')
#                     activity_desc = request.POST.get('ckeditor1')
#                     activityType = ActivityType.objects.get(activitytype_id = activity_type)
#                     activity = Activity.objects.create(activity_name = activity_name, activity_order = activity_order, activity_content = activity_desc, activity_enable = False, activitytype = activityType, lesson = lesson)
#                     activity.save()
#                     return redirect('lessondetail', chapter_id=chapter_id, lesson_id=lesson_id)
#             else:
#                 activities = lesson.activity_set.all().order_by('activity_order')
#                 context = {'chapter': chapter, 'lesson': lesson, 'activities': activities, 'types': types}
#                 return render(request, 'adminpageSIMCODE/lessondetail.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')

# def posttype(request):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             posttypes = PostType.objects.all()
#             if request.method == 'POST':
#                 posttype_name = request.POST.get('posttype_name')
#                 posttype = PostType.objects.create(posttype_name = posttype_name)
#                 posttype.save()
#                 return redirect('posttype')
#             else:
#                 context = {'posttypes': posttypes}
#                 return render(request, 'adminpageSIMCODE/posttype.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')


# def forumpost(request, posttype_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             posttype = PostType.objects.get(posttype_id = posttype_id)
#             posts = Post.objects.filter(posttype = posttype)
#             if request.method == 'POST':
#                 pass
#             else:
#                 context = {'posttype': posttype, 'posts': posts}
#                 return render(request, 'adminpageSIMCODE/forumpost.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')

# def forumanswer(request, post_id):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user = request.user)
#         accounttype = AccountType.objects.get(accounttype_id = account.accounttype.accounttype_id)
#         if accounttype.accounttype_role == 'admin':
#             post = Post.objects.get(post_id = post_id)
#             comments = Comment.objects.filter(post = post, comment_parent = None)
#             if request.method == 'POST':
#                 pass
#             else:
#                 context = {'post': post, 'comments': comments}
#                 return render(request, 'adminpageSIMCODE/forumanswer.html', context)
#         else:
#             return redirect('homepage:Homepage')
#     return redirect('homepage:Register')

def upload_image(request):
    if request.method == 'POST':

        file = request.FILES.get('upload')
        # Lưu tệp vào thư mục media
        folder_name = 'theory_pic'
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, folder_name))
        filename = fs.save(file.name, file)
        saved_file_path = os.path.join(settings.MEDIA_URL, folder_name, filename)
        print(saved_file_path)
        # Trả về đường dẫn tới tệp đã tải lên
        return JsonResponse({
  "uploaded": 1,
  "url":saved_file_path
})
    return JsonResponse({'error': 'Invalid request'})

def load_vn_address_data():
    try:
        data_path = os.path.join(settings.BASE_DIR, 'adminpage', 'static', 'data.json')
        with open(data_path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading VN address data: {e}")
        return []

VN_ADDRESS_DATA = load_vn_address_data()

def get_province_name(code):
    try:
        if not code or code == 'None' or code == '':
            return ''
        for province in VN_ADDRESS_DATA:
            if province.get('Id') == code:
                return province.get('Name', code)
        return code
    except Exception as e:
        print(f"Error in get_province_name: {e}")
        return code if code else ''

def get_district_name(province_code, district_code):
    try:
        if not province_code or province_code == 'None' or province_code == '' or not district_code or district_code == 'None' or district_code == '':
            return ''
        for province in VN_ADDRESS_DATA:
            if province.get('Id') == province_code:
                for district in province.get('Districts', []):
                    if district.get('Id') == district_code:
                        return district.get('Name', district_code)
        return district_code
    except Exception as e:
        print(f"Error in get_district_name: {e}")
        return district_code if district_code else ''

def get_ward_name(province_code, district_code, ward_code):
    try:
        if not province_code or province_code == 'None' or province_code == '' or not district_code or district_code == 'None' or district_code == '' or not ward_code or ward_code == 'None' or ward_code == '':
            return ''
        for province in VN_ADDRESS_DATA:
            if province.get('Id') == province_code:
                for district in province.get('Districts', []):
                    if district.get('Id') == district_code:
                        for ward in district.get('Wards', []):
                            if ward.get('Id') == ward_code:
                                return ward.get('Name', ward_code)
        return ward_code
    except Exception as e:
        print(f"Error in get_ward_name: {e}")
        return ward_code if ward_code else ''

def export_approved_admissions(request):
    """Export approved admissions to Excel file."""
    if not request.user.is_authenticated:
        return redirect('login')

    account = Account.objects.get(user=request.user)
    accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
    if accounttype.accounttype_role != 'admin':
        return redirect('homepage:Homepage')

    # Get all admissions (not just approved ones, apply filters)
    admissions = AdmissionForm.objects.all()

    # Apply filters from GET parameters
    name_filter = request.GET.get('name', '')
    gender_filter = request.GET.get('gender', '')
    status_filter = request.GET.get('status', '')
    campus_filter = request.GET.get('campus', '')
    shift_filter = request.GET.get('shift', '')
    subject_group_filter = request.GET.get('subject_group', '')
    exam_score_order = request.GET.get('exam_score', '')
    avg_score_order = request.GET.get('avg_score', '')
    graduation_year_filter = request.GET.get('graduation_year', '')
    conduct_filter = request.GET.get('conduct', '')
    from_date_filter = request.GET.get('from_date', '')
    to_date_filter = request.GET.get('to_date', '')

    if name_filter:
        admissions = admissions.filter(full_name__icontains=name_filter)

    if gender_filter:
        admissions = admissions.filter(gender=gender_filter)

    if status_filter:
        status_bool = status_filter == '1'
        admissions = admissions.filter(enable=status_bool)

    if campus_filter:
        admissions = admissions.filter(campus_id=campus_filter)

    if shift_filter:
        admissions = admissions.filter(shift_id=shift_filter)

    if subject_group_filter:
        admissions = admissions.filter(subject_group_id=subject_group_filter)

    if exam_score_order:
        order_by = '-exam_score' if exam_score_order == 'desc' else 'exam_score'
        admissions = admissions.order_by(order_by)

    if avg_score_order:
        order_by = '-avg_score' if avg_score_order == 'desc' else 'avg_score'
        admissions = admissions.order_by(order_by)

    if graduation_year_filter:
        admissions = admissions.filter(graduation_year=graduation_year_filter)

    if conduct_filter:
        admissions = admissions.filter(conduct=conduct_filter)
    if from_date_filter:
        admissions = admissions.filter(created_at__date__gte=from_date_filter)
    if to_date_filter:
        admissions = admissions.filter(created_at__date__lte=to_date_filter)

    # Create a new workbook and select the active sheet
    wb = Workbook()
    ws = wb.active

    # Set title based on filters
    title = "Danh sách học sinh"
    if status_filter == '1':
        title += " đã duyệt"
    elif status_filter == '0':
        title += " chưa duyệt"
    else:
        title += " (tất cả)"

    ws.title = title

    # Define headers
    headers = [
        'Họ và tên', 'Giới tính', 'Ngày sinh', 'Dân tộc', 'Tôn giáo',
        'Email', 'CCCD/CMND', 'Ngày cấp', 'Nơi cấp',
        'Địa chỉ thường trú', 'Quê quán',
        'Nơi đăng ký khai sinh', 'Nơi sinh', 'Nơi ở hiện tại',
        'Họ tên cha', 'Nghề nghiệp cha', 'Năm sinh cha', 'SĐT cha',
        'Họ tên mẹ', 'Nghề nghiệp mẹ', 'Năm sinh mẹ', 'SĐT mẹ',
        'Trường đang học', 'Công việc hiện tại',
        'Điểm thi chuyển cấp', 'Điểm TB Toán, Văn',
        'Điểm Toán lớp 6', 'Điểm Văn lớp 6',
        'Điểm Toán lớp 7', 'Điểm Văn lớp 7',
        'Điểm Toán lớp 8', 'Điểm Văn lớp 8',
        'Điểm Toán lớp 9', 'Điểm Văn lớp 9',
        'Hạnh kiểm', 'Học lực', 'Năm tốt nghiệp',
        'Ban đăng ký', 'Ca học', 'Cơ sở'
    ]

    # Style the header row
    header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
    header_font = Font(bold=True)

    # Write headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Write data
    for row, admission in enumerate(admissions, 2):
        data = [
            admission.full_name,
            admission.gender,
            admission.birthday.strftime('%d/%m/%Y') if admission.birthday else '',
            admission.ethnicity,
            admission.religion,
            admission.email,
            admission.id_number,
            admission.id_issued_date.strftime('%d/%m/%Y') if admission.id_issued_date else '',
            admission.id_issued_place,
            # Địa chỉ thường trú
            f"{admission.cccd_town or ''}, "
            f"{get_ward_name(str(admission.cccd_province) if admission.cccd_province else '', str(admission.cccd_district) if admission.cccd_district else '', str(admission.cccd_ward) if admission.cccd_ward else '')}, "
            f"{get_district_name(str(admission.cccd_province) if admission.cccd_province else '', str(admission.cccd_district) if admission.cccd_district else '')}, "
            f"{get_province_name(str(admission.cccd_province) if admission.cccd_province else '')}",
            # Quê quán
            get_province_name(str(admission.hometown_province) if admission.hometown_province else ''),
            # Nơi đăng ký khai sinh
            f"{admission.birth_reg_town or ''}, "
            f"{get_ward_name(str(admission.birth_reg_province) if admission.birth_reg_province else '', str(admission.birth_reg_district) if admission.birth_reg_district else '', str(admission.birth_reg_ward) if admission.birth_reg_ward else '')}, "
            f"{get_district_name(str(admission.birth_reg_province) if admission.birth_reg_province else '', str(admission.birth_reg_district) if admission.birth_reg_district else '')}, "
            f"{get_province_name(str(admission.birth_reg_province) if admission.birth_reg_province else '')}",
            # Nơi sinh
            f"{admission.birth_place_facility or ''}, "
            f"{get_ward_name(str(admission.birth_place_province) if admission.birth_place_province else '', str(admission.birth_place_district) if admission.birth_place_district else '', str(admission.birth_place_ward) if admission.birth_place_ward else '')}, "
            f"{get_district_name(str(admission.birth_place_province) if admission.birth_place_province else '', str(admission.birth_place_district) if admission.birth_place_district else '')}, "
            f"{get_province_name(str(admission.birth_place_province) if admission.birth_place_province else '')}",
            # Nơi ở hiện tại
            f"{get_ward_name(str(admission.current_province) if admission.current_province else '', str(admission.current_district) if admission.current_district else '', str(admission.current_ward) if admission.current_ward else '')}, "
            f"{get_district_name(str(admission.current_province) if admission.current_province else '', str(admission.current_district) if admission.current_district else '')}, "
            f"{get_province_name(str(admission.current_province) if admission.current_province else '')}",
            # Thông tin cha
            admission.father_name,
            admission.father_job,
            admission.father_birth,
            admission.father_phone,
            # Thông tin mẹ
            admission.mother_name,
            admission.mother_job,
            admission.mother_birth,
            admission.mother_phone,
            # Thông tin học vấn
            admission.graduation_school,
            admission.current_job,
            str(admission.exam_score) if admission.exam_score else '',
            str(admission.avg_score) if admission.avg_score else '',
            str(admission.math_score_6) if admission.math_score_6 else '',
            str(admission.literature_score_6) if admission.literature_score_6 else '',
            str(admission.math_score_7) if admission.math_score_7 else '',
            str(admission.literature_score_7) if admission.literature_score_7 else '',
            str(admission.math_score_8) if admission.math_score_8 else '',
            str(admission.literature_score_8) if admission.literature_score_8 else '',
            str(admission.math_score_9) if admission.math_score_9 else '',
            str(admission.literature_score_9) if admission.literature_score_9 else '',
            admission.conduct,
            admission.graduation_rank,
            admission.graduation_year,
            admission.subject_group.code if admission.subject_group else '',
            admission.shift.name if admission.shift else '',
            admission.campus.name if admission.campus else ''  # Chỉ lấy tên của campus
        ]

        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column = list(column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = min(adjusted_width, 30)

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=danh_sach_hoc_sinh_{datetime.now().strftime("%d%m%Y")}.xlsx'

    # Save the workbook to the response
    wb.save(response)
    return response

def delete_admission(request, admission_id):
    if request.method == 'POST' and request.user.is_authenticated:
        admission = get_object_or_404(AdmissionForm, id=admission_id)
        admission.delete()
        return redirect('adminpage:admission')
    return redirect('adminpage:admission')

@csrf_exempt
def import_cccd_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        wb = load_workbook(excel_file, read_only=True)
        ws = wb.active
        cccd_col = None
        start_row = None
        # Tìm dòng tiêu đề chứa 'số CCCD' (không phân biệt hoa thường)
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            for j, cell in enumerate(row):
                if cell and str(cell).strip().lower() in ['số cccd', 'so cccd', 'cccd', 'h2 (số cccd)']:
                    cccd_col = j
                    start_row = i + 1
                    break
            if cccd_col is not None:
                break
        if cccd_col is None:
            return render(request, 'adminpageSIMCODE/admission.html', {'import_result': 'Không tìm thấy cột Số CCCD trong file Excel.'})
        # Lấy danh sách số CCCD từ dòng start_row đến hết
        cccd_list = []
        for row in ws.iter_rows(min_row=start_row, values_only=True):
            cccd = row[cccd_col]
            if cccd:
                cccd_list.append(str(cccd).strip())
        # Duyệt học viên và gửi email
        from homepage.models import AdmissionForm
        approved_count = 0
        email_count = 0
        for cccd in cccd_list:
            qs = AdmissionForm.objects.filter(id_number=cccd, enable=False)
            for admission in qs:
                admission.enable = True
                admission.save()
                approved_count += 1
                if admission.email:
                    try:
                        html_message = render_to_string('adminpageSIMCODE/email_template.html', {
                            'full_name': admission.full_name,
                            'graduation_year': admission.graduation_year,
                            'campus': admission.campus.name,
                            'shift': admission.shift.name,
                            'subject_group': admission.subject_group.code
                        })
                        plain_message = strip_tags(html_message)
                        send_mail(
                            subject='Thông báo xét duyệt hồ sơ nhập học',
                            message=plain_message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[admission.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        email_count += 1
                    except Exception as e:
                        print(f"Error sending email to {admission.email}: {e}")
        result_msg = f'Đã duyệt {approved_count} học viên theo danh sách CCCD. Đã gửi email cho {email_count} học viên.'
        return render(request, 'adminpageSIMCODE/admission.html', {'import_result': result_msg})
    return render(request, 'adminpageSIMCODE/admission.html', {'import_result': 'Vui lòng chọn file Excel hợp lệ.'})

@csrf_exempt
def delete_cccd_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        wb = load_workbook(excel_file, read_only=True)
        ws = wb.active
        cccd_col = None
        start_row = None
        # Tìm dòng tiêu đề chứa 'số CCCD' (không phân biệt hoa thường)
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            for j, cell in enumerate(row):
                if cell and str(cell).strip().lower() in ['số cccd', 'so cccd', 'cccd', 'h2 (số cccd)']:
                    cccd_col = j
                    start_row = i + 1
                    break
            if cccd_col is not None:
                break
        if cccd_col is None:
            return render(request, 'adminpageSIMCODE/admission.html', {'delete_result': 'Không tìm thấy cột Số CCCD trong file Excel.'})
        # Lấy danh sách số CCCD từ dòng start_row đến hết
        cccd_list = []
        for row in ws.iter_rows(min_row=start_row, values_only=True):
            cccd = row[cccd_col]
            if cccd:
                cccd_list.append(str(cccd).strip())
        # Xoá học viên
        from homepage.models import AdmissionForm
        deleted_count, _ = AdmissionForm.objects.filter(id_number__in=cccd_list).delete()
        result_msg = f'Đã xoá {deleted_count} biểu mẫu theo danh sách CCCD.'
        return render(request, 'adminpageSIMCODE/admission.html', {'delete_result': result_msg})
    return render(request, 'adminpageSIMCODE/admission.html', {'delete_result': 'Vui lòng chọn file Excel hợp lệ.'})

def export_cccd_for_delete(request):
    from homepage.models import AdmissionForm
    admissions = AdmissionForm.objects.filter(enable=False)
    wb = Workbook()
    ws = wb.active
    ws.title = "CCCD Chua Duyet"
    ws.append(["Số CCCD"])
    for admission in admissions:
        ws.append([admission.id_number])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=cccd_chua_duyet.xlsx'
    wb.save(response)
    return response

@csrf_exempt
def update_conduct_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        wb = load_workbook(excel_file, read_only=True)
        ws = wb.active

        cccd_col = None
        conduct_col = None
        start_row = None

        # Tìm dòng tiêu đề chứa 'số CCCD' và 'hạnh kiểm'
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            for j, cell in enumerate(row):
                if cell:
                    cell_str = str(cell).strip().lower()
                    if cell_str in ['số cccd', 'so cccd', 'cccd', 'h2 (số cccd)']:
                        cccd_col = j
                    elif cell_str in ['hạnh kiểm', 'hanh kiem', 'conduct', 'hạnh kiểm thpt']:
                        conduct_col = j
            if cccd_col is not None and conduct_col is not None:
                start_row = i + 1
                break

        if cccd_col is None:
            return redirect('adminpage:admission')

        if conduct_col is None:
            return redirect('adminpage:admission')

        # Lấy danh sách CCCD và hạnh kiểm từ dòng start_row đến hết
        update_data = []
        for row in ws.iter_rows(min_row=start_row, values_only=True):
            cccd = row[cccd_col]
            conduct = row[conduct_col]
            if cccd and conduct:
                update_data.append({
                    'cccd': str(cccd).strip(),
                    'conduct': str(conduct).strip()
                })

        # Cập nhật hạnh kiểm cho học viên
        from homepage.models import AdmissionForm
        updated_count = 0
        not_found_count = 0
        invalid_conduct_count = 0

        valid_conduct_values = ['Tốt', 'Khá', 'Trung bình', 'Yếu']

        for data in update_data:
            cccd = data['cccd']
            conduct = data['conduct']

            # Kiểm tra hạnh kiểm có hợp lệ không
            if conduct not in valid_conduct_values:
                invalid_conduct_count += 1
                continue

            # Tìm học viên theo CCCD
            try:
                admission = AdmissionForm.objects.get(id_number=cccd)
                admission.conduct = conduct
                admission.save()
                updated_count += 1
            except AdmissionForm.DoesNotExist:
                not_found_count += 1

        # Tạo thông báo kết quả
        result_msg = f'Đã cập nhật hạnh kiểm cho {updated_count} học viên.'
        if not_found_count > 0:
            result_msg += f' Không tìm thấy {not_found_count} học viên.'
        if invalid_conduct_count > 0:
            result_msg += f' {invalid_conduct_count} giá trị hạnh kiểm không hợp lệ.'

        # Lưu kết quả vào session để hiển thị
        request.session['conduct_update_result'] = result_msg
        return redirect('adminpage:admission')

    return redirect('adminpage:admission')

def export_conduct_template(request):
    """Export template Excel cho việc cập nhật hạnh kiểm"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Template Cập nhật Hạnh kiểm"

    # Thêm tiêu đề
    ws.append(["Số CCCD", "Hạnh kiểm"])
    ws.append(["123456789012", "Tốt"])
    ws.append(["987654321098", "Khá"])
    ws.append(["111222333444", "Trung bình"])

    # Định dạng tiêu đề
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill

    # Điều chỉnh độ rộng cột
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 12

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=template_cap_nhat_hanh_kiem.xlsx'
    wb.save(response)
    return response

def get_ExamRegistration(request):
    """Quản lý đăng ký thi tốt nghiệp của học viên"""
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            # Lấy tất cả đăng ký
            registration_list = StudentExamRegistration.objects.select_related('student', 'student__campus', 'student__subject_group').all()

            # Áp dụng các bộ lọc
            student_code_filter = request.GET.get('student_code', '')
            student_name_filter = request.GET.get('student_name', '')
            campus_filter = request.GET.get('campus', '')
            subject_group_filter = request.GET.get('subject_group', '')
            email_filter = request.GET.get('email', '')
            phone_filter = request.GET.get('phone', '')
            class_name_filter = request.GET.get('class_name', '')
            exam_subjects_filter = request.GET.get('exam_subjects', '')  # 'yes' hoặc 'no'

            if student_code_filter:
                registration_list = registration_list.filter(student__student_code__icontains=student_code_filter)

            if student_name_filter:
                registration_list = registration_list.filter(student__full_name__icontains=student_name_filter)

            if campus_filter:
                registration_list = registration_list.filter(student__campus_id=campus_filter)

            if subject_group_filter:
                registration_list = registration_list.filter(student__subject_group_id=subject_group_filter)

            if class_name_filter:
                registration_list = registration_list.filter(student__class_name__icontains=class_name_filter)

            if email_filter:
                registration_list = registration_list.filter(email__icontains=email_filter)

            if phone_filter:
                registration_list = registration_list.filter(phone__icontains=phone_filter)

            # Lọc theo trạng thái đã/chưa chọn môn thi
            # Với JSONField, cần xử lý đặc biệt
            if exam_subjects_filter == 'yes':
                # Đã chọn môn thi (exam_subjects không rỗng)
                # Lọc trong Python sau khi query để xử lý JSONField
                registration_ids = []
                for reg in registration_list:
                    if reg.exam_subjects and len(reg.exam_subjects) > 0:
                        registration_ids.append(reg.id)
                if registration_ids:
                    registration_list = registration_list.filter(id__in=registration_ids)
                else:
                    registration_list = registration_list.none()  # Không có kết quả
            elif exam_subjects_filter == 'no':
                # Chưa chọn môn thi (exam_subjects rỗng hoặc None)
                # Lọc trong Python sau khi query
                registration_ids = []
                for reg in registration_list:
                    if not reg.exam_subjects or len(reg.exam_subjects) == 0:
                        registration_ids.append(reg.id)
                if registration_ids:
                    registration_list = registration_list.filter(id__in=registration_ids)
                else:
                    registration_list = registration_list.none()  # Không có kết quả

            # Sắp xếp theo tên lớp tăng dần (natural sort), sau đó theo ngày đăng ký mới nhất
            # Chuyển QuerySet thành list để sắp xếp tự nhiên
            registration_list = list(registration_list)
            # Sắp xếp tự nhiên theo tên lớp, sau đó theo ngày đăng ký
            registration_list.sort(key=lambda x: (
                natural_sort_key(x.student.class_name if x.student.class_name else ''),
                -(x.created_at.timestamp() if x.created_at else 0)
            ))

            # Phân trang
            paginator = Paginator(registration_list, 15)  # Hiển thị 15 bản ghi mỗi trang
            page = request.GET.get('page', 1)

            try:
                registrations = paginator.page(page)
            except PageNotAnInteger:
                registrations = paginator.page(1)
            except EmptyPage:
                registrations = paginator.page(paginator.num_pages)

            # Lấy dữ liệu cho dropdown filters
            campuses = Campus.objects.all()
            subject_groups = SubjectGroup.objects.all()

            # Thống kê
            total_registrations = StudentExamRegistration.objects.count()
            today_registrations = StudentExamRegistration.objects.filter(created_at__date=timezone.now().date()).count()

            context = {
                'registrations': registrations,
                'total_registrations': total_registrations,
                'today_registrations': today_registrations,
                # Filter values
                'student_code_filter': student_code_filter,
                'student_name_filter': student_name_filter,
                'campus_filter': campus_filter,
                'subject_group_filter': subject_group_filter,
                'class_name_filter': class_name_filter,
                'exam_subjects_filter': exam_subjects_filter,
                'email_filter': email_filter,
                'phone_filter': phone_filter,
                # Dropdown data
                'campuses': campuses,
                'subject_groups': subject_groups,
            }
            return render(request, 'adminpageSIMCODE/exam_registration.html', context)
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:login')

def view_registration_history(request, registration_id):
    """Xem lịch sử cập nhật của một hồ sơ đăng ký"""
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            try:
                registration = StudentExamRegistration.objects.select_related('student', 'student__campus', 'student__subject_group').get(pk=registration_id)
                # Lấy tất cả lịch sử cập nhật, sắp xếp theo thời gian mới nhất
                history_list = RegistrationHistory.objects.filter(registration=registration).order_by('-created_at')

                context = {
                    'registration': registration,
                    'history_list': history_list,
                }
                return render(request, 'adminpageSIMCODE/registration_history.html', context)
            except StudentExamRegistration.DoesNotExist:
                messages.error(request, 'Không tìm thấy hồ sơ đăng ký.')
                return redirect('adminpage:exam_registration')
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:login')

def export_exam_registrations(request):
    """Xuất danh sách đăng ký thi tốt nghiệp ra Excel theo bộ lọc"""
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            # Lấy danh sách đăng ký với các bộ lọc (giống như trong get_ExamRegistration)
            registration_list = StudentExamRegistration.objects.select_related('student', 'student__campus', 'student__subject_group').all()

            # Áp dụng các bộ lọc từ GET parameters
            student_code_filter = request.GET.get('student_code', '')
            student_name_filter = request.GET.get('student_name', '')
            campus_filter = request.GET.get('campus', '')
            subject_group_filter = request.GET.get('subject_group', '')
            class_name_filter = request.GET.get('class_name', '')
            exam_subjects_filter = request.GET.get('exam_subjects', '')
            email_filter = request.GET.get('email', '')
            phone_filter = request.GET.get('phone', '')

            if student_code_filter:
                registration_list = registration_list.filter(student__student_code__icontains=student_code_filter)

            if student_name_filter:
                registration_list = registration_list.filter(student__full_name__icontains=student_name_filter)

            if campus_filter:
                registration_list = registration_list.filter(student__campus_id=campus_filter)

            if subject_group_filter:
                registration_list = registration_list.filter(student__subject_group_id=subject_group_filter)

            if class_name_filter:
                registration_list = registration_list.filter(student__class_name__icontains=class_name_filter)

            if email_filter:
                registration_list = registration_list.filter(email__icontains=email_filter)

            if phone_filter:
                registration_list = registration_list.filter(phone__icontains=phone_filter)

            # Lọc theo trạng thái đã/chưa chọn môn thi
            if exam_subjects_filter == 'yes':
                # Đã chọn môn thi
                registration_ids = []
                for reg in registration_list:
                    if reg.exam_subjects and len(reg.exam_subjects) > 0:
                        registration_ids.append(reg.id)
                if registration_ids:
                    registration_list = registration_list.filter(id__in=registration_ids)
                else:
                    registration_list = registration_list.none()
            elif exam_subjects_filter == 'no':
                # Chưa chọn môn thi
                registration_ids = []
                for reg in registration_list:
                    if not reg.exam_subjects or len(reg.exam_subjects) == 0:
                        registration_ids.append(reg.id)
                if registration_ids:
                    registration_list = registration_list.filter(id__in=registration_ids)
                else:
                    registration_list = registration_list.none()

            # Sắp xếp theo tên lớp tăng dần (natural sort), sau đó theo ngày đăng ký mới nhất
            # Chuyển QuerySet thành list để sắp xếp tự nhiên
            registration_list = list(registration_list)
            # Sắp xếp tự nhiên theo tên lớp, sau đó theo ngày đăng ký
            registration_list.sort(key=lambda x: (
                natural_sort_key(x.student.class_name if x.student.class_name else ''),
                -(x.created_at.timestamp() if x.created_at else 0)
            ))
            registrations = registration_list

            # Tạo workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Đăng ký thi tốt nghiệp"

            # Header style
            header_fill = PatternFill(start_color="023EB6", end_color="022468", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            header_alignment = Alignment(horizontal="center", vertical="center")

            # Headers
            headers = [
                'STT', 'Mã học viên', 'Họ và tên', 'Lớp', 'Cơ sở', 'Tổ hợp môn',
                'Email', 'Số điện thoại', 'Môn thi 1', 'Môn thi 2', 'Trạng thái chọn môn thi', 'Ngày đăng ký'
            ]
            ws.append(headers)

            # Apply header style
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment

            # Data
            for idx, reg in enumerate(registrations, start=1):
                student = reg.student

                # Tách môn thi thành 2 cột riêng
                exam_subject_1 = ''
                exam_subject_2 = ''
                if reg.exam_subjects and isinstance(reg.exam_subjects, list) and len(reg.exam_subjects) > 0:
                    exam_subject_1 = reg.exam_subjects[0] if len(reg.exam_subjects) > 0 else ''
                    exam_subject_2 = reg.exam_subjects[1] if len(reg.exam_subjects) > 1 else ''

                # Xác định trạng thái chọn môn thi
                if reg.exam_subjects and len(reg.exam_subjects) > 0:
                    exam_status = 'Đã chọn'
                else:
                    exam_status = 'Chưa chọn'

                # Ngày đăng ký (ưu tiên registration_date, nếu không có thì dùng created_at)
                registration_date = reg.registration_date if reg.registration_date else reg.created_at

                row = [
                    idx,
                    student.student_code,
                    student.full_name,
                    student.class_name,
                    student.campus.name if student.campus else '',
                    f'Tổ hợp {student.subject_group.code}' if student.subject_group else '',
                    reg.email or '',
                    reg.phone or '',
                    exam_subject_1,
                    exam_subject_2,
                    exam_status,
                    registration_date.strftime('%d/%m/%Y %H:%M') if registration_date else ''
                ]
                ws.append(row)

            # Auto adjust column widths
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column].width = adjusted_width

            # Response
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f'dang_ky_thi_tot_nghiep_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            wb.save(response)
            return response
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:login')

def import_students_excel(request):
    """Import danh sách học viên từ Excel và hiển thị preview"""
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            if request.method == 'POST' and request.FILES.get('excel_file'):
                excel_file = request.FILES['excel_file']
                try:
                    wb = load_workbook(excel_file, read_only=True)
                    ws = wb.active

                    # Tìm các cột trong header
                    header_row = None
                    col_mapping = {}

                    # Tìm dòng header
                    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
                        row_values = [str(cell).strip().lower() if cell else '' for cell in row]
                        if any(keyword in ' '.join(row_values) for keyword in ['mã hv', 'mã học viên', 'student code', 'ma hv']):
                            header_row = i
                            # Map các cột
                            for j, cell in enumerate(row):
                                if cell:
                                    cell_str = str(cell).strip().lower()
                                    if 'mã hv' in cell_str or 'mã học viên' in cell_str or 'student code' in cell_str:
                                        col_mapping['student_code'] = j
                                    elif 'lớp' in cell_str or 'class' in cell_str:
                                        col_mapping['class_name'] = j
                                    elif 'họ tên' in cell_str or 'họ và tên' in cell_str or 'full name' in cell_str:
                                        col_mapping['full_name'] = j
                                    elif 'ngày sinh' in cell_str or 'date of birth' in cell_str or 'birthday' in cell_str:
                                        col_mapping['birthday'] = j
                                    elif 'số định danh' in cell_str or 'cccd' in cell_str or 'cmnd' in cell_str or 'id number' in cell_str:
                                        col_mapping['id_number'] = j
                                    elif 'nơi sinh' in cell_str or 'birth place' in cell_str or 'tỉnh' in cell_str or 'thành phố' in cell_str:
                                        col_mapping['birth_place'] = j
                                    elif 'dân tộc' in cell_str or 'ethnicity' in cell_str:
                                        col_mapping['ethnicity'] = j
                                    elif 'giới tính' in cell_str or 'gender' in cell_str or 'sex' in cell_str:
                                        col_mapping['gender'] = j
                                    elif 'email' in cell_str:
                                        col_mapping['email'] = j
                                    elif 'số điện thoại' in cell_str or 'phone' in cell_str or 'điện thoại' in cell_str:
                                        col_mapping['phone'] = j
                                    elif 'môn thi' in cell_str or 'exam subject' in cell_str or 'môn' in cell_str:
                                        col_mapping['exam_subjects'] = j
                            break

                    if not header_row or 'student_code' not in col_mapping:
                        return render(request, 'adminpageSIMCODE/import_students.html', {
                            'error': 'Không tìm thấy cột "Mã HV" trong file Excel. Vui lòng kiểm tra lại file.'
                        })

                    # Đọc dữ liệu
                    students_data = []
                    errors = []

                    for i, row in enumerate(ws.iter_rows(min_row=header_row + 1, values_only=True), start=header_row + 1):
                        # Bỏ qua dòng trống
                        if not any(row):
                            continue

                        student_code = str(row[col_mapping['student_code']]).strip() if col_mapping.get('student_code') is not None and row[col_mapping['student_code']] else None

                        if not student_code or len(student_code) != 7 or not student_code.isdigit():
                            errors.append(f"Dòng {i}: Mã học viên không hợp lệ ({student_code})")
                            continue

                        # Parse mã học viên để xác định cơ sở và tổ hợp môn
                        campus_code_num = student_code[:2]
                        subject_group_code = student_code[2:4]
                        student_number = student_code[4:7]

                        # Mapping mã cơ sở
                        campus_code_map = {
                            '10': 'AT', '11': 'BS', '12': 'CS', '13': 'ĐS',
                            '14': 'CN', '15': 'VH', '16': 'HT', '17': 'KT'
                        }
                        campus_code = campus_code_map.get(campus_code_num)

                        if not campus_code:
                            errors.append(f"Dòng {i}: Không tìm thấy cơ sở cho mã {campus_code_num}")
                            continue

                        # Lấy campus và subject_group
                        campus = Campus.objects.filter(code=campus_code).first()
                        subject_group = SubjectGroup.objects.filter(code=subject_group_code).first()

                        if not campus:
                            errors.append(f"Dòng {i}: Không tìm thấy cơ sở với mã {campus_code}")
                            continue

                        if not subject_group:
                            errors.append(f"Dòng {i}: Không tìm thấy tổ hợp môn với mã {subject_group_code}")
                            continue

                        # Parse ngày sinh
                        birthday = None
                        birthday_display = ''
                        if col_mapping.get('birthday') is not None and row[col_mapping['birthday']]:
                            try:
                                birthday_value = row[col_mapping['birthday']]
                                # Nếu là datetime object từ Excel
                                if isinstance(birthday_value, datetime):
                                    birthday = birthday_value.date()
                                    birthday_display = birthday.strftime('%d/%m/%Y')
                                else:
                                    birthday_str = str(birthday_value).strip()
                                    # Hỗ trợ format DD/MM/YYYY
                                    if '/' in birthday_str:
                                        parts = birthday_str.split('/')
                                        if len(parts) == 3:
                                            from datetime import date
                                            birthday = date(int(parts[2]), int(parts[1]), int(parts[0]))
                                            birthday_display = birthday_str
                                    else:
                                        birthday_display = birthday_str
                            except Exception as e:
                                errors.append(f"Dòng {i}: Lỗi parse ngày sinh: {str(e)}")
                                birthday_display = str(row[col_mapping['birthday']])

                        # Lấy các trường khác
                        student_data = {
                            'row_number': i,
                            'student_code': student_code,
                            'class_name': str(row[col_mapping.get('class_name', 0)]).strip() if col_mapping.get('class_name') is not None and row[col_mapping.get('class_name', 0)] else '',
                            'full_name': str(row[col_mapping.get('full_name', 0)]).strip() if col_mapping.get('full_name') is not None and row[col_mapping.get('full_name', 0)] else '',
                            'birthday': birthday.strftime('%Y-%m-%d') if birthday else None,
                            'birthday_display': birthday_display,
                            'id_number': str(row[col_mapping.get('id_number', 0)]).strip() if col_mapping.get('id_number') is not None and row[col_mapping.get('id_number', 0)] else '',
                            'birth_place': str(row[col_mapping.get('birth_place', 0)]).strip() if col_mapping.get('birth_place') is not None and row[col_mapping.get('birth_place', 0)] else '',
                            'ethnicity': str(row[col_mapping.get('ethnicity', 0)]).strip() if col_mapping.get('ethnicity') is not None and row[col_mapping.get('ethnicity', 0)] else '',
                            'gender': str(row[col_mapping.get('gender', 0)]).strip() if col_mapping.get('gender') is not None and row[col_mapping.get('gender', 0)] else '',
                            'campus_id': campus.id,
                            'campus_name': campus.name,
                            'subject_group_id': subject_group.id,
                            'subject_group_code': subject_group.code,
                            # Thông tin đăng ký thi tốt nghiệp (nếu có)
                            'email': str(row[col_mapping.get('email', 0)]).strip() if col_mapping.get('email') is not None and row[col_mapping.get('email', 0)] else '',
                            'phone': str(row[col_mapping.get('phone', 0)]).strip() if col_mapping.get('phone') is not None and row[col_mapping.get('phone', 0)] else '',
                            'exam_subjects': str(row[col_mapping.get('exam_subjects', 0)]).strip() if col_mapping.get('exam_subjects') is not None and row[col_mapping.get('exam_subjects', 0)] else '',
                        }

                        students_data.append(student_data)

                    # Lưu vào session để import sau
                    request.session['students_import_data'] = students_data
                    request.session['students_import_errors'] = errors

                    context = {
                        'students_data': students_data,
                        'errors': errors,
                        'total_count': len(students_data),
                        'error_count': len(errors)
                    }
                    return render(request, 'adminpageSIMCODE/import_students.html', context)

                except Exception as e:
                    return render(request, 'adminpageSIMCODE/import_students.html', {
                        'error': f'Lỗi khi đọc file Excel: {str(e)}'
                    })

            # GET request - hiển thị form upload
            return render(request, 'adminpageSIMCODE/import_students.html')
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:login')

def save_imported_students(request):
    """Lưu danh sách học viên đã import vào database"""
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role == 'admin':
            if request.method == 'POST':
                students_data = request.session.get('students_import_data', [])

                if not students_data:
                    return render(request, 'adminpageSIMCODE/import_students.html', {
                        'error': 'Không có dữ liệu để import. Vui lòng upload file Excel trước.'
                    })

                created_count = 0
                updated_count = 0
                error_count = 0
                errors = []

                for student_data in students_data:
                    try:
                        # Lấy campus và subject_group từ ID
                        campus_id = student_data.get('campus_id')
                        subject_group_id = student_data.get('subject_group_id')

                        if not campus_id or not subject_group_id:
                            error_count += 1
                            errors.append(f"Mã {student_data.get('student_code')}: Thiếu thông tin cơ sở hoặc tổ hợp môn")
                            continue

                        campus = Campus.objects.get(id=campus_id)
                        subject_group = SubjectGroup.objects.get(id=subject_group_id)

                        # Parse birthday
                        birthday = None
                        if student_data.get('birthday'):
                            from datetime import datetime
                            birthday = datetime.strptime(student_data['birthday'], '%Y-%m-%d').date()

                        # Tạo hoặc cập nhật Student
                        student, student_created = Student.objects.update_or_create(
                            student_code=student_data['student_code'],
                            defaults={
                                'campus': campus,
                                'subject_group': subject_group,
                                'class_name': student_data.get('class_name', ''),
                                'full_name': student_data.get('full_name', ''),
                                'birthday': birthday,
                                'id_number': student_data.get('id_number', ''),
                                'birth_place': student_data.get('birth_place', ''),
                                'ethnicity': student_data.get('ethnicity', ''),
                                'gender': student_data.get('gender', ''),
                            }
                        )

                        # Tạo hoặc cập nhật StudentExamRegistration nếu có email hoặc phone
                        email = student_data.get('email', '').strip()
                        phone = student_data.get('phone', '').strip()
                        exam_subjects_str = student_data.get('exam_subjects', '').strip()

                        # Luôn tạo StudentExamRegistration khi import (có thể để trống email/phone để học viên điền sau)
                        # Parse exam_subjects nếu có
                        exam_subjects_list = []
                        if exam_subjects_str:
                            # Hỗ trợ nhiều format: "Môn1, Môn2" hoặc "Môn1; Môn2"
                            exam_subjects_list = [s.strip() for s in exam_subjects_str.replace(';', ',').split(',') if s.strip()]

                        # Tạo hoặc cập nhật StudentExamRegistration
                        registration, reg_created = StudentExamRegistration.objects.update_or_create(
                            student=student,
                            defaults={
                                'email': email if email else None,
                                'phone': phone if phone else None,
                                'exam_subjects': exam_subjects_list if exam_subjects_list else [],
                            }
                        )

                        # Đếm cả Student và Registration
                        if student_created and reg_created:
                            created_count += 1
                        elif not student_created and not reg_created:
                            updated_count += 1
                        elif student_created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as e:
                        error_count += 1
                        errors.append(f"Mã {student_data.get('student_code')}: {str(e)}")

                # Xóa session
                request.session.pop('students_import_data', None)
                request.session.pop('students_import_errors', None)

                context = {
                    'success': True,
                    'created_count': created_count,
                    'updated_count': updated_count,
                    'error_count': error_count,
                    'errors': errors[:20],  # Chỉ hiển thị 20 lỗi đầu tiên
                }
                return render(request, 'adminpageSIMCODE/import_students.html', context)

            return redirect('adminpage:import_students_excel')
        else:
            return redirect('homepage:Homepage')
    return redirect('homepage:login')

# ---------- Chấm công tự động ----------
THU_LABELS = ['', 'CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']  # index 2->8 tương ứng Thứ 2 -> CN


def _date_to_day_of_week(d):
    """Chuyển date sang day_of_week (2=Thứ 2, ..., 8=Chủ nhật)."""
    return d.weekday() + 2  # Monday=0 -> 2, Sunday=6 -> 8


def _week_ranges_in_month(year, month):
    """
    Trả về dict tuần -> (day_start, day_end) theo chuẩn tuần Thứ 2 -> Chủ nhật.
    Các ngày được cắt theo phạm vi trong tháng.
    """
    first_weekday, days_in_month = calendar.monthrange(year, month)  # Monday=0 ... Sunday=6
    max_week = ((days_in_month + first_weekday - 1) // 7) + 1
    ranges = {}
    for week_no in range(1, max_week + 1):
        day_start = max(1, (7 * (week_no - 1)) - first_weekday + 1)
        day_end = min(days_in_month, (7 * week_no) - first_weekday)
        ranges[week_no] = (day_start, day_end)
    return ranges


def _week_of_month(year, month, day):
    """Tuần trong tháng theo chuẩn tuần Thứ 2 -> Chủ nhật (có thể từ 4 đến 6 tuần/tháng)."""
    first_weekday, _ = calendar.monthrange(year, month)  # Monday=0 ... Sunday=6
    return ((day + first_weekday - 1) // 7) + 1


def _resolve_version_for_day(year, month, day, version_cache):
    """
    Áp dụng TKB theo tuần trong cùng tháng: nếu tuần hiện tại chưa nhập thì dùng TKB tuần trước (cascade).
    version_cache: dict (year, month, week) -> ScheduleVersion (hoặc None).
    """
    w = _week_of_month(year, month, day)
    candidates = [(year, month, wk) for wk in range(w, 0, -1)]  # (y, m, w), (y, m, w-1), ..., (y, m, 1)
    for (y, m, wk) in candidates:
        if wk < 1:
            continue
        v = version_cache.get((y, m, wk))
        if v is not None:
            return v
    return None


def attendance_pivot(request):
    """Giao diện bảng pivot chấm công: cột STT, Họ tên, Môn; hàng ngang ngày 1-31; ô = tiết quy đổi."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')

    now = timezone.now().date()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    location_id = request.GET.get('location_id', '')
    grade = request.GET.get('grade', '')
    size_group = request.GET.get('size_group', '')
    version_id = request.GET.get('version_id', '')

    pivot_rows, calendar_days, days_in_month = _build_attendance_pivot_data(
        year, month, location_id, grade, size_group, version_id
    )
    campuses = Campus.objects.exclude(code='AS').order_by('code')
    versions = ScheduleVersion.objects.all().order_by('-year', '-month', '-week')[:30]

    context = {
        'year': year,
        'month': month,
        'days_in_month': days_in_month,
        'calendar_days': calendar_days,
        'campuses': campuses,
        'versions': versions,
        'pivot_rows': pivot_rows,
        'location_id': location_id,
        'grade': grade,
        'size_group': size_group,
        'version_id': version_id,
    }
    return render(request, 'adminpageSIMCODE/attendance_pivot.html', context)


def _build_attendance_pivot_data(year, month, location_id, grade, size_group, version_id):
    """Xây dựng pivot_rows và calendar_days cho bảng chấm công (dùng chung cho view và export)."""
    _, days_in_month = calendar.monthrange(year, month)
    calendar_days = []
    for d in range(1, days_in_month + 1):
        dt = datetime(year, month, d).date()
        calendar_days.append({
            'day': d,
            'weekday': _date_to_day_of_week(dt),
            'label': THU_LABELS[_date_to_day_of_week(dt)] if _date_to_day_of_week(dt) < len(THU_LABELS) else '',
        })
    version_cache = {}
    for v in ScheduleVersion.objects.filter(year__isnull=False, month__isnull=False, week__isnull=False):
        version_cache[(v.year, v.month, v.week)] = v
    base_qs = Schedule.objects.select_related('teacher', 'classroom', 'classroom__managing_campus')
    base_qs = base_qs.filter(classroom__managing_campus_id__isnull=False)
    if location_id:
        base_qs = base_qs.filter(classroom__managing_campus_id=location_id)
    if grade:
        base_qs = base_qs.filter(classroom__grade=int(grade))
    if size_group == 'gte47':
        base_qs = base_qs.filter(classroom__class_size__gte=47)
    elif size_group == 'lt47':
        base_qs = base_qs.filter(classroom__class_size__lt=47)
    use_single_version = bool(version_id)
    if use_single_version:
        schedules_qs = base_qs.filter(version_id=version_id)
    else:
        version_ids_in_month = set()
        for d in range(1, days_in_month + 1):
            v = _resolve_version_for_day(year, month, d, version_cache)
            if v:
                version_ids_in_month.add(v.id)
        schedules_qs = base_qs.filter(version_id__in=version_ids_in_month) if version_ids_in_month else base_qs.none()
    teacher_ids = schedules_qs.values_list('teacher_id', flat=True).distinct()
    teachers = Teacher.objects.filter(id__in=teacher_ids).order_by('full_name')
    by_teacher_dow_version = defaultdict(list)
    for s in schedules_qs:
        if s.version_id:
            by_teacher_dow_version[(s.teacher_id, s.day_of_week, s.version_id)].append(s)
    pivot_cells = defaultdict(lambda: defaultdict(int))
    for teacher in teachers:
        for day_num in range(1, days_in_month + 1):
            dt = datetime(year, month, day_num).date()
            dow = _date_to_day_of_week(dt)
            vid = int(version_id) if use_single_version and version_id else (_resolve_version_for_day(year, month, day_num, version_cache).id if _resolve_version_for_day(year, month, day_num, version_cache) else None)
            if not vid:
                continue
            for sch in by_teacher_dow_version.get((teacher.id, dow, vid), []):
                pivot_cells[teacher.id][day_num] += get_converted_periods_for_schedule(sch)
    overrides = {(o.teacher_id, o.day): o.value for o in AttendanceOverride.objects.filter(
        teacher_id__in=[t.id for t in teachers], year=year, month=month
    )}
    for teacher in teachers:
        for day_num in range(1, days_in_month + 1):
            key = (teacher.id, day_num)
            if key in overrides:
                pivot_cells[teacher.id][day_num] = overrides[key]
    teacher_subject_from_tkb = {}
    for teacher in teachers:
        subs = list(schedules_qs.filter(teacher=teacher).values_list('subject_name', flat=True).distinct())
        teacher_subject_from_tkb[teacher.id] = subs[0] if subs else ''
    pivot_rows = []
    for stt, teacher in enumerate(teachers, 1):
        row_total = 0
        days_list = []
        for day_num in range(1, days_in_month + 1):
            val = pivot_cells[teacher.id].get(day_num, 0)
            days_list.append({'day': day_num, 'val': val})
            row_total += val
        subject_display = (teacher.display_subject or '').strip() or teacher_subject_from_tkb.get(teacher.id, '')
        pivot_rows.append({
            'stt': stt, 'teacher': teacher, 'subject_display': subject_display,
            'days_list': days_list, 'so_tiet_lam_ho_so': row_total, 'tong_cong': row_total,
        })
    return pivot_rows, calendar_days, days_in_month


def _copy_cell_style(source_cell, target_cell):
    """Sao chép định dạng (font, border, fill, alignment...) từ ô nguồn sang ô đích."""
    if source_cell.has_style:
        if source_cell.font:
            target_cell.font = shallow_copy(source_cell.font)
        if source_cell.border:
            target_cell.border = shallow_copy(source_cell.border)
        if source_cell.fill:
            target_cell.fill = shallow_copy(source_cell.fill)
        if source_cell.number_format:
            target_cell.number_format = shallow_copy(source_cell.number_format)
        if source_cell.alignment:
            target_cell.alignment = shallow_copy(source_cell.alignment)
        if source_cell.protection:
            target_cell.protection = shallow_copy(source_cell.protection)


def _split_vn_name(full_name):
    """Tách họ đệm và tên từ họ tên đầy đủ (tách tại khoảng trắng cuối)."""
    if not full_name or not full_name.strip():
        return '', ''
    s = full_name.strip()
    i = s.rfind(' ')
    if i <= 0:
        return '', s
    return s[:i + 1].rstrip() or '', s[i + 1:].lstrip() or s


def export_attendance_excel(request):
    """Xuất bảng chấm công ra Excel theo template CDCN.xlsx và bộ lọc đang áp dụng."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')
    now = timezone.now().date()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    location_id = request.GET.get('location_id', '')
    grade = request.GET.get('grade', '')
    size_group = request.GET.get('size_group', '')
    version_id = request.GET.get('version_id', '')
    pivot_rows, calendar_days, days_in_month = _build_attendance_pivot_data(
        year, month, location_id, grade, size_group, version_id
    )
    template_path = os.path.join(settings.BASE_DIR, 'chấm công tự động', 'CDCN.xlsx')
    if os.path.isfile(template_path):
        try:
            wb = load_workbook(template_path)
            if 'T11.25' in wb.sheetnames:
                ws = wb['T11.25']
            else:
                ws = wb.active
            ws.title = f"T{month}.{year}"
            loc_label = ''
            if location_id:
                try:
                    c = Campus.objects.get(id=location_id)
                    loc_label = f' {c.code} - {c.name}'
                except Campus.DoesNotExist:
                    pass
            grade_label = f' KHỐI {grade}' if grade else ''
            size_label = ''
            if size_group == 'gte47':
                size_label = ' SĨ SỐ ≥ 47'
            elif size_group == 'lt47':
                size_label = ' SĨ SỐ < 47'
            title = f'BẢNG TỔNG HỢP GIỜ DẠY{loc_label}{grade_label}{size_label} THÁNG {month:02d}/{year}'
            ws.cell(3, 1, title)
            day_start_col = 5
            day_end_col = day_start_col + days_in_month - 1
            to_unmerge = [m for m in list(ws.merged_cells.ranges) if m.min_row >= 4 and m.max_row <= 6]
            for m in to_unmerge:
                ws.unmerge_cells(str(m))
            ws.merge_cells(start_row=4, start_column=1, end_row=6, end_column=1)
            ws.merge_cells(start_row=4, start_column=2, end_row=6, end_column=3)
            ws.merge_cells(start_row=4, start_column=4, end_row=6, end_column=4)
            ws.merge_cells(start_row=4, start_column=day_start_col, end_row=4, end_column=day_end_col)
            ws.cell(4, 1, 'STT')
            ws.cell(4, 2, 'HỌ VÀ TÊN')
            ws.cell(4, 4, 'Môn')
            ws.cell(4, day_end_col + 1, 'Số tiết\nlàm hồ sơ CN')
            ws.cell(4, day_end_col + 2, 'Tổng\ncộng')
            ws.merge_cells(start_row=4, start_column=day_end_col + 1, end_row=6, end_column=day_end_col + 1)
            ws.merge_cells(start_row=4, start_column=day_end_col + 2, end_row=6, end_column=day_end_col + 2)
            for c, cd in enumerate(calendar_days, start=day_start_col):
                ws.cell(5, c, cd['day'])
                ws.cell(6, c, cd['label'])
            # Sao chép định dạng cho phần tiêu đề ngày/thứ nếu vượt cột mẫu
            header_base = ws.cell(5, day_start_col)
            weekday_base = ws.cell(6, day_start_col)
            for c in range(day_start_col + 1, day_end_col + 1):
                _copy_cell_style(header_base, ws.cell(5, c))
                _copy_cell_style(weekday_base, ws.cell(6, c))
            for row_idx in range(7, ws.max_row + 1):
                for col_idx in range(1, ws.max_column + 1):
                    cell = ws.cell(row_idx, col_idx)
                    if cell.value is not None:
                        cell.value = None
            for idx, row in enumerate(pivot_rows, start=7):
                ho_dem, ten = _split_vn_name(row['teacher'].full_name)
                ws.cell(idx, 1, row['stt'])
                ws.cell(idx, 2, ho_dem)
                ws.cell(idx, 3, ten)
                ws.cell(idx, 4, row['subject_display'])
                for c, item in enumerate(row['days_list'], start=day_start_col):
                    ws.cell(idx, c, item['val'] if item['val'] else None)
                ws.cell(idx, day_end_col + 1, row['so_tiet_lam_ho_so'])
                ws.cell(idx, day_end_col + 2, row['tong_cong'])
            # Sao chép định dạng từ dòng mẫu (7) sang tất cả dòng dữ liệu, kể cả dòng vượt quá mẫu
            num_cols = day_end_col + 2
            for idx in range(7, 7 + len(pivot_rows)):
                for col in range(1, num_cols + 1):
                    src = ws.cell(7, col)
                    if not src.has_style and col >= day_start_col:
                        src = ws.cell(7, day_start_col)
                    tgt = ws.cell(idx, col)
                    _copy_cell_style(src, tgt)
        except Exception:
            wb = None
    else:
        wb = None
    if wb is None:
        wb = Workbook()
        ws = wb.active
        ws.title = f"Cham_cong_T{month}_{year}"
        header = ['STT', 'Họ và Tên', 'Môn'] + [f"{cd['day']}({cd['label']})" for cd in calendar_days] + ['Số tiết làm hồ sơ', 'Tổng cộng']
        ws.append(header)
        for row in pivot_rows:
            r = [row['stt'], row['teacher'].full_name, row['subject_display']]
            r += [item['val'] for item in row['days_list']]
            r += [row['so_tiet_lam_ho_so'], row['tong_cong']]
            ws.append(r)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="cham_cong_T{month}_{year}.xlsx"'
    wb.save(response)
    return response


def import_tkb_excel(request):
    """Import TKB từ Excel theo phiên bản thời gian (tuần/tháng)."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        year_import = request.POST.get('year')
        month_import = request.POST.get('month')
        week_import = request.POST.get('week')
        session = request.POST.get('session', 'sang')
        if session not in ('sang', 'chieu', 'toi'):
            session = 'sang'
        if not year_import or not month_import or not week_import:
            messages.warning(request, 'Vui lòng chọn Năm, Tháng và Tuần.')
            return redirect('adminpage:import_tkb_excel')
        try:
            year_import = int(year_import)
            month_import = int(month_import)
            week_import = int(week_import)
            week_ranges = _week_ranges_in_month(year_import, month_import)
            if week_import not in week_ranges:
                raise ValueError(f'Tuần phải nằm trong khoảng 1-{len(week_ranges)} của tháng đã chọn.')
        except (ValueError, TypeError):
            messages.warning(request, 'Năm/Tháng/Tuần không hợp lệ.')
            return redirect('adminpage:import_tkb_excel')

        day_start, day_end = week_ranges[week_import]
        effective_from = datetime(year_import, month_import, day_start).date()
        effective_to = datetime(year_import, month_import, day_end).date()
        version_name = f"T{month_import}/{year_import} Tuần {week_import}"

        # Cùng tuần (năm, tháng, tuần) chỉ dùng 1 phiên bản — Sáng/Chiều/Tối cộng dồn vào 1 phiên
        version, version_created = ScheduleVersion.objects.get_or_create(
            year=year_import,
            month=month_import,
            week=week_import,
            defaults={
                'name': version_name,
                'effective_from': effective_from,
                'effective_to': effective_to,
            },
        )
        excel_file = request.FILES['excel_file']
        try:
            n = import_tkb_from_excel(excel_file, version, session=session)
            session_label = dict(Schedule.SESSION_CHOICES).get(session, session)
            if version_created:
                messages.success(request, f'Đã tạo phiên bản "{version.name}" và import TKB buổi {session_label}: {n} tiết.')
            else:
                messages.success(request, f'Đã thêm TKB buổi {session_label} vào phiên bản "{version.name}": {n} tiết (cộng dồn với Sáng/Chiều/Tối).')
        except Exception as e:
            if version_created:
                version.delete()
            messages.error(request, f'Lỗi import: {str(e)}')
        return redirect('adminpage:attendance_pivot')
    selected_year = int(request.GET.get('year', timezone.now().year))
    selected_month = int(request.GET.get('month', timezone.now().month))
    week_ranges = _week_ranges_in_month(selected_year, selected_month)
    week_options = [
        {
            'value': week_no,
            'start_day': day_start,
            'end_day': day_end,
        }
        for week_no, (day_start, day_end) in week_ranges.items()
    ]
    return render(
        request,
        'adminpageSIMCODE/import_tkb.html',
        {
            'selected_year': selected_year,
            'selected_month': selected_month,
            'week_options': week_options,
        },
    )


def import_dsgv_excel(request):
    """Import riêng file DSGV (danh sách giáo viên). Cột: STT, Mã GV, Họ tên [, Môn]."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')

    if request.method == 'POST' and request.FILES.get('dsgv_file'):
        f = request.FILES['dsgv_file']
        try:
            n = import_dsgv_from_excel(f)
            messages.success(request, f'Đã import DSGV: {n} giáo viên mới (đã cập nhật họ tên và môn nếu có).')
        except Exception as e:
            messages.error(request, f'Lỗi import DSGV: {str(e)}')
        return redirect('adminpage:attendance_pivot')
    return render(request, 'adminpageSIMCODE/import_dsgv.html', {})


def import_dsl_excel(request):
    """Import danh sách lớp (DSL) cập nhật sĩ số ClassRoom. Cột: Lớp, Số HS."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')

    if request.method == 'POST' and request.FILES.get('dsl_file'):
        f = request.FILES['dsl_file']
        try:
            n = import_dsl_from_excel(f)
            messages.success(request, f'Đã import DSL: cập nhật sĩ số cho {n} lớp.')
        except Exception as e:
            messages.error(request, f'Lỗi import DSL: {str(e)}')
        return redirect('adminpage:attendance_pivot')
    return render(request, 'adminpageSIMCODE/import_dsl.html', {})


def import_dsl_from_excel(excel_file):
    """Đọc file DSL: cột Lớp, Số HS. Cập nhật ClassRoom.class_size theo tên lớp."""
    try:
        import pandas as pd
    except ImportError:
        raise ValueError('Cần cài đặt pandas: pip install pandas xlrd openpyxl')
    df = pd.read_excel(excel_file, header=None)
    rows = df.values.tolist()
    updated = 0
    for i, row in enumerate(rows):
        if i == 0:
            continue
        if len(row) < 2:
            continue
        try:
            class_name = str(row[0]).strip() if pd.notna(row[0]) else None
            so_hs = int(float(row[1])) if pd.notna(row[1]) else None
        except (ValueError, TypeError):
            continue
        if not class_name or so_hs is None or class_name.upper() == 'LỚP':
            continue
        n = ClassRoom.objects.filter(name=class_name).update(class_size=so_hs)
        if n:
            updated += 1
    return updated


def clear_attendance_data(request):
    """Xóa hết dữ liệu DSGV (Teacher) và TKB (Schedule, ScheduleVersion, ClassRoom). Chỉ admin."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')

    if request.method == 'POST':
        # Thứ tự xóa: Schedule (FK) -> ScheduleVersion, ClassRoom -> Teacher
        n_schedule = Schedule.objects.count()
        n_version = ScheduleVersion.objects.count()
        n_classroom = ClassRoom.objects.count()
        n_teacher = Teacher.objects.count()
        Schedule.objects.all().delete()
        ScheduleVersion.objects.all().delete()
        ClassRoom.objects.all().delete()
        Teacher.objects.all().delete()
        messages.success(
            request,
            f'Đã xóa hết: {n_schedule} tiết TKB, {n_version} phiên bản TKB, {n_classroom} lớp, {n_teacher} giáo viên.'
        )
        return redirect('adminpage:attendance_pivot')

    return render(request, 'adminpageSIMCODE/clear_attendance_data.html', {})
def _ensure_campuses_and_linked_points():
    """Tất cả (cơ sở + liên kết) lấy từ homepage.Campus. Bỏ AS, chỉ dùng AT."""
    # Cơ sở: AT, BS, CS. Điểm liên kết: CN, ĐS, KT, HT, VH — đều trong Campus
    codes_names = [
        ('AT', 'Trụ sở chính'), ('BS', 'Cơ sở 1'), ('CS', 'Cơ sở 2'),
        ('CN', 'Trường Cao đẳng Công nghệ TPHCM'), ('ĐS', 'Trường Trung cấp Đông Sài Gòn'),
        ('KT', 'Trường Cao đẳng Kinh tế Kỹ thuật Thủ Đức'), ('HT', 'Trung tâm Huấn luyện Thể thao Quốc gia'),
        ('VH', 'Trường Cao đẳng Kỹ Nghệ II'),
    ]
    for code, name in codes_names:
        Campus.objects.get_or_create(code=code, defaults={'name': name, 'address': ''})


def _loc_code_to_campus_code(loc_code):
    """AS và AT đều quy về Campus AT; BS, CS, CN, ĐS, KT, HT, VH giữ nguyên (đều trong Campus)."""
    if loc_code == 'AS' or loc_code == 'AT':
        return 'AT'
    if loc_code in ('BS', 'CS', 'CN', 'ĐS', 'KT', 'HT', 'VH'):
        return loc_code
    return None


def _parse_class_name(class_name):
    """Từ tên lớp như 10AS1, 12CN3 trả về (grade, location_code). Ví dụ: 10AS1 -> (10, 'AS')."""
    s = (class_name or '').strip()
    m = re.match(r'^(\d+)\s*([A-Za-zĐ]+)\s*\d*$', s)
    if m:
        grade = int(m.group(1))
        loc_code = m.group(2).upper()
        if 'Đ' in loc_code or 'D' in loc_code:
            loc_code = loc_code.replace('D', 'Đ')
        return (grade, loc_code)
    return (None, None)


def import_dsgv_from_excel(excel_file):
    """
    Đọc file DSGV.xls: dòng 6+ có cột STT, Mã GV, Họ tên [, Môn].
    Tạo/cập nhật Teacher (teacher_code, full_name, display_subject từ cột Môn nếu có).
    """
    try:
        import pandas as pd
    except ImportError:
        raise ValueError('Cần cài đặt pandas: pip install pandas xlrd openpyxl')
    df = pd.read_excel(excel_file, header=None)
    rows = df.values.tolist()
    created = 0
    updated = 0
    for i, row in enumerate(rows):
        if i < 5:
            continue
        if len(row) < 3:
            continue
        try:
            code = str(row[1]).strip() if pd.notna(row[1]) else None
            name = str(row[2]).strip() if pd.notna(row[2]) else None
            mon = str(row[3]).strip() if len(row) > 3 and pd.notna(row[3]) else ''
            if mon and (mon.upper() == 'MÔN' or mon == 'Môn'):
                mon = ''
        except (ValueError, TypeError):
            continue
        if not code or not name or code.upper() == 'MÃ GV':
            continue
        teacher, created_this = Teacher.objects.get_or_create(
            teacher_code=code,
            defaults={'full_name': name, 'display_subject': mon or ''},
        )
        if created_this:
            created += 1
        else:
            teacher.full_name = name
            if len(row) > 3:
                teacher.display_subject = mon or ''
            teacher.save(update_fields=['full_name', 'display_subject'])
            updated += 1
    return created


def import_tkb_from_excel(excel_file, version, session='sang'):
    """
    Đọc file TKB.xls (ma trận): dòng header có "Tiết" và tên lớp (10AS1, 10AS2, ...);
    mỗi ô dữ liệu dạng "MÔN - MãGV" (vd: SH - C.Quyên, TOAN - T.T.Bảo).
    Cột 0 = Ngày (Thứ 2, Thứ 3...), cột 1 = Tiết; từ cột 2 = từng lớp.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ValueError('Cần cài đặt pandas: pip install pandas xlrd openpyxl')
    _ensure_campuses_and_linked_points()
    df = pd.read_excel(excel_file, header=None)
    rows = df.values.tolist()
    # Tìm dòng header: có "Tiết" ở cột 1 và các cột sau là tên lớp (số+chữ+số)
    header_row_idx = None
    for i, row in enumerate(rows):
        if len(row) < 3:
            continue
        c1 = str(row[1]).strip() if pd.notna(row[1]) else ''
        if 'Tiết' in c1 or (c1.isdigit() and i > 5):
            # Cột 2 có thể là tên lớp kiểu 10AS1
            c2 = str(row[2]).strip() if pd.notna(row[2]) else ''
            if c2 and re.match(r'^\d+[A-ZĐ]', c2, re.IGNORECASE):
                header_row_idx = i
                break
    if header_row_idx is None:
        for i in range(min(15, len(rows))):
            row = rows[i]
            if len(row) >= 10:
                c1 = str(row[1]).strip() if pd.notna(row[1]) else ''
                c2 = str(row[2]).strip() if pd.notna(row[2]) else ''
                if 'Tiết' in c1 or (c1 == '1' and c2):
                    header_row_idx = i
                    break
    if header_row_idx is None:
        header_row_idx = 7
    header_row = rows[header_row_idx]
    class_names = []
    for j in range(2, len(header_row)):
        cn = str(header_row[j]).strip() if pd.notna(header_row[j]) else ''
        if cn and (re.match(r'^\d+[A-ZĐ]', cn, re.IGNORECASE) or cn.isdigit() is False):
            class_names.append((j, cn))
    # Map Thứ N -> day_of_week
    def day_label_to_dow(label):
        s = (str(label or '').strip()).lower()
        if 'thứ 2' in s or 'thu 2' in s:
            return 2
        if 'thứ 3' in s or 'thu 3' in s:
            return 3
        if 'thứ 4' in s or 'thu 4' in s:
            return 4
        if 'thứ 5' in s or 'thu 5' in s:
            return 5
        if 'thứ 6' in s or 'thu 6' in s:
            return 6
        if 'thứ 7' in s or 'thu 7' in s:
            return 7
        if 'chủ nhật' in s or 'cn' == s or 'chu nhat' in s:
            return 8
        return None
    current_day = None
    created_schedules = 0
    for i in range(header_row_idx + 1, len(rows)):
        row = rows[i]
        if len(row) < 3:
            continue
        day_label = row[0]
        period_val = row[1]
        if pd.notna(day_label) and str(day_label).strip():
            current_day = day_label_to_dow(day_label)
        try:
            period = int(float(period_val)) if pd.notna(period_val) else None
        except (ValueError, TypeError):
            period = None
        if current_day is None or period is None:
            continue
        for col_idx, class_name in class_names:
            if col_idx >= len(row):
                continue
            cell = row[col_idx]
            if pd.isna(cell) or not str(cell).strip():
                continue
            cell_str = str(cell).strip()
            if ' - ' in cell_str:
                parts = cell_str.split(' - ', 1)
                subject_name = (parts[0] or '').strip()
                teacher_code = (parts[1] or '').strip()
            else:
                continue
            if not teacher_code or not subject_name:
                continue
            teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
            if not teacher:
                teacher = Teacher.objects.create(teacher_code=teacher_code, full_name=teacher_code)
            grade, loc_code = _parse_class_name(class_name)
            campus_code = _loc_code_to_campus_code(loc_code) if loc_code else None
            managing_campus = None
            if campus_code:
                managing_campus = Campus.objects.filter(code=campus_code).first()
                if not managing_campus:
                    managing_campus = Campus.objects.create(code=campus_code, name=campus_code, address='')
            classroom, _ = ClassRoom.objects.get_or_create(
                name=class_name,
                defaults={
                    'grade': grade,
                    'class_size': 0,
                    'managing_campus': managing_campus,
                },
            )
            if managing_campus and classroom.managing_campus_id != managing_campus.id:
                classroom.managing_campus = managing_campus
                classroom.save(update_fields=['managing_campus'])
            _, created = Schedule.objects.get_or_create(
                teacher=teacher,
                classroom=classroom,
                day_of_week=current_day,
                period=period,
                version=version,
                defaults={
                    'subject_name': subject_name,
                    'session': session,
                    'effective_date': version.effective_from,
                },
            )
            if created:
                created_schedules += 1
    return created_schedules

# ---------- Sổ đầu bài số (theo nhóm bộ môn) ----------

def _require_journal_admin(request):
    """Kiểm tra quyền admin cho sổ đầu bài."""
    if not request.user.is_authenticated:
        return redirect('homepage:Login')
    try:
        account = Account.objects.get(user=request.user)
        accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
        if accounttype.accounttype_role != 'admin':
            return redirect('homepage:Homepage')
    except (Account.DoesNotExist, AccountType.DoesNotExist):
        return redirect('homepage:Login')
    return None


def _create_13_weeks(subject_journal):
    """Tạo 13 tuần liền kề từ week1_start_date."""
    from datetime import timedelta
    start = subject_journal.week1_start_date
    if not start:
        return
    for w in range(1, 14):
        week_start = start + timedelta(days=(w - 1) * 7)
        week_end = week_start + timedelta(days=6)
        JournalWeek.objects.update_or_create(
            subject_journal=subject_journal, week_number=w,
            defaults={'start_date': week_start, 'end_date': week_end, 'is_locked': False}
        )


def journal_manager_dashboard(request):
    """Quản lý sổ đầu bài theo nhóm bộ môn: tạo sổ (môn+năm), set tuần 1, import DSGV, import DSL."""
    err = _require_journal_admin(request)
    if err:
        return err
    from datetime import date
    current_year = date.today().year
    journals = SubjectJournal.objects.prefetch_related('weeks', 'rows').order_by('-year', 'subject')
    subject_choices = SUBJECT_CHOICES

    if request.method == 'POST':
        action = request.POST.get('journal_action')
        if action == 'delete_selected':
            selected_ids = request.POST.getlist('selected_journal_ids')
            if not selected_ids:
                messages.error(request, 'Vui lòng chọn ít nhất 1 sổ đầu bài để xoá.')
                return redirect('adminpage:journal_manager_dashboard')
            deleted_count = SubjectJournal.objects.filter(id__in=selected_ids).count()
            SubjectJournal.objects.filter(id__in=selected_ids).delete()
            messages.success(request, f'Đã xoá {deleted_count} sổ đầu bài đã chọn.')
            return redirect('adminpage:journal_manager_dashboard')
        if action == 'create_journal':
            subject = (request.POST.get('subject') or '').strip()
            year = request.POST.get('year', current_year)
            try:
                year = int(year)
            except ValueError:
                year = current_year
            if subject:
                sj, created = SubjectJournal.objects.get_or_create(subject=subject, year=year)
                messages.success(request, f'Đã tạo sổ {subject} năm {year}.')
            else:
                messages.error(request, 'Chọn môn.')
            return redirect('adminpage:journal_manager_dashboard')
        if action == 'set_week1':
            journal_id = request.POST.get('journal_id')
            week1_str = request.POST.get('week1_start_date', '').strip()
            try:
                sj = SubjectJournal.objects.get(id=journal_id)
                from datetime import datetime
                d = datetime.strptime(week1_str, '%Y-%m-%d').date()
                sj.week1_start_date = d
                sj.save()
                _create_13_weeks(sj)
                messages.success(request, f'Đã set tuần 1 và tạo 13 tuần cho {sj.subject} {sj.year}.')
            except (SubjectJournal.DoesNotExist, ValueError) as e:
                messages.error(request, 'Ngày không hợp lệ hoặc sổ không tồn tại.')
            return redirect('adminpage:journal_manager_dashboard')
        if action == 'toggle_week_lock':
            week_id = request.POST.get('week_id')
            journal_id = request.POST.get('journal_id')
            try:
                w = JournalWeek.objects.get(id=week_id)
                is_expired = w.end_date < date.today()
                effective_locked = w.is_locked or (is_expired and not w.allow_late_edit)
                if effective_locked:
                    # Mở lại: nếu quá hạn thì bật cờ cho phép sửa quá hạn
                    w.is_locked = False
                    if is_expired:
                        w.allow_late_edit = True
                else:
                    # Khóa lại: tuần quá hạn sẽ quay về cơ chế tự khóa
                    w.is_locked = True
                    w.allow_late_edit = False
                w.save()
                is_now_locked = w.is_locked or (is_expired and not w.allow_late_edit)
                messages.success(request, f'Tuần {w.week_number} đã {"khóa" if is_now_locked else "mở lại"}.')
            except JournalWeek.DoesNotExist:
                messages.error(request, 'Tuần không tồn tại.')
            if journal_id:
                return redirect('adminpage:journal_subject_detail', journal_id=journal_id)
            return redirect('adminpage:journal_manager_dashboard')

    context = {
        'journals': journals,
        'subject_choices': subject_choices,
        'current_year': current_year,
    }
    return render(request, 'adminpageSIMCODE/journal_manager_dashboard.html', context)


def journal_subject_detail(request, journal_id):
    """Chi tiết sổ đầu bài: danh sách hàng, tuần, khóa/mở tuần."""
    err = _require_journal_admin(request)
    if err:
        return err
    from datetime import date
    journal = get_object_or_404(SubjectJournal, id=journal_id)
    rows = JournalRow.objects.filter(subject_journal=journal).order_by('row_order')
    weeks = JournalWeek.objects.filter(subject_journal=journal).order_by('week_number')
    context = {'journal': journal, 'rows': rows, 'weeks': weeks, 'today': date.today()}
    return render(request, 'adminpageSIMCODE/journal_subject_detail.html', context)

def journal_thong_ke_export(request):
    """Export Excel thống kê GV ghi sổ đầu bài theo mẫu thong-ke.xlsx: Môn | Họ tên GV | Ngày dạy | Các tiết."""
    err = _require_journal_admin(request)
    if err:
        return err
    from io import BytesIO
    from datetime import date

    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        year = today.year
    try:
        week_number = int(request.GET.get('week', 1))
    except (TypeError, ValueError):
        week_number = 1

    # Tất cả entry trong tuần này (năm đã chọn)
    entries = JournalEntry.objects.filter(
        journal_row__subject_journal__year=year,
        week_number=week_number,
    ).select_related('journal_row__teacher', 'journal_row__subject_journal').order_by(
        'journal_row__subject_journal__subject',
        'journal_row__teacher__full_name',
        'lesson_date',
        'period',
    )

    # Gom theo (môn, giáo viên, ngày) -> danh sách tiết
    group = defaultdict(list)
    for e in entries:
        sj = e.journal_row.subject_journal
        teacher = e.journal_row.teacher
        key = (sj.id, sj.get_subject_display(), teacher.id, teacher.full_name, e.lesson_date)
        group[key].append(e.period)

    # Mỗi dòng: (subject_display, teacher_name, lesson_date, periods_str) — sort tiết
    rows_data = []
    for (sj_id, subject_label, _tid, teacher_name, lesson_date), periods in group.items():
        periods_str = ','.join(str(p) for p in sorted(set(periods)))
        rows_data.append((subject_label, teacher_name, lesson_date, periods_str))
    rows_data.sort(key=lambda r: (r[0], r[1], r[2]))

    wb = Workbook()
    ws = wb.active
    ws.title = f'Tuan {week_number}'
    title = f'THỐNG KÊ GIÁO VIÊN GHI SỔ ĐẦU BÀI TUẦN {week_number} NĂM HỌC {year}'
    ws.cell(row=1, column=1, value=title)
    ws.cell(row=2, column=1, value=None)
    prev_subject = None
    for idx, (subject_label, teacher_name, lesson_date, periods_str) in enumerate(rows_data, start=3):
        cell_subject = subject_label if subject_label != prev_subject else None
        if subject_label is not None:
            prev_subject = subject_label
        ws.cell(row=idx, column=1, value=cell_subject)
        ws.cell(row=idx, column=2, value=teacher_name or '')
        ws.cell(row=idx, column=3, value=lesson_date)
        ws.cell(row=idx, column=4, value=periods_str)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f'Thong-ke-so-dau-bai-tuan-{week_number}-{year}.xlsx'
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def journal_week_summary(request, journal_id, week_number):
    """Tổng hợp sổ đầu bài theo tuần: tất cả tiết đã nhập, sắp xếp theo ngày dạy + tiết."""
    err = _require_journal_admin(request)
    if err:
        return err
    journal = get_object_or_404(SubjectJournal, id=journal_id)
    week_obj = JournalWeek.objects.filter(
        subject_journal=journal, week_number=week_number
    ).first()
    if not week_obj:
        messages.error(request, f'Không tìm thấy tuần {week_number}.')
        return redirect('adminpage:journal_subject_detail', journal_id=journal_id)

    rows = JournalRow.objects.filter(subject_journal=journal).select_related('teacher').order_by('row_order')
    entries = []
    for row in rows:
        ents = JournalEntry.objects.filter(
            journal_row=row, week_number=week_number
        ).order_by('lesson_date', 'period')
        for e in ents:
            entries.append({'entry': e, 'teacher': row.teacher})
    entries.sort(key=lambda x: (x['teacher'].access_code, x['entry'].lesson_date, x['entry'].period))

    context = {
        'journal': journal,
        'week_obj': week_obj,
        'entries': entries,
    }
    return render(request, 'adminpageSIMCODE/journal_week_summary.html', context)

def journal_week_missing_export(request, journal_id, week_number):
    """Export Excel: thống kê giáo viên chưa ghi đủ sổ đầu bài trong tuần (còn bao nhiêu tiết)."""
    err = _require_journal_admin(request)
    if err:
        return err
    from io import BytesIO

    journal = get_object_or_404(SubjectJournal, id=journal_id)
    week_obj = JournalWeek.objects.filter(
        subject_journal=journal, week_number=week_number
    ).first()
    if not week_obj:
        messages.error(request, f'Không tìm thấy tuần {week_number}.')
        return redirect('adminpage:journal_subject_detail', journal_id=journal_id)

    # Số hàng (dòng) mỗi giáo viên trong sổ này
    rows_qs = JournalRow.objects.filter(subject_journal=journal).select_related('teacher')
    required = rows_qs.values(
        'teacher_id',
        'teacher__full_name',
        'teacher__access_code',
        'teacher__subject',
    ).annotate(total_rows=django_models.Count('id')).order_by('teacher__access_code')

    # Số tiết đã ghi trong tuần này của mỗi giáo viên
    actual_qs = JournalEntry.objects.filter(
        journal_row__subject_journal=journal,
        week_number=week_number,
    ).values('journal_row__teacher_id').annotate(total_entries=django_models.Count('id'))
    actual_map = {row['journal_row__teacher_id']: row['total_entries'] for row in actual_qs}

    missing_list = []
    for rec in required:
        tid = rec['teacher_id']
        total_required = rec['total_rows']
        total_actual = actual_map.get(tid, 0)
        missing = max(total_required - total_actual, 0)
        if missing > 0:
            missing_list.append({
                'teacher_code': rec['teacher__access_code'],
                'teacher_name': rec['teacher__full_name'],
                'teacher_subject': rec['teacher__subject'],
                'required': total_required,
                'actual': total_actual,
                'missing': missing,
            })

    wb = Workbook()
    ws = wb.active
    ws.title = f'Tuan {week_number}'
    header_font = Font(bold=True)
    headers = [
        'STT', 'Mã GV', 'Họ và tên giáo viên', 'Môn',
        'Số hàng (cần)', 'Số tiết đã ghi', 'Số tiết còn thiếu',
    ]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font

    for idx, row in enumerate(missing_list, start=1):
        ws.cell(row=idx + 1, column=1, value=idx)
        ws.cell(row=idx + 1, column=2, value=row['teacher_code'])
        ws.cell(row=idx + 1, column=3, value=row['teacher_name'])
        ws.cell(row=idx + 1, column=4, value=row['teacher_subject'])
        ws.cell(row=idx + 1, column=5, value=row['required'])
        ws.cell(row=idx + 1, column=6, value=row['actual'])
        ws.cell(row=idx + 1, column=7, value=row['missing'])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    subject_label = journal.get_subject_display() if hasattr(journal, 'get_subject_display') and callable(getattr(journal, 'get_subject_display')) else journal.subject
    safe_name = re.sub(r'[^\w\s-]', '', str(subject_label)).strip() or journal.subject
    filename = f'Thong-ke-chua-ghi-{safe_name}-tuan-{week_number}-{journal.year}.xlsx'
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    return response


def journal_missing_all_subjects_week_export(request):
    """Export Excel: thống kê GV còn thiếu tiết ở TẤT CẢ môn trong một tuần (theo năm + tuần)."""
    err = _require_journal_admin(request)
    if err:
        return err
    from datetime import date
    from io import BytesIO

    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        year = today.year
    try:
        week_number = int(request.GET.get('week', 1))
    except (TypeError, ValueError):
        week_number = 1

    journals = SubjectJournal.objects.filter(year=year).prefetch_related('weeks')
    rows_global = []

    for journal in journals:
        week_obj = next((w for w in journal.weeks.all() if w.week_number == week_number), None)
        if not week_obj:
            continue

        rows_qs = JournalRow.objects.filter(subject_journal=journal).select_related('teacher')
        if not rows_qs.exists():
            continue

        required = rows_qs.values(
            'teacher_id',
            'teacher__full_name',
            'teacher__access_code',
            'teacher__subject',
        ).annotate(total_rows=django_models.Count('id')).order_by('teacher__access_code')

        actual_qs = JournalEntry.objects.filter(
            journal_row__subject_journal=journal,
            week_number=week_number,
        ).values('journal_row__teacher_id').annotate(total_entries=django_models.Count('id'))
        actual_map = {row['journal_row__teacher_id']: row['total_entries'] for row in actual_qs}

        subject_label = journal.get_subject_display() if hasattr(journal, 'get_subject_display') and callable(getattr(journal, 'get_subject_display')) else journal.subject

        for rec in required:
            tid = rec['teacher_id']
            total_required = rec['total_rows']
            total_actual = actual_map.get(tid, 0)
            missing = max(total_required - total_actual, 0)
            if missing > 0:
                rows_global.append({
                    'subject': subject_label,
                    'teacher_code': rec['teacher__access_code'],
                    'teacher_name': rec['teacher__full_name'],
                    'teacher_subject': rec['teacher__subject'],
                    'required': total_required,
                    'actual': total_actual,
                    'missing': missing,
                })

    rows_global.sort(key=lambda r: (str(r['subject']), str(r['teacher_code'])))

    wb = Workbook()
    ws = wb.active
    ws.title = f'Tuan {week_number}'
    header_font = Font(bold=True)
    headers = [
        'STT', 'Môn', 'Mã GV', 'Họ và tên giáo viên',
        'Môn (từ DSGV)', 'Số hàng (cần)', 'Số tiết đã ghi', 'Số tiết còn thiếu',
    ]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font

    for idx, row in enumerate(rows_global, start=1):
        ws.cell(row=idx + 1, column=1, value=idx)
        ws.cell(row=idx + 1, column=2, value=row['subject'])
        ws.cell(row=idx + 1, column=3, value=row['teacher_code'])
        ws.cell(row=idx + 1, column=4, value=row['teacher_name'])
        ws.cell(row=idx + 1, column=5, value=row['teacher_subject'])
        ws.cell(row=idx + 1, column=6, value=row['required'])
        ws.cell(row=idx + 1, column=7, value=row['actual'])
        ws.cell(row=idx + 1, column=8, value=row['missing'])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f'Thong-ke-chua-ghi-tuan-{week_number}-{year}.xlsx'
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    return response


def journal_export_excel(request, journal_id):
    """Export sổ đầu bài 1 môn ra Excel: mỗi tuần một sheet. Không STT, tối ưu độ rộng cột để in 2 trang ngang."""
    err = _require_journal_admin(request)
    if err:
        return err
    from io import BytesIO

    journal = get_object_or_404(SubjectJournal, id=journal_id)
    weeks = JournalWeek.objects.filter(subject_journal=journal).order_by('week_number')
    if not weeks.exists():
        messages.error(request, 'Chưa có tuần nào. Set ngày bắt đầu tuần 1 trước.')
        return redirect('adminpage:journal_subject_detail', journal_id=journal_id)

    wb = Workbook()
    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']

    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')
    # Theo bố cục in thực tế (như ảnh): không cần STT
    header_row4 = [
        'Họ và tên giáo viên', 'Ngày dạy', 'Lớp dạy', 'Tiết', 'Sĩ số',
        'Học viên vắng', 'Tên bài giảng', 'NHẬN XÉT CỦA GIÁO VIÊN SAU TIẾT DẠY'
    ]
    row6_vals = [1, 2, 3, 4, 5, 6, 7, 8]
    rows_by_journal = JournalRow.objects.filter(subject_journal=journal).select_related('teacher').order_by('row_order')

    for week_obj in weeks:
        sheet_name = f"Tuần {week_obj.week_number}"
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        ws = wb.create_sheet(title=sheet_name)
        _write_journal_sheet_one_week(
            ws, week_obj, rows_by_journal,
            thin_border, header_font, header_fill, header_row4, row6_vals,
            fit_two_pages=True
        )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    subject_label = journal.get_subject_display() if hasattr(journal, 'get_subject_display') and callable(getattr(journal, 'get_subject_display')) else journal.subject
    safe_name = re.sub(r'[^\w\s-]', '', str(subject_label)).strip() or journal.subject
    filename = f"So-dau-bai-{safe_name}-{journal.year}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _write_journal_sheet_one_week(ws, week_obj, rows_by_journal, thin_border, header_font, header_fill, header_row4, row6_vals, wrap_lop_vang=False, fit_two_pages=True):
    """Ghi một sheet sổ đầu bài cho một tuần: header + dữ liệu. Không STT, tối ưu độ rộng cột để phủ hết 2 trang ngang."""
    # Cột A-H: A=Họ tên, B=Ngày, C=Lớp, D=Tiết, E=Sĩ số, F=Học viên vắng, G=Tên bài, H=Nhận xét
    # Style giống dashboard (journal_week_summary.html): font 13, border 1px, header nền xanh nhạt.
    # Chỉ cần đảm bảo cột gọn 1 trang ngang; 2 cột cuối rộng nhất.
    col_widths = [22, 12, 14, 6, 6, 18, 28, 36]
    for c, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w

    # Lấy tên môn hiển thị để ghi tiêu đề lớn
    subject_label = ''
    if rows_by_journal:
        sj = rows_by_journal[0].subject_journal
        if hasattr(sj, 'get_subject_display') and callable(getattr(sj, 'get_subject_display')):
            subject_label = sj.get_subject_display()
        else:
            subject_label = str(sj.subject)

    # Tiêu đề tuần (hàng 1) trải ngang toàn bảng để không bị cụt
    ws.merge_cells('A1:H1')
    title_cell = ws.cell(
        row=1,
        column=1,
        value=f"Tuần: {week_obj.week_number}   Từ ngày: {week_obj.start_date.strftime('%d/%m/%Y')}   Đến ngày: {week_obj.end_date.strftime('%d/%m/%Y')}"
    )
    title_cell.border = thin_border
    title_cell.alignment = Alignment(horizontal='left', vertical='center')

    # Hàng 2-3: tiêu đề lớn ÔN THI TỐT NGHIỆP...
    ws.merge_cells('A2:H3')
    big_title = f"ÔN THI TỐT NGHIỆP THPT NĂM 2026 - MÔN {subject_label.upper() if subject_label else ''}"
    big_title_cell = ws.cell(row=2, column=1, value=big_title)
    big_title_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    big_title_cell.font = Font(name='Times New Roman', bold=True, size=14)

    for col, h in enumerate(header_row4, start=1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        # Header căn giữa
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[4].height = 18
    for col_idx, val in enumerate(row6_vals, start=1):
        cell = ws.cell(row=6, column=col_idx, value=val)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        # Hàng 6 (số thứ tự cột) căn giữa
        cell.alignment = Alignment(horizontal='center', vertical='center')

    entries = []
    for row in rows_by_journal:
        for e in JournalEntry.objects.filter(journal_row=row, week_number=week_obj.week_number).order_by('lesson_date', 'period'):
            entries.append({'entry': e, 'teacher': row.teacher})
    entries.sort(key=lambda x: (x['teacher'].access_code, x['entry'].lesson_date, x['entry'].period))

    for offset, item in enumerate(entries):
        e, t = item['entry'], item['teacher']
        row_num = 7 + offset
        classes_val = (e.classes_taught or '').strip()
        absent_val = (e.absent_students or '').strip()
        if absent_val in ('0', '00'):
            absent_val = ''

        data_cols = [
            t.full_name or '',
            e.lesson_date.strftime('%d/%m/%Y') if e.lesson_date else '',
            classes_val,
            e.period or '',
            e.student_count if e.student_count is not None else '',
            absent_val,
            e.lesson_title or '',
            e.comment or ''
        ]
        for col, val in enumerate(data_cols, start=1):
            cell = ws.cell(row=row_num, column=col, value=val)
            cell.border = thin_border
            # Canh giống dashboard: Ngày/Tiết/Sĩ số center; còn lại left.
            if col in (2, 4, 5):  # Ngày, Tiết, Sĩ số
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)
            else:
                # Giống dashboard: nội dung dài tự xuống dòng trong ô
                wrap = col in (3, 6, 7, 8)  # Lớp dạy, HV vắng, Tên bài, Nhận xét
                # Riêng cột Lớp (col=3) căn giữa theo chiều dọc
                v_align = 'center' if col == 3 else ('top' if wrap else 'center')
                cell.alignment = Alignment(
                    horizontal='left',
                    vertical=v_align,
                    wrap_text=wrap
                )

    if fit_two_pages:
        # Vùng in + lặp lại header cho trang 2
        last_row = max(ws.max_row, 7)
        ws.print_area = f"A1:H{last_row}"
        ws.print_title_rows = "1:6"

        # In: cột gọn trong 1 trang ngang, hàng tối đa 2 trang dọc
        ws.page_setup.orientation = 'portrait'
        ws.page_setup.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 2

        # Lề
        ws.page_margins.left = 0.2
        ws.page_margins.right = 0.2
        ws.page_margins.top = 0.4
        ws.page_margins.bottom = 0.4
        ws.print_options.horizontalCentered = False


def journal_export_excel_all_week(request):
    """Export sổ đầu bài: 1 file Excel, 1 sheet = 1 môn, theo tuần đã chọn. Autofit, in vừa 2 trang, Lớp/Học viên vắng xuống dòng."""
    err = _require_journal_admin(request)
    if err:
        return err
    from io import BytesIO
    from datetime import date

    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        year = today.year
    try:
        week_number = int(request.GET.get('week', 1))
    except (TypeError, ValueError):
        week_number = 1

    # Tất cả sổ đầu bài (môn) trong năm có tuần này
    journals = SubjectJournal.objects.filter(year=year).prefetch_related('weeks')
    journals_with_week = [j for j in journals if any(w.week_number == week_number for w in j.weeks.all())]
    if not journals_with_week:
        messages.error(request, f'Năm {year} không có sổ đầu bài nào có tuần {week_number}.')
        return redirect('adminpage:journal_manager_dashboard')

    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')
    header_row4 = [
        'Họ và tên giáo viên', 'Ngày dạy', 'Lớp dạy', 'Tiết', 'Sĩ số',
        'Học viên vắng', 'Tên bài giảng', 'NHẬN XÉT CỦA GIÁO VIÊN SAU TIẾT DẠY'
    ]
    row6_vals = [1, 2, 3, 4, 5, 6, 7, 8]

    wb = Workbook()
    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']

    for journal in journals_with_week:
        week_obj = next((w for w in journal.weeks.all() if w.week_number == week_number), None)
        if not week_obj:
            continue
        subject_label = journal.get_subject_display() if hasattr(journal, 'get_subject_display') and callable(getattr(journal, 'get_subject_display')) else journal.subject
        sheet_name = re.sub(r'[^\w\s-]', '', str(subject_label)).strip() or journal.subject
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        ws = wb.create_sheet(title=sheet_name)
        rows_by_journal = JournalRow.objects.filter(subject_journal=journal).select_related('teacher').order_by('row_order')
        _write_journal_sheet_one_week(
            ws, week_obj, rows_by_journal,
            thin_border, header_font, header_fill, header_row4, row6_vals,
            fit_two_pages=True
        )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f"So-dau-bai-tat-ca-mon-tuan-{week_number}-{year}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def import_journal_dsgv(request):
    """Import DSGV: Mã GV, Họ tên, Môn, Số lớp. Tạo sổ môn nếu chưa có, tạo GV + hàng (số lớp × 2)."""
    err = _require_journal_admin(request)
    if err:
        return err
    from datetime import date
    current_year = date.today().year
    if request.method == 'POST' and request.FILES.get('dsgv_file'):
        try:
            import pandas as pd
            df = pd.read_excel(request.FILES['dsgv_file'], header=0)
            if df.shape[1] < 4:
                messages.error(request, 'File cần ít nhất 4 cột: Mã GV, Họ và tên, Môn, Số lớp.')
                return redirect('adminpage:import_journal_dsgv')
            df.columns = [str(c).strip() for c in df.columns]
            col_map = {}
            for i, c in enumerate(df.columns):
                c_lower = str(c).lower()
                if 'mã' in c_lower or 'ma' in c_lower:
                    col_map['code'] = i
                elif 'họ' in c_lower or 'tên' in c_lower or 'tên' in c_lower:
                    col_map['name'] = i
                elif 'môn' in c_lower or 'mon' in c_lower:
                    col_map['subject'] = i
                elif 'số lớp' in c_lower or 'so lop' in c_lower or 'lớp' in c_lower:
                    col_map['num_classes'] = i
            if 'code' not in col_map or 'name' not in col_map or 'subject' not in col_map:
                messages.error(request, 'File cần cột Mã GV, Họ và tên, Môn.')
                return redirect('adminpage:import_journal_dsgv')
            num_created = 0
            num_rows_created = 0
            for _, row in df.iterrows():
                code = str(row.iloc[col_map['code']]).strip()
                name = str(row.iloc[col_map['name']]).strip()
                subject_raw = str(row.iloc[col_map['subject']]).strip()
                subject_code = normalize_subject_code(subject_raw)
                num_classes = 1
                if 'num_classes' in col_map:
                    try:
                        num_classes = max(1, int(float(row.iloc[col_map['num_classes']])))
                    except (ValueError, TypeError):
                        pass
                if not code or not name or not subject_raw:
                    continue
                teacher, created = JournalTeacher.objects.update_or_create(
                    access_code=code, defaults={'full_name': name, 'subject': subject_raw, 'num_classes': num_classes}
                )
                if created:
                    num_created += 1
                sj, _ = SubjectJournal.objects.get_or_create(subject=subject_code, year=current_year)
                existing_rows = JournalRow.objects.filter(subject_journal=sj, teacher=teacher).count()
                if existing_rows == 0:
                    max_order = JournalRow.objects.filter(subject_journal=sj).aggregate(
                        m=django_models.Max('row_order')
                    )['m'] or 0
                    for r in range(teacher.num_rows()):
                        JournalRow.objects.create(subject_journal=sj, teacher=teacher, row_order=max_order + r + 1)
                        num_rows_created += 1
            messages.success(request, f'Đã import: {num_created} GV mới, {num_rows_created} hàng.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
        return redirect('adminpage:journal_manager_dashboard')
    return render(request, 'adminpageSIMCODE/import_journal_dsgv.html', {})


def import_journal_dsl(request):
    """Import DSL: cột Lớp -> JournalClass."""
    err = _require_journal_admin(request)
    if err:
        return err
    if request.method == 'POST' and request.FILES.get('dsl_file'):
        try:
            import pandas as pd
            df = pd.read_excel(request.FILES['dsl_file'], header=0)
            col_class = None
            for i, c in enumerate(df.columns):
                if 'lớp' in str(c).lower() and 'chủ nhiệm' not in str(c).lower():
                    col_class = i
                    break
            if col_class is None:
                messages.error(request, 'Không tìm thấy cột Lớp.')
                return redirect('adminpage:import_journal_dsl')
            num = 0
            for _, row in df.iterrows():
                val = str(row.iloc[col_class]).strip()
                if val and len(val) <= 50:
                    _, c = JournalClass.objects.get_or_create(name=val)
                    if c:
                        num += 1
            messages.success(request, f'Đã thêm {num} lớp mới.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
        return redirect('adminpage:journal_manager_dashboard')
    return render(request, 'adminpageSIMCODE/import_journal_dsl.html', {})


