# WeasyPrint server

## But

Convertir des documents html en pdf.

## Développement
### installation

On utilise [uv](https://github.com/astral-sh/uv) pour gérer python et ces dépendances.

On copy les variables d'env

```bash
cp env.example .env
```
---
Pour macosx il faut ajouter ces 2 étapes :

1- installer weasyprint avec homebrew 
```bash
brew install weasyprint
```

2- éxécuter cette ligne de commande
```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
```

### lancement de l'application

```bash
uv run flask run --debug

# or any process manager reading Procfile.dev
overmind start
```

### tests

```bash
uv run python -m unittest
```

### linters

```bash
uv run ruff format --check && uv run ruff check
```

## Packaging

voir package_scripts/main.sh

## installation par dépôt debian
En root (ou en préfixant les commandes par `sudo`), exécuter les commandes suivantes :
``` bash
# ajout du dépôt de Démarche Numerique
echo 'deb [signed-by=/usr/share/keyrings/packages.demarche.numerique.gouv.fr.gpg] http://packages.demarche.numerique.gouv.fr/jammy /' > /etc/apt/sources.list.d/packages_demarche_numerique.list
curl -s https://demarche.numerique.gouv.fr/packages.demarche.numerique.gouv.fr.gpg -o /usr/share/keyrings/packages.demarche.numerique.gouv.fr.gpg

# installation
apt-get update && apt-get install weasyprint-server
```
