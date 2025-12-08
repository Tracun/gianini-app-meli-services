import datetime
import requests
import os, sys
from dotenv import load_dotenv
from firebase import firebase
import schedule, time
import urllib.parse

class App_Services:

    def __init__(self):
        load_dotenv()
        # self.firebaseAuth = firebase.FirebaseAuthentication(os.getenv("FIREBASE_SECRET"), os.getenv("FIREBASE_EMAIL"))
        self.firebaseApp = firebase.FirebaseApplication(
            'https://gianini-manutencao.firebaseio.com/', None)
        self.whatsappURL = "https://api.callmebot.com/whatsapp.php?"
        self.myWhatsAppApi = "https://competent-nonentertaining-coral.ngrok-free.app"
        self.gianiniPhone = ""
        self.gianiniToken = ""
        self.devPhone = ""
        self.devToken = ""
        self.franciscoPhone = ""
        self.franciscoToken = ""
        self.version = "v1.1.0"
        self.readConfig()

    def readConfig(self):
        
        self.gianiniPhone = os.getenv('GIANINIPHONE')
        self.gianiniToken = os.getenv('GIANINITOKEN')

        self.devPhone = os.getenv('DEVPHONE')
        self.devToken = os.getenv('DEVTOKEN')

        self.franciscoPhone = os.getenv('FRANCISCOPHONE')
        self.franciscoToken = os.getenv('FRANCISCOTOKEN')

        self.amadeuPhone = os.getenv('AMADEUPHONE')
        self.amadeuToken = os.getenv('AMADEUTOKEN')
        
        self.secret = os.getenv('SECRET_WEBHOOK')
        self.secret = os.getenv('MY_API_TOKEN')
        
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


    def getAllSchedules(self):
        try:
            schedules = self.firebaseApp.get('Schedules/', '')
            return schedules
        except Exception as e:
            self.sendErrorMessage("Erro getAllSchedules: " + str(e))
        return None

    def getAllExpenses(self):
        try:
            expenses = self.firebaseApp.get('Expenses/', '')
            return expenses
        except Exception as e:
            self.sendErrorMessage("Erro getAllExpenses: " + str(e))
        return None

    def diffBetweenDates(self, date):
        date = self.convertStr2Date(str(date))
        nowDate = datetime.datetime(datetime.datetime.now(
        ).year, datetime.datetime.now().month, datetime.datetime.now().day, 0, 0, 0)
        return (date - nowDate).days

    def checkPreventivaScheduleCloseToDueDate(self, to):

        scheduleList = self.getAllSchedules()
        count = 0
        message = "*##### Verifique as PREVENTIVAS abaixo - {0}/{1}/{2} #####*\n\n".format(
            datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

        for key, schedules in scheduleList.items():
            diff = self.diffBetweenDates(schedules["date"])
            status = schedules["status"]

            if status == "Agendado":
                if diff < 0:
                    dueDate = self.convertStr2Date(schedules["date"])
                    count += 1
                    message += "{0} - *_(❌ATRASADO)_* - Preventiva no hospital *{1}* no dia *{2}/{3}/{4}* - *OBS: {5}*\n\n".format(
                        count, schedules["hospitalName"], dueDate.day, dueDate.month, dueDate.year, schedules["obs"])
                elif diff == 0:
                    dueDate = self.convertStr2Date(schedules["date"])
                    count += 1
                    message += "{0} - *_(⚠️HOJE)_* - Preventiva no hospital *{1}* no dia *{2}/{3}/{4}* - *OBS: {5}*\n\n".format(
                        count, schedules["hospitalName"], dueDate.day, dueDate.month, dueDate.year, schedules["obs"])
                elif diff == 1:
                    dueDate = self.convertStr2Date(schedules["date"])
                    count += 1
                    message += "{0} - *_(😉AMANHÃ)_* - Preventiva no hospital *{1}* no dia *{2}/{3}/{4}* - *OBS: {5}*\n\n".format(
                        count, schedules["hospitalName"], dueDate.day, dueDate.month, dueDate.year, schedules["obs"])

        if count == 0:
            message += "Nenhuma preventiva pendente para o dia de hoje - {0}/{1}/{2}".format(
                datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        message = urllib.parse.quote(message)

        return self.sendMessagePreventiva(to, message)

    def sendMessagePreventiva(self, to, message):
        if to == None or to == 'dev':
            return self.sendWhatsappMessage(message, self.devPhone, self.devToken)
        elif to == "all":
            self.sendWhatsappMessage(message, self.devPhone, self.devToken)
            # self.sendWhatsappMessage(message, self.vitorPhone, self.vitorToken)
            # self.sendWhatsappMessage(message, self.amadeuPhone, self.amadeuToken)
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        elif to == "gianini":
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        
        return None

    def checkExpensesCloseToDueDate(self, to):

        expensesList = self.getAllExpenses()
        count = 0
        message = "*##### As DESPESAS abaixo que estão com o status de 'Pendente', vencidas e/ou próximas do vencimento - {0}/{1}/{2} #####*\n\n".format(
            datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

        for key, expense in expensesList.items():
            diff = self.diffBetweenDates(expense["dueDate"])
            status = expense["status"]
            
            if "isDeleted" in expense: 
                isDeleted = expense["isDeleted"]
            else:
                isDeleted = False

            if status != "Pago" and (isDeleted == None or isDeleted == False):
                if diff < 0:
                    dueDate = self.convertStr2Date(expense["dueDate"])
                    count += 1
                    message += "{0} - *_(❌VENCIDO)_* - *{1}({2})* com o valor de *R$ {3}* e vencimento em *{4}/{5}/{6}* - *{7}*\n\n".format(
                        count, expense["description"], expense["obs"], expense["value"], dueDate.day, dueDate.month, dueDate.year, expense["type"])
                    
                    # Envia de 5 em 5 mensagens, para evitar corte
                    if count % 5 == 0:
                        message = urllib.parse.quote(message)
                        self.sendMessageExpenses(to, message)
                        message = ""

                elif diff == 0:
                    dueDate = self.convertStr2Date(expense["dueDate"])
                    count += 1
                    message += "{0} -  *_(⚠️HOJE)_* - *{1}({2})* com o valor de *R$ {3}* e vencimento em *{4}/{5}/{6}* - *{7}*\n\n".format(
                        count, expense["description"], expense["obs"], expense["value"], dueDate.day, dueDate.month, dueDate.year, expense["type"])
                    
                    # Envia de 5 em 5 mensagens, para evitar corte
                    if count % 5 == 0:
                        message = urllib.parse.quote(message)
                        self.sendMessageExpenses(to, message)
                        message = ""

                elif diff < 2:
                    dueDate = self.convertStr2Date(expense["dueDate"])
                    count += 1
                    message += "{0} - *{1}({2})* com o valor de *R$ {3}* e vencimento em *{4}/{5}/{6}* - *{7}*\n\n".format(
                        count, expense["description"], expense["obs"], expense["value"], dueDate.day, dueDate.month, dueDate.year, expense["type"])
                    
                    # Envia de 5 em 5 mensagens, para evitar corte
                    if count % 5 == 0:
                        message = urllib.parse.quote(message)
                        self.sendMessageExpenses(to, message)
                        message = ""

        if count == 0:
            message += "Nenhum despesa pendente para o dia de hoje - {0}/{1}/{2}".format(
                datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        message = urllib.parse.quote(message)

        print("SENDING WHATSAPP")
        return self.sendMessageExpenses(to, message)

    def sendMessageExpenses(self, to, message):
        if to == None or to == 'dev':
            return self.sendWhatsappMessage(message, self.devPhone, self.devToken)
        elif to == "all":
            self.sendWhatsappMessage(message, self.devPhone, self.devToken)
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        elif to == "gianini":
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        return None

    def convertStr2Date(self, strDate):
        date_time_obj = datetime.datetime.strptime(
            strDate, '%Y-%m-%d %H:%M:%S.%f')
        return date_time_obj

    def sendSMS(self):
        print("TO BE DEF")

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

    # Using WWEBJS from my server
    def sendWhatsappMessageMyApi(self, message, phone):
        endpoint = f'{self.myWhatsAppApi}/chat-message'
        self.log(endpoint)
        payload = f'number={self.devPhone}&message={message}'
        headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Bearer {self.myApiToken}'
                    }

        res = requests.post(endpoint, headers=headers, data=payload)

        if res.status_code != 200:
            self.sendErrorMessage("Erro ao enviar Whatsapp via MyApi_wwebjs: " + res.text)

        self.log(res.text)
        return res

    def log(self, message):
        print("{0} - {1}".format(datetime.datetime.now(), message))

    def sendErrorMessage(self, message):
        print(f"SENDING WHATSAPP ERROR {message}")
        self.sendWhatsappMessage(
            "{0} - {1}".format(datetime.datetime.now(), message), self.devPhone, self.devToken)


def main():
    app_services = App_Services()
    try:
        app_services.log("Executando serviço {0} ...".format(app_services.version))

        res = app_services.checkExpensesCloseToDueDate(to="dev")
        # res = services.checkPreventivaScheduleCloseToDueDate(to="dev")

        app_services.log("Execução finalizada ...")

    except Exception as e:
        # services.sendErrorMessage("Erro main: " + str(e))
        app_services.log("Erro main: " + str(e))

if __name__ == "__main__":
    try:
        print("Serviço iniciado ...")
        schedule.every(10).seconds.do(main)
        main()
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        print("Erro ao executar serviço: " + str(e))
        sys.exit()