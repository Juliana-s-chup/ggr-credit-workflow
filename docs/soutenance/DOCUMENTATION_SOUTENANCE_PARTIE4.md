# 📚 DOCUMENTATION SOUTENANCE - PARTIE 4
## Base de Données et Logique Métier

---

# 6. BASE DE DONNÉES

## 6.1 Structure des tables

### Vue d'ensemble des relations :

```
┌─────────────────────┐
│    auth_user        │  (Django par défaut)
│  - id               │
│  - username         │
│  - password         │
│  - email            │
└──────────┬──────────┘
           │ 1:1
           │
┌──────────▼──────────┐
│  UserProfile        │
│  - user_id          │
│  - full_name        │
│  - phone            │
│  - role             │  ← CLIENT, GESTIONNAIRE, etc.
└─────────────────────┘

┌─────────────────────┐
│  DossierCredit      │  ← Table centrale
│  - id               │
│  - client_id        │  → auth_user
│  - reference        │  (unique)
│  - montant          │
│  - statut_agent     │
│  - statut_client    │
│  - acteur_courant_id│  → auth_user
│  - date_soumission  │
└──────────┬──────────┘
           │ 1:N
           │
┌──────────▼──────────┐
│  PieceJointe        │
│  - id               │
│  - dossier_id       │  → DossierCredit
│  - fichier          │  (path)
│  - type_piece       │
│  - upload_at        │
└─────────────────────┘

┌─────────────────────┐
│  CanevasProposition │  (1:1 avec DossierCredit)
│  - dossier_id       │  → DossierCredit
│  - nom_prenom       │
│  - date_naissance   │
│  - emploi_occupe    │
│  - salaire_net      │
│  - ... (50+ champs) │
└─────────────────────┘

┌─────────────────────┐
│  JournalAction      │  ← Audit trail
│  - id               │
│  - dossier_id       │  → DossierCredit
│  - acteur_id        │  → auth_user
│  - action           │
│  - timestamp        │
└─────────────────────┘

┌─────────────────────┐
│  Notification       │
│  - id               │
│  - utilisateur_cible_id│ → auth_user
│  - dossier_id       │  → DossierCredit
│  - message          │
│  - lu               │
└─────────────────────┘

┌─────────────────────┐
│  Commentaire        │
│  - id               │
│  - dossier_id       │  → DossierCredit
│  - auteur_id        │  → auth_user
│  - contenu          │
└─────────────────────┘
```

## 6.2 Rôle de chaque table

### 1. `auth_user` (Django)
**Rôle** : Gère l'authentification de base

**Champs principaux** :
- `username` : Identifiant de connexion (unique)
- `password` : Mot de passe hashé (PBKDF2-SHA256)
- `email` : Email de l'utilisateur
- `is_active` : Compte actif ou non
- `is_staff` : Accès à l'admin Django
- `is_superuser` : Super administrateur

**Exemple de données** :
```
id | username    | email              | is_active | is_staff
---+-------------+--------------------+-----------+---------
1  | admin       | admin@ggr.cg       | true      | true
2  | gestionnaire| gest@ggr.cg        | true      | true
5  | jean.dupont | jean@email.com     | true      | false
```

### 2. `UserProfile`
**Rôle** : Étend `auth_user` avec des informations métier

**Champs principaux** :
- `user_id` : Lien vers auth_user (OneToOne)
- `full_name` : Nom complet
- `phone` : Numéro de téléphone
- `role` : Rôle métier (CLIENT, GESTIONNAIRE, etc.)
- `address` : Adresse
- `birth_date` : Date de naissance

**Exemple de données** :
```
id | user_id | full_name    | phone        | role
---+---------+--------------+--------------+-------------
1  | 1       | Admin System | 0600000000   | SUPER_ADMIN
2  | 2       | Marie Kouka  | 0611111111   | GESTIONNAIRE
5  | 5       | Jean Dupont  | 0622222222   | CLIENT
```

**Pourquoi** : Django ne connaît pas nos rôles métier, on les ajoute ici

### 3. `DossierCredit` ⭐ Table centrale
**Rôle** : Représente une demande de crédit

**Champs principaux** :
- `reference` : Référence unique (ex: CRED-2025-001)
- `client_id` : Qui a créé le dossier
- `montant` : Montant demandé (Decimal)
- `produit` : Type de crédit (personnel, immobilier, etc.)
- `statut_agent` : Statut interne (NOUVEAU, TRANSMIS_ANALYSTE, etc.)
- `statut_client` : Statut visible par le client (EN_ATTENTE, EN_COURS, etc.)
- `acteur_courant_id` : Qui traite actuellement le dossier
- `date_soumission` : Date de création
- `date_maj` : Dernière modification (auto)

**Exemple de données** :
```
id | reference     | client_id | montant    | statut_agent      | acteur_courant_id
---+---------------+-----------+------------+-------------------+------------------
1  | CRED-2025-001 | 5         | 5000000.00 | NOUVEAU           | 2
2  | CRED-2025-002 | 5         | 3000000.00 | TRANSMIS_ANALYSTE | 3
3  | CRED-2025-003 | 7         | 10000000.00| FONDS_LIBERE      | NULL
```

**Index** : Sur `reference`, `statut_agent`, `client_id` pour les performances

### 4. `PieceJointe`
**Rôle** : Stocke les documents uploadés

**Champs principaux** :
- `dossier_id` : À quel dossier appartient le document
- `fichier` : Chemin du fichier (FileField)
- `type_piece` : Type de document (CNI, FICHE_PAIE, etc.)
- `taille` : Taille en octets
- `upload_by` : Qui a uploadé
- `upload_at` : Quand

**Exemple de données** :
```
id | dossier_id | fichier                        | type_piece    | taille
---+------------+--------------------------------+---------------+--------
1  | 1          | dossiers/CRED-2025-001/cni.pdf | CNI           | 245678
2  | 1          | dossiers/CRED-2025-001/paie.pdf| FICHE_PAIE    | 189234
3  | 2          | dossiers/CRED-2025-002/cni.jpg | CNI           | 156789
```

**Pourquoi** : Un dossier peut avoir plusieurs documents (relation 1:N)

### 5. `CanevasProposition`
**Rôle** : Formulaire détaillé de proposition de crédit (NOKI NOKI)

**Sections** :
1. **En-tête** : Agence, date, exploitant
2. **Renseignements demandeur** : Identité, adresse, emploi
3. **Situation financière** : Salaire, charges, endettement
4. **Objet du crédit** : Montant, durée, taux
5. **Garanties** : Domiciliation, assurance
6. **Calculs** : Capacité de remboursement, taux d'endettement
7. **Documents** : Flags des documents reçus

**Champs importants** :
- `nom_prenom` : Nom complet
- `emploi_occupe` : Poste occupé
- `salaire_net` : Salaire net mensuel
- `charges_mensuelles` : Charges totales
- `taux_endettement` : Calculé automatiquement
- `capacite_remboursement` : Calculée automatiquement

**Exemple** :
```
id | dossier_id | nom_prenom  | salaire_net | taux_endettement
---+------------+-------------+-------------+-----------------
1  | 1          | Jean Dupont | 800000.00   | 35.5
2  | 2          | Paul Martin | 650000.00   | 42.3
```

**Pourquoi** : Relation 1:1 avec DossierCredit (un dossier = un canevas)

### 6. `JournalAction` ⭐ Audit trail
**Rôle** : Traçabilité totale de toutes les actions

**Champs** :
- `dossier_id` : Sur quel dossier
- `acteur_id` : Qui a fait l'action
- `action` : Type d'action (CREATION, VALIDATION, TRANSMISSION, etc.)
- `details` : Détails supplémentaires (JSON)
- `timestamp` : Quand (auto)

**Exemple** :
```
id | dossier_id | acteur_id | action              | timestamp
---+------------+-----------+---------------------+----------
1  | 1          | 5         | CREATION            | 2026-04-01 10:00
2  | 1          | 2         | VERIFICATION_DOCS   | 2026-04-01 14:30
3  | 1          | 2         | TRANSMISSION_ANALYSTE| 2026-04-02 09:15
4  | 1          | 3         | ANALYSE_RISQUE      | 2026-04-02 16:45
```

**Pourquoi** : 
- Traçabilité complète (qui a fait quoi et quand)
- Audit légal
- Résolution de litiges

### 7. `Notification`
**Rôle** : Notifications aux utilisateurs

**Champs** :
- `utilisateur_cible_id` : À qui
- `dossier_id` : Concernant quel dossier
- `type_notification` : Type (NOUVEAU_DOSSIER, COMMENTAIRE, etc.)
- `message` : Texte de la notification
- `lu` : Lue ou non (boolean)
- `created_at` : Date de création

**Exemple** :
```
id | utilisateur_cible_id | message                        | lu    | created_at
---+----------------------+--------------------------------+-------+------------
1  | 2                    | Nouveau dossier CRED-2025-001  | false | 2026-04-01
2  | 5                    | Votre dossier est en cours     | true  | 2026-04-02
3  | 3                    | Dossier à analyser             | false | 2026-04-02
```

**Pourquoi** : Communication en temps réel entre les acteurs

### 8. `Commentaire`
**Rôle** : Commentaires sur les dossiers

**Champs** :
- `dossier_id` : Sur quel dossier
- `auteur_id` : Qui a commenté
- `contenu` : Texte du commentaire
- `created_at` : Date

**Exemple** :
```
id | dossier_id | auteur_id | contenu                          | created_at
---+------------+-----------+----------------------------------+------------
1  | 1          | 2         | Documents vérifiés, tout est OK  | 2026-04-01
2  | 1          | 3         | Risque faible, avis favorable    | 2026-04-02
```

**Pourquoi** : Communication asynchrone, historique des échanges

## 6.3 Relations entre les tables

### Schéma des relations :

```
auth_user (1) ←──────────→ (1) UserProfile
    │
    │ (1:N)
    ├──→ DossierCredit (client)
    │       │
    │       │ (1:N)
    │       ├──→ PieceJointe
    │       │
    │       │ (1:1)
    │       ├──→ CanevasProposition
    │       │
    │       │ (1:N)
    │       ├──→ JournalAction
    │       │
    │       │ (1:N)
    │       ├──→ Notification
    │       │
    │       │ (1:N)
    │       └──→ Commentaire
    │
    │ (1:N)
    ├──→ DossierCredit (acteur_courant)
    │
    │ (1:N)
    ├──→ JournalAction (acteur)
    │
    │ (1:N)
    ├──→ Notification (utilisateur_cible)
    │
    │ (1:N)
    └──→ Commentaire (auteur)
```

### Types de relations :

**1. OneToOne (1:1)** :
- `User` ↔ `UserProfile` : Un utilisateur = un profil
- `DossierCredit` ↔ `CanevasProposition` : Un dossier = un canevas

**2. ForeignKey (1:N)** :
- `User` → `DossierCredit` : Un utilisateur peut créer plusieurs dossiers
- `DossierCredit` → `PieceJointe` : Un dossier peut avoir plusieurs documents
- `DossierCredit` → `JournalAction` : Un dossier a plusieurs actions

**3. ManyToMany (N:N)** :
- Aucune dans ce projet (pas nécessaire)

## 6.4 Exemple de requêtes SQL

### Requête 1 : Récupérer tous les dossiers d'un client avec leurs documents

```sql
SELECT 
    d.reference,
    d.montant,
    d.statut_client,
    COUNT(p.id) as nb_documents
FROM suivi_demande_dossiercredit d
LEFT JOIN suivi_demande_piecejointe p ON p.dossier_id = d.id
WHERE d.client_id = 5
GROUP BY d.id
ORDER BY d.date_soumission DESC;
```

**Équivalent Django ORM** :
```python
dossiers = DossierCredit.objects.filter(client_id=5)\
    .annotate(nb_documents=Count('pieces'))\
    .order_by('-date_soumission')
```

### Requête 2 : Historique complet d'un dossier

```sql
SELECT 
    ja.timestamp,
    u.username as acteur,
    ja.action,
    ja.details
FROM suivi_demande_journalaction ja
JOIN auth_user u ON u.id = ja.acteur_id
WHERE ja.dossier_id = 1
ORDER BY ja.timestamp ASC;
```

**Équivalent Django ORM** :
```python
historique = JournalAction.objects.filter(dossier_id=1)\
    .select_related('acteur')\
    .order_by('timestamp')
```

### Requête 3 : Statistiques globales

```sql
SELECT 
    COUNT(*) as total_dossiers,
    SUM(CASE WHEN statut_agent = 'FONDS_LIBERE' THEN 1 ELSE 0 END) as approuves,
    SUM(CASE WHEN statut_agent = 'REFUSE' THEN 1 ELSE 0 END) as refuses,
    SUM(montant) as montant_total
FROM suivi_demande_dossiercredit;
```

**Équivalent Django ORM** :
```python
from django.db.models import Count, Sum, Q

stats = DossierCredit.objects.aggregate(
    total=Count('id'),
    approuves=Count('id', filter=Q(statut_agent='FONDS_LIBERE')),
    refuses=Count('id', filter=Q(statut_agent='REFUSE')),
    montant_total=Sum('montant')
)
```

---

# 7. LOGIQUE MÉTIER

## 7.1 Règles métier importantes

### 1. Validation des montants

**Règle** : Le montant du crédit doit être entre 100 000 et 50 000 000 FCFA

**Implémentation** :
```python
# Dans constants.py
MONTANT_MINIMUM_CREDIT = 100_000
MONTANT_MAXIMUM_CREDIT = 50_000_000

# Dans models.py
class DossierCredit(models.Model):
    montant = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    def clean(self):
        if self.montant < MONTANT_MINIMUM_CREDIT:
            raise ValidationError(
                f"Le montant minimum est de {MONTANT_MINIMUM_CREDIT} FCFA"
            )
        if self.montant > MONTANT_MAXIMUM_CREDIT:
            raise ValidationError(
                f"Le montant maximum est de {MONTANT_MAXIMUM_CREDIT} FCFA"
            )
```

### 2. Calcul du taux d'endettement

**Règle** : Taux d'endettement = (Charges mensuelles / Salaire net) × 100

**Seuil** : Maximum 40% recommandé

**Implémentation** :
```python
# Dans models.py - CanevasProposition
def calculer_taux_endettement(self):
    if self.salaire_net > 0:
        return (self.charges_mensuelles / self.salaire_net) * 100
    return 0

def save(self, *args, **kwargs):
    # Calcul automatique avant sauvegarde
    self.taux_endettement = self.calculer_taux_endettement()
    super().save(*args, **kwargs)
```

### 3. Capacité de remboursement

**Règle** : Capacité = Salaire net - Charges - Marge de sécurité (20%)

**Implémentation** :
```python
def calculer_capacite_remboursement(self):
    marge_securite = self.salaire_net * 0.20
    capacite = self.salaire_net - self.charges_mensuelles - marge_securite
    return max(capacite, 0)  # Ne peut pas être négatif
```

### 4. Workflow de validation

**Règle** : Un dossier suit un workflow strict

**États possibles** :
1. NOUVEAU → Créé par le client
2. TRANSMIS_ANALYSTE → Envoyé à l'analyste
3. EN_COURS_VALIDATION_GGR → Validation GGR
4. EN_ATTENTE_DECISION_DG → Décision finale
5. APPROUVE_ATTENTE_FONDS → Approuvé, en attente de fonds
6. FONDS_LIBERE → Fonds libérés (fin)
7. REFUSE → Refusé (fin)

**Transitions autorisées** :
```python
TRANSITIONS_AUTORISEES = {
    'NOUVEAU': {
        'roles': ['GESTIONNAIRE'],
        'actions': ['transmettre_analyste']
    },
    'TRANSMIS_ANALYSTE': {
        'roles': ['ANALYSTE'],
        'actions': ['valider_analyse', 'refuser']
    },
    'EN_COURS_VALIDATION_GGR': {
        'roles': ['RESPONSABLE_GGR'],
        'actions': ['approuver', 'refuser']
    },
    # ... etc
}
```

**Implémentation** :
```python
# Dans decorators.py
def transition_allowed(view_func):
    def wrapper(request, pk, action, *args, **kwargs):
        dossier = get_object_or_404(DossierCredit, pk=pk)
        user_role = request.user.profile.role
        
        # Vérifie si la transition est autorisée
        transitions = TRANSITIONS_AUTORISEES.get(dossier.statut_agent, {})
        
        if user_role not in transitions.get('roles', []):
            return HttpResponseForbidden("Action non autorisée")
        
        if action not in transitions.get('actions', []):
            return HttpResponseForbidden("Transition non autorisée")
        
        return view_func(request, pk, action, *args, **kwargs)
    
    return wrapper
```

### 5. Contrôle d'accès (RBAC)

**Règle** : Chaque rôle a des permissions spécifiques

**Matrice de permissions** :

| Action | CLIENT | GESTIONNAIRE | ANALYSTE | RESPONSABLE_GGR | BOE |
|--------|--------|--------------|----------|-----------------|-----|
| Créer dossier | ✅ | ✅ | ❌ | ❌ | ❌ |
| Voir ses dossiers | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voir tous les dossiers | ❌ | ✅ | ✅ | ✅ | ✅ |
| Transmettre à analyste | ❌ | ✅ | ❌ | ❌ | ❌ |
| Analyser risque | ❌ | ❌ | ✅ | ❌ | ❌ |
| Valider dossier | ❌ | ❌ | ❌ | ✅ | ❌ |
| Libérer fonds | ❌ | ❌ | ❌ | ❌ | ✅ |

**Implémentation** :
```python
# Dans decorators.py
def role_required(*allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_role = request.user.profile.role
            
            if user_role not in allowed_roles:
                return HttpResponseForbidden(
                    "Vous n'avez pas les permissions nécessaires"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Utilisation
@role_required("GESTIONNAIRE", "ANALYSTE")
def view_all_dossiers(request):
    # Seuls gestionnaires et analystes peuvent voir tous les dossiers
    ...
```

### 6. Validation des documents

**Règle** : Certains documents sont obligatoires

**Documents obligatoires** :
- CNI (Carte Nationale d'Identité)
- Fiche de paie (3 derniers mois)
- Attestation de domiciliation

**Implémentation** :
```python
def verifier_documents_obligatoires(dossier):
    pieces = dossier.pieces.all()
    types_presents = set(p.type_piece for p in pieces)
    
    documents_obligatoires = ['CNI', 'FICHE_PAIE', 'ATTESTATION_DOMICILIATION']
    
    manquants = [doc for doc in documents_obligatoires if doc not in types_presents]
    
    return len(manquants) == 0, manquants
```

### 7. Génération de référence unique

**Règle** : Format CRED-YYYY-NNN (ex: CRED-2025-001)

**Implémentation** :
```python
def generate_reference():
    from datetime import datetime
    
    year = datetime.now().year
    
    # Compte les dossiers de l'année
    count = DossierCredit.objects.filter(
        date_soumission__year=year
    ).count()
    
    numero = count + 1
    
    return f"CRED-{year}-{numero:03d}"
```

## 7.2 Service Layer Pattern

**Pourquoi** : Séparer la logique métier des vues

**Avantages** :
- Code réutilisable
- Plus facile à tester
- Meilleure organisation

**Exemple** :
```python
# services/dossier_service.py
class DossierService:
    @staticmethod
    def creer_dossier(client, data):
        """Crée un dossier avec toute la logique métier"""
        # 1. Génère la référence
        reference = generate_reference()
        
        # 2. Assigne un gestionnaire
        gestionnaire = get_gestionnaire_disponible()
        
        # 3. Crée le dossier
        dossier = DossierCredit.objects.create(
            client=client,
            reference=reference,
            acteur_courant=gestionnaire,
            **data
        )
        
        # 4. Crée le journal
        JournalAction.objects.create(
            dossier=dossier,
            acteur=client,
            action='CREATION'
        )
        
        # 5. Notifie le gestionnaire
        Notification.objects.create(
            utilisateur_cible=gestionnaire,
            dossier=dossier,
            message=f"Nouveau dossier {reference}"
        )
        
        return dossier
```

---

**Suite dans DOCUMENTATION_SOUTENANCE_PARTIE5.md**
