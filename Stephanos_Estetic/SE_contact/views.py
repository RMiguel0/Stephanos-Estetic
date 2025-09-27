import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from .serializers import ContactRequestSerializer
from .models import ContactRequest

class ContactRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact_form"

    def post(self, request):
        # honeypot: si viene con valor, ignoramos en silencio
        if request.data.get("website"):
            return Response(status=204)

        # tiempo mínimo en formulario (>= 3s desde que cargó)
        try:
            sent_at = int(request.data.get("sent_at", 0))
        except ValueError:
            sent_at = 0
        if time.time() - sent_at < 3:
            return Response({"detail": "Too fast"}, status=400)

        ser = ContactRequestSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)

        obj = ContactRequest.objects.create(
            name=ser.validated_data["name"],
            email=ser.validated_data["email"],
            phone=ser.validated_data.get("phone", ""),
            message=ser.validated_data["message"],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.headers.get("User-Agent", ""),
        )
        # TODO: aquí puedes encolar un email/telegram, etc.
        return Response({"ok": True, "id": obj.id})
