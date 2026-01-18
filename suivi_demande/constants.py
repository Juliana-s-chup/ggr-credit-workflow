"""
Constantes pour l'application suivi_demande.
Évite les "magic numbers" et centralise les valeurs configurables.
"""

from decimal import Decimal

# Taux et limites financières
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

# Délais (en jours)
DELAI_TRAITEMENT_STANDARD = 15
DELAI_ALERTE_RETARD = 20

# Messages
MSG_DOSSIER_CREE = "Dossier créé avec succès"
MSG_DOSSIER_MODIFIE = "Dossier modifié avec succès"
MSG_DOSSIER_SUPPRIME = "Dossier supprimé avec succès"
MSG_ACCES_REFUSE = "Accès refusé pour votre rôle"
MSG_TRANSITION_REUSSIE = "Transition effectuée avec succès"
MSG_TRANSITION_REFUSEE = "Action non autorisée pour votre rôle ou l'état du dossier"
