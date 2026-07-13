import logging

def get_provider_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"provider.{name}")
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)
    return logger
