from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json
import time

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')


# - - - - - - - - - - - - - - - - - - - - - -#
# - - - - C R U D  C H A T - - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - -#

@app.route('/chat', methods = ['GET'])
def get_chat():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []
    for message in dbResponse:
        data.append(message)
    return Response(json.dumps(data,  cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/chat', methods = ['POST'])
def post_chat():
    c = json.loads(request.form['values'])
    message = entities.Message(
        content=c['content'],
        user_from_id=c['user_from_id'],
        user_to_id=c['user_to_id']
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    return 'Sent Message'

@app.route('/chat', methods = ['PUT'])
def update_chat():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(message, key, c[key])
    session.add(message)
    session.commit()
    return 'Updated User'


@app.route('/chat', methods = ['DELETE'])
def delete_chat():
    id = request.form['key']
    session = db.getSession(engine)
    chats = session.query(entities.Message).filter(entities.Message.id == id)
    for chat in chats:
        session.delete(chat)
    session.commit()
    return "Chat Deleted"


@app.route('/chat/getConversation/<id1>/and/<id2>', methods = ['GET'])
def get_chats_id(id1, id2):
    def sortVal(val):
        return val["sent_on"]

    db_session = db.getSession(engine)

    info1 = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == id1 and
        entities.Message.user_to_id == id2)

    info2 = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == id2 and
        entities.Message.user_to_id == id1)
    data = []
    try:
        for user in info1:
            data.append(user)
        for user in info2:
            data.append(user)
        #data.sort(key=sortVal)
        return Response(json.dumps(data, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')
    except Exception:
        message = {'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')



# - - - - - - - - - - - - - - - - - - - - - -#
# - - - - C R U D  U S E R S - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - -#

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/users', methods = ['PUT'])
def update_users():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "User Deleted"\

# - - - - - - - - - - - - - - - - - - - - - -#
# - - - - - - - - C H A T  - - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - -#





@app.route('/authenticate', methods = ["POST"])
def authenticate():
    time.sleep(1)
    message = json.loads(request.data)
    username = message['username']
    password = message['password']
    #2. look in database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User
            ).filter(entities.User.username == username
            ).filter(entities.User.password == password
            ).one()
        message = {'message': 'Authorized'}
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))
