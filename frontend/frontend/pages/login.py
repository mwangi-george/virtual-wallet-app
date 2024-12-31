import reflex as rx
from frontend.states.auth import AuthState


@rx.page(route="/login", title="Login")
def login_page() -> rx.Component:
    return rx.container(
        rx.flex(
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.center(
                            rx.heading(
                                "Sign in to your account",
                                size="6",
                                as_="h2",
                                text_align="center",
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                            width="100%",
                        ),
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
                                required=True,  # Ensure this field is required
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Password",
                                    size="3",
                                    weight="medium",
                                ),
                                rx.link(
                                    "Forgot password?",
                                    href="/forgot-password",
                                    size="3",
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.input(
                                rx.input.slot(rx.icon("lock")),
                                placeholder="Enter your password",
                                type="password",
                                size="3",
                                width="100%",
                                value=AuthState.password,
                                on_change=AuthState.set_password,
                                required=True,  # Ensure this field is required
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.text(
                            # LoginState.message,
                            color="red",
                            text_align="center",
                            width="100%",
                            margin_top="1em",
                        ),
                        rx.button(
                            "Sign in",
                            size="3",
                            width="100%",
                            type="submit",
                            _hover={"bg": "green"},
                        ),
                        rx.center(
                            rx.text("New here?", size="3"),
                            rx.link("Sign up", href="/signup", size="3"),
                            opacity="0.8",
                            spacing="2",
                            direction="row",
                            width="100%",
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    on_submit=AuthState.login,
                    auto_complete=True,
                ),
                max_width="30em",
                min_width="28em",
                size="4",
                width="100%",
            ),
            justify="center",

        ),
        padding="100px"
    )
