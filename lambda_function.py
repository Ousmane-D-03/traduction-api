import json
import os
import boto3
import requests
from botocore.exceptions import ClientError

# Initialisation des clients AWS
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')
table = dynamodb.Table('Translations')

# Cache pour la clé API (évite de récupérer à chaque invocation)
deepl_api_key_cache = None


def get_deepl_api_key():
    """Récupère la clé API DeepL depuis Secrets Manager avec mise en cache"""
    global deepl_api_key_cache
    
    if deepl_api_key_cache:
        return deepl_api_key_cache
    
    secret_name = os.environ.get('DEEPL_SECRET_NAME', 'DeepLAPIKey')
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        deepl_api_key_cache = response['SecretString']
        return deepl_api_key_cache
    except ClientError as e:
        print(f"Erreur lors de la récupération du secret: {e}")
        raise


def validate_input(text, target_lang):
    """Valide les paramètres d'entrée"""
    if not text or not isinstance(text, str):
        return False, "Le paramètre 'text' est requis et doit être une chaîne de caractères"
    
    if not target_lang or not isinstance(target_lang, str):
        return False, "Le paramètre 'target_lang' est requis et doit être une chaîne de caractères"
    
    if len(text) > 5000:
        return False, "Le texte ne doit pas dépasser 5000 caractères"
    
    # Langues supportées par DeepL
    valid_langs = ['BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 
                   'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 
                   'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TR', 'UK', 'ZH']
    
    if target_lang.upper() not in valid_langs:
        return False, f"Langue cible non supportée. Langues valides: {', '.join(valid_langs)}"
    
    return True, None


def get_from_cache(cache_key):
    """Récupère une traduction du cache DynamoDB"""
    try:
        response = table.get_item(Key={'cache_key': cache_key})
        if 'Item' in response:
            print(f"Cache hit pour: {cache_key}")
            return response['Item']['translation_data']
        return None
    except ClientError as e:
        print(f"Erreur lors de la lecture du cache: {e}")
        return None


def save_to_cache(cache_key, translation_data):
    """Sauvegarde une traduction dans le cache DynamoDB"""
    try:
        table.put_item(Item={
            'cache_key': cache_key,
            'translation_data': translation_data
        })
        print(f"Traduction mise en cache: {cache_key}")
    except ClientError as e:
        print(f"Erreur lors de la sauvegarde en cache: {e}")


def translate_with_deepl(text, target_lang, api_key):
    """Effectue la traduction via l'API DeepL"""
    url = "https://api-free.deepl.com/v2/translate"
    
    data = {
        'text': text,
        'target_lang': target_lang.upper(),
        'auth_key': api_key
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        deepl_response = response.json()
        
        return {
            'source_lang': deepl_response['translations'][0]['detected_source_language'],
            'original_text': text,
            'target_lang': target_lang.upper(),
            'translated_text': deepl_response['translations'][0]['text']
        }
    
    except requests.exceptions.Timeout:
        raise Exception("Timeout lors de l'appel à l'API DeepL")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur lors de l'appel à l'API DeepL: {str(e)}")


def lambda_handler(event, context):
    """Point d'entrée de la fonction Lambda"""
    
    print(f"Event reçu: {json.dumps(event)}")
    
    # Gestion des requêtes API Gateway
    try:
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        text = body.get('text')
        target_lang = body.get('target_lang')
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Corps de requête JSON invalide'
            }, ensure_ascii=False)
        }
    
    # Validation des inputs
    is_valid, error_message = validate_input(text, target_lang)
    if not is_valid:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': error_message
            }, ensure_ascii=False)
        }
    
    # Vérification du cache
    cache_key = f"{text}-{target_lang.upper()}"
    cached_translation = get_from_cache(cache_key)
    
    if cached_translation:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'data': cached_translation,
                'cached': True
            }, ensure_ascii=False)
        }
    
    # Traduction via DeepL
    try:
        api_key = get_deepl_api_key()
        translation_data = translate_with_deepl(text, target_lang, api_key)
        
        # Sauvegarde en cache
        save_to_cache(cache_key, translation_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'data': translation_data,
                'cached': False
            }, ensure_ascii=False)
        }
    
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Erreur interne du serveur',
                'message': str(e)
            }, ensure_ascii=False)
        }