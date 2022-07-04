# Ludi Gestion

Outil de gestion associative pour la LUDI de Toulouse.

# Prérequis

- [Python 3.10 ou supérieur](https://www.python.org/downloads/)
- [Make](https://www.gnu.org/software/make/)

# Installation

Installer poetry:

```bash
curl -sS https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
```

Installer ludigestion:

```bash
make setup
```

# Utilisation
## Configuration

Créer un .env.prod:

(Exemple de format de clé secrète: `24den3&v&0f_=ugjw(^si#6!qv45wyr%5oldb9ci^&*jrqt%e4`)
```bash
echo "LUDIGESTION_SECRET_KEY=Une chaine de caractères aléatoire" > .env.prod
```

## Execution

```bash
make run
```

# Developpement
## Tester

```bash
make test
```
