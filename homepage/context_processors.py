from homepage.models import Category


def site_categories(request):
    return {
        'categories': Category.objects.filter(enable=True),
    }
