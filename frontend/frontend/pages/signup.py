import reflex as rx
# from ..state.auth import AuthState


@rx.page(route="/signup", title="Signup")
def signup_page() -> rx.Component:
    """
    User registration component
    :return: Component
    """
    return rx.container(
        rx.flex(
            rx.card(
                rx.vstack(
                    rx.center(
                        rx.heading(
                            "Create an Account",
                            size="3",
                            as_="h2",
                            text_align="center",
                            width="100%",
                        ),
                        direction="column",
                        spacing="5",
                        width="100%",
                    ),
                    rx.form(
                        rx.vstack(
                            rx.vstack(
                                rx.text(
                                    "First Name",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("user")),
                                    placeholder="Enter your first name",
                                    type="name",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    # value=AuthState.first_name,
                                    # on_change=AuthState.set_first_name,
                                ),
                                justify="center",
                                spacing="3",
                                width="100%",
                            ),

                            rx.vstack(
                                rx.text(
                                    "Last Name",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("user")),
                                    placeholder="Enter your last name",
                                    type="name",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    # value=AuthState.last_name,
                                    # on_change=AuthState.set_last_name,
                                ),
                                justify="center",
                                spacing="3",
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
                                    placeholder="Enter your email address",
                                    type="name",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    # value=AuthState.email,
                                    # on_change=AuthState.set_email,
                                ),
                                justify="center",
                                spacing="3",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Password",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock")),
                                    placeholder="Create a password",
                                    type="password",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    # value=AuthState.password,
                                    # on_change=AuthState.set_password,
                                ),
                                justify="center",
                                spacing="3",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Confirm Password",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock")),
                                    placeholder="Retype your password",
                                    type="password",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    # value=AuthState.confirm_password,
                                    # on_change=AuthState.set_confirm_password,
                                ),
                                justify="center",
                                spacing="3",
                                width="100%",
                            ),
                            rx.button(
                                "Sign Up",
                                size="3",
                                width="100%",
                                type="submit",
                                _hover={"bg": "green"},
                            ),
                        ),
                        spacing="9",
                        # on_submit=AuthState.signup
                    ),
                    rx.center(
                        rx.text("Already registered?", size="3"),
                        rx.link("Sign in", href="/login", size="3"),
                        opacity="0.8",
                        spacing="2",
                        direction="row",
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                ),
                # card style
                max_width="30em",
                size="4",
                width="100%",
                spacing="5",
            ),
            justify="center"
        ),
        padding="20px"
    )
