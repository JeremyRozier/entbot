import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def display_message(message, show_message=True, level=logging.INFO) -> None:
    """Displays message using logging library.

    Args:
        - message (str): The message to display
        - show_message (bool): If it is set to True the function will display
        the message, otherwise the function will do nothing
        - level (int): Value used in the logging library to qualify the
        message between logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
        and logging.CRITICAL. Default value is logging.INFO.

    Returns None
    """

    if show_message:
        if level == logging.DEBUG:
            logging.debug(message)
        elif level == logging.INFO:
            logging.info(message)
        elif level == logging.WARNING:
            logging.warning(message)
        elif level == logging.ERROR:
            logging.error(message)
        elif level == logging.CRITICAL:
            logging.critical(message)
