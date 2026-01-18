"""
Configuration et helpers pour le logging professionnel de l'application.
"""

import logging
from functools import wraps

# Loggers specialises
logger = logging.getLogger("suivi_demande")
security_logger = logging.getLogger("suivi_demande.security")
workflow_logger = logging.getLogger("suivi_demande.workflow")
models_logger = logging.getLogger("suivi_demande.models")


# LOGS Me‰TIER - DOSSIERS
def log_dossier_creation(dossier, user):
    """Log la creation d'un nouveau dossier."""
    workflow_logger.info(
        f"[CRe‰ATION DOSSIER] Reference: {dossier.reference} | "
        f"Client: {dossier.client.username} | Montant: {dossier.montant} FCFA | "
        f"Cree par: {user.username}"
    )


def log_dossier_update(dossier, user, fields_changed=None):
    """Log la modification d'un dossier."""
    fields_info = f" | Champs: {', '.join(fields_changed)}" if fields_changed else ""
    workflow_logger.info(
        f"[MODIFICATION DOSSIER] Reference: {dossier.reference} | "
        f"Par: {user.username}{fields_info}"
    )


def log_dossier_deletion(dossier, user):
    """Log la suppression d'un dossier."""
    workflow_logger.warning(
        f"[SUPPRESSION DOSSIER] Reference: {dossier.reference} | "
        f"Client: {dossier.client.username} | Supprime par: {user.username}"
    )


# LOGS WORKFLOW - TRANSITIONS
def log_transition(dossier, action, user, from_status, to_status, comment=None):
    """Log une transition de statut."""
    comment_info = f" | Commentaire: {comment}" if comment else ""
    workflow_logger.info(
        f"[TRANSITION] Dossier: {dossier.reference} | "
        f"{from_status} â†’ {to_status} | Action: {action} | "
        f"Par: {user.username} | Role: {getattr(user.profile, 'role', 'N/A')}{comment_info}"
    )


def log_workflow_error(dossier, action, user, error):
    """Log une erreur lors d'une transition."""
    workflow_logger.error(
        f"[ERREUR WORKFLOW] Dossier: {dossier.reference} | "
        f"Action: {action} | Par: {user.username} | Erreur: {str(error)}"
    )


# LOGS Se‰CURITe‰
def log_login_success(user, ip_address=None):
    """Log une connexion reussie."""
    ip_info = f" | IP: {ip_address}" if ip_address else ""
    security_logger.info(
        f"[LOGIN SUCCESS] User: {user.username} | "
        f"Role: {getattr(user.profile, 'role', 'N/A')}{ip_info}"
    )


def log_login_failure(username, ip_address=None, reason=None):
    """Log une tentative de connexion echouee."""
    ip_info = f" | IP: {ip_address}" if ip_address else ""
    reason_info = f" | Raison: {reason}" if reason else ""
    security_logger.warning(f"[LOGIN FAILED] Username: {username}{ip_info}{reason_info}")


def log_logout(user):
    """Log une deconnexion."""
    security_logger.info(f"[LOGOUT] User: {user.username}")


def log_unauthorized_access(user, resource, action, reason=None):
    """Log une tentative d'acces non autorise."""
    reason_info = f" | Raison: {reason}" if reason else ""
    security_logger.warning(
        f"[ACCeˆS REFUSe‰] User: {user.username} | "
        f"Role: {getattr(user.profile, 'role', 'N/A')} | "
        f"Ressource: {resource} | Action: {action}{reason_info}"
    )


def log_permission_denied(user, permission, resource=None):
    """Log un refus de permission."""
    resource_info = f" | Ressource: {resource}" if resource else ""
    security_logger.warning(
        f"[PERMISSION DENIED] User: {user.username} | " f"Permission: {permission}{resource_info}"
    )


# LOGS MODeˆLES
def log_model_creation(model_name, instance_id, user=None):
    """Log la creation d'une instance."""
    user_info = f" | Par: {user.username}" if user else ""
    models_logger.debug(f"[CREATE] {model_name} | ID: {instance_id}{user_info}")


def log_model_update(model_name, instance_id, fields=None, user=None):
    """Log la mise e  jour d'une instance."""
    fields_info = f" | Champs: {', '.join(fields)}" if fields else ""
    user_info = f" | Par: {user.username}" if user else ""
    models_logger.debug(f"[UPDATE] {model_name} | ID: {instance_id}{fields_info}{user_info}")


def log_model_deletion(model_name, instance_id, user=None):
    """Log la suppression d'une instance."""
    user_info = f" | Par: {user.username}" if user else ""
    models_logger.warning(f"[DELETE] {model_name} | ID: {instance_id}{user_info}")


# LOGS ERREURS
def log_error(context, error, user=None, extra_info=None):
    """Log une erreur generique."""
    user_info = f" | User: {user.username}" if user else ""
    extra = f" | Info: {extra_info}" if extra_info else ""
    logger.error(f"[ERREUR] Contexte: {context} | Erreur: {str(error)}{user_info}{extra}")


def log_exception(context, exception, user=None):
    """Log une exception avec traceback."""
    user_info = f" | User: {user.username}" if user else ""
    logger.exception(f"[EXCEPTION] Contexte: {context}{user_info}", exc_info=exception)


def log_validation_error(form_name, errors, user=None):
    """Log une erreur de validation."""
    user_info = f" | User: {user.username}" if user else ""
    logger.warning(f"[VALIDATION ERROR] Formulaire: {form_name} | Erreurs: {errors}{user_info}")


# LOGS NOTIFICATIONS
def log_notification_sent(notification_type, recipient, title):
    """Log l'envoi d'une notification."""
    logger.info(
        f"[NOTIFICATION] Type: {notification_type} | "
        f"Destinataire: {recipient.username} | Titre: {title}"
    )


def log_email_sent(recipient, subject, success=True):
    """Log l'envoi d'un email."""
    status = "SUCCESS" if success else "FAILED"
    level = logger.info if success else logger.error
    level(f"[EMAIL {status}] Destinataire: {recipient} | Sujet: {subject}")


# De‰CORATEURS
def log_view_access(view_name):
    """Decorateur pour logger l'acces e  une vue."""

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user if request.user.is_authenticated else "Anonymous"
            logger.debug(
                f"[VIEW ACCESS] Vue: {view_name} | User: {user} | Method: {request.method}"
            )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
