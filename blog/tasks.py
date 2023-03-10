from celery import shared_task

from django.core.mail import send_mail


@shared_task
def send_email_task(from_email, subject, message):
    """Sends an email when the feedback form has been submitted."""
    send_mail(
        subject,
        message,
        [from_email],
        ["support@example.com"],
        fail_silently=False,
    )


@shared_task
def send_email_task_to_client(from_email, subject, message):
    """Sends an email when the feedback form has been submitted."""
    send_mail(
        subject,
        message,
        ['admin@example.com'],
        [from_email],
        fail_silently=False,)
