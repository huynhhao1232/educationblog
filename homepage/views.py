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
import json
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.cache import cache
import logging
from .address_data import (
    data_is_available,
    is_valid_province_code,
    load_communes,
    load_provinces,
)
from .validators import validate_vn_cccd, validate_vn_phone
from .admission_validation import validate_admission_post
# Create your views here.
logger = logging.getLogger(__name__)

ADMISSION_NEWS_CATEGORY_NAME = 'Bảng tin tuyển sinh'


def _get_admission_news_category():
    category, _ = Category.objects.get_or_create(
        name=ADMISSION_NEWS_CATEGORY_NAME,
        defaults={'enable': True},
    )
    return category


def _send_admission_confirmation_email(email, full_name):
    if not email:
        return False
    try:
        send_mail(
            subject='Xác nhận đăng ký nhập học',
            message=(
                f'Cảm ơn {full_name} đã đăng ký nhập học tại Trung tâm GDNN-GDTX Thủ Đức. '
                'Chúng tôi đã nhận được đơn đăng ký của bạn và sẽ liên hệ lại trong thời gian sớm nhất. '
                'Mọi thắc mắc xin liên hệ SĐT: 0338968006 (thầy Hào)'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info('Đã gửi email xác nhận đăng ký tới %s', email)
        return True
    except Exception:
        logger.exception('Không gửi được email xác nhận đăng ký tới %s', email)
        return False


def group_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


ACTIVITY_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')


def _activity_image_files(post):
    files = []
    for uploaded in UploadedFile.objects.filter(post=post):
        name = (uploaded.pdf_file.name or '').lower()
        if any(name.endswith(ext) for ext in ACTIVITY_IMAGE_EXTENSIONS):
            files.append(uploaded)
    return files

def getHomePage(request):
    categories = Category.objects.filter(enable = True)
    postTT = Post.objects.filter(enable = True, category = 1).order_by('-createdate')[:3]
    posttt = Post.objects.filter(enable = True, category = 4).order_by('-createdate')[:3]
    postViews = Post.objects.filter(enable=True).order_by('-views')[:10]
    notifications_HV = Post.objects.filter(enable=True, category=3).order_by('-createdate')[:4]
    admission_category = Category.objects.filter(name=ADMISSION_NEWS_CATEGORY_NAME).first()
    admission_news = (
        Post.objects.filter(enable=True, category=admission_category).order_by('-createdate')[:6]
        if admission_category else Post.objects.none()
    )
    latest_news_qs = Post.objects.filter(enable=True).exclude(category=3)
    if admission_category:
        latest_news_qs = latest_news_qs.exclude(category=admission_category)
    notifination_news = latest_news_qs.order_by('-createdate')[:6]
    lichcongtacs = Post.objects.filter(enable=True, category=2).order_by('-createdate')[:6]
    context = {
        'categories': categories,
        'postTT': postTT,
        'notifications_HV': notifications_HV,
        'notification_news': notifination_news,
        'lichcongtacs': lichcongtacs,
        'postViews': postViews,
        'posttt': posttt,
        'admission_news': admission_news,
    }
    return render(request, 'homepage/index.html', context)


def post_admission_news(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Bạn không có quyền đăng tin tuyển sinh.')
        return redirect('homepage:Homepage')

    if request.method != 'POST':
        return redirect('homepage:Homepage')

    title = (request.POST.get('title') or '').strip()
    content = (request.POST.get('content') or '').strip()
    image = request.FILES.get('image')

    if not title or not content:
        messages.error(request, 'Vui lòng nhập đầy đủ tiêu đề và nội dung.')
        return redirect('homepage:Homepage')

    category = _get_admission_news_category()
    post = Post.objects.create(
        title=title[:50],
        content=content,
        category=category,
        enable=True,
    )
    if image:
        post.image_file = image
        post.save()

    messages.success(request, 'Đã đăng tin tuyển sinh thành công.')
    return redirect('homepage:Homepage')


def search_posts(request):
    q = request.GET.get('q', '').strip()
    posts = []
    if q:
        posts = Post.objects.filter(enable=True, title__icontains=q).order_by('-createdate')[:30]
    return render(request, 'homepage/search.html', {'q': q, 'posts': posts})


def getCyberHomePage(request):
    notifination_news = Post.objects.filter(enable=True).exclude(category=3).order_by('-createdate')[:6]
    return render(request, 'homepage/cyber_home.html', {'notification_news': notifination_news})


def getCategory(request, category_id):
    categories = Category.objects.filter(enable = True)
    lichcongtac = LichCongTac.objects.filter(namhoc = False).order_by('-createdate')
    posts = Post.objects.filter(enable=True, category=category_id).order_by('-createdate')
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
    posts = PostForum.objects.filter(enable=True).order_by('-createdate')
    context = {'categories': categories, 'posts':posts}
    return render(request, 'homepage/forumBase.html', context)

def getForumView(request, forum_id):
    categories = Category.objects.filter(enable = True)
    post = get_object_or_404(PostForum, id=forum_id)
    if not post.enable:
        if not request.user.is_authenticated:
            raise Http404()
        try:
            account = Account.objects.get(user=request.user)
            at = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
            if at.accounttype_role != 'admin':
                raise Http404()
        except (Account.DoesNotExist, AccountType.DoesNotExist):
            raise Http404()

    if request.method == 'POST':
        author_name = (request.POST.get('author_name') or '').strip()
        body = (request.POST.get('body') or '').strip()
        parent_raw = (request.POST.get('parent_id') or '').strip()
        if author_name and body:
            parent = None
            if parent_raw.isdigit():
                parent = PostForumComment.objects.filter(
                    id=int(parent_raw), post_id=post.id
                ).first()
                if parent is None:
                    return redirect('homepage:forumView', forum_id=post.id)
            PostForumComment.objects.create(
                post=post,
                parent=parent,
                author_name=author_name[:100],
                body=body[:2000],
            )
        return redirect('homepage:forumView', forum_id=post.id)

    top_comments = (
        post.comments.filter(parent=None)
        .order_by('createdate')
        .prefetch_related('replies__replies__replies')
    )
    context = {'post': post, 'categories': categories, 'top_comments': top_comments}
    return render(request, 'homepage/forumView.html', context)

def getActivity(request):
    posts = Post.objects.filter(enable=True, category__id=8).order_by('-createdate')
    categories = Category.objects.filter(enable=True)
    post_data = []
    for post in posts:
        post_data.append({
            'post': post,
            'files': _activity_image_files(post),
        })

    context = {
        'post_data': post_data,
        'categories': categories,
    }

    return render(request, 'homepage/activity.html', context)

def getAdmission(request):
    if request.method == 'POST':
        data = request.POST

        validation_err, scores = validate_admission_post(data)
        if validation_err:
            return JsonResponse({'error': validation_err}, status=400)

        graduation_year = data.get('graduation_year', '')
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        id_number = (data.get('id_number') or '').strip()
        father_phone = (data.get('father_phone') or '').strip()
        mother_phone = (data.get('mother_phone') or '').strip()

        cccd_town = data.get('permanent_house_number', '')
        cccd_district = data.get('permanent_street', '')
        cccd_ward = data.get('permanent_ward', '')
        cccd_province = data.get('permanent_province', '')

        current_house = data.get('current_house_number', '')
        current_district = data.get('current_street', '')
        current_ward = data.get('current_ward', '')
        current_province = data.get('current_province', '')

        conduct_6 = data.get('conduct_6', '')
        conduct_7 = data.get('conduct_7', '')
        conduct_8 = data.get('conduct_8', '')
        conduct_9 = data.get('conduct_9', '')

        try:
            campus = Campus.objects.get(id=data['campus_id'])
            shift = Shift.objects.get(id=data['shift_id'])
            subject_group = SubjectGroup.objects.get(id=data['subject_group_id'])
        except (Campus.DoesNotExist, Shift.DoesNotExist, SubjectGroup.DoesNotExist, KeyError):
            return JsonResponse({
                'error': 'Thông tin cơ sở/ca/tổ hợp môn không hợp lệ'
            }, status=400)

        study_vocational = data.get('study_vocational', 'no')
        vocational_campus_obj = None
        vocational_trade_obj = None
        if study_vocational == 'yes':
            vc_id = data.get('vocational_campus_id')
            vt_id = data.get('vocational_trade_id')
            if not CampusVocationalLink.objects.filter(
                admission_campus=campus,
                vocational_campus_id=vc_id,
            ).exists():
                return JsonResponse({'error': 'Cơ sở dạy nghề không hợp lệ với cơ sở tuyển sinh'}, status=400)
            try:
                vocational_trade_obj = VocationalTrade.objects.get(
                    id=vt_id, vocational_campus_id=vc_id
                )
                vocational_campus_obj = vocational_trade_obj.vocational_campus
            except VocationalTrade.DoesNotExist:
                return JsonResponse({'error': 'Nghề đăng ký không hợp lệ'}, status=400)

        try:
            with transaction.atomic():
                campus_shift_group = CampusShiftGroup.objects.select_for_update().get(
                    campus=campus,
                    shift=shift,
                    subject_group=subject_group,
                )

                if campus_shift_group.registration_count <= 0:
                    return JsonResponse({
                        'error': 'Tổ hợp môn này đã hết chỗ'
                    }, status=400)

                campus_shift_group.registration_count -= 1
                campus_shift_group.save(update_fields=['registration_count'])

                obj = AdmissionForm.objects.create(
                    full_name=(data.get('full_name') or '').strip().upper(),
                    gender=data.get('gender', ''),
                    ethnicity=data.get('ethnicity', ''),
                    birthday=data.get('birthday', ''),
                    religion='Không',
                    email=email,
                    phone=phone,

                    cccd_province=cccd_province,
                    cccd_district=cccd_district,
                    cccd_ward=cccd_ward,
                    cccd_town=cccd_town,

                    hometown_province='',

                    birth_reg_province='',
                    birth_reg_district='',
                    birth_reg_ward='',
                    birth_reg_town=current_house,

                    birth_place_province='',
                    birth_place_district='',
                    birth_place_ward='',
                    birth_place_facility=data.get('birth_place', ''),

                    current_province=current_province,
                    current_district=current_district,
                    current_ward=current_ward,

                    id_number=id_number,
                    id_issued_date=data.get('id_issued_date', ''),

                    graduation_year=graduation_year,
                    graduation_school=data.get('graduation_school', ''),
                    graduation_rank='',

                    exam_score=scores['exam_score'],
                    avg_score=scores['avg_score'],
                    math_score_6=scores['math_score_6'],
                    literature_score_6=scores['literature_score_6'],
                    math_score_7=scores['math_score_7'],
                    literature_score_7=scores['literature_score_7'],
                    math_score_8=scores['math_score_8'],
                    literature_score_8=scores['literature_score_8'],
                    math_score_9=scores['math_score_9'],
                    literature_score_9=scores['literature_score_9'],

                    conduct=conduct_9,
                    conduct_6=conduct_6,
                    conduct_7=conduct_7,
                    conduct_8=conduct_8,
                    conduct_9=conduct_9,

                    current_job='',

                    father_name=data.get('father_name', ''),
                    father_job=data.get('father_job', ''),
                    father_birth=data.get('father_birth', ''),
                    father_phone=father_phone,

                    mother_name=data.get('mother_name', ''),
                    mother_job=data.get('mother_job', ''),
                    mother_birth=data.get('mother_birth', ''),
                    mother_phone=mother_phone,

                    study_vocational=study_vocational,
                    vocational_campus=vocational_campus_obj,
                    vocational_trade=vocational_trade_obj,

                    campus=campus,
                    shift=shift,
                    subject_group=subject_group,
                )
        except CampusShiftGroup.DoesNotExist:
            return JsonResponse({
                'error': 'Không tìm thấy tổ hợp môn này'
            }, status=404)
        except IntegrityError:
            return JsonResponse({
                'error': 'Số CCCD này đã được đăng ký'
            }, status=400)
        except Exception:
            logger.exception('Error creating admission form')
            return JsonResponse({
                'error': 'Có lỗi xảy ra khi xử lý đơn đăng ký'
            }, status=500)

        transaction.on_commit(
            lambda e=email, n=obj.full_name: _send_admission_confirmation_email(e, n)
        )
        return JsonResponse({'success': True, 'redirect': '/admission/?success=1'})

    configured_campus_ids = CampusShiftGroup.objects.values_list('campus_id', flat=True).distinct()
    campuses = Campus.objects.filter(id__in=configured_campus_ids).order_by('name')
    subject_groups = SubjectGroup.objects.all()
    shifts = Shift.objects.all()
    current_year = timezone.now().year
    graduation_year_min = 1985
    graduation_year_options = list(range(current_year, graduation_year_min - 1, -1))
    return render(request, 'homepage/admission.html', {
        'campuses': campuses,
        'subject_groups': subject_groups,
        'shifts': shifts,
        'graduation_year_options': graduation_year_options,
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
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'cccd_check:{ip}'
    attempts = cache.get(cache_key, 0)
    if attempts >= 30:
        return JsonResponse({
            'error': 'Bạn đã kiểm tra quá nhiều lần. Vui lòng thử lại sau.',
            'exists': False,
        }, status=429)
    cache.set(cache_key, attempts + 1, 60)

    cccd_err = validate_vn_cccd(cccd)
    if cccd_err:
        return JsonResponse({'error': cccd_err, 'exists': False}, status=400)
    exists = AdmissionForm.objects.filter(id_number=cccd.strip()).exists()
    return JsonResponse({'exists': exists})


def get_vocational_campuses_by_admission_campus(request, campus_id):
    link_ids = CampusVocationalLink.objects.filter(
        admission_campus_id=campus_id
    ).values_list('vocational_campus_id', flat=True)
    campuses = VocationalCampus.objects.filter(id__in=link_ids).order_by('name')
    data = [{'id': c.id, 'name': c.name} for c in campuses]
    return JsonResponse({'campuses': data})


def get_vocational_trades_by_campus(request, vocational_campus_id):
    trades = VocationalTrade.objects.filter(
        vocational_campus_id=vocational_campus_id
    ).order_by('name')
    data = [{'id': t.id, 'name': t.name} for t in trades]
    return JsonResponse({'trades': data})


def get_address_provinces(request):
    if not data_is_available():
        return JsonResponse(
            {'error': 'Dữ liệu địa chỉ chưa được cài đặt. Chạy: python manage.py sync_address_data'},
            status=503,
        )
    try:
        return JsonResponse(load_provinces())
    except Exception:
        return JsonResponse({'error': 'Không thể tải dữ liệu tỉnh/thành phố'}, status=502)


def get_address_communes(request, province_code):
    if not is_valid_province_code(province_code):
        return JsonResponse({'error': 'Mã tỉnh/thành phố không hợp lệ'}, status=400)
    if not data_is_available():
        return JsonResponse(
            {'error': 'Dữ liệu địa chỉ chưa được cài đặt. Chạy: python manage.py sync_address_data'},
            status=503,
        )
    try:
        return JsonResponse(load_communes(province_code))
    except FileNotFoundError:
        return JsonResponse({'error': 'Không tìm thấy dữ liệu xã/phường'}, status=404)
    except Exception:
        return JsonResponse({'error': 'Không thể tải dữ liệu xã/phường'}, status=502)


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

from .forms import (
    StudentCodeForm,
    StudentExamRegistrationForm,
    StudentInfoLookupForm,
    StudentInfoVerificationForm,
    STUDENT_INFO_VERIFIABLE_STATUS_FIELDS,
)
from .models import (
    Student,
    StudentExamRegistration,
    RegistrationHistory,
    StudentInfoRecord,
    StudentInfoVerification,
    StudentInfoVerificationHistory,
)

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


def student_info_lookup(request):
    """Học viên nhập mã để vào trang kiểm tra thông tin."""
    categories = Category.objects.filter(enable=True)
    form = StudentInfoLookupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        student_code = form.cleaned_data["student_code"]
        student = StudentInfoRecord.objects.filter(student_code=student_code).first()
        if student:
            request.session["student_info_code"] = student.student_code
            return redirect("homepage:student_info_verify")
        form.add_error("student_code", "Mã học viên không tồn tại trong danh sách kiểm tra thông tin.")

    return render(
        request,
        "homepage/student_info_lookup.html",
        {"form": form, "categories": categories},
    )


def _student_info_verification_payload(verification):
    fields = (
        "class_name_status",
        "full_name_status",
        "birthday_status",
        "birth_place_status",
        "gender_status",
        "ethnicity_status",
        "id_number_status",
        "contact_address_status",
        "email_status",
        "phone_status",
        "highschool_10_status",
        "highschool_11_status",
        "exam_subjects_status",
    )
    wrong_labels = [
        lab
        for attr, lab in STUDENT_INFO_VERIFIABLE_STATUS_FIELDS
        if getattr(verification, attr, "") == "S"
    ]
    return {f: getattr(verification, f, "") or "" for f in fields} | {
        "note": verification.note or "",
        "wrong_field_labels": wrong_labels,
        "all_correct": len(wrong_labels) == 0,
    }


def student_info_verify(request):
    """Học viên xem thông tin, xác nhận một lần (đúng hết / có mục sai + tick) — tối đa 2 lần gửi."""
    from django.db import transaction

    categories = Category.objects.filter(enable=True)
    student_code = request.session.get("student_info_code")
    if not student_code:
        return redirect("homepage:student_info_lookup")

    student = StudentInfoRecord.objects.filter(student_code=student_code).first()
    if not student:
        request.session.pop("student_info_code", None)
        return redirect("homepage:student_info_lookup")

    verification, _ = StudentInfoVerification.objects.get_or_create(student=student)
    read_only = verification.submit_count >= 2

    form = None
    if request.method == "POST":
        if read_only:
            messages.error(
                request,
                "Bạn đã dùng hết 2 lần gửi xác nhận. Chỉ được xem thông tin, không chỉnh sửa.",
            )
            return redirect("homepage:student_info_verify")
        form = StudentInfoVerificationForm(request.POST, instance=verification)
        if form.is_valid():
            with transaction.atomic():
                v = form.save(commit=False)
                v.submit_count += 1
                v.save()
                StudentInfoVerificationHistory.objects.create(
                    verification=v,
                    submit_index=v.submit_count,
                    payload=_student_info_verification_payload(v),
                )
            return redirect("homepage:student_info_verify_success")
    elif not read_only:
        form = StudentInfoVerificationForm(instance=verification)

    g_raw = (student.gender or "").strip()
    g_low = g_raw.lower()
    if g_low in ("nam", "m", "male"):
        gender_display = "Nam"
    elif g_low in ("nữ", "nu", "f", "female"):
        gender_display = "Nữ"
    else:
        gender_display = g_raw or "—"

    flat_info = [
        ("Mã học viên", student.student_code or "—"),
        ("Lớp", student.class_name or "—"),
        ("Họ và tên", (student.full_name or "—").upper()),
        (
            "Ngày sinh",
            student.birthday.strftime("%d/%m/%Y") if student.birthday else "—",
        ),
        ("Nơi sinh", student.birth_place or "—"),
        ("Giới tính", gender_display),
        ("Dân tộc", student.ethnicity or "—"),
        ("Số CCCD", student.id_number or "—"),
        ("Địa chỉ liên hệ", student.contact_address or "—"),
        ("Gmail", student.email or "—"),
        ("Số điện thoại", student.phone or "—"),
        ("Nơi học THPT lớp 10", student.highschool_10 or "—"),
        ("Nơi học THPT lớp 11", student.highschool_11 or "—"),
        (
            "Môn thi TN THPT",
            ", ".join(student.exam_subjects or []) or "—",
        ),
    ]
    info_row_pairs = [flat_info[i : i + 2] for i in range(0, len(flat_info), 2)]

    wrong_labels_readonly = [
        lab
        for attr, lab in STUDENT_INFO_VERIFIABLE_STATUS_FIELDS
        if getattr(verification, attr, "") == "S"
    ]
    all_marked_ok_readonly = read_only and not wrong_labels_readonly

    remaining_attempts = max(0, 2 - verification.submit_count)

    return render(
        request,
        "homepage/student_info_verify.html",
        {
            "categories": categories,
            "student": student,
            "verification": verification,
            "form": form,
            "info_row_pairs": info_row_pairs,
            "read_only": read_only,
            "remaining_attempts": remaining_attempts,
            "wrong_labels_readonly": wrong_labels_readonly,
            "all_marked_ok_readonly": all_marked_ok_readonly,
        },
    )


def student_info_verify_success(request):
    """Trang thành công sau khi gửi xác nhận (GET, giống đăng ký thi tốt nghiệp)."""
    categories = Category.objects.filter(enable=True)
    student_code = request.session.get("student_info_code")
    if not student_code:
        return redirect("homepage:student_info_lookup")

    student = StudentInfoRecord.objects.filter(student_code=student_code).first()
    if not student:
        request.session.pop("student_info_code", None)
        return redirect("homepage:student_info_lookup")

    verification = StudentInfoVerification.objects.filter(student=student).first()
    if not verification or verification.submit_count < 1:
        return redirect("homepage:student_info_verify")

    wrong_labels = [
        lab
        for attr, lab in STUDENT_INFO_VERIFIABLE_STATUS_FIELDS
        if getattr(verification, attr, "") == "S"
    ]
    all_correct = len(wrong_labels) == 0
    remaining_attempts = max(0, 2 - verification.submit_count)

    return render(
        request,
        "homepage/student_info_verify_success.html",
        {
            "categories": categories,
            "student": student,
            "verification": verification,
            "wrong_labels": wrong_labels,
            "all_correct": all_correct,
            "remaining_attempts": remaining_attempts,
        },
    )


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
        JournalTeacher, JournalRow, JournalEntry, JournalClass, JournalTeacherWeekLimitOverride,
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
    allow_over_limit = False
    if selected_week_obj:
        week_start = selected_week_obj.start_date
        week_end = selected_week_obj.end_date
        current_week_num = selected_week_obj.week_number
        current_week_obj = selected_week_obj
        is_expired = today > week_end
        is_effective_locked = selected_week_obj.is_locked or (is_expired and not selected_week_obj.allow_late_edit)
        # Tuần quá hạn tự khóa, nhưng nếu admin mở lại (allow_late_edit=True) thì vẫn cho nhập/sửa.
        can_edit = (not is_effective_locked) and today >= week_start
        allow_over_limit = JournalTeacherWeekLimitOverride.objects.filter(
            journal_week=selected_week_obj,
            teacher=teacher,
            allow_over_limit=True,
        ).exists()
    else:
        current_week_obj = None
        can_edit = False
        allow_over_limit = False

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
        if (not allow_over_limit) and (entries_count_week + slots_needed > max_entries):
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

    # Chỉ cho nhập thêm khi còn chỗ (số tiết < số hàng), trừ khi đã bật override theo tuần cho GV.
    can_add_entry = can_edit and (allow_over_limit or len(entries) < rows.count())

    # Theo dõi (ngày → các tiết đã có) cho JS ẩn/disable tiết trùng (template có thể dùng sau)
    occupied_periods_by_date = {}
    for e in entries:
        if not e.lesson_date:
            continue
        key = e.lesson_date.strftime("%Y-%m-%d")
        try:
            occupied_periods_by_date.setdefault(key, set()).add(int(e.period))
        except (TypeError, ValueError):
            continue
    occupied_periods_serializable = {
        k: sorted(v) for k, v in occupied_periods_by_date.items()
    }
    occupied_periods_by_date_json = json.dumps(
        occupied_periods_serializable, ensure_ascii=False
    )

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
        'occupied_periods_by_date_json': occupied_periods_by_date_json,
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
