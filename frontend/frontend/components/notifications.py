import reflex as rx


def notify_info(message: str):
    return rx.toast.info(message, position="bottom-right")


def notify_error(message: str):
    return rx.toast.error(message, position="bottom-right")


def notify_success(message: str):
    return rx.toast.success(message, position="bottom-right")


def notify_warning(message: str):
    return rx.toast.warning(message, position="bottom-right")
