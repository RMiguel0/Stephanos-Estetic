from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth import logout

@ensure_csrf_cookie
@require_GET
def csrf_view(request):
    get_token(request)
    return JsonResponse({"detail": "CSRF cookie set"})

@login_required
@require_GET
def current_user(request):
    u = request.user
    return JsonResponse({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
        "is_authenticated": True,
    })


@csrf_protect
@require_GET
def logout_api(request):
    logout(request)
    return JsonResponse({"ok": True})
