import logging


def setup_logger(name: str, output_file: str, level=logging.DEBUG) -> logging.Logger:
    """
    This function creates a logging object with the given parameters.

    Parameters:
    ---------------
        name:
            The name for the logging object.

        output_file:
            The output file where the log messages will me written.

    Returns:
    ---------------
        The initialized logger (logging object).
    """

    handler = logging.FileHandler(output_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
