import requests
import base64

from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
import os

#Cargar las variables de entorno
load_dotenv()

watsonx_api_key = os.environ["WATSONX_API_KEY"]
ibm_cloud_url = os.environ["IBM_CLOUD_URL"]
watsonx_project_id = os.environ["WATSONX_PROJECT_ID"]

creds = {"url": ibm_cloud_url, "apikey": watsonx_api_key}

def call_watsonx(
    prompt: str,
    max_tokens: int = 500,
    min_tokens: int = 1,
    model: str = "mistralai/mistral-large",
):
    params = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MIN_NEW_TOKENS: min_tokens,
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.REPETITION_PENALTY: 1,
    }

    modelo = ModelInference(model_id=model, params=params, credentials=creds, project_id=watsonx_project_id)

    watsonx_response = modelo.generate_text(prompt)
    return watsonx_response




def call_watsonx_vision_model(image):

    #Cargar las variables de entorno
    load_dotenv()

    #Leer los bytes de la foto
    image_bytes = image.getvalue()

    #Codificar la imagen en base 64
    image_base64_encoded_bytes = base64.b64encode(image_bytes)

    #Decodificar de base 64 a utf8
    image_utf8_string = image_base64_encoded_bytes.decode('utf-8')

    #Crear un autenticador para llamar a WatsonX
    authenticator = IAMAuthenticator(watsonx_api_key)

    #Generar un bearer token
    bearer_token = authenticator.token_manager.get_token()

    #Definir la url a la que se va a hacer la consulta:
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"


    #Definir el body de la peticion, en esta se incluye el prompt que vamos a hacer y la imagen en los mensajes
    body = {
	"messages": [
        {"role":"user",
         "content":[
            {"type":"text",
              "text":"En la imagen hay apuntes tomados por una persona en un documento digital o en un documento fisico, por favor extrae todo el texto que esta en ese documento de apuntes. Unicamente menciona el texto que esta en los apuntes, no digas nada mas."
            },
            {"type":"image_url",
             "image_url":{"url":f"data:image/png;base64,{image_utf8_string}"}
            }
        ]}
    ],
	"project_id": watsonx_project_id,
	"model_id": "meta-llama/llama-3-2-90b-vision-instruct",
	"decoding_method": "greedy",
	"max_tokens": 3000
    }

    #Headers de la peticion
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ bearer_token
    }

    #Se realiza la peticion al modelo
    response = requests.post(url, headers=headers, json=body)

    #Si la respuesta no es exitosa generar un error
    if response.status_code != 200:
        raise Exception("Non-200 response: "+ str(response.text))
    
    #Si la respuesta fue exitosa entonces leer el json de la respuesta y retornar el texto generado por el modelo
    response_json = response.json()
    return response_json['choices'][0]['message']['content']


    
    
    

    
