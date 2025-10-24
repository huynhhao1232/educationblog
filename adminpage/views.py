import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
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
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from openpyxl import load_workbook

# Create your views here.

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
                else:
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