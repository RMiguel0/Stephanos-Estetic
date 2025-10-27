# SE_users/views.py
import json
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth.decorators import login_required



User = get_user_model()

def _json(req):
    try:
        return json.loads(req.body.decode("utf-8"))
    except Exception:
        return {}

# --- CSRF: setea cookie 'csrftoken' ---
@ensure_csrf_cookie
@require_GET
def csrf_view(request):
    get_token(request)  # fuerza generar/renovar token
    return JsonResponse({"detail": "CSRF cookie set"})

# --- Registro ---
@csrf_protect
@require_POST
def register_view(request):
    data = _json(request)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not email or not password:
        return JsonResponse({"detail": "email and password are required"}, status=400)

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"detail": "email already registered"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
    # crea/actualiza profile si lo tienes
    prof = getattr(user, "profile", None)
    if prof and full_name:
        prof.full_name = full_name
        prof.save(update_fields=["full_name"])

    return JsonResponse({"detail": "registered"}, status=201)

# --- Login ---
@csrf_protect
@require_POST
def login_view(request):
    data = _json(request)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return JsonResponse({"detail": "email and password are required"}, status=400)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    login(request, user)  # crea cookie de sesión
    return JsonResponse({"detail": "ok"})

# --- Logout ---
@csrf_protect
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "logged out"})

# --- Perfil ---
@login_required
@require_http_methods(["GET", "PUT"])
def profile_view(request):
    user = request.user
    prof = getattr(user, "profile", None)

    if request.method == "GET":
        return JsonResponse({
            "email": user.email,
            "full_name": (getattr(prof, "full_name", "") or user.first_name),
            "phone": getattr(prof, "phone", ""),
            "created_at": getattr(prof, "created_at", None).isoformat() if getattr(prof, "created_at", None) else "",
            "updated_at": getattr(prof, "updated_at", None).isoformat() if getattr(prof, "updated_at", None) else "",
        })

    data = _json(request)
    full_name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip()

    # crea profile si faltara
    if prof is None:
        from .models import Profile
        prof = Profile.objects.create(user=user)

    changed = False
    if full_name:
        prof.full_name = full_name
        user.first_name = full_name
        changed = True
    if phone:
        prof.phone = phone
        changed = True

    if changed:
        prof.save()
        user.save(update_fields=["first_name"])

    return JsonResponse({"detail": "updated"})

@csrf_exempt
@require_POST
def google_login_view(request):
    # Stub temporal: evita el ImportError y te deja levantar el server
    return JsonResponse({"detail": "google login not implemented yet"}, status=501)