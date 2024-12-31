import reflex as rx
from ..state.auth import AuthState


@rx.page(route="/forgot-password", title="Forgot Password")
def forgot_password_page() -> rx.Component:
    return rx.container(
        rx.flex(
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.center(
                            rx.heading(
                                "Forgot your password?",
                                size="3",
                                as_="h2",
                                text_align="center",
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                            width="100%",
                        ),
                        rx.text("Enter your email below to get reset link"),
                        rx.vstack(
                            rx.text(
                                "Email address",
                                size="3",
                                weight="medium",
                                text_align="left",
                                width="100%",
                            ),
                            rx.input(
                                rx.input.slot(rx.icon("user")),
                                placeholder="user@gmail.com",
                                type="email",
                                size="3",
                                width="100%",
                                value=AuthState.email,
                                on_change=AuthState.set_email,
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.button(
                            "Submit",
                            type="submit",
                            size="3",
                            width="100%",
                            _hover={"bg": "green"},
                        ),
                        rx.center(
                            rx.text("Remembered your password?", size="3"),
                            rx.link("Sign in", href="/login", size="3"),
                            opacity="0.8",
                            spacing="2",
                            direction="row",
                            width="100%",
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    on_submit=AuthState.send_password_reset_email_in_bg
                ),
                max_width="28em",
                size="4",
                width="100%",
            ),
            justify="center",
        ),
        padding="100px",
    )
