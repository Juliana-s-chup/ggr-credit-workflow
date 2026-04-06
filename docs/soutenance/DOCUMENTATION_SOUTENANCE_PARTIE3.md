# 📚 DOCUMENTATION SOUTENANCE - PARTIE 3
## Fonctionnement Interne (FLOW)

---

# 5. FONCTIONNEMENT INTERNE (FLOW)

## 5.1 Que se passe-t-il quand un utilisateur arrive sur le site ?

### Scénario : Un client visite http://localhost:8000/client/login/

```
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 1 : L'utilisateur tape l'URL                 │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Requête HTTP GET /client/login/
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 2 : Nginx reçoit la requête                  │
│ - Vérifie si c'est un fichier statique             │
│ - Si oui : sert directement le fichier             │
│ - Si non : transmet à Gunicorn                     │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Transmet à Django
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 3 : Django analyse l'URL                     │
│ - Lit core/urls.py                                 │
│ - Trouve : path('client/', include(...))           │
│ - Lit suivi_demande/urls_client.py                 │
│ - Trouve : path('login/', views_portals.login_client_view)│
└────────────────┬────────────────────────────────────┘
                 │
                 │ Appelle la vue
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 4 : La vue login_client_view s'exécute       │
│                                                     │
│ def login_client_view(request):                    │
│     if request.method == 'POST':                   │
│         # Traite la connexion                      │
│     else:                                          │
│         # Affiche le formulaire                    │
│         form = AuthenticationForm()                │
│         return render(request, 'login.html', {...})│
└────────────────┬────────────────────────────────────┘
                 │
                 │ Cherche le template
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 5 : Django charge le template                │
│ - Cherche dans templates/accounts/login.html       │
│ - Remplace {{ form }} par le HTML du formulaire    │
│ - Génère le HTML final                             │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Renvoie le HTML
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 6 : L'utilisateur voit la page de connexion  │
│ - Formulaire avec username et password             │
│ - Bouton "Se connecter"                            │
└─────────────────────────────────────────────────────┘
```

**Temps total** : ~50-100ms

## 5.2 Que se passe-t-il lors d'une connexion ?

### Scénario : Le client entre son username/password et clique sur "Se connecter"

```
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 1 : L'utilisateur soumet le formulaire       │
│ - Username : "jean.dupont"                          │
│ - Password : "********"                             │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Requête HTTP POST /client/login/
                 │ Données : {username: "jean.dupont", password: "..."}
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 2 : Django reçoit la requête POST            │
│ - Appelle login_client_view(request)               │
│ - request.method == 'POST' → Traite la connexion   │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Vérifie les identifiants
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 3 : Authentification                         │
│                                                     │
│ user = authenticate(                                │
│     username=request.POST['username'],             │
│     password=request.POST['password']              │
│ )                                                  │
│                                                     │
│ Django :                                            │
│ 1. Cherche l'utilisateur dans auth_user            │
│ 2. Vérifie le hash du mot de passe (PBKDF2-SHA256)│
│ 3. Si OK : retourne l'objet User                   │
│ 4. Si KO : retourne None                           │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Si authentification réussie
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 4 : Vérification du rôle                     │
│                                                     │
│ if user.profile.role != UserRoles.CLIENT:          │
│     # Pas un client ! Refuser l'accès              │
│     return HttpResponseForbidden("Accès refusé")   │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Si rôle OK
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 5 : Création de la session                   │
│                                                     │
│ auth_login(request, user)                          │
│                                                     │
│ Django :                                            │
│ 1. Génère un session_id unique                     │
│ 2. Stocke la session dans Redis                    │
│ 3. Envoie un cookie au navigateur                  │
│    Cookie: sessionid=abc123...                     │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Redirection
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 6 : Redirection vers le dashboard            │
│ - return redirect('client:dashboard')              │
│ - Le navigateur reçoit un HTTP 302 (redirection)   │
│ - URL de redirection : /client/dashboard/          │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Nouvelle requête GET /client/dashboard/
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 7 : Affichage du dashboard                   │
│ - Django lit le cookie sessionid                   │
│ - Récupère la session depuis Redis                 │
│ - Sait que l'utilisateur est connecté              │
│ - Affiche le dashboard avec ses dossiers           │
└─────────────────────────────────────────────────────┘
```

**Sécurité appliquée** :
1. ✅ Mot de passe hashé (jamais en clair)
2. ✅ Rate limiting (5 tentatives max / 5 min)
3. ✅ Vérification du rôle
4. ✅ Session sécurisée (HttpOnly, Secure en prod)
5. ✅ CSRF protection

## 5.3 Que se passe-t-il lors de la création d'un dossier ?

### Scénario : Un client crée une demande de crédit

```
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 1 : Le client clique sur "Nouvelle demande"  │
│ - URL : /client/demande/                            │
└────────────────┬────────────────────────────────────┘
                 │
                 │ GET /client/demande/
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 2 : Affichage du formulaire (Étape 1/4)      │
│ - Vue : demande_start(request)                     │
│ - Template : demande_step1.html                    │
│ - Formulaire : DemandeStep1Form                    │
│   - Produit de crédit                              │
│   - Montant demandé                                │
│   - Durée de remboursement                         │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Le client remplit et soumet
                 │ POST /client/demande/etape1/
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 3 : Validation des données (Étape 1)         │
│                                                     │
│ form = DemandeStep1Form(request.POST)              │
│ if form.is_valid():                                │
│     # Validation Django                            │
│     # - Montant entre 100k et 50M FCFA             │
│     # - Durée entre 6 et 120 mois                  │
│                                                     │
│     # Sauvegarde temporaire en session             │
│     request.session['step1_data'] = form.cleaned_data│
│                                                     │
│     # Redirection vers étape 2                     │
│     return redirect('demande_step2')               │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Étapes 2, 3, 4 similaires
                 │ (informations personnelles, documents, etc.)
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 4 : Validation finale (Étape 4/4)            │
│                                                     │
│ # Récupère toutes les données des sessions         │
│ step1_data = request.session.get('step1_data')     │
│ step2_data = request.session.get('step2_data')     │
│ step3_data = request.session.get('step3_data')     │
│ step4_data = form.cleaned_data                     │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Création du dossier
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 5 : Création en base de données              │
│                                                     │
│ # 1. Génère une référence unique                   │
│ reference = generate_reference()  # CRED-2025-001  │
│                                                     │
│ # 2. Crée le dossier                               │
│ dossier = DossierCredit.objects.create(            │
│     client=request.user,                           │
│     reference=reference,                           │
│     produit=step1_data['produit'],                 │
│     montant=step1_data['montant'],                 │
│     statut_agent='NOUVEAU',                        │
│     statut_client='EN_ATTENTE',                    │
│     acteur_courant=get_gestionnaire()              │
│ )                                                  │
│                                                     │
│ # 3. Crée le canevas (proposition)                 │
│ CanevasProposition.objects.create(                 │
│     dossier=dossier,                               │
│     nom_prenom=step2_data['nom_prenom'],           │
│     # ... autres champs                            │
│ )                                                  │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Création du journal d'actions
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 6 : Traçabilité                              │
│                                                     │
│ JournalAction.objects.create(                      │
│     dossier=dossier,                               │
│     acteur=request.user,                           │
│     action='CREATION',                             │
│     details='Dossier créé par le client',          │
│     timestamp=timezone.now()                       │
│ )                                                  │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Notification au gestionnaire
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 7 : Notification                             │
│                                                     │
│ Notification.objects.create(                       │
│     utilisateur_cible=dossier.acteur_courant,      │
│     type_notification='NOUVEAU_DOSSIER',           │
│     message=f"Nouveau dossier {reference}",        │
│     dossier=dossier                                │
│ )                                                  │
│                                                     │
│ # Optionnel : Envoi d'email                        │
│ send_mail(                                         │
│     subject=f"Nouveau dossier {reference}",        │
│     message="Un nouveau dossier à traiter",        │
│     recipient_list=[gestionnaire.email]            │
│ )                                                  │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Nettoyage de la session
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 8 : Nettoyage et redirection                 │
│                                                     │
│ # Supprime les données temporaires                 │
│ del request.session['step1_data']                  │
│ del request.session['step2_data']                  │
│ del request.session['step3_data']                  │
│                                                     │
│ # Message de succès                                │
│ messages.success(request, f"Dossier {reference} créé !")│
│                                                     │
│ # Redirection vers le détail du dossier            │
│ return redirect('client:dossier_detail', pk=dossier.pk)│
└────────────────┬────────────────────────────────────┘
                 │
                 │ Le client voit son dossier
                 ▼
┌─────────────────────────────────────────────────────┐
│ ÉTAPE 9 : Affichage du dossier créé                │
│ - Référence : CRED-2025-001                         │
│ - Statut : "En attente de traitement"              │
│ - Montant : 5 000 000 FCFA                         │
│ - Durée : 24 mois                                  │
│ - Bouton : "Ajouter des documents"                 │
└─────────────────────────────────────────────────────┘
```

**Ce qui se passe en base de données** :

```sql
-- Table: suivi_demande_dossiercredit
INSERT INTO suivi_demande_dossiercredit (
    client_id, reference, produit, montant, 
    statut_agent, statut_client, acteur_courant_id, 
    date_soumission
) VALUES (
    5, 'CRED-2025-001', 'Crédit personnel', 5000000.00,
    'NOUVEAU', 'EN_ATTENTE', 2,
    '2026-04-01 23:30:00'
);

-- Table: suivi_demande_journalaction
INSERT INTO suivi_demande_journalaction (
    dossier_id, acteur_id, action, timestamp
) VALUES (
    1, 5, 'CREATION', '2026-04-01 23:30:00'
);

-- Table: suivi_demande_notification
INSERT INTO suivi_demande_notification (
    utilisateur_cible_id, message, dossier_id, lu
) VALUES (
    2, 'Nouveau dossier CRED-2025-001 à traiter', 1, FALSE
);
```

## 5.4 Workflow complet d'un dossier

### Du début à la fin :

```
[1] CLIENT crée le dossier
    ↓
    Statut: NOUVEAU
    Acteur: GESTIONNAIRE
    ↓
[2] GESTIONNAIRE vérifie les documents
    ↓
    Action: "Transmettre à l'analyste"
    ↓
    Statut: TRANSMIS_ANALYSTE
    Acteur: ANALYSTE
    ↓
[3] ANALYSTE évalue le risque
    ↓
    - Calcule la capacité de remboursement
    - Vérifie l'historique de crédit
    - Donne un avis (favorable/défavorable)
    ↓
    Action: "Transmettre au Responsable GGR"
    ↓
    Statut: EN_COURS_VALIDATION_GGR
    Acteur: RESPONSABLE_GGR
    ↓
[4] RESPONSABLE GGR valide
    ↓
    Action: "Transmettre à la DG"
    ↓
    Statut: EN_ATTENTE_DECISION_DG
    Acteur: RESPONSABLE_GGR (décision finale)
    ↓
[5] Décision finale
    ↓
    ┌─────────────┬─────────────┐
    │  APPROUVÉ   │   REFUSÉ    │
    └──────┬──────┴──────┬──────┘
           │             │
           ▼             ▼
    APPROUVE_ATTENTE_FONDS  REFUSE
    Acteur: BOE         (Fin du workflow)
           │
           │
           ▼
    [6] BOE libère les fonds
           │
           ▼
    FONDS_LIBERE
    (Fin du workflow - Succès)
```

**Durée moyenne** : 5-10 jours ouvrés

---

**Suite dans DOCUMENTATION_SOUTENANCE_PARTIE4.md**
