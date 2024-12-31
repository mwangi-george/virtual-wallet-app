import logging


def create_logger(name, log_level) -> logging.Logger:
    """ Creates a logger for a given module for a specific log level."""
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
