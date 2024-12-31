import reflex as rx
from ..components.navbar_home import navbar


@rx.page(route="/", title="SmartSpend")
def home_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.color_mode.button(position="bottom-right"),
            rx.vstack(
                rx.heading(
                    "Welcome to SmartSpend: Your Personal Financial Companion!", size="6"),
                rx.heading("Hello there!", size="4", color_scheme="red"),
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
                    color_scheme="red"
                ),
                rx.text(
                    f"SmartSpend is your all-in-one financial assistant that helps you take control of your money with "
                    f"ease and confidence. Our platform isn’t just about numbers; it’s about empowering you to make better "
                    f"decisions, stay consistent, and achieve your financial dreams.",
                    size="5"
                ),
                rx.text(
                    "Here’s how we make it happen: ",
                    size="5"
                ),
                rx.list.unordered(
                    rx.list.item(
                        rx.heading("Seamless Account Management", size="3"),
                    ),
                    rx.text(
                        "Sign up in minutes and create your own personal financial hub. Your account is secure, verified, and ready to grow with you.",
                        size="5"
                    ),
                    rx.list.item(
                        rx.heading("Automated Spending Allocations", size="3"),
                    ),
                    rx.text(
                        "Deposit funds into your SmartSpend wallet, tell us how long you need it to last, and we’ll handle the rest. Our system calculates and allocates daily spending limits, ensuring you never overspend while staying on track. ",
                        size="5"
                    ),
                    rx.list.item(
                        rx.heading("Real-Time Analytics", size="3"),
                    ),
                    rx.text(
                        "Get detailed insights into your spending habits with interactive graphs and monthly trends. See where your money goes and discover ways to save more.",
                        size="5"
                    ),
                    rx.list.item(
                        rx.heading(
                            "Customized Wallets for Financial Goals", size="3"),
                    ),
                    rx.text(
                        "Need to save for a vacation? Or maybe a rainy-day fund? Set up tailored wallets with ease and let SmartSpend guide you toward your goals.",
                        size="5"
                    ),
                ),
                rx.divider(),
                rx.heading(
                    "Why Choose SmartSpend?",
                    size="5",
                    color_scheme="red"
                ),
                rx.list.unordered(
                    rx.list.item(
                        "💡 Intelligent Planning: Our smart algorithms take the guesswork out of budgeting."),
                    rx.list.item(
                        "🔒 Secure & Reliable: Your financial data is safe with us, backed by industry-standard encryption."),
                    rx.list.item(
                        "🌍 Accessible Anytime, Anywhere: Manage your money on the go, on any device."),
                    rx.list.item(
                        "🚀 Fast & Simple: From sign-up to saving, everything is designed to be intuitive and hassle-free."),
                    list_style_type=None,
                ),
                rx.divider(),
                rx.heading(
                    "Get Started Today!",
                    size="5",
                    color_scheme="red"
                ),
                rx.heading(
                    "Take charge of your financial future.",
                    size="3",
                ),
                rx.text(
                    "Join thousands of users who trust SmartSpend to simplify their money management and unlock the freedom to focus on what really matters.",
                    size="5",
                ),
                rx.text(
                    "Click the button below to create your free account and start your journey toward smarter spending today!",
                    size="4",
                ),
                rx.button("Sign Up Now", on_click=rx.redirect(path="/signup")),
                spacing="5",
                justify="center",
                min_height="85vh",
            ),
        ),
    )
