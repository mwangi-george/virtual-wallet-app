import logging


def create_logger(name, log_level) -> logging.Logger:
    """
    Creates a logger for a given module with a specified log level.

    Args:
        name (str): The name of the logger, typically the module or class name.
        log_level (int): The logging level, such as logging.DEBUG, logging.INFO, etc.

    Returns:
        logging.Logger: A configured logger instance.

    This function sets up a logger that:
    - Outputs logs of level INFO or higher to the console.
    - Writes log entries to a file named 'logs.txt' with a specific format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level=log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.INFO)
    logger.addHandler(console_handler)

    logging.basicConfig(
        filename='logs.txt',
        format="%(levelname)-5s %(name)-10s %(asctime)-10s %(message)s",
    )
    return logger
