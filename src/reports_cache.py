from src.logger import logger


def get_cached_report(session_state, report_name, generator_fun):
    """Retrieves a cached report by name if it exists, otherwise generates and caches the report globally.

    Args:
        session_state: A streamlit SessionState dict like object to st.
        report_name (str): The name of the report.
        generator_fun (function): A function that generates the report.

    Returns:
        The cached report if it exists, otherwise the generated report.

    """
    key = _session_state_key(report_name)

    if key in session_state:
        logger.info(f'Using cached report for "{key}" key')
        return session_state[key]
    else:
        logger.info(f'Generating report for "{key}" key')
        report = session_state[key] = generator_fun()
        return report


def is_report_cached(session_state, report_name):
    return bool(session_state.get(_session_state_key(report_name)))


def _session_state_key(report_name):
    return "get_cached_report_" + report_name
