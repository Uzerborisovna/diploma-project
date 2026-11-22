from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .models import ConfirmEmailToken

User = get_user_model()


@receiver(post_save, sender=User)
def new_user_registered(sender, instance, created, **kwargs):
    if created:
        token = ConfirmEmailToken.objects.create(user=instance)
        send_mail(
            subject='Подтверждение регистрации',
            message=f'Ваш токен для подтверждения: {token.key}',
            from_email=None,
            recipient_list=[instance.email],
            fail_silently=True,
        )


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    send_mail(
        subject='Сброс пароля',
        message=f'Ваш токен для сброса пароля: {reset_password_token.key}',
        from_email=None,
        recipient_list=[reset_password_token.user.email],
        fail_silently=True,
    )