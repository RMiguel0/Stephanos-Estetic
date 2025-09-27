from rest_framework import serializers
from .models import ContactRequest

class ContactRequestSerializer(serializers.ModelSerializer):
    # anti-spam (solo escritura)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    sent_at = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = ContactRequest
        fields = ["name", "email", "phone", "message", "website", "sent_at"]

    def validate_message(self, v: str):
        # ejemplo simple: limitar cantidad de enlaces
        if v.count("http://") + v.count("https://") > 1:
            raise serializers.ValidationError("Demasiados enlaces en el mensaje.")
        return v
