from django.shortcuts import render
from .models import *
from itertools import zip_longest
# Create your views here.
def group_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def getHomePage(request):
    categories = Category.objects.filter(enable = True)
    postTT = Post.objects.filter(enable = True, category = 1).order_by('-createdate')[:3]
    notifications_HV = Post.objects.filter(category = 3).order_by('-createdate')[:4]
    notifination_news = Post.objects.filter(enable = True).exclude(category=3).order_by('-createdate')[:6]
    lichcongtacs = Post.objects.filter(category = 2).order_by('-createdate')[:6]
    context = {'categories': categories, 'postTT': postTT, 'notifications_HV': notifications_HV, 'notification_news': notifination_news, 'lichcongtacs': lichcongtacs}
    return render(request, 'homepage/index.html', context)

def getCategory(request, category_id):
    categories = Category.objects.filter(enable = True)
    lichcongtac = LichCongTac.objects.filter(namhoc = False).order_by('-createdate')
    posts = Post.objects.filter(category = category_id).order_by('-createdate')
    context = {'category_id': category_id,'posts': posts, 'categories': categories }

    return render(request, 'homepage/list-post.html', context)
def getViewPost(request, post_id):
    categories = Category.objects.filter(enable = True)
    post = Post.objects.get(id = post_id)
    category = Category.objects.get(id = post.category.id)
    posts = Post.objects.filter(category = category).exclude(id=post_id).order_by('-createdate')[:5]
    files = UploadedFile.objects.filter(post = post)
    file_names = None
    if(files):
        file_names = [file.pdf_file.name.split('/')[-1] for file in files]

    context = {'categories': categories, 'post':post,'files':files, 'filenames': file_names, 'category': category, 'posts':posts}
    return render(request, 'homepage/view-post.html', context)

def getCCTC(request, pb_id):
    categories = Category.objects.filter(enable = True)
    pbs = PhongBan.objects.all().exclude(id = pb_id)
    pb = PhongBan.objects.get(id = pb_id)
    pb_gv = PB_GV.objects.filter(phongban__id = pb_id, phongban__enable = True)
    pb_gv2 = PB_GV.objects.filter(phongban__id = pb_id, phongban__enable = True, gv__bac = 2)
    pb_gv_grouped = group_list(list(pb_gv2), 2)
    context = {'categories': categories, 'pbs':pbs, 'pb':pb, 'pb_gv': pb_gv, 'pb_gv_grouped': pb_gv_grouped}
    return render(request, 'homepage/cctc.html', context)

def getForum(request):
    return render(request, 'form/forumQA.html')