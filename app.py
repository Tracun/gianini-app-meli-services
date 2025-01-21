from flask_restful import Api
from flask import Flask, render_template, request
import threading
from ml_services import ML_services

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

@app.route('/answer', methods=["POST"])
def answer():
    print(f"Respondendo questão, corpo da solicitacao = {request.json}")
    
    return ML_services().answerQuestion(request.json['question_id'], request.json['text'])
    return {"message":"Respondendo ..."}, 200

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
    
def notifying_running_task(**kwargs):
        json = kwargs.get('body', {})
        print("Starting notifying task")
        
        print("##################################################################\n")
        print(f"JSON = {json}")
        print("##################################################################\n")
        
        ML_services().notify(json['topic'], json['resource'])

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()