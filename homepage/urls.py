from django.urls import path
from django.conf import settings
from . import views

app_name = 'homepage'
urlpatterns = [
    path('', views.getHomePage, name="Homepage"),
    path('bang-tin-tuyen-sinh/dang-tin/', views.post_admission_news, name='post_admission_news'),
    path('tim-kiem/', views.search_posts, name="search"),
    path('neon-demo/', views.getCyberHomePage, name="cyber_home"),
    path('category/<int:category_id>/', views.getCategory, name="category"),
    path('post/<int:post_id>/', views.getViewPost, name='post'),
    path('cctc/<int:pb_id>/', views.getCCTC, name="cctc"),
    path('forum/', views.getForum, name="forum" ),
    path('forumView/<int:forum_id>/', views.getForumView, name="forumView"),
    path('activity/', views.getActivity, name="activity" ),
    path('admission/', views.getAdmission, name="admission"),
    path('api/subject-groups/', views.get_subject_groups_api, name='subject-groups-api'),
    path('api/shifts/<int:campus_id>/', views.get_shifts_by_campus),
    path('api/subjectgroups/<int:campus_id>/<int:shift_id>/', views.get_subjectgroups_by_campus_shift),
    path('api/check-cccd/<str:cccd>/', views.check_cccd_exists, name='check-cccd'),
    path('api/vocational-campuses/<int:campus_id>/', views.get_vocational_campuses_by_admission_campus),
    path('api/vocational-trades/<int:vocational_campus_id>/', views.get_vocational_trades_by_campus),
    path('api/address/provinces/', views.get_address_provinces),
    path('api/address/provinces/<str:province_code>/communes/', views.get_address_communes),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('student-exam-registration/', views.student_exam_registration_step1, name='student_exam_registration_step1'),
    # path('student-exam-registration/step2/', views.student_exam_registration_step2, name='student_exam_registration_step2'),
    # Sổ đầu bài số
    path('so-dau-bai/', views.journal_login, name='journal_login'),
    path('so-dau-bai/ca-nhan/', views.journal_personal, name='journal_personal'),
    path('so-dau-bai/ca-nhan/sua/<int:entry_id>/', views.journal_entry_edit, name='journal_entry_edit'),
    path('so-dau-bai/thoat/', views.journal_logout, name='journal_logout'),
    # Kiểm tra thông tin học viên (THPT)
    path('kiem-tra-thong-tin/', views.student_info_lookup, name='student_info_lookup'),
    path('kiem-tra-thong-tin/xac-nhan/', views.student_info_verify, name='student_info_verify'),
    path('kiem-tra-thong-tin/da-xac-nhan/', views.student_info_verify_success, name='student_info_verify_success'),
]
