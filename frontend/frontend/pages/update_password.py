import reflex as rx
from ..state.auth import AuthState


@rx.page(route="/update-user-password/[user_token]", title="Update Password")
def update_password_page() -> rx.Component:
    return rx.container(
        rx.flex(
            rx.card(
                rx.form(
                    rx.vstack(
                        rx.center(
                            rx.heading(
                                "Reset your password",
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
                            rx.vstack(
                                rx.text(
                                    "New Password",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock")),
                                    placeholder="Create a new Password",
                                    type="password",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    value=AuthState.password,
                                    on_change=AuthState.set_password,
                                ),
                                justify="center",
                                spacing="3",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Confirm New Password",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock")),
                                    placeholder="Retype your New Password",
                                    type="password",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    value=AuthState.confirm_password,
                                    on_change=AuthState.set_confirm_password
                                ),
                                justify="center",
                                spacing="3",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.button(
                            "Submit",
                            type="submit",
                            size="3",
                            width="100%",
                            # disabled=AuthState.disable_submit,
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    on_submit=AuthState.update_password,
                ),
                max_width="28em",
                size="4",
                width="100%",
            ),
            justify="center",

        ),
        padding="100px"
    )