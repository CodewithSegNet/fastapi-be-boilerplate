from fastapi import BackgroundTasks, Request, requests

from api.v1.models.user import User
from api.core.dependencies.email.email_sender import send_email


SUPPORT_LINK = ''
UNSUBSCRIBE_LINK = ''


class EmailSendingService:
    """
    This service just allows for sending different types of email messages
    """

    def send_welcome_email(self, request: Request, background_tasks: BackgroundTasks, user: User):
        '''This function sends the welcome email to a user'''

        background_tasks.add_task(
            send_email,
            recipient=user.email,
            template_name="welcome-marketing.html",
            subject="Welcome to TiFi",
            context={
                "request": request,
                "user": user,
                "cta_link": "https://tifi.tv/about"
            }
        )
     
    
    def send_magic_link_email(self, request: Request, background_tasks: BackgroundTasks, user: User, magic_link_url: str):
        '''This function sends the magic link authentication email to a user'''

        background_tasks.add_task(
            send_email,
            recipient=user.email,
            template_name="magic-link.html",
            subject="Magic Link Authentication",
            context={
                "request": request,
                "user": user,
                "url": magic_link_url
            }
        )
    

    def send_reset_password_email(self, request: Request, background_tasks: BackgroundTasks, user: User, reset_url: str):
        '''This function sends the reset password email to a user'''

        background_tasks.add_task(
            send_email,
            recipient=user.email,
            template_name="reset-password.html",
            subject="Reset Password",
            context={
                "request": request,
                "user": user,
                "url": reset_url
            }
        )
    

    def send_reset_password_success_email(self, request: Request, background_tasks: BackgroundTasks, user: User):
        '''This function sends the reset password success email to a user'''

        background_tasks.add_task(
            send_email,
            recipient=user.email,
            template_name="password-reset-complete.html",
            subject="Password Reset Complete",
            context={
                "request": request,
                "user": user,
            }
        )
    


email_sending_service = EmailSendingService()
