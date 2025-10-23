# API de Traduction Serverless

Une API de traduction serverless construite avec AWS Lambda, API Gateway, DynamoDB et l'API DeepL. Ce projet utilise AWS SAM (Serverless Application Model) pour le déploiement et la gestion de l'infrastructure.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Déploiement](#déploiement)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [API Reference](#api-reference)

## ✨ Fonctionnalités

- **Traduction multilingue** via l'API DeepL
- **Mise en cache** des traductions dans DynamoDB pour optimiser les performances et réduire les coûts
- **Architecture serverless** scalable et économique
- **Détection automatique** de la langue source
- **Déploiement automatisé** avec AWS SAM

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│ Lambda Function │
└─────────────┘      └──────────────┘      └─────────────────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                                    │                │                │
                                    ▼                ▼                ▼
                             ┌──────────┐    ┌──────────┐    ┌──────────┐
                             │ DynamoDB │    │ DeepL API│    │CloudWatch│
                             │  Cache   │    │          │    │   Logs   │
                             └──────────┘    └──────────┘    └──────────┘
```

## 📦 Prérequis

- [AWS CLI](https://aws.amazon.com/cli/) installé et configuré
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installé
- [Python 3.11](https://www.python.org/downloads/) ou supérieur
- Un compte [DeepL API](https://www.deepl.com/pro-api) (clé API gratuite ou payante)
- Un compte AWS avec les permissions appropriées

## 🚀 Installation

1. Cloner le repository :
```bash
git clone <votre-repo-url>
cd traduction-api
```

2. Installer les dépendances Python :
```bash
pip install -r requirement.txt
```

## ⚙️ Configuration

### 1. Configuration de la clé API DeepL

Remplacez la clé API DeepL dans les fichiers suivants :

- `template.yaml` (ligne 18)
- `lambda_function.py` (ligne 26)

```python
key_deepl = "VOTRE_CLE_API_DEEPL"
```

### 2. Configuration AWS SAM

Modifiez le fichier `samconfig.toml` selon vos besoins :

```toml
[defaullt.deploy.parameters]
stack_name = "traduction-api"
region = "eu-north-1"  # Changez selon votre région préférée
```

### 3. Table DynamoDB

La table DynamoDB `Translations` doit être créée avec :
- **Nom de la table** : `Translations`
- **Clé de partition** : `cache_key` (String)

## 🚢 Déploiement

### 1. Build du projet

```bash
sam build
```

### 2. Déploiement sur AWS

```bash
sam deploy --guided
```

Pour les déploiements suivants :
```bash
sam deploy
```

### 3. Récupérer l'URL de l'API

Après le déploiement, l'URL de votre API sera affichée dans les outputs :
```
TraductionApiUrl: https://xxxxxxxxxx.execute-api.eu-north-1.amazonaws.com/Prod/translate
```

## 💻 Utilisation

### Exemple de requête avec curl

```bash
curl -X POST https://votre-api-url/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "FR"
  }'
```

### Exemple de réponse

```json
{
  "source_lang": "EN",
  "original_text": "Hello, how are you?",
  "lang": "FR",
  "translated_text": "Bonjour, comment allez-vous ?"
}
```

### Langues supportées

L'API supporte toutes les langues disponibles dans DeepL. Exemples de codes :
- `EN` - Anglais
- `FR` - Français
- `DE` - Allemand
- `ES` - Espagnol
- `IT` - Italien
- `JA` - Japonais
- `ZH` - Chinois

Voir la [documentation DeepL](https://www.deepl.com/docs-api/translate-text/) pour la liste complète.

## 📁 Structure du projet

```
traduction-api/
├── lambda_function.py      # Code de la fonction Lambda
├── template.yaml           # Template SAM pour l'infrastructure
├── requirement.txt         # Dépendances Python
├── samconfig.toml         # Configuration SAM
├── README.md              # Documentation
└── .aws-sam/              # Dossier de build SAM (généré)
```

## 📖 API Reference

### POST /translate

Traduit un texte dans la langue cible spécifiée.

**Paramètres de la requête :**

| Paramètre    | Type   | Requis | Description                        |
|--------------|--------|--------|------------------------------------|
| text         | string | Oui    | Le texte à traduire               |
| target_lang  | string | Oui    | Code de la langue cible (ex: FR)  |

**Réponses :**

- **200 OK** : Traduction réussie
- **400 Bad Request** : Paramètres manquants
- **500 Internal Server Error** : Erreur lors de la traduction

## 🔧 Développement local

Pour tester localement :

```bash
sam local start-api
```

L'API sera disponible sur `http://localhost:3000`

## 📊 Monitoring

Les logs de la fonction Lambda sont disponibles dans CloudWatch Logs. Vous pouvez les consulter via :

```bash
sam logs -n TraductionFunction --tail
```

## 💰 Coûts

Ce projet utilise :
- **AWS Lambda** : Facturation à l'utilisation (1M de requêtes gratuites/mois)
- **API Gateway** : Facturation par requête
- **DynamoDB** : Mode à la demande (25 Go gratuits/mois)
- **DeepL API** : Plan gratuit (500 000 caractères/mois) ou payant

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## 📝 License

Ce projet est sous licence MIT.

## ⚠️ Sécurité

**Important** : Ne commitez jamais vos clés API dans le code source. Utilisez des variables d'environnement ou AWS Secrets Manager pour la production.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.