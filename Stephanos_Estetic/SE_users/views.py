# SE_users/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout

@ensure_csrf_cookie
@require_GET
def csrf_view(request):
    get_token(request)
    return JsonResponse({"detail": "CSRF cookie set"})

@require_GET
def current_user(request):
    u = request.user
    if not u.is_authenticated:
        # Para SPA es más práctico responder 200 con flag
        return JsonResponse({"is_authenticated": False})
    return JsonResponse({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
        "is_authenticated": True,
    })

@require_GET
def logout_api(request):
    logout(request)
    return JsonResponse({"ok": True})
