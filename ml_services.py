import requests
from services import Services
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
import base64
import hashlib
import pandas as pd

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
            # original_time = datetime.datetime(2020, 2, 19, 12, 0, 0)
            # print("Given Datetime: ", original_time)
            # time_change = datetime.timedelta(days=1, hours=10, minutes=40)
        except Exception as e:
            print(f"Erro ao obter/renovar token: {e}")
        
    def notify(self, topic, resource):
        
        token = self.refreshToken()
                
        headers = {
        'Authorization': f"Bearer {token}"
        }
        try:
            data = requests.get(self.meliEndpoint + resource, headers=headers)
            print(f"data = {data.json()}")
            
            if topic == 'orders' or topic == 'orders_v2':
                
                canceled = data.json()['cancel_detail']
                
                dateClosed = pd.to_datetime(data.json()['date_closed']) #  data de confirmação da ordem. Quando uma ordem muda pela primeira vez de status é definida como: confirmed / paid e descontada do estoque do item.
                lastUpdated = pd.to_datetime(data.json()['last_updated'])
                
                # Diff em minutos
                diffDates = pd.Timedelta(lastUpdated - dateClosed).total_seconds() / 60
                
                notified = Services().readNotifiedOrders(str(data.json()['id']))
                
                # Não notifica caso a diferenca da data closed e lastUpdate maior que 15 minutos
                print(f'Diff {diffDates} minutes')
                if canceled is None and not notified and diffDates < 15:
                    message = f"⚠️ *VENDA NO MERCADO LIVRE:* ⚠️\n*{data.json()['order_items'][0]['quantity']}* - *{data.json()['order_items'][0]['item']['title']}*"
                elif canceled is None and diffDates > 10:
                    print('Pedido já notificado, apenas uma alteração de status. ignorando...')
                    return 'Pedido já notificado, apenas uma alteração de status. ignorando...'
                elif canceled is not None:
                    message = f"❌ *VENDA CANCELADA NO MERCADO LIVRE:* ❌\n*{data.json()['order_items'][0]['quantity']}* - *{data.json()['order_items'][0]['item']['title']}*\n*{canceled}*"
                else:
                    return 'Pedido já notificado, ignorando...'
                print(message)
            elif topic == 'questions':
                if data.json()['status'] == 'UNANSWERED':
                    notified = False
                    notified = Services().readNotifiedQuestions(str(data.json()['id']))
                    
                    if not notified:
                        product = getItem(self, data.json()['id'], headers)
                        message = f"⚠️ *NOVA PERGUNTA NO MERCADO LIVRE - {product}: * ⚠️\n*{data.json()['text']}*"
                    else:
                        return 'Pergunta já notificada, ignorando...'
                else:
                    return 'Pergunta já notificada, ignorando...'
            else:
                print(f"Tópico {topic} não mapeado para notificação")
                return {"message":f"Tópico {topic} não mapeado para notificação"}, 200
            return Services().sendMessage('all', message)
        except Exception as e:
            print(f"Erro ao obter notificação: {e}")


    def getItem(self, id, headers):
        try:
            data = requests.get(self.meliEndpoint + f"/items/{id}", headers=headers)
        
            return data.json()['title']
        except:
            return "Não foi possível obter o produto"