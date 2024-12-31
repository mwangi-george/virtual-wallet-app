import reflex as rx


class BaseState(rx.State):

    user: User | None = None

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
