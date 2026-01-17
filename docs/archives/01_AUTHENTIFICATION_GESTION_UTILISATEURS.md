# DOCUMENTATION TECHNIQUE DÉTAILLÉE
## Module 1 : Authentification et Gestion des Utilisateurs

---

## FONCTIONNALITÉ 1.1 : INSCRIPTION (SIGNUP)

### **Technologies utilisées**
- **Backend** : Django 4.x (Python 3.x)
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Sécurité** : Django Authentication System, PBKDF2 password hashing

### **Fichiers impliqués**
- `suivi_demande/views.py` → fonction `signup()`
- `suivi_demande/forms.py` → classe `SignupForm`
- `suivi_demande/models.py` → modèles `User`, `UserProfile`, `UserRoles`
- `templates/registration/signup.html` → interface utilisateur
- `suivi_demande/urls.py` → route `accounts/signup/`

### **Modèles de données**

#### **User (Django built-in)**
```python
# Modèle Django par défaut (django.contrib.auth.models.User)
- id: AutoField (PK)
- username: CharField(150) UNIQUE
- password: CharField(128) # Hashé avec PBKDF2
- email: EmailField(254)
- first_name: CharField(150)
- last_name: CharField(150)
- is_active: BooleanField (default=False) # Inactif jusqu'à validation admin
- is_staff: BooleanField (default=False)
- is_superuser: BooleanField (default=False)
- date_joined: DateTimeField (auto_now_add=True)
- last_login: DateTimeField (nullable)
```

#### **UserProfile (Modèle personnalisé)**
```python
# suivi_demande/models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, related_name="profile")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    role = models.CharField(max_length=32, choices=UserRoles.choices, default=CLIENT)
```

#### **UserRoles (Énumération)**
```python
class UserRoles(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire"
    ANALYSTE = "ANALYSTE", "Analyste crédit"
    RESPONSABLE_GGR = "RESPONSABLE_GGR", "Responsable GGR"
    BOE = "BOE", "Back Office Engagement"
    SUPER_ADMIN = "SUPER_ADMIN", "Super administrateur"
```

### **Algorithme et logique**

#### **Étape 1 : Affichage du formulaire (GET)**
```python
def signup(request):
    if request.method == 'GET':
        form = SignupForm()
        return render(request, 'registration/signup.html', {'form': form})
```

#### **Étape 2 : Validation et création (POST)**
```python
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # 1. Créer l'utilisateur (inactif par défaut)
            user = form.save(commit=False)
            user.is_active = False  # Nécessite validation admin
            user.save()
            
            # 2. Créer le profil associé
            UserProfile.objects.create(
                user=user,
                full_name=form.cleaned_data.get('full_name'),
                phone=form.cleaned_data.get('phone'),
                address=form.cleaned_data.get('address'),
                role=UserRoles.CLIENT  # Rôle par défaut
            )
            
            # 3. Message de confirmation
            messages.success(request, "Compte créé. En attente de validation.")
            
            # 4. Redirection vers page d'attente
            return redirect('suivi:pending_approval')
```

### **Validation des données**

#### **SignupForm (forms.py)**
```python
class SignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=30, required=True)
    address = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email
```

### **Paramètres de configuration**

#### **settings.py**
```python
# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Algorithme de hashage
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Par défaut
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

### **Interface utilisateur**

#### **Éléments UI (signup.html)**
- Formulaire avec 6 champs : username, email, password1, password2, full_name, phone, address
- Validation HTML5 (required, type="email", minlength)
- Affichage des erreurs par champ
- Bouton "Créer un compte"
- Lien vers la page de connexion
- Design responsive (Bootstrap 5)
- Variables CSS personnalisées pour la charte graphique

### **Flux de données**
```
1. Utilisateur → Formulaire HTML
2. Submit → POST /accounts/signup/
3. Django → Validation SignupForm
4. Si valide → Création User (is_active=False)
5. Création UserProfile (role=CLIENT)
6. Redirection → /accounts/pending/
7. Admin → Activation manuelle via admin_users
```

### **Sécurité**
- **CSRF Token** : protection contre les attaques CSRF
- **Password hashing** : PBKDF2 avec 260 000 itérations
- **Validation email** : unicité garantie
- **Compte inactif** : validation admin obligatoire
- **XSS protection** : auto-escaping des templates Django

---

## FONCTIONNALITÉ 1.2 : CONNEXION (LOGIN)

### **Technologies utilisées**
- **Backend** : Django Authentication System
- **Frontend** : HTML5, CSS3, JavaScript (show/hide password)
- **Session** : Django sessions (cookies sécurisés)

### **Fichiers impliqués**
- `suivi_demande/views.py` → utilise `django.contrib.auth.views.LoginView`
- `templates/registration/login.html` → interface personnalisée
- `suivi_demande/urls.py` → route `accounts/login/`

### **Modèles de données**
- **User** : username, password (hashé)
- **Session** : django_session table (session_key, session_data, expire_date)

### **Algorithme et logique**

```python
# Django LoginView (built-in)
1. Affichage du formulaire (GET)
2. Soumission (POST)
3. Authentification : authenticate(username, password)
4. Vérification du hash : check_password()
5. Si valide et is_active=True :
   - Création de session
   - login(request, user)
   - Redirection vers LOGIN_REDIRECT_URL
6. Si invalide : message d'erreur
```

### **Configuration**

#### **settings.py**
```python
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semaines (en secondes)
SESSION_COOKIE_HTTPONLY = True  # Protection XSS
SESSION_COOKIE_SECURE = True  # HTTPS uniquement (production)
SESSION_COOKIE_SAMESITE = 'Lax'  # Protection CSRF
```

### **Améliorations UX (login.html)**

#### **JavaScript : Show/Hide Password**
```javascript
const toggleBtn = document.getElementById('togglePwd');
const passwordField = document.getElementById('id_password');

toggleBtn.addEventListener('click', function() {
    const isText = passwordField.getAttribute('type') === 'text';
    passwordField.setAttribute('type', isText ? 'password' : 'text');
    this.querySelector('i').classList.toggle('fa-eye');
    this.querySelector('i').classList.toggle('fa-eye-slash');
});
```

#### **JavaScript : Loading State**
```javascript
const form = document.getElementById('loginForm');
const submitBtn = document.getElementById('loginSubmit');

form.addEventListener('submit', function() {
    submitBtn.classList.add('btn-loading');
    submitBtn.setAttribute('disabled', 'disabled');
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connexion...';
});
```

#### **Attributs HTML5**
```html
<input type="text" id="id_username" 
       placeholder="ex: jdupont" 
       required 
       autocomplete="username" 
       autofocus>

<input type="password" id="id_password" 
       placeholder="Votre mot de passe" 
       required 
       autocomplete="current-password">
```

### **Flux de données**
```
1. GET /accounts/login/ → Affichage formulaire
2. POST /accounts/login/ → {username, password}
3. authenticate(username, password)
4. check_password(raw_password, hashed_password)
5. Si OK → login(request, user) → Création session
6. Redirection → /dashboard/
7. Dashboard → Détection du rôle → Template spécifique
```

### **Sécurité**
- **Brute force protection** : possibilité d'ajouter django-axes (limitation tentatives)
- **Session fixation** : nouvelle session à chaque login
- **HTTPS** : cookies sécurisés en production
- **Password timing attack** : constant-time comparison

---

## FONCTIONNALITÉ 1.3 : GESTION DES RÔLES (RBAC)

### **Technologies utilisées**
- **Pattern** : Role-Based Access Control (RBAC)
- **Backend** : Django permissions + décorateurs personnalisés
- **Modèle** : UserProfile.role (énumération)

### **Fichiers impliqués**
- `suivi_demande/models.py` → UserRoles, UserProfile
- `suivi_demande/decorators.py` → @role_required, @transition_allowed
- `suivi_demande/permissions.py` → logique de permissions
- `suivi_demande/views.py` → contrôles d'accès dans les vues

### **Énumération des rôles**

```python
class UserRoles(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    GESTIONNAIRE = "GESTIONNAIRE", "Gestionnaire"
    ANALYSTE = "ANALYSTE", "Analyste crédit"
    RESPONSABLE_GGR = "RESPONSABLE_GGR", "Responsable GGR"
    BOE = "BOE", "Back Office Engagement"
    SUPER_ADMIN = "SUPER_ADMIN", "Super administrateur"
```

### **Décorateur personnalisé : @role_required**

```python
# suivi_demande/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(*allowed_roles):
    """Décorateur pour restreindre l'accès par rôle."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            role = getattr(profile, 'role', None)
            
            if role not in allowed_roles:
                messages.error(request, "Accès refusé. Rôle insuffisant.")
                return redirect('suivi:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Utilisation
@login_required
@role_required(UserRoles.SUPER_ADMIN, UserRoles.RESPONSABLE_GGR)
def admin_users(request):
    # Vue réservée aux admins et responsables GGR
    pass
```

### **Matrice de permissions**

| Fonctionnalité | CLIENT | GESTIONNAIRE | ANALYSTE | RESP_GGR | BOE | SUPER_ADMIN |
|----------------|--------|--------------|----------|----------|-----|-------------|
| Soumettre demande | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Créer dossier pour client | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Transmettre à analyste | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Analyser dossier | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Retour gestionnaire | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Transmettre GGR | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Approuver/Refuser | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Libérer fonds | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Archiver dossier | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| Gérer utilisateurs | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Consulter rapports | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |

### **Auto-élévation Superuser → SUPER_ADMIN**

```python
# suivi_demande/views.py (dashboard)
profile = getattr(request.user, "profile", None)
role = getattr(profile, "role", UserRoles.CLIENT)

# Si superuser Django, forcer le rôle SUPER_ADMIN
if getattr(request.user, 'is_superuser', False) and role != UserRoles.SUPER_ADMIN:
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'phone': '',
            'address': '',
            'role': UserRoles.SUPER_ADMIN,
        }
    )
    if profile.role != UserRoles.SUPER_ADMIN:
        profile.role = UserRoles.SUPER_ADMIN
        profile.save(update_fields=["role"])
    role = profile.role
```

### **Dashboards par rôle**

```python
# suivi_demande/views.py
def dashboard(request):
    role = request.user.profile.role
    
    if role == UserRoles.CLIENT:
        return render(request, "suivi_demande/dashboard_client.html", context)
    elif role == UserRoles.GESTIONNAIRE:
        return render(request, "suivi_demande/dashboard_gestionnaire.html", context)
    elif role == UserRoles.ANALYSTE:
        return render(request, "suivi_demande/dashboard_analyste.html", context)
    elif role == UserRoles.RESPONSABLE_GGR:
        return render(request, "suivi_demande/dashboard_responsable_ggr_pro.html", context)
    elif role == UserRoles.BOE:
        return render(request, "suivi_demande/dashboard_boe.html", context)
    elif role == UserRoles.SUPER_ADMIN:
        return render(request, "suivi_demande/dashboard_super_admin.html", context)
```

---

## FONCTIONNALITÉ 1.4 : ACTIVATION DES COMPTES (ADMIN)

### **Technologies utilisées**
- **Backend** : Django ORM, formulaires Django
- **Frontend** : HTML, Bootstrap 5, JavaScript

### **Fichiers impliqués**
- `suivi_demande/views.py` → `admin_users()`, `admin_activate_user()`
- `templates/suivi_demande/admin_users.html`
- `suivi_demande/urls.py` → routes admin

### **Algorithme**

```python
@login_required
@role_required(UserRoles.SUPER_ADMIN)
def admin_activate_user(request, user_id):
    """Active un compte utilisateur en attente."""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        # 1. Activer le compte
        user.is_active = True
        user.save(update_fields=['is_active'])
        
        # 2. Optionnel : Envoyer email de confirmation
        if user.email:
            send_mail(
                subject="Compte activé - Crédit du Congo",
                message=f"Bonjour {user.username}, votre compte a été activé.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        
        # 3. Message de succès
        messages.success(request, f"Utilisateur {user.username} activé.")
        
        # 4. Redirection
        return redirect('suivi:admin_users')
```

### **Flux de données**
```
1. Inscription → User créé (is_active=False)
2. Admin → Accès /admin/users/
3. Liste des utilisateurs inactifs
4. Clic "Activer" → POST /admin/users/<id>/activate/
5. is_active = True
6. Email de confirmation (optionnel)
7. Utilisateur peut se connecter
```

---

## FONCTIONNALITÉ 1.5 : MODIFICATION DES RÔLES (ADMIN)

### **Fichiers impliqués**
- `suivi_demande/views.py` → `admin_change_role()`
- `templates/suivi_demande/admin_users.html`

### **Algorithme**

```python
@login_required
@role_required(UserRoles.SUPER_ADMIN)
def admin_change_role(request, user_id):
    """Modifie le rôle d'un utilisateur."""
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        
        # Validation
        if new_role not in dict(UserRoles.choices):
            messages.error(request, "Rôle invalide.")
            return redirect('suivi:admin_users')
        
        # Mise à jour
        profile.role = new_role
        profile.save(update_fields=['role'])
        
        messages.success(request, f"Rôle de {user.username} changé en {new_role}.")
        return redirect('suivi:admin_users')
```

### **Interface (admin_users.html)**
```html
<select name="role" class="form-select">
    <option value="CLIENT" {% if user.profile.role == 'CLIENT' %}selected{% endif %}>Client</option>
    <option value="GESTIONNAIRE" {% if user.profile.role == 'GESTIONNAIRE' %}selected{% endif %}>Gestionnaire</option>
    <option value="ANALYSTE" {% if user.profile.role == 'ANALYSTE' %}selected{% endif %}>Analyste</option>
    <option value="RESPONSABLE_GGR" {% if user.profile.role == 'RESPONSABLE_GGR' %}selected{% endif %}>Responsable GGR</option>
    <option value="BOE" {% if user.profile.role == 'BOE' %}selected{% endif %}>BOE</option>
    <option value="SUPER_ADMIN" {% if user.profile.role == 'SUPER_ADMIN' %}selected{% endif %}>Super Admin</option>
</select>
```

---

## RÉSUMÉ MODULE 1

### **Tables de base de données**
1. **auth_user** (Django built-in)
2. **suivi_demande_userprofile** (personnalisé)
3. **django_session** (sessions)

### **Endpoints**
- `GET/POST /accounts/signup/` → Inscription
- `GET/POST /accounts/login/` → Connexion
- `POST /accounts/logout/` → Déconnexion
- `GET /accounts/pending/` → Page d'attente validation
- `GET /admin/users/` → Liste utilisateurs (admin)
- `POST /admin/users/<id>/activate/` → Activation compte
- `POST /admin/users/<id>/change-role/` → Modification rôle

### **Paramètres chiffrés**
- **Password hashing** : PBKDF2, 260 000 itérations
- **Session cookie age** : 1 209 600 secondes (14 jours)
- **Min password length** : 8 caractères
- **Username max length** : 150 caractères
- **Email max length** : 254 caractères

### **Interactions entre modules**
- **Authentification** ↔ **Dashboard** : redirection selon rôle
- **UserProfile** ↔ **Workflow** : permissions de transition
- **UserProfile** ↔ **Notifications** : ciblage par rôle
- **SUPER_ADMIN** ↔ **Tous modules** : accès complet
