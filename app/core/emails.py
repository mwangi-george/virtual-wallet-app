import os
import json
import requests
import resend
from jinja2 import Environment, FileSystemLoader

from .config import settings

# Set up Jinja2 environment
templates_dir = os.path.join(os.getcwd(), "templates")
jinja_env = Environment(loader=FileSystemLoader(templates_dir))


def send_email(recipient: str, subject: str, email_body_data: dict,
               redirect_to: str | None, button_label: str, email_template: str):
    """ Custom function for sending an email with an HTML template """
    url = "https://api.brevo.com/v3/smtp/email"

    # Load and render the template with provided data
    template = jinja_env.get_template(email_template)
    email_body_data['redirect_to'] = redirect_to
    email_body_data['button_label'] = button_label
    email_body = template.render(subject=subject, **email_body_data)

    # Define the payload
    payload = json.dumps(
        {
            "sender": {"name": "VMS Team", "email": settings.BREVO_EMAIL},
            "to": [{"email": recipient}],
            "subject": subject,
            "htmlContent": email_body  # Use htmlContent for HTML emails
        }
    )

    # Define headers
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=payload)
    print(response.text)


def send_email_with_resend(recipient: str, subject: str, body: str):
    resend.api_key = settings.RESEND_API_KEY

    params = {
        "from": "VWS Team <vws-team@resend.dev>",
        "to": [recipient],
        "subject": subject,
        "html": body
    }

    email = resend.Emails.send(params)
    print(email)
