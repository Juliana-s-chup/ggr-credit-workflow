"""
Fonctions utilitaires partagees entre les modules de vues.
"""

import logging
from datetime import date, datetime
from decimal import Decimal

logger = logging.getLogger("suivi_demande")


def serialize_form_data(data):
    """Convertit les objets Decimal, date et datetime en strings pour la serialisation JSON."""
    serialized = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, date):
            serialized[key] = value.isoformat()
        elif isinstance(value, float):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized
