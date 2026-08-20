# RRA Docs — site public

Ce dépôt public reçoit exclusivement le site statique généré depuis le dépôt
privé `oreafone-labs/rra-docs` après validation et approbation humaine.

## Organisation

- `site/` : artefact public généré ;
- `site/build-metadata.json` : révision exacte du dépôt source privé ;
- `.github/workflows/pages.yml` : déploiement GitHub Pages ;
- `tools/validate_public.py` : dernier contrôle autonome avant déploiement.

Le contenu de `site/` ne doit pas être modifié manuellement. Une correction se
fait dans le dépôt source privé, est rendue avec Quarto, validée, puis publiée à
nouveau.

Chaque projection arrive sur une branche `publication/*` et dans une Pull
Request en brouillon. La CI valide le site candidat ; seule la fusion humaine
de cette PR dans `main` déclenche GitHub Pages.

## Autorité

Ce dépôt est une projection de lecture. Il n'adopte ni méthode, ni décision
métier, ni résultat de recherche. Les dépôts sources et autorités locales
restent compétents dans leurs périmètres respectifs.

Le site ne contient aucun lien cliquable vers les dépôts privés Oreafone. Une
source privée peut être identifiée par son nom, sa version et sa révision avec
la mention « accès restreint ».
