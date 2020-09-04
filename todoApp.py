from flask import Flask, jsonify, session, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import make_response
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
import json, os, sys
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['JWT_AUTH_URL_RULE'] = '/todo/api/login'
app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt()
app.config['SECRET_KEY'] = '========SECRET_KEY============'



def authenticate(email, password):
    user = User.query.filter_by(email=email).first()    
    if user and bcrypt.check_password_hash(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    user = User.query.get(user_id)
    if user:
        return user
    else:
        return(none)

jwt = JWT(app, authenticate, identity)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=True)
    description = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    completed = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def __repr__(self):
        return f'{self.username} {self.email}'



@app.route('/todo/api/signup', methods=['POST'])
def userRegistration():
    if request.method == 'POST':
        data = json.loads(request.data)
        username = data.get('username')
        if not username:
            return jsonify({'Error':'Username is Required'})
        email = data.get('email')
        euser = User.query.filter_by(username=username).first()
        eemail = User.query.filter_by(email=email).first()
        if euser:
            return jsonify({'Error':'This username is already taken'})
        elif eemail:
            return jsonify({'Error':'This email is already exist'})
        else:
            hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
            print('Password Hashed ', hashed_password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'msg':'user created successfully you can log in now'})

# @app.route('/todo/api/login', methods=['POST'])
# def login():
#     if request.method == 'POST':
#         data = json.loads(request.data)
#         email = data.get('email')
#         password = data.get('password')
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify({'Error':'email not exist! please signup'})
#         if user.password == password:
#             return jsonify({'msg':'User logged in successfully!'})
#         else:
#             return jsonify({'Error':'Incorrect password!'})
@app.route('/todo/api/tasks/', methods=['GET','POST'])
@jwt_required()
def show_tasks():
    print(current_identity)
    if request.method == 'GET':
        tasks = Task.query.all()
        data_dict = dict()
        data = []
        print(len(tasks))
        for task in tasks:
            temp_data = {
                'task_id': task.id,
                'title':task.title,
                'description':task.description,
                'status':task.done,
                'creation_time':task.created,
                'complition_time':task.completed,
                'user': task.user.username }
            print(temp_data)
            data.append(temp_data)
        data_dict.update(data_dict)
        if not data:
            return jsonify({"msg":"There is no task available"})
        return jsonify(data)
    elif request.method == 'POST':
        print('Got in Post method')
        data = json.loads(request.data)
        try:
            title = data.get('title')
            task = Task.query.filter_by(title=title).first()
            if task:
                return jsonify({'Error':'task Already Exist'})
            description = data.get('description')
            status = data.get('status')
            new_task = Task(title=title, description=description, done=status, user_id=current_identity.id)
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'msg':'task created successfully'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
            return jsonify({"ERROR":str(e)})


@app.route('/todo/api/tasks/<id>',methods=['GET','PUT','DELETE'])
@jwt_required()
def get_task_by_id(id):
    task = Task.query.get(id)
    if task:
        if request.method == 'PUT':
            update = json.loads(request.data)
            print(update)
            if update.get('status') == True:
                task.done = update.get('status')
                task.completed = datetime.utcnow()
                db.session.commit()
            else:
                task.done = update.get('status')
                task.completed = None
                db.session.commit()
            updated_data = Task.query.get(id)
            updated_data = {
                'task_id': task.id,
                'title':task.title,
                'description':task.description,
                'status':task.done,
                'creation_time':task.created,
                'complition_time':task.completed }
            return jsonify(updated_data)
        elif request.method == 'DELETE':
            try:
                print('GOT Delete MEthod')
                db.session.delete(task)
                db.session.commit()
                return jsonify({'msg':'task deleted successfully'})
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
                print(e)
                return jsonify({"ERROR":str(e)})
        else:
            temp_data = {
                'task_id': task.id,
                'title':task.title,
                'description':task.description,
                'status':task.done,
                'creation_time':task.created,
                'complition_time':task.completed }
            return jsonify(temp_data)
    else:
        return jsonify({'msg':'task not exist'})



if __name__=='__main__':
    app.run(debug=True)
