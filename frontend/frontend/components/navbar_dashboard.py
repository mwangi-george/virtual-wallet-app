import reflex as rx
from ..state.auth import AuthState


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.text(text, size="4", weight="medium"), href=url,
    )


def navbar_content(user_first_name: str, user_last_name: str, data: str) -> rx.Component:
    return rx.flex(
        rx.badge(
            rx.icon(tag="table-2", size=28),
            rx.heading(f"Personal Finance Manager - {user_first_name} {user_last_name} {data}", size="6"),
            color_scheme="green",
            radius="large",
            align="center",
            variant="surface",
            padding="0.65rem",
        ),
        spacing="7",
        flex_direction=["column", "column", "row"],
        align="center",
        width="100%",
        top="0px",
        padding_top="1em",
    )


def navbar_dashboard(data: str) -> rx.Component:
    setting_button = rx.menu.root(
        rx.menu.trigger(
            rx.icon_button(
                rx.icon("user"),
                size="2",
                radius="full",
            ),
        ),
        rx.menu.content(
            rx.menu.item("Settings", on_click=rx.redirect(path="/dashboard/settings")),
            rx.menu.separator(),
            rx.menu.item("Log out", on_click=AuthState.logout),
        ),
        justify="end",
    )

    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    navbar_content(AuthState.user.first_name, AuthState.user.last_name, data),
                    align_items="center",
                ),
                setting_button,
                justify="between",
                align_items="center",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    navbar_content(AuthState.user.first_name, AuthState.user.last_name, data),
                    align_items="center",
                ),
                setting_button,
                justify="between",
                align_items="center",
            ),
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        width="100%",
    )
