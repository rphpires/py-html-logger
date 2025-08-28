from .core import Logger

# Create a singleton instance
_logger = Logger()

# Export the main functions


def log(message, color="white", tag="log"):
    _logger.log(message, color, tag)


def info(message, color="white", tag="info"):
    _logger.info(message, color, tag)


def debug(message, color="white", tag="debug"):
    _logger.debug(message, color, tag)


def warning(message, color="gold", tag="warning"):
    _logger.warning(message, color, tag)


def error(message, tag="error"):
    _logger.error(message, tag)


def report_exception(exc, timeout=None):
    _logger.report_exception(exc, timeout)


def config(**kwargs):
    from . import config as cfg
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)


def flush():
    """Força escrita imediata dos logs pendentes"""
    _logger.flush()


def close():
    """Fecha logger e finaliza arquivo HTML adequadamente"""
    _logger.close()


def finalize():
    """Finaliza arquivo HTML com tags de fechamento corretas"""
    _logger.close()


def disable_filter_monitoring():
    """Desabilita monitoramento de filtros para máxima performance"""
    _logger.disable_filter_monitoring()


def enable_filter_monitoring():
    """Habilita monitoramento de filtros"""
    _logger.enable_filter_monitoring()
