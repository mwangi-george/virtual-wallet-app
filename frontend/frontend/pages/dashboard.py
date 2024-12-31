import reflex as rx

from ..componets.income_table import income_table
from ..componets.expense_table import expense_table
from ..componets.navbar_dashboard import navbar_dashboard
from ..componets.stat_cards import stats_cards_group
from ..state.auth import AuthState
from ..state.income import IncomeState
from ..state.expense import ExpenseState


@rx.page(route='/dashboard/home', title="Dashboard", on_load=AuthState.check_login)
def dashboard_home() -> rx.Component:
    return rx.vstack(
        navbar_dashboard(data=""),
        # rx.text("Info coming"),
        rx.flex(
            rx.button(
                "View your incomes",
                size="2",
                on_click=rx.redirect(path="/dashboard/incomes"),
            ),
            rx.button(
                "View your expenses",
                size="2",
                on_click=rx.redirect(path="/dashboard/expenses"),
            ),
            spacing="2",
            justify="center",
            align="center",
            width="100%",

        )
    )


@rx.page(route="/dashboard/incomes", title="Incomes", on_load=AuthState.check_login)
def incomes_dashboard() -> rx.Component:
    return rx.vstack(
        navbar_dashboard(data="Incomes"),
        rx.card(
            stats_cards_group("Incomes", IncomeState.count_of_all_incomes, IncomeState.sum_of_all_incomes),
            rx.box(
                income_table(),
                width="100%",
            ),
            width="100%",
        ),
        width="100%",
        spacing="6",
        # padding_x=["1.5em", "1.5em", "3em"],
    )


@rx.page(route="/dashboard/expenses", title="Expenses", on_load=AuthState.check_login)
def expenses_dashboard() -> rx.Component:
    return rx.vstack(
        navbar_dashboard(data="Expenses"),
        rx.card(
            stats_cards_group("Expenses", ExpenseState.count_of_all_expenses, ExpenseState.sum_of_all_expenses),
            rx.box(
                expense_table(),
                width="100%",
            ),
            width="100%",
        ),
        width="100%",
        spacing="6",
    )
