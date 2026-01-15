# 🏗️ SCHÉMA ARCHITECTURE SYSTÈME

## Architecture 4 Couches

```
┌─────────────────────────────────────────────────────────────────┐
│  COUCHE 1 : PRÉSENTATION (Frontend)                            │
├─────────────────────────────────────────────────────────────────┤
│  Portail Client  │  Portail Pro  │  Dashboard Admin            │
│  HTML5, CSS3, JavaScript, Bootstrap 5, Charts.js               │
└─────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  COUCHE 2 : LOGIQUE MÉTIER (Backend)                           │
├─────────────────────────────────────────────────────────────────┤
│  Django Views (Contrôleurs)                                     │
│  ┌──────────────┬──────────────┬──────────────┐               │
│  │ Workflow     │ Analytics    │ Reports      │               │
│  │ Views        │ Views        │ Views        │               │
│  └──────────────┴──────────────┴──────────────┘               │
│                                                                 │
│  Services (Logique Métier)                                      │
│  ┌──────────────────┬──────────────────┬──────────────────┐   │
│  │ AnalyticsService │ MLPredictionSvc  │ ExportService    │   │
│  │ • Calcul KPIs    │ • Random Forest  │ • Excel (pandas) │   │
│  │ • Statistiques   │ • 85% précision  │ • PDF (ReportLab)│   │
│  └──────────────────┴──────────────────┴──────────────────┘   │
│  Django 5.2, Python 3.12, scikit-learn, pandas                 │
└─────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  COUCHE 3 : DONNÉES (Modèles)                                  │
├─────────────────────────────────────────────────────────────────┤
│  Django ORM (Models)                                            │
│  ┌────────────────┬────────────────┬────────────────┐          │
│  │ DossierCredit  │ JournalAction  │ Statistiques   │          │
│  │ Utilisateur    │ Document       │ Notification   │          │
│  └────────────────┴────────────────┴────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  COUCHE 4 : PERSISTANCE (Base de Données)                      │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL 16                                                  │
│  • Transactions ACID  • Index optimisés  • Backup auto          │
│  Performance : <500ms pour 95% des requêtes                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MODULES TRANSVERSAUX                                           │
├─────────────────────────────────────────────────────────────────┤
│  🔒 SÉCURITÉ        📊 MONITORING      🧪 TESTS                │
│  • CSRF, XSS, SQL   • Logs Django      • 66 tests auto         │
│  • RBAC (5 rôles)   • Sentry           • 85% couverture        │
│  • 12 tests OWASP   • Métriques        • CI/CD GitHub          │
└─────────────────────────────────────────────────────────────────┘
```

## Flux de Données

```
CLIENT → FRONTEND → BACKEND → DATABASE
  │         │          │          │
  │ Soumet  │  POST    │ INSERT   │
  │────────>│─────────>│─────────>│
  │         │          │ Scoring  │
  │         │<─────────│  ML      │
  │ Confirm │          │          │
  │<────────│          │          │
```
