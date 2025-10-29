# SE_users/signals.py
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

def update_profile_from_google(user, extra_data):
    """
    Actualiza o completa el perfil del usuario con datos de Google.
    """
    first = (extra_data.get("given_name") or "").strip()
    last = (extra_data.get("family_name") or "").strip()
    full = (extra_data.get("name") or f"{first} {last}".strip()).strip()
    picture = extra_data.get("picture") or ""

    # Actualizar campos básicos del usuario
    if not user.first_name:
        user.first_name = first
    if not user.last_name:
        user.last_name = last
    if not user.email:
        user.email = extra_data.get("email", user.email)
    user.save()

    # Actualizar o crear perfil
    profile, _ = Profile.objects.get_or_create(user=user)
    if full and not profile.full_name:
        profile.full_name = full
        profile.display_name = full
    if picture and not profile.picture:
        profile.picture = picture
    profile.save()


@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    update_profile_from_google(sociallogin.user, sociallogin.account.extra_data)


@receiver(social_account_updated)
def on_social_account_updated(request, sociallogin, **kwargs):
    update_profile_from_google(sociallogin.user, sociallogin.account.extra_data)
