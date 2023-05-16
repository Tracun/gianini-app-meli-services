import requests
from services import Services
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key

class ML_services:

    def __init__(self):
        load_dotenv()
        self.meliEndpoint = "https://api.mercadolibre.com"

    def refreshToken(self):
        load_dotenv()
        try:
            print("######## Verificando validade do token ...")
            datetime.now() - timedelta(days=1)
            tokenExp = os.getenv("EXPIRES")
            
            # print(datetime.strptime(tokenExp, '%Y-%m-%d %H:%M:%S.%f') < datetime.now())
            
            if datetime.strptime(tokenExp, '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
                # Expirou, obter novo token
                print("Token expirou, renovando ...")
                url = f"{self.meliEndpoint}/oauth/token"

                payload=f'grant_type=refresh_token&client_id={os.getenv("CLIENT_ID")}&client_secret={os.getenv("CLIENT_SECRET")}&refresh_token={os.getenv("REFRESH_TOKEN")}'
                headers = {
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                print(response.text)
                
                set_key(".env", 'TOKEN', response.json()['access_token'])
                os.system(f"heroku config:set TOKEN = {response.json()['access_token']}")
                
                set_key(".env", 'REFRESH_TOKEN', response.json()['refresh_token'])
                os.system(f"heroku config:set REFRESH_TOKEN = {response.json()['refresh_token']}")
                
                expires = str(datetime.now() + timedelta(seconds=float(response.json()['expires_in'])))
                set_key(".env", 'EXPIRES', expires)
                os.system(f"heroku config:set EXPIRES = {expires}")
                
                load_dotenv()
                print("Token renovado ...")
            # original_time = datetime.datetime(2020, 2, 19, 12, 0, 0)
            # print("Given Datetime: ", original_time)
            # time_change = datetime.timedelta(days=1, hours=10, minutes=40)
        except Exception as e:
            print(f"Erro ao obter/renovar token: {e}")
        
    def notify(self, topic, resource):
        
        self.refreshToken()
        
        headers = {
        'Authorization': f"Bearer {os.getenv('TOKEN')}"
        }
        try:
            data = requests.get(self.meliEndpoint + resource, headers=headers)
            print(f"data = {data.json()}")
            
            if topic == 'orders' or topic == 'orders_v2':
                
                canceled = data.json()['cancel_detail']
                
                if canceled is None:
                    message = f"⚠️ *VENDA NO MERCADO LIVRE:* ⚠️\n*{data.json()['order_items'][0]['quantity']}* - *{data.json()['order_items'][0]['item']['title']}*"
                else:
                    message = f"❌ *VENDA CANCELADA NO MERCADO LIVRE:* ❌\n*{data.json()['order_items'][0]['quantity']}* - *{data.json()['order_items'][0]['item']['title']}*\n*{canceled}*"
                print(message)
            elif topic == 'questions':
                message = f"⚠️ *NOVA PERGUNTA NO MERCADO LIVRE:* ⚠️\n*{data.json()['text']}*"
            
            else:
                print(f"Tópico {topic} não mapeado para notificação")
                return {"message":f"Tópico {topic} não mapeado para notificação"}, 200
            return Services().sendMessage('dev', message)
        except Exception as e:
            print(f"Erro ao obter notificação: {e}")
        