import reflex as rx
from ..componets.navbar_dashboard import navbar_dashboard
from ..state.auth import AuthState


@rx.page(route="/dashboard/settings", title="Settings", on_load=AuthState.check_login)
def settings_page() -> rx.Component:
    return rx.fragment(
        navbar_dashboard(data=""),
        rx.container(
            rx.avatar(src="/logo.jpg", fallback="RU", size="9"),
            rx.text(f"{AuthState.user.first_name} {AuthState.user.last_name}", weight="bold", size="4"),
            rx.text(f"@{AuthState.user.email}", color_scheme="gray"),
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.button(
                        rx.icon("plus", size=26),
                        rx.text("Update your profile", size="4"),
                    ),
                ),
                rx.dialog.content(
                    rx.dialog.title(
                        "Update your profile",
                    ),
                    rx.dialog.description(
                        "Fill the form with your new data",
                    ),
                    rx.form(
                        rx.flex(
                            rx.input(
                                placeholder="First Name",
                                name="first_name",
                                required=True,
                                value=AuthState.user.first_name,
                                on_change=AuthState.set_updated_first_name,
                            ),
                            rx.input(
                                placeholder="Last Name",
                                name="last_name",
                                required=True,
                                value=AuthState.user.last_name,
                                on_change=AuthState.set_updated_last_name,
                            ),
                            rx.input(
                                placeholder="user@gmail.com",
                                name="email",
                                required=True,
                                value=AuthState.user.email,
                                on_change=AuthState.set_updated_email,
                            ),
                            rx.flex(
                                rx.dialog.close(
                                    rx.button(
                                        "Cancel",
                                        variant="soft",
                                        color_scheme="gray",
                                    ),
                                ),
                                rx.dialog.close(
                                    rx.button("Submit", type="submit"),
                                ),
                                spacing="3",
                                justify="end",
                            ),
                            direction="column",
                            spacing="4",
                        ),
                        on_submit=AuthState.update_user_profile,
                        reset_on_submit=False,
                    ),
                    max_width="450px",
                ),
            ),
            spacing="1",
        ),
    )
