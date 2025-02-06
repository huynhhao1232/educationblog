from django.contrib import admin
from django.urls import path, re_path
from . import views
from . import ajax
from django.views.decorators.csrf import csrf_exempt
app_name = 'adminpage'
urlpatterns = [
    path('', views.adminpage, name = "adminpagee"),
    path('category/', views.getCategory, name = "category"),
    path('categorydetail/<int:category_id>/', views.getCategoryDetail, name='categorydetail'),
    path('get-post-data/<int:post_id>/', views.get_post_data, name='get_post_data'),

    path('phongban/', views.get_PB, name="phongban" ),
    path('cctc/<int:pb_id>/', views.get_CCTC, name="CCTC")
    # path('get_role/', ajax.get_role, name="get_role"),
    # path('course/', views.course, name = "course"),
    # path('get_course/', ajax.get_course, name="get_course"),
    # path('get_course_update/', ajax.get_course_update, name="get_course_update"),
    # # path('coursedetail/<int:course_id>/', views.coursedetail, name="coursedetail"),
    # # path('get_chapter/', ajax.get_chapter, name="get_chapter"),
    # # path('chapterdetail/<int:chapter_id>/<int:course_id>/', views.chapterdetail, name="chapterdetail"),
    # # path('get_chapter_update/', ajax.get_chapter_update, name="get_chapter_update"),
    # # path('get_lesson/', ajax.get_lesson, name="get_lesson"),
    # # path('lessondetail/<int:chapter_id>/<int:lesson_id>/', views.lessondetail, name="lessondetail"),
    # # path('get_lesson_update/', ajax.get_lesson_update, name="get_lesson_update"),
    # path('get_activity/', ajax.get_activity, name="get_activity"),
    # path('activity/<int:course_id>/', views.activity, name="activity"),
    # path('activitydetail/<int:activity_id>/', views.activitydetail, name="activitydetail"),
    # path('check_activity/', ajax.check_activity, name="check_activity"),
    # path('get_data_activity/', ajax.get_data_activity, name="get_data_activity"),
    # path('Phaser/',views.Phaser,name="Phaser"),
    # path('posttype/', views.posttype, name="posttype"),
    # path('get_posttype/', ajax.get_posttype, name="get_posttype"),
    # path('forumpost/<int:posttype_id>/', views.forumpost, name='forumpost'),
    # path('forumanswer/<int:post_id>/', views.forumanswer, name="forumanswer"),
    # path('submit_approved/', ajax.submit_approved, name="submit_approved"),
    # path('delete_comment/', ajax.delete_comment, name="delete_comment"),
    # path('change_active/', ajax.change_active, name="change_active"),
    # path('upload_image/',csrf_exempt(views.upload_image), name='upload_image'),
]