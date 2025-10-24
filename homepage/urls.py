from django.urls import path
from django.conf import settings
from . import views

app_name = 'homepage'
urlpatterns = [
    path('', views.getHomePage, name="Homepage"),
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
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
