# Solveur d'argumentation abstraite (Dung)

Solveur en Python pour les **systèmes d'argumentation abstraits** de Dung : calcul des extensions **complètes** et **stables**, et décision de l'acceptation **crédule** ou **sceptique** d'un argument. Projet du cours *Représentation des connaissances et raisonnement* (Master 1, Université Paris Cité, 2024–2025).

## Notions

Un système d'argumentation est un graphe orienté `AF = (A, R)` : `A` est un ensemble d'arguments et `(a, b) ∈ R` signifie que `a` attaque `b`. Pour un ensemble `S ⊆ A` :

- **sans conflit** : aucun argument de `S` n'en attaque un autre de `S` ;
- **admissible** : sans conflit, et `S` défend chacun de ses arguments contre tous ses attaquants ;
- **extension complète** : admissible, et contient tous les arguments qu'il défend ;
- **extension stable** : sans conflit, et attaque tous les arguments hors de `S`.

Un argument est **accepté crédulement** s'il appartient à au moins une extension, **sceptiquement** s'il appartient à toutes.

## Format d'entrée (`.apx`)

```
arg(A).
arg(B).
arg(C).
att(A,B).
att(B,A).
att(A,C).
```

## Utilisation

```bash
# Énumérer les extensions (SE) complètes (CO) ou stables (ST)
python my_solver.py -p SE-CO -f tests/data/test_af1.apx
# [[], [D, B], [D, A]]

# Acceptation crédule (DC) ou sceptique (DS) d'un argument
python my_solver.py -p DC-ST -f tests/data/test_af1.apx -a A
# YES
python my_solver.py -p DS-ST -f tests/data/test_af1.apx -a D
# YES
```

| Option | Rôle |
|---|---|
| `-p` | problème : `SE-CO`, `SE-ST`, `DC-CO`, `DS-CO`, `DC-ST`, `DS-ST` |
| `-f` | fichier `.apx` |
| `-a` | argument interrogé (problèmes `DC-*` et `DS-*`) |

Visualiser un graphe (nécessite `networkx` et `matplotlib`) :

```bash
python visualize.py tests/data/test_af1.apx
```

## Tests

```bash
python tests/run_tests.py
```

Le script compare, pour les 5 graphes fournis avec le sujet, les extensions et les arguments acceptés aux résultats attendus : **10/10 cas réussis**. Le fichier attendu `test_af4_co.txt` contenait une coquille : `A,D,C,D,E` pour les arguments acceptés crédulement, alors que l'extension `[B]` figure dans le même fichier. Elle a été corrigée en `A,B,C,D,E`.

## Implémentation

Le solveur énumère les sous-ensembles d'arguments et filtre ceux qui satisfont chaque sémantique. Cette approche exhaustive est exacte et lisible, mais exponentielle : elle convient aux graphes de petite taille comme ceux du projet. Le [rapport](docs/rapport.pdf) détaille les choix.

## Licence

Code distribué sous [licence MIT](LICENSE).

## Auteurs

**Amar Merabti** (M1 DCI) — Université Paris Cité.
