from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    send_mail(
        subject='Сброс пароля',
        message=f'Ваш токен для сброса пароля: {reset_password_token.key}',
        from_email=None,
        recipient_list=[reset_password_token.user.email],
        fail_silently=True,
    )
