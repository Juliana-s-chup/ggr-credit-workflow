"""
Monitoring et Error Tracking
Sentry + Logging structurÃ©
"""

import logging
from django.conf import settings

# Import optionnel de Sentry (ne pas bloquer si absent)
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None

logger = logging.getLogger(__name__)


def init_sentry():
    """
    Initialise Sentry pour le tracking d'erreurs
    """
    if not SENTRY_AVAILABLE:
        logger.warning("âš ï¸ Sentry SDK not installed. Monitoring disabled.")
        return

    if not settings.DEBUG and hasattr(settings, "SENTRY_DSN"):
        sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
                sentry_logging,
            ],
            traces_sample_rate=0.1,  # 10% des transactions
            send_default_pii=False,  # Pas de donnÃ©es personnelles
            environment=getattr(settings, "ENVIRONMENT", "development"),
            release=getattr(settings, "VERSION", "1.0.0"),
        )

        logger.info("âœ… Sentry initialized")
    else:
        logger.info("â„¹ï¸ Sentry disabled (DEBUG=True or no DSN)")


def log_business_event(event_type: str, user_id: int, data: dict):
    """
    Log un Ã©vÃ©nement mÃ©tier important

    Args:
        event_type: Type d'Ã©vÃ©nement (DOSSIER_CREATED, STATUS_CHANGED, etc.)
        user_id: ID de l'utilisateur
        data: DonnÃ©es de l'Ã©vÃ©nement
    """
    logger.info(
        f"Business Event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "data": data,
        },
    )


def log_security_event(event_type: str, user=None, ip: str = None, details: dict = None, **kwargs):
    """
    Log un Ã©vÃ©nement de sÃ©curitÃ©

    Args:
        event_type: Type (LOGIN_FAILED, UNAUTHORIZED_ACCESS, etc.)
        user: Objet User Django (optionnel)
        ip: Adresse IP (optionnel)
        details: DÃ©tails de l'Ã©vÃ©nement (optionnel)
        **kwargs: Arguments supplÃ©mentaires
    """
    user_id = user.id if user else kwargs.get("user_id", None)

    logger.warning(
        f"Security Event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "ip": ip,
            "details": details or {},
        },
    )
