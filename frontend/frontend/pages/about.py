import reflex as rx
from ..componets.navbar_dashboard import navbar_dashboard
from ..state.auth import AuthState


@rx.page(route="/about", title="About")
def about_page() -> rx.Component:
    return rx.fragment(
        navbar_dashboard(data=""),
        rx.container(
            rx.heading(
                "Welcome to about page"
            )
        )
    )
