"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from reflex.components.radix.themes import theme

from rxconfig import config


class State(rx.State):
    """The app state."""

    ...


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to SmartSpend: Your Personal Financial Companion!", size="6"),
            rx.heading("Hello there", size="4"),
            rx.text(
                f"We’re thrilled to have you here at SmartSpend, the platform designed to revolutionize how you "
                f"manage your money. Whether you’re saving for a big goal, tracking your spending habits, or simply "
                f"trying to make smarter financial decisions, you’ve come to the right place.",
                size="5"
            ),
            rx.divider(),
            rx.heading(
                "What is SmartSpend?",
                size="5",
            ),
            rx.text(
                f"SmartSpend is your all-in-one financial assistant that helps you take control of your money with "
                f"ease and confidence. Our platform isn’t just about numbers; it’s about empowering you to make better "
                f"decisions, stay consistent, and achieve your financial dreams.",
                size="5"
            ),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )


app = rx.App(
    theme=theme(appearance="light", has_background=True, radius="large", accent_color="teal")
)
app.add_page(index)
