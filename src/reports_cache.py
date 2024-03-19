from src.logger import logger

_cache = {}


def get_cached_report(name, report_fun):
    """Retrieves a cached report by name if it exists, otherwise generates and caches the report globally.

    Args:
        name (str): The name of the report.
        report_fun (function): A function that generates the report.

    Returns:
        The cached report if it exists, otherwise the generated report.

    """
    if name in _cache:
        logger.info(f'Using cached report for "{name}" key')
        return _cache[name]
    else:
        logger.info(f'Generating report for "{name}" key')
        report = _cache[name] = report_fun()
        return report
