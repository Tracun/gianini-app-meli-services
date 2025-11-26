import datetime
import requests
import os
from dotenv import load_dotenv
from firebase import firebase

class Services:

    def __init__(self):
        load_dotenv()
        # self.firebaseAuth = firebase.FirebaseAuthentication(os.getenv("FIREBASE_SECRET"), os.getenv("FIREBASE_EMAIL"))
        self.firebaseApp = firebase.FirebaseApplication(
            'https://gianini-manutencao.firebaseio.com/', None)
        self.whatsappURL = "https://api.callmebot.com/whatsapp.php?"
        self.botpressWebhook = "https://webhook.botpress.cloud/e7c8cf69-de6d-48ce-b445-9a9fea2313ca"
        self.gianiniPhone = ""
        self.gianiniToken = ""
        self.devPhone = ""
        self.devToken = ""
        self.franciscoPhone = ""
        self.franciscoToken = ""
        self.version = "v1.0.3"
        self.readConfig()
        
    def setToken(self, data):
        try:            
            return self.firebaseApp.patch('ml_service', data)
        except Exception as e:
            print(e)
        return None
        
    def getToken(self):
        try:
            return self.firebaseApp.get('ml_service', '')
        except Exception as e:
            print(e)
        return None

    def readConfig(self):
        
        self.gianiniPhone = os.getenv('GIANINIPHONE')
        self.gianiniToken = os.getenv('GIANINITOKEN')

        self.devPhone = os.getenv('DEVPHONE')
        self.devToken = os.getenv('DEVTOKEN')

        self.franciscoPhone = os.getenv('FRANCISCOPHONE')
        self.franciscoToken = os.getenv('FRANCISCOTOKEN')

        self.vitorPhone = os.getenv('VITORPHONE')
        self.vitorToken = os.getenv('VITORTOKEN')

        self.amadeuPhone = os.getenv('AMADEUPHONE')
        self.amadeuToken = os.getenv('AMADEUTOKEN')
        
        self.secret = os.getenv('SECRET_WEBHOOK')

    def readNotifiedOrders(self, order):
        with open("./orders.data", 'r') as orders:
            if order in orders.read():
                print("Pedido já notificado ...")
                return True
        print("Novo Pedido, Notificando ...")
        self.writeNotifiedOrders(order)
        return False

    def writeNotifiedOrders(self, order):
        try:
            with open("./orderss.data", '+a') as orders:
                orders.write(f'{orders.read()}\n{order}')
        except e as Exception:
            print(f"Erro ao salvar pedido notificado: {e}")
        return False

    def readNotifiedQuestions(self, question):
        with open("./questions.data", 'r') as questions:
            if question in questions.read():
                print("Pergunta já notificada ...")
                return True
        print("Nova Pergunta, Notificando ...")
        self.writeNotifiedQuestions(question)
        return False

    def writeNotifiedQuestions(self, question):
        try:
            with open("./questions.data", '+a') as questions:
                questions.write(f'{questions.read()}\n{question}')
        except e as Exception:
            print(f"Erro ao salvar questão notificada: {e}")
        return False

    def convertStr2Date(self, strDate):
        date_time_obj = datetime.datetime.strptime(
            strDate, '%Y-%m-%d %H:%M:%S.%f')
        return date_time_obj

    def sendSMS(self):
        print("TO BE DEF")
        
    def sendMessage(self, to, message):
        if to == None or to == 'dev':
            return self.sendWhatsappMessage(message, self.devPhone, self.devToken)
        elif to == "all":
            self.sendWhatsappMessage(message, self.devPhone, self.devToken)
            self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
            return self.sendWhatsappMessage(message, self.franciscoPhone, self.franciscoToken)
        elif to == "gianini":
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        return None

    # Using CallMeBot, a free tool
    def sendWhatsappMessage(self, message, phone, apiKey, isFromErrorMessage=False):
        endpoint = self.whatsappURL + \
            "phone={0}&text={1}&apikey={2}".format(phone, message, apiKey)
        self.log(endpoint)

        res = requests.get(url=endpoint)

        if res.status_code != 200:
            self.sendErrorMessage("Erro ao enviar Whatsapp: " + res.text, isFromErrorMessage=isFromErrorMessage)

        self.log(res.text)
        return res

    # Using webhook from botpress, a free tool
    def callWebhookBotpress(self, data):
        endpoint = self.botpressWebhook
        self.log(endpoint)
        headers = {
            'x-bp-secret':self.secret
        }
        
        print(data)
        res = requests.post(url=endpoint, data=data, headers=headers)

        if res.status_code != 200:
            self.sendErrorMessage("Erro ao enviar Whatsapp: " + res.text)

        self.log(res.text)
        print(f"response webhook = {res.text}")
        return res

    def log(self, message):
        print("{0} - {1}".format(datetime.datetime.now(), message))

    def sendErrorMessage(self, message, isFromErrorMessage=False):
        if not isFromErrorMessage:
            self.sendWhatsappMessage(
                "{0} - {1}".format(datetime.datetime.now(), message), self.devPhone, self.devToken, isFromErrorMessage=True)

