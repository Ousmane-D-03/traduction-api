import json
import requests
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Translations')

        

def lambda_handler(event, context):
    # Extraire les données de l'événement
    text = event.get('text')
    target_lang = event.get('target_lang')

    # Vérifier que les données sont là
    if not text or not target_lang:
        return {
            'statusCode': 400,
            'body': 'Erreur : text et target_lang sont requis.'
        }
    
    # Vérifier si la traduction est déjà en cache
    cache_key = f"{text}-{target_lang}"
    reponse = table.get_item(Key={'cache_key': cache_key})
    if 'Item' in reponse:
        return {
            'statusCode': 200,
            'body': json.dumps(reponse['Item']['translation_data'], ensure_ascii=False)
        }

    url = "https://api-free.deepl.com/v2/translate"  
    key_deepl = "2ecfb542-6389-4204-8fb2-48df6101a2cb:fx"
    data = {
        'text': text,
        'target_lang': target_lang,
        'auth_key': key_deepl
    }
    # Envoyer la requête à l'API DeepL
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Vérifier si la requête a réussi
        deepl_reponse = response.json()
        translation_data = {
            'source_lang': deepl_reponse['translations'][0]['detected_source_language'],
            'original_text': text,
            'lang': target_lang,
            'translated_text': deepl_reponse['translations'][0]['text']
        }
        # Stocker la traduction dans DynamoDB
        table.put_item(Item={
            'cache_key': cache_key,
            'translation_data': translation_data
        })
        
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': f'Erreur lors de la requête à l\'API DeepL : {str(e)}'
        }
    # Pour l'instant, on ne fait qu'afficher les données reçues
    return {
        'statusCode': 200,
        'body': json.dumps(translation_data, ensure_ascii=False)
    }
