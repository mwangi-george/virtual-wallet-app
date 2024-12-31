import reflex as rx
from frontend.core.login import login_to_api
import asyncio


class BaseState(rx.State):

    user: dict | None = None

    def logout(self):
        """Logs out a user."""
        self.reset()
        return rx.redirect(path="/")

    def check_login(self):
        """Redirects login to login page if the user is not logged in."""
        if not self.logged_in:
            return rx.redirect(path="/login")

    @rx.var
    def logged_in(self) -> bool:
        """Checks if the user is logged in."""
        return self.user is not None


class AuthState(BaseState):
    """The authentication state for login and signup"""
    first_name: str
    last_name: str
    email: str = "mwangigeorge648@gmail.com"
    password: str = "zxcv"
    confirm_password: str
    token: str
    updated_first_name: str
    updated_last_name: str
    updated_email: str

    def login(self):
        user = login_to_api(self.email, self.password)
        if user:
            self.user = user
            return rx.redirect(path="/")
        else:
            return rx.window_alert("Incorrect email or password")
