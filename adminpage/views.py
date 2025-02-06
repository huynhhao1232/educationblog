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
            
# def upload_image(request):
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