import datetime
import json
import requests
import sys
import urllib.parse
import configparser

class Services:

    def __init__(self):
        self.whatsappURL = "https://api.callmebot.com/whatsapp.php?"
        self.gianiniPhone = ""
        self.gianiniToken = ""
        self.devPhone = ""
        self.devToken = ""
        self.version = "v1.0.2"
        self.readConfig()

    def readConfig(self):
        parser = configparser.ConfigParser()
        parser.read_file(open(r'config.txt'))
        self.gianiniPhone = parser.get('config', 'gianiniPhone')
        self.gianiniToken = parser.get('config', 'gianiniToken')

        self.devPhone = parser.get('config', 'devPhone')
        self.devToken = parser.get('config', 'devToken')

        self.vitorPhone = parser.get('config', 'vitorPhone')
        self.vitorToken = parser.get('config', 'vitorToken')

        self.amadeuPhone = parser.get('config', 'amadeuPhone')
        self.amadeuToken = parser.get('config', 'amadeuToken')

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
