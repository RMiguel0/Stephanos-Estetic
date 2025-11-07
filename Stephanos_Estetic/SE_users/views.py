# SE_users/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import json

from .models import UserOrderHistory

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
    profile = getattr(u, "profile", None)
    phone = profile.phone if profile else ""
    return JsonResponse({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
        "phone": phone,
        "is_authenticated": True,
    })

@require_GET
def logout_api(request):
    logout(request)
    return JsonResponse({"ok": True})


@method_decorator([login_required, csrf_protect], name="dispatch")
class ProfileView(View):
    """
    GET  -> retorna los datos del perfil
    PUT  -> actualiza nombre y teléfono
    """

    def get(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        data = {
            "id": profile.id,
            "email": request.user.email,
            "full_name": profile.full_name or f"{request.user.first_name} {request.user.last_name}".strip(),
            "display_name": getattr(profile, "display_name", ""),
            "phone": profile.phone,
            "picture": getattr(profile, "picture", ""),
            "created_at": profile.created_at,
        }
        return JsonResponse(data)

    def put(self, request):
        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)

        profile = request.user.profile
        profile.full_name = body.get("full_name", profile.full_name)
        profile.display_name = body.get("display_name", profile.display_name)
        profile.phone = body.get("phone", profile.phone)
        profile.save()

        return JsonResponse({
            "ok": True,
            "full_name": profile.full_name,
            "display_name": profile.display_name,
            "phone": profile.phone,
            "picture": getattr(profile, "picture", ""),
        })
        
@method_decorator([login_required], name="dispatch")
class UserOrdersView(View):
    """GET -> historial de compras del usuario autenticado."""

    def get(self, request):
        histories = (
            UserOrderHistory.objects
            .filter(user=request.user, order__status="paid")  # <- opcional
            .select_related("order")
            .prefetch_related("order__items__product")       # <- evita N+1
            .order_by("-viewed_at")
        )

        orders = []
        for h in histories:
            o = h.order
            items = [
                {
                    "product": it.product.name,
                    "qty": int(it.qty),
                    "price_at": float(it.price_at),
                    "line_total": float(it.line_total),
                }
                for it in o.items.all()
            ]
            orders.append({
                "order_id": o.id,
                "customer_name": o.customer_name or "",
                "customer_email": o.customer_email or "",
                "total_amount": float(o.total_amount),
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
                "viewed_at": h.viewed_at.isoformat(),
                "items": items,
            })

        return JsonResponse({"orders": orders})