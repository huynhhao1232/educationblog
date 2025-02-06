from django.http import JsonResponse
from .models import *
from django.forms.models import model_to_dict


from django.core.serializers import serialize

def get_category(request):
    try:
        course_name = request.GET.get('courseName')

        course_enable = int(request.GET.get('course_enable'))

        if course_enable == 1:
            course_enable = True
        else:
            course_enable = False

        course = Course.objects.get(course_id = course_id)
        grade = Grade.objects.get(grade_id = grade_id)
        subject = Subject.objects.get(subject_id = subject_id)


        if course.course_name == course_name:
            if course.course_enable != course_enable:
                return JsonResponse({'submit': True})
            else:
                return JsonResponse({'name': False})
        else:
            courses_with_name = Course.objects.filter(course_name = course_name, grade = grade, subject = subject)
            if courses_with_name.exists():
                return JsonResponse({'name': False})
            else:
                return JsonResponse({'submit': True})
        
        # Kiểm tra dữ liệu đầu vào

    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

# def get_role(request):
#     role = int(request.GET.get('role'))
#     account_id = request.GET.get('account_id')
#     account = Account.objects.get(account_id = account_id)
#     accounttype = AccountType.objects.get(accounttype_id = role)
#     account.accounttype = accounttype
#     account.save()

#     return JsonResponse('change', safe=False)

# def get_course(request):
#     try:
#         course_name = request.GET.get('courseName')
#         grade_id = request.GET.get('grade_id')
#         subject_id = request.GET.get('subject_id')

#         grade = Grade.objects.get(grade_id = grade_id)
#         subject = Subject.objects.get(subject_id = subject_id)

#         courses_with_name = Course.objects.filter(course_name = course_name, grade = grade, subject = subject)

#         if courses_with_name.exists():
#             return JsonResponse({'name': False})
#         else:
#             return JsonResponse({'submit': True})
        
#         # Kiểm tra dữ liệu đầu vào

#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    

# def get_course_update(request):
#     try:
#         course_name = request.GET.get('courseName')
#         grade_id = request.GET.get('grade_id')
#         subject_id = request.GET.get('subject_id')
#         course_id = request.GET.get('course_id')
#         course_enable = int(request.GET.get('course_enable'))

#         if course_enable == 1:
#             course_enable = True
#         else:
#             course_enable = False

#         course = Course.objects.get(course_id = course_id)
#         grade = Grade.objects.get(grade_id = grade_id)
#         subject = Subject.objects.get(subject_id = subject_id)


#         if course.course_name == course_name:
#             if course.course_enable != course_enable:
#                 return JsonResponse({'submit': True})
#             else:
#                 return JsonResponse({'name': False})
#         else:
#             courses_with_name = Course.objects.filter(course_name = course_name, grade = grade, subject = subject)
#             if courses_with_name.exists():
#                 return JsonResponse({'name': False})
#             else:
#                 return JsonResponse({'submit': True})
        
#         # Kiểm tra dữ liệu đầu vào

#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    

# def get_course_update(request):
#     try:
#         id = request.GET.get('id')

#         course = Course.objects.get(course_id=id)
#         grades = Grade.objects.all()
#         grades_data = serialize('json', grades)  # Chuyển đổi danh sách grades thành JSON

#         subjects = Subject.objects.all()
#         subjects_data = serialize('json', subjects)  # Chuyển đổi danh sách subjects thành JSON

#         course_dict = model_to_dict(course)
#         context = {'course': course_dict, 'grades': grades_data, 'subjects': subjects_data}

#         return JsonResponse(context)

#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    





# def get_chapter(request):
#     try:
#         chapterName = request.GET.get('chapterName')
#         stt = request.GET.get('stt')
#         course_id = request.GET.get('course_id')
        
#         # Kiểm tra dữ liệu đầu vào

        
#         course = Course.objects.get(course_id=course_id)
        
#         # Sử dụng .filter() thay vì vòng lặp
#         chapters_with_name = course.chapter_set.filter(chapter_name=chapterName)
#         chapters_with_order = course.chapter_set.filter(chapter_order=stt)
        
#         if chapters_with_name.exists():
#             return JsonResponse({'name': False})
#         elif chapters_with_order.exists():
#             return JsonResponse({'order': False})
#         else:
#             return JsonResponse({'submit': True})

#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})


# def get_chapter_update(request):
#     try:
#         chapterName = request.GET.get('chapterName')
#         stt = int(request.GET.get('stt'))
#         course_id = request.GET.get('course_id')
#         chapter_id = request.GET.get('chapter_id')
#         enableHidden = int(request.GET.get('enableHidden'))
#         # Kiểm tra dữ liệu đầu vào

#         if enableHidden == 1:
#             enableHidden = True
#         else:
#             enableHidden = False
#         course = Course.objects.get(course_id=course_id)
#         chapter = Chapter.objects.get(chapter_id = chapter_id)
        
#         if chapter.chapter_order == stt:
#             if chapter.chapter_enable == enableHidden:
#                 if chapter.chapter_name == chapterName:
#                     return JsonResponse({'name': False})
#                 else:
#                     chapters_with_name = course.chapter_set.filter(chapter_name=chapterName)
#                     if chapters_with_name.exists():
#                         return JsonResponse({'name': False})
#                     else:
#                         return JsonResponse({'submit': True})
#             else:
#                 if chapter.chapter_name == chapterName:
#                     return JsonResponse({'submit': True})
#                 else:
#                     chapters_with_name = course.chapter_set.filter(chapter_name=chapterName)
#                     if chapters_with_name.exists():
#                         return JsonResponse({'name': False})
#                     else:
#                         return JsonResponse({'submit': True})
#         else:
#             if chapter.chapter_name == chapterName:
#                 chapters_with_order = course.chapter_set.filter(chapter_order=stt)
#                 if chapters_with_order.exists():
#                     return JsonResponse({'order': False, 'chapter_order': stt})
#                 else:
#                     return JsonResponse({'submit': True})
#             else:
#                 chapters_with_name = course.chapter_set.filter(chapter_name=chapterName)
#                 chapters_with_order = course.chapter_set.filter(chapter_order=stt)
#                 if chapters_with_name.exists():
#                     return JsonResponse({'name': False})
#                 elif chapters_with_order.exists():
#                     return JsonResponse({'order': False, 'chapter_order': stt})
#                 else:
#                     return JsonResponse({'submit': True})
#         # Sử dụng .filter() thay vì vòng lặp

        


#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})

# def get_lesson(request):
#     try:
#         lesson_name = request.GET.get('lessonName')
#         lesson_order = request.GET.get('lessonOrder')
#         chapter_id = request.GET.get('chapter_id')
        
#         # Kiểm tra dữ liệu đầu vào

#         chapter = Chapter.objects.get(chapter_id = chapter_id)
        
#         lessons_with_name = chapter.lesson_set.filter(lesson_name = lesson_name)
#         lessons_with_order = chapter.lesson_set.filter(lesson_order = lesson_order)

#         if lessons_with_name.exists():
#             return JsonResponse({'name': False})
#         elif lessons_with_order.exists():
#             return JsonResponse({'order': False})
#         else:
#             return JsonResponse({'submit': True})
#         # Sử dụng .filter() thay vì vòng lặp

        


#     except Chapter.DoesNotExist:
#         return JsonResponse({'error': 'Chapter not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    

# def get_lesson_update(request):
#     try:
#         lesson_name = request.GET.get('lessonName')
#         lesson_order = int(request.GET.get('lessonOrder'))
#         chapter_id = request.GET.get('chapter_id')
#         enableHidden = int(request.GET.get('enableHidden'))
#         lesson_id = request.GET.get('lesson_id')
#         if enableHidden == 1:
#             enableHidden = True
#         else:
#             enableHidden = False
#         # Kiểm tra dữ liệu đầu vào

#         chapter = Chapter.objects.get(chapter_id = chapter_id)
#         lesson = Lesson.objects.get(lesson_id = lesson_id)

#         if lesson.lesson_order == lesson_order:
#             if lesson.lesson_enable == enableHidden:
#                 if lesson.lesson_name == lesson_name:
#                     return JsonResponse({'name': False})
#                 else:
#                     lessons_with_name = chapter.lesson_set.filter(lesson_name = lesson_name)
#                     if lessons_with_name.exists():
#                         return JsonResponse({'name': False})
#                     else:
#                         return JsonResponse({'submit': True})
#             else:
#                 if lesson.lesson_name == lesson_name:
#                     return JsonResponse({'submit': True})
#                 else:
#                     lessons_with_name = chapter.lesson_set.filter(lesson_name = lesson_name)
#                     if lessons_with_name.exists():
#                         return JsonResponse({'name': False})
#                     else:
#                         return JsonResponse({'submit': True})
#         else:
#             if lesson.lesson_name == lesson_name:
#                 lessons_with_order = chapter.lesson_set.filter(lesson_order = lesson_order)
#                 if lessons_with_order.exists():
#                     return JsonResponse({'order': False})
#                 else:
#                     return JsonResponse({'submit': True})
#             else:
#                 lessons_with_name = chapter.lesson_set.filter(lesson_name = lesson_name)
#                 lessons_with_order = chapter.lesson_set.filter(lesson_order = lesson_order)
#                 if lessons_with_name.exists():
#                     return JsonResponse({'name': False})
#                 elif lessons_with_order.exists():
#                     return JsonResponse({'order': False})
#                 else:
#                     return JsonResponse({'submit': True})

#         # Sử dụng .filter() thay vì vòng lặp



#     except Chapter.DoesNotExist:
#         return JsonResponse({'error': 'Chapter not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})

# def get_activity(request):
#     try:
#         activity_name = request.GET.get('activityName')
#         activity_order = request.GET.get('activityOrder')
#         course_id = request.GET.get('course_id')
        
#         # Kiểm tra dữ liệu đầu vào

#         course = Course.objects.get( course_id= course_id)
        
#         activities_with_name = course.activity_set.filter(activity_name = activity_name)
#         activities_with_order = course.activity_set.filter(activity_order = activity_order)

#         if activities_with_name.exists():
#             return JsonResponse({'name': False})
#         elif activities_with_order.exists():
#             return JsonResponse({'order': False})
#         else:
#             return JsonResponse({'submit': True})
#         # Sử dụng .filter() thay vì vòng lặp

        


#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})


# def get_posttype(request):
#     try:
#         posttype_name = request.GET.get('posttypeName')
        
#         # Kiểm tra dữ liệu đầu vào

#         posttypes_with_name = PostType.objects.filter(posttype_name = posttype_name)
        

#         if posttypes_with_name.exists():
#             return JsonResponse({'name': False})
#         else:
#             return JsonResponse({'submit': True})
#         # Sử dụng .filter() thay vì vòng lặp

        


#     except PostType.DoesNotExist:
#         return JsonResponse({'error': 'PostType not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    
# def submit_approved(request):
#     try:
#         postId = int(request.GET.get('post_id'))
#         action = int(request.GET.get('action'))

#         post = Post.objects.get(post_id = postId)

#         post.post_approved = True
#         post.post_enable = (True if action == 1 else False)
#         post.save()
#         return JsonResponse('change', safe=False)

        


#     except Post.DoesNotExist:
#         return JsonResponse({'error': 'Post not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    
# def delete_comment(request):
#     try:
#         comment_id = int(request.GET.get('comment_id'))
#         comment = Comment.objects.get(comment_id = comment_id)
#         if comment.comment_parent is not None:
#             parentComment = Comment.objects.filter(comment_parent = comment_id)
#             for p in parentComment:
#                 interact = Interact.objects.filter(comment = p)
#                 for i in interact:
#                     i.delete()
#                 p.delete()
#             interact = Interact.objects.get(comment = comment)
#             interact.delete()
#             comment.delete()
            
#         else:
#             interact = Interact.objects.get(comment = comment)
#             interact.delete()
#             comment.delete()
            
#         return JsonResponse('change', safe=False)

        


#     except Comment.DoesNotExist:
#         return JsonResponse({'error': 'Comment not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})

# def change_active(request):
#     try:
#         postId = int(request.GET.get('post_id'))
#         action = int(request.GET.get('action'))

#         post = Post.objects.get(post_id = postId)

#         post.post_enable = (True if action == 1 else False)
#         post.save()
#         return JsonResponse('change', safe=False)

        


#     except Post.DoesNotExist:
#         return JsonResponse({'error': 'Post not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
    

# def check_activity(request):
#     try:
#         activity_id = request.GET.get('activity_id')
#         type_id = int(request.GET.get('type_id'))
#         name = request.GET.get('name')
#         action = int(request.GET.get('action'))

#         activity = Activity.objects.get(activity_id = activity_id)


#         if action == 0:
#         # Kiểm tra dữ liệu đầu vào
#             if type_id == 1:
#                 order = request.GET.get('order')
#                 activities_with_name = activity.theory_set.filter(theory_name = name)
#                 activities_with_order = activity.theory_set.filter(theory_order = order)
#                 if activities_with_name.exists():
#                     return JsonResponse({'name': False})
#                 elif activities_with_order.exists():
#                     return JsonResponse({'order': False})
#                 else:
#                     return JsonResponse({'submit': True})
#             elif type_id == 2:
#                 activities_with_name = activity.game_set.filter(game_name = name)
#                 if activities_with_name.exists():
#                     return JsonResponse({'name': False})
#                 else:
#                     return JsonResponse({'submit': True})
#             else:
#                 activities_with_name = activity.simulation_set.filter(simulation_name = name)
#                 if activities_with_name.exists():
#                     return JsonResponse({'name': False})
#                 else:
#                     return JsonResponse({'submit': True})
#         else:
#             id = int(request.GET.get('data'))
#             if type_id == 1:
#                 order = request.GET.get('order')
#                 activities_with_name = activity.theory_set.filter( theory_name=name).exclude(theory_id=id)
#                 activities_with_order = activity.theory_set.filter(theory_order = order).exclude(theory_id = id)
#                 if activities_with_name.exists():
#                     return JsonResponse({'name': False})
#                 elif activities_with_order.exists():
#                     return JsonResponse({'order': False})
#                 else:
#                     return JsonResponse({'submit': True})
#             elif type_id == 2:
#                 activities_with_name = activity.game_set.filter(game_name = name).exclude(game_id = id)
#                 if activities_with_name.exists():
#                     return JsonResponse({'name': False})
#                 else:
#                     return JsonResponse({'submit': True})
#             else:
#                 activities_with_name = activity.simulation_set.filter(simulation_name = name).exclude(simulation_id = id)
#                 if activities_with_name.exists():
#                     return JsonResponse({'name': False})
#                 else:
#                     return JsonResponse({'submit': True})

#         # Sử dụng .filter() thay vì vòng lặp

        


#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})


# def get_data_activity(request):
#     try:
#         id = int(request.GET.get('id'))
#         type_id = int(request.GET.get('type_id'))

#         if type_id == 1:
#             theory = Theory.objects.get(theory_id = id)
#             theory_dict = model_to_dict(theory)
#             return JsonResponse({'theory': theory_dict})
#         elif type_id == 2:
#             game = Game.objects.get(game_id = id)
#             game_dict = model_to_dict(game)
#             return JsonResponse({'game': game_dict})
#         else:
#             simulation = Simulation.objects.get(simulation_id = id)
#             simulation_dict = model_to_dict(simulation)
#             return JsonResponse({'simulaiton': simulation_dict})

        
#         # Kiểm tra dữ liệu đầu vào

#     except Course.DoesNotExist:
#         return JsonResponse({'error': 'Course not found'})
#     except Exception as e:
#         return JsonResponse({'error': str(e)})
         
