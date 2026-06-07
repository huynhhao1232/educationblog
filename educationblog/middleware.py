from django.contrib.sessions.exceptions import SessionInterrupted
from django.http import HttpResponseRedirect
from django.urls import reverse


class SessionInterruptedGuardMiddleware:
    """
    Convert SessionInterrupted into a safe redirect instead of HTTP 500.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except SessionInterrupted:
            try:
                return HttpResponseRedirect(reverse("adminpage:exam_room_manage"))
            except Exception:
                return HttpResponseRedirect("/")
