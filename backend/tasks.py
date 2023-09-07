from time import sleep
from django.core.mail import send_mail
from info import EMAIL_HOST_USER
from celery import shared_task

@shared_task()
def send_feedback_email_task(feedback,email_address, message):
    sleep(20) 
    send_mail(
        f"{feedback}",
        message,
        EMAIL_HOST_USER,
        [email_address],
        fail_silently=False,
    )