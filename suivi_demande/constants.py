"""
Constantes pour l'application suivi_demande.
Ã‰vite les "magic numbers" et centralise les valeurs configurables.
"""

from decimal import Decimal

# Taux et limites financiÃ¨res
TAUX_ENDETTEMENT_MAX = Decimal("0.40")  # 40% du salaire
MONTANT_MINIMUM_CREDIT = Decimal("100000.00")  # 100 000 FCFA
MONTANT_MAXIMUM_CREDIT = Decimal("50000000.00")  # 50 000 000 FCFA
DUREE_MINIMUM_MOIS = 6
DUREE_MAXIMUM_MOIS = 120  # 10 ans

# Uploads
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_FILE_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
]
ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]

# Pagination
ITEMS_PER_PAGE = 25
NOTIFICATIONS_PER_PAGE = 20

# Cache
CACHE_TIMEOUT_STATS = 300  # 5 minutes
CACHE_TIMEOUT_DASHBOARD = 180  # 3 minutes

# Age minimum pour un demandeur
AGE_MINIMUM = 18
AGE_MAXIMUM = 70

# DÃ©lais (en jours)
DELAI_TRAITEMENT_STANDARD = 15
DELAI_ALERTE_RETARD = 20

# Messages
MSG_DOSSIER_CREE = "Dossier crÃ©Ã© avec succÃ¨s"
MSG_DOSSIER_MODIFIE = "Dossier modifiÃ© avec succÃ¨s"
MSG_DOSSIER_SUPPRIME = "Dossier supprimÃ© avec succÃ¨s"
MSG_ACCES_REFUSE = "AccÃ¨s refusÃ© pour votre rÃ´le"
MSG_TRANSITION_REUSSIE = "Transition effectuÃ©e avec succÃ¨s"
MSG_TRANSITION_REFUSEE = "Action non autorisÃ©e pour votre rÃ´le ou l'Ã©tat du dossier"
