import reflex as rx
from rxconfig import config


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.text(text, size="4", weight="medium"), href=url
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        tag="landmark", stroke_width=2,
                    ),
                    rx.heading(
                        "SmartSpend", size="7", weight="bold",
                    ),
                    align_items="center",
                ),
                rx.hstack(
                    navbar_link("About", "/about"),
                    spacing="5",
                ),
                rx.hstack(
                    rx.button(
                        "Sign Up", size="3", on_click=rx.redirect(path="/signup"),
                        _hover={"bg": "green"},
                    ),
                    rx.button(
                        "Log In", size="3", on_click=rx.redirect(path="/login"),
                        _hover={"bg": "green"},
                    ),
                    spacing="4",
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(

                    rx.heading(
                        config.app_name, size="6", weight="bold"
                    ),
                    align_items="center",
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.icon("menu", size=30)
                    ),
                    rx.menu.content(
                        rx.menu.item(
                            "About", on_click=rx.redirect(path="/about")),
                        rx.menu.separator(),
                        rx.menu.item(
                            "Log in", on_click=rx.redirect(path="/login")),
                        rx.menu.item(
                            "Sign up", on_click=rx.redirect(path="/signup")),
                    ),
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        # position="fixed",
        # top="0px",
        # z_index="5",
        width="100%",
    )
