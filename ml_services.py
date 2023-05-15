import requests
from services import Services
import os
from dotenv import load_dotenv, set_key

class ML_services:

    def __init__(self):
        load_dotenv()
        self.meliEndpoint = "https://api.mercadolibre.com"

    def getNewToken():
        set_key(".env", 'TOKEN', '123456789')
        
    def notify(self, topic, resource):
        
        headers = {
        'Authorization': f"Bearer {os.getenv('TOKEN')}"
        }
        data = requests.get(self.meliEndpoint + resource, headers=headers)
        # print(f"data = {data.json()}")
        
        if topic == 'orders':
            
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
        
        