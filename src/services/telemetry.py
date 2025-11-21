import os
from typing import Dict

APP_INSIGHTS_KEY = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")

# Lightweight telemetry wrapper. If APPINSIGHTS_INSTRUMENTATIONKEY is provided,
# you can extend this module to push to Application Insights or another APM.


def track_event(name: str, properties: Dict[str, str] | None = None):
    # Placeholder: log to stdout for now
    import logging
    logger = logging.getLogger("telemetry")
    logger.info(f"TELEMETRY EVENT: {name} - {properties}")


def track_exception(exc: Exception, properties: Dict[str, str] | None = None):
    import logging
    logger = logging.getLogger("telemetry")
    logger.exception(f"TELEMETRY EXCEPTION: {exc} - {properties}")


def set_user_context(user_id: str):
    # Placeholder for user-scoped telemetry
    pass
