# 🔄 DIAGRAMME BPMN - WORKFLOW CRÉDIT

## Workflow Complet du Traitement d'un Dossier

```
[CLIENT] Soumettre demande
    ↓
[NOUVEAU] Dossier créé
    ↓
[GESTIONNAIRE] Vérifier complétude
    ↓ (complet)
[TRANSMIS_ANALYSTE]
    ↓
[ANALYSTE] Analyser risque
    ↓
[EN_COURS_ANALYSE]
    ↓
[ANALYSTE] Proposer décision
    ↓
[EN_COURS_VALIDATION_GGR]
    ↓
[RESPONSABLE GGR] Décision finale
    ↓
    ├─→ [APPROUVE_ATTENTE_FONDS]
    │       ↓
    │   [BOE] Libérer fonds
    │       ↓
    │   [FONDS_LIBERE] ✅ FIN
    │
    └─→ [REFUSE] ❌ FIN
```

## Statuts et Transitions

| Statut | Acteur | Actions Possibles |
|--------|--------|-------------------|
| NOUVEAU | Gestionnaire | Transmettre à analyste, Retourner au client |
| TRANSMIS_ANALYSTE | Analyste | Commencer analyse |
| EN_COURS_ANALYSE | Analyste | Proposer approbation/refus |
| EN_COURS_VALIDATION_GGR | Responsable GGR | Approuver, Refuser |
| APPROUVE_ATTENTE_FONDS | BOE | Libérer fonds |
| FONDS_LIBERE | - | Archiver |
| REFUSE | - | Archiver |
