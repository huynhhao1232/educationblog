from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from itertools import zip_longest
from django.http import JsonResponse, Http404
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
# Create your views here.
def group_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def getHomePage(request):
    categories = Category.objects.filter(enable = True)
    postTT = Post.objects.filter(enable = True, category = 1).order_by('-createdate')[:3]
    posttt = Post.objects.filter(enable = True, category = 4).order_by('-createdate')[:3]
    postViews = Post.objects.filter(enable=True).order_by('-views')[:10]
    notifications_HV = Post.objects.filter(category = 3).order_by('-createdate')[:4]
    notifination_news = Post.objects.filter(enable = True).exclude(category=3).order_by('-createdate')[:6]
    lichcongtacs = Post.objects.filter(category = 2).order_by('-createdate')[:6]
    context = {'categories': categories, 'postTT': postTT, 'notifications_HV': notifications_HV, 'notification_news': notifination_news, 'lichcongtacs': lichcongtacs, 'postViews': postViews, 'posttt': posttt}
    return render(request, 'homepage/index.html', context)

def getCategory(request, category_id):
    categories = Category.objects.filter(enable = True)
    lichcongtac = LichCongTac.objects.filter(namhoc = False).order_by('-createdate')
    posts = Post.objects.filter(category = category_id).order_by('-createdate')
    context = {'category_id': category_id,'posts': posts, 'categories': categories }

    return render(request, 'homepage/list-post.html', context)
def getViewPost(request, post_id):
    try:
        # Lấy bài viết và kiểm tra trạng thái
        post = get_object_or_404(Post, id=post_id)
        if not post.enable:
            raise Http404("Bài viết này không tồn tại hoặc đã bị ẩn")

        # Lấy danh mục
        categories = Category.objects.filter(enable=True)

        try:
            category = Category.objects.get(id=post.category.id)
            # Lấy các bài viết liên quan
            related_posts = Post.objects.filter(
                category=category,
                enable=True
            ).exclude(id=post_id).order_by('-createdate')[:5]
        except ObjectDoesNotExist:
            category = None
            related_posts = []

        # Lấy files đính kèm
        files = UploadedFile.objects.filter(post=post)
        file_names = [file.pdf_file.name.split('/')[-1] for file in files] if files else None

        # Tăng lượt xem
        post.views += 1
        post.save(update_fields=['views'])

        context = {
            'categories': categories,
            'post': post,
            'files': files,
            'filenames': file_names,
            'category': category,
            'posts': related_posts
        }
        return render(request, 'homepage/view-post.html', context)

    except Http404:
        # Xử lý khi bài viết không tồn tại
        categories = Category.objects.filter(enable=True)
        context = {
            'categories': categories,
            'error_message': 'Bài viết này không tồn tại hoặc đã bị ẩn',
        }
        return render(request, 'homepage/404.html', context, status=404)

    except Exception as e:
        # Log lỗi nếu cần
        print(f"Error in getViewPost: {str(e)}")
        categories = Category.objects.filter(enable=True)
        context = {
            'categories': categories,
            'error_message': 'Đã có lỗi xảy ra, vui lòng thử lại sau',
        }
        return render(request, 'homepage/error.html', context, status=500)

def getCCTC(request, pb_id):
    categories = Category.objects.filter(enable = True)
    pbs = PhongBan.objects.all().exclude(id = pb_id)
    pb = PhongBan.objects.get(id = pb_id)
    pb_gv = PB_GV.objects.filter(phongban__id = pb_id, phongban__enable = True, gv__enable = True)
    pb_gv2 = PB_GV.objects.filter(phongban__id = pb_id, phongban__enable = True, gv__bac = 2, gv__enable = True)
    pb_gv_grouped = group_list(list(pb_gv2), 2)
    context = {'categories': categories, 'pbs':pbs, 'pb':pb, 'pb_gv': pb_gv, 'pb_gv_grouped': pb_gv_grouped}
    return render(request, 'homepage/cctc.html', context)

def getForum(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        post_title = request.POST.get('post-title')
        post_content = request.POST.get('post-content')
        post = PostForum.objects.create(name = name, title = post_title, content = post_content)
        post.save()
        return redirect('homepage:forum')
    categories = Category.objects.filter(enable = True)
    posts = PostForum.objects.all().order_by('-createdate')
    context = {'categories': categories, 'posts':posts}
    return render(request, 'homepage/forumBase.html', context)

def getForumView(request, forum_id):
    categories = Category.objects.filter(enable = True)
    post = PostForum.objects.get(id = forum_id).order_by('-createdate')
    context = {'post':post, 'categories': categories}
    return render(request, 'homepage/forumView.html',context)

def getActivity(request):
    # Lấy tất cả các bài viết được kích hoạt
    posts = Post.objects.filter(category__id = 8).order_by('-createdate')
    categories = Category.objects.filter(enable = True)
    # Tạo một danh sách chứa thông tin về từng bài post và hình ảnh liên quan
    post_data = []
    for post in posts:
        # Lấy tất cả hình ảnh liên quan đến bài post
        files = UploadedFile.objects.filter(post=post)
        post_data.append({
            'post': post,
            'files': files,
        })

    # Truyền dữ liệu vào template
    context = {
        'post_data': post_data,
        'categories': categories
    }

    return render(request, 'homepage/activity.html', context)

def getAdmission(request):
    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        # Xử lý điểm dựa vào năm tốt nghiệp
        graduation_year = data.get('graduation_year')
        exam_score = None
        avg_score = None

        # Xử lý điểm các lớp THCS
        math_score_6 = data.get('math_score_6')
        literature_score_6 = data.get('literature_score_6')
        math_score_7 = data.get('math_score_7')
        literature_score_7 = data.get('literature_score_7')
        math_score_8 = data.get('math_score_8')
        literature_score_8 = data.get('literature_score_8')
        math_score_9 = data.get('math_score_9')
        literature_score_9 = data.get('literature_score_9')

        if graduation_year == '2025':
            exam_score = data.get('examScore')
            if exam_score and exam_score.strip():  # Check if not empty
                try:
                    exam_score = Decimal(exam_score)
                except (ValueError, InvalidOperation):
                    exam_score = None
        else:
            avg_score = data.get('avg_score')
            if avg_score and avg_score.strip():  # Check if not empty
                try:
                    avg_score = Decimal(avg_score)
                except (ValueError, InvalidOperation):
                    avg_score = None

        # Chuyển đổi điểm các lớp THCS sang Decimal
        if math_score_6 and math_score_6.strip():
            try:
                math_score_6 = Decimal(math_score_6)
            except (ValueError, InvalidOperation):
                math_score_6 = None
        else:
            math_score_6 = None

        if literature_score_6 and literature_score_6.strip():
            try:
                literature_score_6 = Decimal(literature_score_6)
            except (ValueError, InvalidOperation):
                literature_score_6 = None
        else:
            literature_score_6 = None

        if math_score_7 and math_score_7.strip():
            try:
                math_score_7 = Decimal(math_score_7)
            except (ValueError, InvalidOperation):
                math_score_7 = None
        else:
            math_score_7 = None

        if literature_score_7 and literature_score_7.strip():
            try:
                literature_score_7 = Decimal(literature_score_7)
            except (ValueError, InvalidOperation):
                literature_score_7 = None
        else:
            literature_score_7 = None

        if math_score_8 and math_score_8.strip():
            try:
                math_score_8 = Decimal(math_score_8)
            except (ValueError, InvalidOperation):
                math_score_8 = None
        else:
            math_score_8 = None

        if literature_score_8 and literature_score_8.strip():
            try:
                literature_score_8 = Decimal(literature_score_8)
            except (ValueError, InvalidOperation):
                literature_score_8 = None
        else:
            literature_score_8 = None

        if math_score_9 and math_score_9.strip():
            try:
                math_score_9 = Decimal(math_score_9)
            except (ValueError, InvalidOperation):
                math_score_9 = None
        else:
            math_score_9 = None

        if literature_score_9 and literature_score_9.strip():
            try:
                literature_score_9 = Decimal(literature_score_9)
            except (ValueError, InvalidOperation):
                literature_score_9 = None
        else:
            literature_score_9 = None

        try:
            # Lấy các ForeignKey từ form
            campus = Campus.objects.get(id=data['campus_id'])
            shift = Shift.objects.get(id=data['shift_id'])
            subject_group = SubjectGroup.objects.get(id=data['subject_group_id'])

            # Kiểm tra và cập nhật số lượng đăng ký
            campus_shift_group = CampusShiftGroup.objects.get(
                campus=campus,
                shift=shift,
                subject_group=subject_group
            )

            # Kiểm tra nếu còn chỗ
            if campus_shift_group.registration_count <= 0:
                return JsonResponse({
                    'error': 'Tổ hợp môn này đã hết chỗ'
                }, status=400)

            # Giảm số lượng đăng ký đi 1
            campus_shift_group.registration_count -= 1
            campus_shift_group.save()

            # Tạo bản ghi mới
            obj = AdmissionForm.objects.create(
                full_name = data.get('full_name', ''),
                gender = data.get('gender', ''),
                ethnicity = data.get('ethnicity', ''),
                birthday = data.get('birthday', ''),
                religion = data.get('religion', ''),
                email = data.get('email', ''),
                phone = data.get('phone', ''),

                cccd_province = data.get('cccd_province', ''),
                cccd_district = data.get('cccd_district', ''),
                cccd_ward = data.get('cccd_ward', ''),
                cccd_town = data.get('cccd_town', ''),

                hometown_province = data.get('hometown_province', ''),

                birth_reg_province = data.get('birth_reg_province', ''),
                birth_reg_district = data.get('birth_reg_district', ''),
                birth_reg_ward = data.get('birth_reg_ward', ''),
                birth_reg_town = data.get('birth_reg_town', ''),

                birth_place_province = data.get('birth_place_province', ''),
                birth_place_district = data.get('birth_place_district', ''),
                birth_place_ward = data.get('birth_place_ward', ''),
                birth_place_facility = data.get('birth_place_facility', ''),

                current_province = data.get('current_province', ''),
                current_district = data.get('current_district', ''),
                current_ward = data.get('current_ward', ''),

                id_number = data.get('id_number', ''),
                id_issued_date = data.get('id_issued_date', ''),
                id_issued_place = data.get('id_issued_place', ''),

                graduation_year = graduation_year,
                graduation_school = data.get('graduation_school', ''),
                graduation_rank = data.get('graduation_rank', ''),
                exam_score = exam_score,
                conduct = data.get('conduct2025') or data.get('conductBefore') or '',
                avg_score = avg_score,

                # Điểm các lớp THCS
                math_score_6 = math_score_6,
                literature_score_6 = literature_score_6,
                math_score_7 = math_score_7,
                literature_score_7 = literature_score_7,
                math_score_8 = math_score_8,
                literature_score_8 = literature_score_8,
                math_score_9 = math_score_9,
                literature_score_9 = literature_score_9,

                current_job = data.get('current_job', ''),

                father_name = data.get('father_name', ''),
                father_job = data.get('father_job', ''),
                father_birth = data.get('father_birth', ''),
                father_phone = data.get('father_phone', ''),

                mother_name = data.get('mother_name', ''),
                mother_job = data.get('mother_job', ''),
                mother_birth = data.get('mother_birth', ''),
                mother_phone = data.get('mother_phone', ''),

                campus = campus,
                shift = shift,
                subject_group = subject_group,

                # Add file uploads
                cccd_image = files.get('cccd_image'),
                school_record_image = files.get('school_record_image')
            )
            # Gửi email xác nhận nếu có email
            if obj.email:
                send_mail(
                    subject='Xác nhận đăng ký nhập học',
                    message=f'Cảm ơn {obj.full_name} đã đăng ký nhập học tại Trung tâm GDNN-GDTX Thủ Đức. Chúng tôi đã nhận được đơn đăng ký của bạn và sẽ liên hệ lại trong thời gian sớm nhất. Mọi thắc mắc xin liên hệ SĐT: 0338968006 (thầy Hào)',
                    from_email=settings.EMAIL_HOST_USER,  # Sử dụng DEFAULT_FROM_EMAIL trong settings
                    recipient_list=[obj.email],
                    fail_silently=True,
                )
            return redirect('/admission/?success=1')

        except CampusShiftGroup.DoesNotExist:
            return JsonResponse({
                'error': 'Không tìm thấy tổ hợp môn này'
            }, status=404)
        except Exception as e:
            print(f"Error in admission: {str(e)}")
            return JsonResponse({
                'error': 'Có lỗi xảy ra khi xử lý đơn đăng ký'
            }, status=500)

    campuses = Campus.objects.all()
    subject_groups = SubjectGroup.objects.all()
    shifts = Shift.objects.all()
    return render(request, 'homepage/admission.html', {
        'campuses': campuses,
        'subject_groups': subject_groups,
        'shifts': shifts
    })


def get_subject_groups_api(request):
    data = {}
    for row in CampusShiftGroup.objects.select_related('campus', 'shift', 'subject_group'):
        key = f"{row.campus.code}_{row.shift.code}"
        if key not in data:
            data[key] = []
        data[key].append({
            "code": row.subject_group.code,
            "description": row.subject_group.description,
            "subjects": row.subject_group.subjects.split(", "),
            "classes": row.number_of_classes,
            "registrations": row.registration_count,
        })
    return JsonResponse(data)
def get_shifts_by_campus(request, campus_id):
    shift_ids = CampusShiftGroup.objects.filter(campus_id=campus_id).values_list('shift_id', flat=True).distinct()
    shifts = Shift.objects.filter(id__in=shift_ids)
    data = [{'id': s.id, 'name': s.name} for s in shifts]
    return JsonResponse({'shifts': data})

def get_subjectgroups_by_campus_shift(request, campus_id, shift_id):
    try:
        # Lấy campus và shift
        campus = Campus.objects.get(id=campus_id)
        shift = Shift.objects.get(id=shift_id)

        # Lấy các tổ hợp môn và số lượng còn lại
        campus_shift_groups = CampusShiftGroup.objects.filter(
            campus=campus,
            shift=shift
        ).select_related('subject_group')

        subject_groups_data = []
        for csg in campus_shift_groups:
            subject_group = csg.subject_group
            # Số lượng còn lại chính là registration_count
            remaining_count = csg.registration_count

            subject_groups_data.append({
                'id': subject_group.id,
                'code': subject_group.code,
                'subjects': [s.strip() for s in subject_group.subjects.split(',')],
                'remaining_count': remaining_count
            })

        return JsonResponse({
            'subject_groups': subject_groups_data
        })
    except (Campus.DoesNotExist, Shift.DoesNotExist) as e:
        print(f"Error in get_subjectgroups_by_campus_shift: {str(e)}")
        return JsonResponse({'error': 'Campus or Shift not found'}, status=404)
    except Exception as e:
        print(f"Unexpected error in get_subjectgroups_by_campus_shift: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def check_cccd_exists(request, cccd):
    exists = AdmissionForm.objects.filter(id_number=cccd).exists()
    return JsonResponse({'exists': exists})

def login_view(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('homepage:Homepage')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # If remember me is not checked, expire session when browser closes
            if not remember:
                request.session.set_expiry(0)

            # Redirect to different pages based on user type
            if user.is_staff:
                return redirect('adminpage:adminpagee')  # Redirect to admission management for staff
            else:
                return redirect('homepage:Homepage')  # Redirect to homepage for regular users
        else:
            return render(request, 'homepage/login.html', {
                'error_message': 'Tên đăng nhập hoặc mật khẩu không đúng!'
            })

    return render(request, 'homepage/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('homepage:login')

from .forms import StudentCodeForm, StudentExamRegistrationForm
from .models import Student, StudentExamRegistration, RegistrationHistory

def student_exam_registration_step1(request):
    """Bước 1: Nhập mã học viên"""
    if request.method == 'POST':
        form = StudentCodeForm(request.POST)
        if form.is_valid():
            student_code = form.cleaned_data['student_code']
            try:
                # Tìm học viên theo mã
                student = Student.objects.get(student_code=student_code)
                # Lưu mã học viên vào session để dùng ở bước 2
                request.session['student_code'] = student_code
                return redirect('homepage:student_exam_registration_step2')
            except Student.DoesNotExist:
                form.add_error('student_code', 'Mã học viên không tồn tại trong hệ thống')
    else:
        form = StudentCodeForm()

    categories = Category.objects.filter(enable=True)
    context = {
        'form': form,
        'categories': categories,
        'step': 1
    }
    return render(request, 'homepage/student_exam_registration_step1.html', context)

def student_exam_registration_step2(request):
    """Bước 2: Điền thông tin đăng ký"""
    # Kiểm tra xem có mã học viên trong session không
    student_code = request.session.get('student_code')
    if not student_code:
        return redirect('homepage:student_exam_registration_step1')

    try:
        student = Student.objects.get(student_code=student_code)
    except Student.DoesNotExist:
        del request.session['student_code']
        return redirect('homepage:student_exam_registration_step1')

    # Kiểm tra xem học viên đã đăng ký chưa
    existing_registration = None
    try:
        existing_registration = StudentExamRegistration.objects.get(student=student)
    except StudentExamRegistration.DoesNotExist:
        pass

    # Kiểm tra xem học viên có thể cập nhật không (tối đa 2 lần)
    can_update = True
    if existing_registration:
        can_update = existing_registration.can_update()

    if request.method == 'POST':
        # Nếu đã quá 2 lần cập nhật, không cho phép cập nhật nữa
        if existing_registration and not can_update:
            categories = Category.objects.filter(enable=True)
            context = {
                'form': None,
                'student': student,
                'categories': categories,
                'step': 2,
                'has_existing_registration': True,
                'existing_registration': existing_registration,
                'can_update': False,
                'error_message': 'Bạn đã cập nhật thông tin đăng ký quá 2 lần. Bạn chỉ có thể xem thông tin đăng ký.'
            }
            return render(request, 'homepage/student_exam_registration_step2.html', context)

        if existing_registration:
            # Cập nhật thông tin đã có
            form = StudentExamRegistrationForm(request.POST, subject_group=student.subject_group, instance=existing_registration)
        else:
            # Tạo mới
            form = StudentExamRegistrationForm(request.POST, subject_group=student.subject_group)

        if form.is_valid():
            # Lưu thông tin đăng ký
            registration = form.save(commit=False)
            registration.student = student

            # Lưu thông tin cũ trước khi cập nhật (nếu là cập nhật)
            old_email = None
            old_phone = None
            old_exam_subjects = []
            action_type = 'created'
            update_count_value = 0

            if existing_registration:
                # Lưu thông tin cũ
                old_email = existing_registration.email
                old_phone = existing_registration.phone
                old_exam_subjects = existing_registration.exam_subjects if existing_registration.exam_subjects else []

                # Cập nhật số lần cập nhật
                update_count_value = existing_registration.update_count + 1
                registration.update_count = update_count_value
                action_type = 'updated'
            else:
                # Lần đầu đăng ký, update_count = 0
                registration.update_count = 0
                update_count_value = 0

            # Cập nhật ngày đăng ký
            registration.registration_date = timezone.now()

            # Lưu registration trước
            registration.save()

            # Lưu lịch sử cập nhật
            RegistrationHistory.objects.create(
                registration=registration,
                old_email=old_email,
                old_phone=old_phone,
                old_exam_subjects=old_exam_subjects,
                new_email=registration.email,
                new_phone=registration.phone,
                new_exam_subjects=registration.exam_subjects if registration.exam_subjects else [],
                action_type=action_type,
                update_count=update_count_value
            )

            # Xóa mã học viên khỏi session
            del request.session['student_code']

            # Hiển thị thông báo thành công
            categories = Category.objects.filter(enable=True)
            context = {
                'student': student,
                'registration': registration,
                'categories': categories,
                'success': True,
                'updated': existing_registration is not None
            }
            return render(request, 'homepage/student_exam_registration_success.html', context)
    else:
        if existing_registration:
            # Kiểm tra nếu không thể cập nhật nữa, chỉ hiển thị thông tin
            if not can_update:
                form = None
            else:
                # Hiển thị form với dữ liệu đã có để cập nhật
                form = StudentExamRegistrationForm(subject_group=student.subject_group, instance=existing_registration)
        else:
            # Form trống để điền mới
            form = StudentExamRegistrationForm(subject_group=student.subject_group)

    categories = Category.objects.filter(enable=True)
    context = {
        'form': form,
        'student': student,
        'categories': categories,
        'step': 2,
        'has_existing_registration': existing_registration is not None,
        'existing_registration': existing_registration,
        'can_update': can_update
    }
    return render(request, 'homepage/student_exam_registration_step2.html', context)

# ---------- Sổ đầu bài số ----------

def _get_school_config():
    """Lấy cấu hình ngày/tuần hiện tại (một bản ghi, fallback nếu chưa có)."""
    from adminpage.models import SchoolConfig
    config = SchoolConfig.objects.first()
    if config:
        return config.current_date, config.current_week
    from datetime import date
    today = date.today()
    # Tuần trong năm (ISO): 1-53
    week = today.isocalendar()[1]
    return today, week


def journal_login(request):
    """Form nhập Mã số giáo viên. POST: kiểm tra mã, lưu session, chuyển đến Sổ đầu bài cá nhân."""
    from adminpage.models import JournalTeacher
    categories = Category.objects.filter(enable=True)
    error = None
    if request.method == 'POST':
        code = (request.POST.get('access_code') or '').strip()
        if not code:
            error = 'Vui lòng nhập mã số.'
        else:
            teacher = JournalTeacher.objects.filter(access_code=code).first()
            if teacher:
                request.session['journal_teacher_id'] = teacher.id
                return redirect('homepage:journal_personal')
            error = 'Mã số không hợp lệ.'
    context = {'error': error, 'categories': categories}
    return render(request, 'homepage/journal_login.html', context)


def journal_personal(request):
    """Sổ đầu bài cá nhân: theo JournalRow/JournalEntry, tuần từ SubjectJournal."""
    from adminpage.models import (
        JournalTeacher, JournalRow, JournalEntry, JournalClass,
        SubjectJournal, JournalWeek, normalize_subject_code,
    )
    from datetime import date, timedelta

    teacher_id = request.session.get('journal_teacher_id')
    if not teacher_id:
        return redirect('homepage:journal_login')
    teacher = get_object_or_404(JournalTeacher, id=teacher_id)
    today = date.today()
    current_year = today.year
    subject_code = normalize_subject_code(teacher.subject)
    subject_raw_lower = str(teacher.subject).strip().lower()
    categories = Category.objects.filter(enable=True)

    # Tìm SubjectJournal cho môn + năm (thử cả mã chuẩn và tên gốc vì DB có thể lưu "kt-pl" hoặc "ktpl")
    subject_journal = SubjectJournal.objects.filter(
        subject=subject_code, year=current_year
    ).first()
    if not subject_journal and subject_raw_lower != subject_code:
        subject_journal = SubjectJournal.objects.filter(
            subject=subject_raw_lower, year=current_year
        ).first()
    if not subject_journal:
        context = {
            'teacher': teacher, 'categories': categories,
            'error': 'Chưa có sổ đầu bài cho môn của bạn trong năm nay. Liên hệ quản trị viên.',
        }
        return render(request, 'homepage/journal_personal.html', context)

    # Danh sách tuần của sổ (cho phép GV xem lại tuần trước)
    all_weeks = list(
        JournalWeek.objects.filter(subject_journal=subject_journal).order_by('week_number')
    )
    # Tuần chứa hôm nay (nếu có)
    week_today_obj = JournalWeek.objects.filter(
        subject_journal=subject_journal,
        start_date__lte=today,
        end_date__gte=today,
    ).first()

    # Danh sách hàng của giáo viên
    rows = JournalRow.objects.filter(
        subject_journal=subject_journal, teacher=teacher
    ).order_by('row_order')
    journal_classes = JournalClass.objects.all().order_by('name')

    # Chọn tuần hiển thị: ưu tiên query param/post, nếu không có thì lấy tuần hiện tại
    selected_week_raw = (request.GET.get('week') or request.POST.get('selected_week_number') or '').strip()
    selected_week_obj = None
    if selected_week_raw.isdigit():
        selected_week_num = int(selected_week_raw)
        selected_week_obj = next((w for w in all_weeks if w.week_number == selected_week_num), None)
    if not selected_week_obj:
        selected_week_obj = week_today_obj or (all_weeks[0] if all_weeks else None)

    week_start = week_end = current_week_num = None
    if selected_week_obj:
        week_start = selected_week_obj.start_date
        week_end = selected_week_obj.end_date
        current_week_num = selected_week_obj.week_number
        current_week_obj = selected_week_obj
        is_expired = today > week_end
        is_effective_locked = selected_week_obj.is_locked or (is_expired and not selected_week_obj.allow_late_edit)
        # Tuần quá hạn tự khóa, nhưng nếu admin mở lại (allow_late_edit=True) thì vẫn cho nhập/sửa.
        can_edit = (not is_effective_locked) and today >= week_start
    else:
        current_week_obj = None
        can_edit = False

    # POST: Lưu tiết mới (tự gán hàng đầu tiên, giới hạn theo số hàng)
    if request.method == 'POST' and can_edit and current_week_obj and not current_week_obj.is_locked:
        # Đếm số tiết đã nhập tuần này (giới hạn = số hàng của GV)
        entries_count_week = 0
        if current_week_num and rows:
            for row in rows:
                entries_count_week += JournalEntry.objects.filter(
                    journal_row=row, week_number=current_week_num
                ).count()
        max_entries = rows.count() if rows else 0

        lesson_date_str = request.POST.get('lesson_date', '').strip()
        classes_taught = request.POST.getlist('classes_taught')  # checkbox
        period = request.POST.get('period', '1')
        student_count = request.POST.get('student_count', '').strip()
        lesson_title = (request.POST.get('lesson_title') or '').strip()
        absent_students = (request.POST.get('absent_students') or '').strip()
        comment = (request.POST.get('comment') or '').strip()

        try:
            period = max(1, min(5, int(period)))
        except (ValueError, TypeError):
            period = 1

        # Kiểm tra bắt buộc (trừ học viên vắng)
        classes_str = ', '.join(c for c in classes_taught if c)
        # Tiết đôi: chọn tiết X thì tự tạo tiết X+1 với cùng nội dung (X=1..4; tiết 5 chỉ 1 ô)
        next_period = period + 1 if period < 5 else None
        slots_needed = 2 if next_period else 1
        if entries_count_week + slots_needed > max_entries:
            messages.error(
                request,
                f'Bạn chỉ có {max_entries} hàng trong tuần này. Đã nhập {entries_count_week} tiết.'
                + (f' Khi ghi tiết {period} sẽ tự tạo thêm tiết {next_period}, cần 2 ô trống.' if next_period else '')
            )
        elif not lesson_date_str or not classes_str or not lesson_title.strip() or not comment.strip():
            messages.error(request, 'Vui lòng nhập đủ: Ngày dạy, Lớp dạy, Sĩ số, Tên bài giảng, Nhận xét.')
        elif not student_count:
            messages.error(request, 'Vui lòng nhập Sĩ số.')
        else:
            try:
                sc_val = max(0, min(999, int(student_count)))
            except (ValueError, TypeError):
                sc_val = None
            if sc_val is None:
                messages.error(request, 'Sĩ số không hợp lệ.')
            else:
                journal_row = rows.first() if rows else None
                if journal_row and lesson_date_str:
                    from datetime import datetime
                    lesson_date = datetime.strptime(lesson_date_str, '%Y-%m-%d').date()
                    if week_start <= lesson_date <= week_end and lesson_date <= today:
                        JournalEntry.objects.create(
                            journal_row=journal_row,
                            week_number=current_week_num,
                            lesson_date=lesson_date,
                            period=period,
                            classes_taught=classes_str,
                            student_count=sc_val,
                            lesson_title=lesson_title,
                            absent_students=absent_students,
                            comment=comment,
                        )
                        # Tiết đôi: chọn tiết X thì tự tạo tiết X+1 với cùng nội dung (X=1..4)
                        if next_period:
                            JournalEntry.objects.create(
                                journal_row=journal_row,
                                week_number=current_week_num,
                                lesson_date=lesson_date,
                                period=next_period,
                                classes_taught=classes_str,
                                student_count=sc_val,
                                lesson_title=lesson_title,
                                absent_students=absent_students,
                                comment=comment,
                            )
                            messages.success(request, f'Đã lưu tiết {period} và tiết {next_period} với cùng nội dung.')
        target_url = f"{reverse('homepage:journal_personal')}?week={current_week_num}" if current_week_num else reverse('homepage:journal_personal')
        return redirect(target_url)

    # Ngày có thể chọn: từ đầu tuần đến min(hôm nay, cuối tuần)
    selectable_dates = []
    if week_start and week_end:
        d = week_start
        while d <= week_end and d <= today:
            selectable_dates.append(d)
            d += timedelta(days=1)

    # Lấy entries của tuần hiện tại (theo các hàng của GV)
    entries = []
    if current_week_num:
        for row in rows:
            ents = JournalEntry.objects.filter(
                journal_row=row, week_number=current_week_num
            ).order_by('lesson_date', 'period')
            entries.extend(ents)
    entries.sort(key=lambda e: (e.lesson_date, e.period))

    # Chỉ cho nhập thêm khi còn chỗ (số tiết < số hàng)
    can_add_entry = can_edit and len(entries) < rows.count()

    context = {
        'teacher': teacher,
        'subject_journal': subject_journal,
        'rows': rows,
        'all_weeks': all_weeks,
        'journal_classes': journal_classes,
        'current_week_obj': current_week_obj,
        'week_start': week_start,
        'week_end': week_end,
        'current_week_num': current_week_num or 0,
        'entries': entries,
        'selectable_dates': selectable_dates,
        'can_edit': can_edit,
        'can_add_entry': can_add_entry,
        'today': today,
        'categories': categories,
    }
    return render(request, 'homepage/journal_personal.html', context)


def journal_entry_edit(request, entry_id):
    """Sửa tiết đã nhập (chỉ khi tuần chưa khóa)."""
    from adminpage.models import (
        JournalTeacher, JournalRow, JournalEntry, JournalClass,
        SubjectJournal, JournalWeek, normalize_subject_code,
    )
    from datetime import date, timedelta, datetime

    teacher_id = request.session.get('journal_teacher_id')
    if not teacher_id:
        return redirect('homepage:journal_login')
    teacher = get_object_or_404(JournalTeacher, id=teacher_id)
    entry = get_object_or_404(JournalEntry, id=entry_id)

    # Chỉ được sửa entry thuộc hàng của mình
    if entry.journal_row.teacher_id != teacher_id:
        messages.error(request, 'Bạn không có quyền sửa tiết này.')
        return redirect('homepage:journal_personal')

    # Kiểm tra tuần có bị khóa không
    subject_journal = entry.journal_row.subject_journal
    week_obj = JournalWeek.objects.filter(
        subject_journal=subject_journal, week_number=entry.week_number
    ).first()
    today = date.today()
    is_expired = week_obj.end_date < today if week_obj else True
    is_effective_locked = (week_obj.is_locked if week_obj else True) or (is_expired and not (week_obj.allow_late_edit if week_obj else False))
    if not week_obj or is_effective_locked or today < week_obj.start_date:
        messages.error(request, 'Tuần này đang ở chế độ chỉ xem, không thể sửa.')
        return redirect('homepage:journal_personal')

    week_start, week_end = week_obj.start_date, week_obj.end_date
    journal_classes = JournalClass.objects.all().order_by('name')

    # Ngày có thể chọn
    selectable_dates = []
    d = week_start
    while d <= week_end and d <= today:
        selectable_dates.append(d)
        d += timedelta(days=1)

    # Lớp đã chọn (từ DB hoặc từ POST khi validation fail)
    entry_classes = [c.strip() for c in (entry.classes_taught or '').split(',') if c.strip()]

    if request.method == 'POST':
        lesson_date_str = request.POST.get('lesson_date', '').strip()
        classes_taught = request.POST.getlist('classes_taught')
        period = request.POST.get('period', '1')
        student_count = request.POST.get('student_count', '').strip()
        lesson_title = (request.POST.get('lesson_title') or '').strip()
        absent_students = (request.POST.get('absent_students') or '').strip()
        comment = (request.POST.get('comment') or '').strip()

        try:
            period = max(1, min(5, int(period)))
        except (ValueError, TypeError):
            period = 1

        classes_str = ', '.join(c for c in classes_taught if c)
        valid = True
        if not lesson_date_str or not classes_str or not lesson_title.strip() or not comment.strip():
            messages.error(request, 'Vui lòng nhập đủ: Ngày dạy, Lớp dạy, Sĩ số, Tên bài giảng, Nhận xét.')
            valid = False
        elif not student_count:
            messages.error(request, 'Vui lòng nhập Sĩ số.')
            valid = False
        else:
            try:
                sc_val = max(0, min(999, int(student_count)))
            except (ValueError, TypeError):
                sc_val = None
            if sc_val is None:
                messages.error(request, 'Sĩ số không hợp lệ.')
                valid = False

        if valid and lesson_date_str:
            lesson_date = datetime.strptime(lesson_date_str, '%Y-%m-%d').date()
            if week_start <= lesson_date <= week_end and lesson_date <= today:
                try:
                    sc_val = max(0, min(999, int(student_count)))
                except (ValueError, TypeError):
                    sc_val = None
                entry.lesson_date = lesson_date
                entry.period = period
                entry.classes_taught = classes_str
                entry.student_count = sc_val
                entry.lesson_title = lesson_title
                entry.absent_students = absent_students
                entry.comment = comment
                entry.save()
                messages.success(request, 'Đã cập nhật tiết.')
                return redirect('homepage:journal_personal')
        if valid:
            return redirect('homepage:journal_personal')
        # Validation failed: dùng giá trị POST để hiển thị lại form
        entry_classes = [c for c in classes_taught if c]

    categories = Category.objects.filter(enable=True)
    context = {
        'entry': entry,
        'teacher': teacher,
        'journal_classes': journal_classes,
        'selectable_dates': selectable_dates,
        'entry_classes': entry_classes,
        'week_obj': week_obj,
        'categories': categories,
    }
    return render(request, 'homepage/journal_entry_edit.html', context)


def journal_logout(request):
    """Thoát sổ đầu bài (xóa mã khỏi session)."""
    request.session.pop('journal_teacher_id', None)
    return redirect('homepage:journal_login')
