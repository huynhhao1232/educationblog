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
    path('cctc/<int:pb_id>/', views.get_CCTC, name="CCTC"),
    path('admission/', views.get_Admission, name="admission"),
    path('letter/<int:admission_id>/', views.get_Letter, name="letter"),
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

    # API endpoints for address data
    path('api/provinces/', ajax.get_provinces, name='get_provinces'),
    path('api/districts/<str:province_code>/', ajax.get_districts, name='get_districts'),
    path('api/wards/<str:district_code>/', ajax.get_wards, name='get_wards'),
    path('export-approved-admissions/', views.export_approved_admissions, name='export_approved_admissions'),
]
urlpatterns += [
    path('import-cccd-excel/', views.import_cccd_excel, name='import_cccd_excel'),
    path('delete-cccd-excel/', views.delete_cccd_excel, name='delete_cccd_excel'),
    path('update-conduct-excel/', views.update_conduct_excel, name='update_conduct_excel'),
    path('export-conduct-template/', views.export_conduct_template, name='export_conduct_template'),
]