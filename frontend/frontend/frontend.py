"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from reflex.components.radix.themes import theme

from frontend.pages import *


app = rx.App(
    theme=theme(appearance="light", has_background=True,
                radius="large", accent_color="red")
)
app.add_page(home_page)
app.add_page(login_page)
app.add_page(signup_page)
