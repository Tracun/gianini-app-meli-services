import requests
from services import Services
import sys, os
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
import base64
import hashlib
import pandas as pd
import json
from db import DB

class ML_services:

    def __init__(self):
        load_dotenv()
        self.meliEndpoint = "https://api.mercadolibre.com"

    def encrypt(self, data):
        key = os.getenv("CLIENT_SECRET")
        key = hashlib.sha256(key.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(key).decode('utf-8')
        
        fernet = Fernet(key)
        return fernet.encrypt(data.encode('utf-8')).decode("utf-8")

    def decrypt(self, data):
        key = os.getenv("CLIENT_SECRET")
        key = hashlib.sha256(key.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(key).decode('utf-8')
        
        fernet = Fernet(key)        
        return fernet.decrypt(data.encode('utf-8')).decode("utf-8")

    def treatData(self, data):
        return data.replace('"', '')
    
    def refreshToken(self):
        load_dotenv()
        try:
            print("######## Verificando validade do token ...")
            datetime.now() - timedelta(days=1)
            tokenExp = os.getenv("EXPIRES")
            data = Services().getToken()
            
            tokenExp = data['expires']
                        
            if datetime.strptime(tokenExp, '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
                # Expirou, obter novo token
                print("Token expirou, renovando ...")
                
                refreshToken = self.decrypt(data['refresh_token'])
                url = f"{self.meliEndpoint}/oauth/token"

                payload=f'grant_type=refresh_token&client_id={os.getenv("CLIENT_ID")}&client_secret={os.getenv("CLIENT_SECRET")}&refresh_token={refreshToken}'
                headers = {
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                # print(response.text)
                
                set_key(".env", 'TOKEN', response.json()['access_token'])
                
                set_key(".env", 'REFRESH_TOKEN', response.json()['refresh_token'])
                
                expires = str(datetime.now() + timedelta(seconds=float(response.json()['expires_in'])))
                set_key(".env", 'EXPIRES', expires)
                
                Services().setToken({
                'token':self.encrypt(response.json()['access_token']),
                'refresh_token':self.encrypt(response.json()['refresh_token']),
                'expires':expires
                })
                
                load_dotenv()
                print("Token renovado ...")
                
                return response.json()['access_token']
            
            print("Token na validade ...")
            return self.decrypt(data['token'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Erro ao obter/renovar token: {e} - {exc_tb.tb_lineno}")
        
    def notify(self, topic, resource):
        
        token = self.refreshToken()
                
        headers = {
        'Authorization': f"Bearer {token}"
        }
        try:
            data = requests.get(self.meliEndpoint + resource, headers=headers)
            id = str(data.json()['id'])
            
            print(f"data = {data.json()}")
            print(f"ID = {id}")
            
            if topic == 'orders' or topic == 'orders_v2':
                
                canceled = data.json()['cancel_detail']
                
                dateClosed = pd.to_datetime(data.json()['date_closed']) #  data de confirmação da ordem. Quando uma ordem muda pela primeira vez de status é definida como: confirmed / paid e descontada do estoque do item.
                lastUpdated = pd.to_datetime(data.json()['last_updated'])
                
                # Diff em minutos
                diffDates = pd.Timedelta(lastUpdated - dateClosed).total_seconds() / 60
                
                notified = DB().isNotified(id)
                print(f"Order already notified? = {notified}")
                
                if(not notified):
                    DB().insert_notified(id)
                
                # Não notifica caso a diferenca da data closed e lastUpdate maior que 15 minutos
                print(f'Diff {diffDates} minutes')
                if canceled is None and not notified: # and diffDates < 15:
                    message = f"⚠️ *VENDA NO MERCADO LIVRE:* ⚠️\n*{data.json()['order_items'][0]['quantity']}* - *{data.json()['order_items'][0]['item']['title']}*"
                    
                    # Send request to botpress webhook
                    data = json.dumps({
                        "topic":"new_order",
                        "id": id,
                        "quantity":data.json()['order_items'][0]['quantity'],
                        "title":data.json()['order_items'][0]['item']['title']
                    })
                    
                    # Services().callWebhookBotpress(data)
                elif canceled is None and diffDates > 10:
                    print('Pedido já notificado, apenas uma alteração de status. ignorando...')
                    return 'Pedido já notificado, apenas uma alteração de status. ignorando...'
                elif canceled is not None:
                    message = f"❌ *VENDA CANCELADA NO MERCADO LIVRE:* ❌\n*{data.json()['order_items'][0]['quantity']}* - *{data.json()['order_items'][0]['item']['title']}*\n*{canceled}*"
                    
                    # Send request to botpress webhook
                    data = json.dumps({
                        "topic":"order_canceled",
                        "id": id,
                        "quantity":data.json()['order_items'][0]['quantity'],
                        "title":data.json()['order_items'][0]['item']['title']
                    })
                    
                    # Services().callWebhookBotpress(data)
                else:
                    return 'Pedido já notificado, ignorando...'
                print(message)
            elif topic == 'questions':
                if data.json()['status'] == 'UNANSWERED':
                    notified = False
                    notified = DB().isNotified(id)
                    print(f"Question already notified? = {notified}")
                    
                    if(not notified):
                        DB().insert_notified(id)
                    
                    if not notified:
                        product = self.getItem(data.json()['item_id'], headers)
                        message = f"⚠️ *{id} - NOVA PERGUNTA NO MERCADO LIVRE - {product}:* ⚠️\n*{self.treatData(data.json()['text'])}*"
                        
                        # Send request to botpress webhook
                        data = json.dumps({
                            "topic":"question",
                            "id": id,
                            "title":product,
                            "question":data.json()['text']
                        })
                        
                        # Services().callWebhookBotpress(data)
                    else:
                        return 'Pergunta já notificada, ignorando...'
                else:
                    return 'Pergunta já notificada, ignorando...'
            elif topic == 'messages':
                if data.json()['status'] == 'UNANSWERED':
                    notified = False
                    notified = DB().isNotified(id)
                    print(f"Messages already notified? = {notified}")
                    
                    if(not notified):
                        DB().insert_notified(id)
                    
                    if not notified:
                        message = f"⚠️ *NOVA MENSAGEM DENTRO EM UMA VENDA:* ⚠️\n*{self.treatData(data.json()['messages']['text'])}*"
                    else:
                        return 'Pergunta já notificada, ignorando...'
                else:
                    return 'Pergunta já notificada, ignorando...'
            else:
                print(f"Tópico {topic} não mapeado para notificação")
                return {"message":f"Tópico {topic} não mapeado para notificação"}, 200
            return Services().sendMessage(message)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Erro ao obter notificação: {e} - {exc_tb.tb_lineno}")

    def getItem(self, id, headers):
        try:
            data = requests.get(self.meliEndpoint + f"/items/{id}", headers=headers)
        
            return data.json()['title']
        except:
            return "Não foi possível obter o produto"

    def answerQuestion(self, questionId, answer):
        try:
            
            token = self.refreshToken()
                
            headers = {
            'Authorization': f"Bearer {token}"
            }
            
            payload = json.dumps({
                "question_id": questionId,
                "text": answer
            })
                    
            data = requests.post(self.meliEndpoint + "/answers", headers=headers, data=payload)
            
            return data.json()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return {"message":"Não foi possível responder a pergunta", "error":e}, 200

    def getUnansweredQuestions(self, status):
        try:
            
            if status == '':
                status = 'UNANSWERED'
            
            token = self.refreshToken()
                
            headers = {
            'Authorization': f"Bearer {token}"
            }
            
            response = requests.get(self.meliEndpoint + "/my/received_questions/search", headers=headers)
            
            if response.status_code >=200 and response.status_code < 300:
                questionsList = response.json()['questions']
                unansweredQuestionsList = []
                
                for question in questionsList:
                    if question['status'] == status.upper():
                        unansweredQuestionsList.append(question)
                    
                return {"unansweredQuestionsList": unansweredQuestionsList}, 200
            return {"unansweredQuestionsList":[]}, 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"ERRO: {e} - {exc_tb.tb_lineno}")
            return {"message":"Não foi possível responder a pergunta", "unansweredQuestionsList":[], "error":e}, 500