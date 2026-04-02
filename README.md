# data_corrections.py

Script Python de nettoyage automatique de fichiers CSV.

## Prérequis

Python 3 doit être installé. Aucune librairie externe requise.

## Lancer le script

Placez vos fichiers CSV dans le même dossier que `data_corrections.py`, puis exécutez :

```bash
python3 data_corrections.py
```

## Fichiers générés

Pour chaque fichier `nom.csv` traité, deux fichiers sont créés :

| Fichier | Contenu |
|---|---|
| `nom_cleaned.csv` | Lignes valides après corrections |
| `nom_rejected.csv` | Lignes rejetées car non corrigeables |

## Corrections appliquées

### Détection du type attendu par colonne

Pour chaque colonne, le script analyse toutes les valeurs et retient le **type le plus fréquent** comme type attendu. Les types reconnus sont :

| Type | Exemples |
|---|---|
| `int` | `42`, `-8` |
| `float` | `22.4`, `3,14` |
| `bool` | `yes`, `no`, `true`, `false`, `oui`, `non` |
| `datetime` | `2026-03-10 08:00`, `10/03/2026 08:00` |
| `string` | `active`, `Laura` |

### Conversions automatiques

Les corrections suivantes sont appliquées sans rejeter la ligne :

| Cas | Avant | Après |
|---|---|---|
| Entier dans une colonne float | `160` | `160.00` |
| Booléen non normalisé | `true`, `oui` | `yes` |
| Booléen non normalisé | `false`, `non` | `no` |
| Date avec `/` | `10/03/2026 08:00` | `2026-03-10 08:00` |

### Lignes rejetées

Une ligne est rejetée si une de ses valeurs :
- est **vide**
- est d'un **type incompatible** avec le type attendu de la colonne (ex: texte dans une colonne numérique)
- est une **date sans heure** dans une colonne datetime (ex: `2026-03-10`)
# Test1_Verdon
