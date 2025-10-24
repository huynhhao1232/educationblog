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
from django.core.mail import send_mail
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
