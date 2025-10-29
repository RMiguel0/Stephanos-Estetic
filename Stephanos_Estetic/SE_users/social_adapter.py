# SE_users/social_adapter.py
from django.contrib.auth import get_user_model
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Auto-vincula el SocialAccount a un User existente con el mismo email
    y realiza el login, evitando /accounts/3rdparty/signup/.
    """
    def pre_social_login(self, request, sociallogin):
        # Si ya está logueado no hacemos nada
        if request.user.is_authenticated:
            return

        email = (sociallogin.user.email or "").strip().lower()
        if not email:
            # Sin email no podemos vincular automáticamente
            return

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # No hay usuario local con ese email -> allauth seguirá con alta normal
            return

        # Vincula el proveedor actual (Google) al usuario existente
        sociallogin.connect(request, user)

        # Autentica al usuario ya vinculado (saltando verificación en dev)
        perform_login(request, user, email_verification="none")
