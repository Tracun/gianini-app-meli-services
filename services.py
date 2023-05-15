import datetime
import requests
import os
from dotenv import load_dotenv

class Services:

    def __init__(self):
        self.whatsappURL = "https://api.callmebot.com/whatsapp.php?"
        self.gianiniPhone = ""
        self.gianiniToken = ""
        self.devPhone = ""
        self.devToken = ""
        self.version = "v1.0.2"
        load_dotenv()
        self.readConfig()

    def readConfig(self):
        
        self.gianiniPhone = os.getenv('GIANINIPHONE')
        self.gianiniToken = os.getenv('GIANINITOKEN')

        self.devPhone = os.getenv('DEVPHONE')
        self.devToken = os.getenv('DEVTOKEN')

        self.vitorPhone = os.getenv('VITORPHONE')
        self.vitorToken = os.getenv('VITORTOKEN')

        self.amadeuPhone = os.getenv('AMADEUPHONE')
        self.amadeuToken = os.getenv('AMADEUTOKEN')

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
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        elif to == "gianini":
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        return None

    # Using CallMeBot, a free tool
    def sendWhatsappMessage(self, message, phone, apiKey):
        endpoint = self.whatsappURL + \
            "phone={0}&text={1}&apikey={2}".format(phone, message, apiKey)
        self.log(endpoint)

        res = requests.get(url=endpoint)

        if res.status_code != 200:
            self.sendErrorMessage("Erro ao enviar Whatsapp: " + res.text)

        self.log(res.text)
        return res

    def log(self, message):
        print("{0} - {1}".format(datetime.datetime.now(), message))

    def sendErrorMessage(self, message):
        self.sendWhatsappMessage(
            "{0} - {1}".format(datetime.datetime.now(), message), self.devPhone, self.devToken)
