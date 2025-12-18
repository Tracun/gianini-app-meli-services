from flask_restful import Api
from flask import Flask, render_template, request
import threading
import os
from ml_services import ML_services
from app_services import App_Services
from dotenv import load_dotenv

app = Flask(__name__)
api = Api(app) 

@app.route('/')
@app.route('/home')
def index():
    return render_template(
        'index.html',
        title='Home Page'
    )

@app.route('/login', methods=["GET", "POST"])
def login():
    return "login"

@app.route('/verifDespesasProxVenc', methods=["GET", "POST"])
@app.route('/verifDespesasProxVenc/<string:to>', methods=["GET", "POST"])
def checkeExpenses(to=None):
    app_services = App_Services()

    res = app_services.checkExpensesCloseToDueDate(to)
    print(f"checkExpensesCloseToDueDate res = {res}")
    
    if res != None and res.status_code == 200:
        return {'message': 'Em breve receberá um whatsapp com as informações requeridas', 'response': {}, 'status code':'{0}'.format(res.status_code)}
    elif res != None and res.status_code > 200:
        return {'message': 'Ocorreu um erro', 'response': res.text, 'status code':'{0}'.format(res.status_code)}
    elif res == None:
        return {'message': 'Endpoint inválido, era esperado um dos abaixos: /all ou /dev ou /gianini', 'response': {}, 'status code':'{0}'.format('400')}

    return {'message':'Internal error', 'status code':500}

@app.route('/verifPreventivasProxVenc')
@app.route('/verifPreventivasProxVenc/<string:to>')
def checkePreventivasSchedule(to=None):
    app_services = App_Services()

    res = app_services.checkPreventivaScheduleCloseToDueDate(to)
    print(f"checkPreventivaScheduleCloseToDueDate res = {res}")
    
    if res != None and res.status_code == 200:
        return {'message': 'Em breve receberá um whatsapp com as informações requeridas', 'response': {}, 'status code':'{0}'.format(res.status_code)}
    elif res != None and res.status_code > 200:
        return {'message': 'Ocorreu um erro', 'response': res.text, 'status code':'{0}'.format(res.status_code)}
    elif res == None:
        return {'message': 'Endpoint inválido, era esperado um dos abaixos: /all ou /dev ou /gianini', 'response': {}, 'status code':'{0}'.format('400')}

    return {'message':'Internal error', 'status code':500}

@app.route('/answer', methods=["POST"])
def answer():
    load_dotenv()
    print(f"Respondendo questão, corpo da solicitacao = {request.json}")
    
    # Check if header contain phone number, and verify if phone number is in env, to accept req
    if("Phone-Number" not in request.headers):
        return {"error":"missing header parameter", "status":400}, 200
    else:
        if(os.getenv("GIANINIPHONE") != request.headers['Phone-Number'] and os.getenv("DEVPHONE") != request.headers['Phone-Number']):
            return {"error":"Unauthorized", "message":"whatsapp number not allowed", "status":401}, 200
    
    return ML_services().answerQuestion(request.json['question_id'], request.json['text']), 200

@app.route('/unanswered_questions', methods=["GET"])
def unanswered_questions():
    
    print(f"Obtendo questoes {request.args.get('status')} ...")
    
    return ML_services().getUnansweredQuestions(request.args.get('status'))

@app.route('/notifications', methods=["POST"])
def notifications():
    thread = threading.Thread(target=notifying_running_task, kwargs={
                    'body': request.json})
    thread.start()
    
    return {"message":"received"}, 200

@app.route('/test_notifications', methods=["POST"])
def notifications():
    thread = threading.Thread(target=notifying_running_task, kwargs={
                    'body': request.json, 'isTest':True})
    thread.start()
    
    return {"message":"received"}, 200
    
def notifying_running_task(**kwargs):
        json = kwargs.get('body', {})
        isTest = kwargs.get('isTest', False)
        
        print("Starting notifying task")
        
        print("##################################################################\n")
        print(f"notifying_running_task isTest = {isTest} & JSON = {json}")
        print("##################################################################\n")
        
        ML_services().notify(json['topic'], json['resource'], isTest=isTest)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()