import logging
from pdf2qa.utils.logging import setup_logging

def test_setup_logging_idempotent():
    """setup_logging should not add duplicate handlers"""
    logger1 = setup_logging(verbose=True)
    handlers_after_first = len(logger1.handlers)
    logger2 = setup_logging(verbose=False)
    handlers_after_second = len(logger2.handlers)
    assert handlers_after_first == handlers_after_second == 1
