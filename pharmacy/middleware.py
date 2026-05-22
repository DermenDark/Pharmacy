from zoneinfo import ZoneInfo
from django.utils import timezone

class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = "UTC"
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            tzname = request.user.profile.timezone or "UTC"

        try:
            timezone.activate(ZoneInfo(tzname))
        except Exception:
            timezone.activate(ZoneInfo("UTC"))

        response = self.get_response(request)
        timezone.deactivate()
        return response