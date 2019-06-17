from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
from operator import itemgetter, attrgetter
import json
import time
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import or_

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    if 'logged_user' in session:
        return render_template('chat.html')
    else:
        return render_template('login2.html')


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


# - - - - - - - - - - - - - - - - - - - - - -#
#  - - D E F A U L T - C R U D  C H A T - -  #
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

# - - - - - - - - - - - - - - - - - - - - - -#
# - - - - - - C R U D  C H A T - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - -#

@app.route('/chat/getConversation/<id1>/and/<id2>', methods = ['GET'])
def get_chats_id(id1, id2):
    db_session = db.getSession(engine)
    """
    info1 = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == id1).filter(
        entities.Message.user_to_id == id2)

    info2 = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == id2).filter(
        entities.Message.user_to_id == id1)
    data = []
    try:
        for user in info1:
            data.append(user)
        for user in info2:
            data.append(user)
        if data:
            data = sorted(data, key=attrgetter('sent_on'), reverse=False)
        else:
            raise Exception
            """
    data = []
    info1 = db_session.query(entities.Message).\
        filter(or_(entities.Message.user_from_id == id1, entities.Message.user_from_id == id2))
    info2 = info1.filter(or_(entities.Message.user_to_id == id1, entities.Message.user_to_id == id2))
    for user in info2:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')


@app.route('/chat/firstCheck/<id1>/and/<id2>', methods = ['PUT'])
def firstCheck_chat(id1, id2):
    c = json.loads(request.data)
    session = db.getSession(engine)
    for idRecibido in c['chatsDescargados']:
        message = session.query(entities.Message).filter(entities.Message.id == idRecibido).first()
        message.last_seen = func.now()
    session.commit()
    return 'Updated Users'



@app.route('/chat/getLastConversation/<id1>/and/<id2>', methods = ['GET'])
def get_last_chats_id(id1, id2):
    try:
        db_session = db.getSession(engine)
        try:
            info1 = db_session.query(entities.Message).filter(
                entities.Message.user_from_id == id2).filter(
                entities.Message.user_to_id == id1).order_by(
                entities.Message.id.desc()).first()
        except Exception:
            info1 = False

        try:
            info2 = db_session.query(entities.Message).filter(
                entities.Message.user_from_id == id1).filter(
                entities.Message.user_to_id == id2).order_by(
                entities.Message.id.desc()).first()
        except Exception:
            info2 = False

        if not info1:
            resultado = info2
        elif not info2:
            resultado = info1
        else:
            if info1.id > info2.id:
                resultado = info1
            else:
                resultado = info2

        return Response(json.dumps(resultado, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')
    except Exception:
        message = {'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')



@app.route('/newMesssage', methods = ['POST'])
def newMesssage():
    try:
        c = json.loads(request.data)
        message = entities.Message(
            content=c['content'],
            user_from_id=c['user_from_id'],
            user_to_id=c['user_to_id']
        )
        session = db.getSession(engine)
        session.add(message)
        session.commit()
        message = {'message': 'Authorized'}
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')



# - - - - - - - - - - - - - - - - - - - - - -#
# - - D E F A U L T - C R U D  U S E R S - - #
# - - - - - - - - - - - - - - - - - - - - - -#



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
        lastname=c['lastname'],
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
# - - - - - - C R U D  U S E R S - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - -#

@app.route('/user/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

@app.route('/user/allExcept/<id>', methods = ['GET'])
def get_user_allExcept(id):
    db_session = db.getSession(engine)
    try:
        dbResponse = db_session.query(entities.User).filter(entities.User.id != id)
        data = []
        for user in dbResponse:
            data.append(user)
        return Response(json.dumps(data, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')
    except Exception:
        message = { 'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')

# - - - - - - - - - - - - - - - - - - - - - -#
# - - - - - - - - L O G I N  - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - -#

@app.route("/login")
def login():
    return render_template('login2.html')

@app.route('/authenticate', methods = ["POST"])
def authenticate():
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
        session['logged_user']=user.id
        message = {'message': 'Authorized'}
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')

# - - - - - - - - - - - - - - - - - - - - - - - #
# - - - - - - - -  L O G O U T  - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - - - #

@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    return render_template('login2.html')

# - - - - - - - - - - - - - - - - - - - - - - - #
# - - - - - - - -  S T A R T  - - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - - - #

@app.route('/start', methods = ['GET'])
def start_user():
    try:
        db_session = db.getSession(engine)
        user = db_session.query(entities.User).filter(entities.User.id == session['logged_user']).first()
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')
    except Exception:
        message = {'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))
