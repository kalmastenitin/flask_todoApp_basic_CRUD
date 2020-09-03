from flask import Flask, jsonify, session, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import make_response
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'nuibwugbfih309u3r09jc9f3r924ug0j'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=True)
    description = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    completed = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return self.title


@app.route('/todo/api/tasks/', methods=['GET','POST'])
def show_tasks():
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
                'complition_time':task.completed }
            print(temp_data)
            data.append(temp_data)
        data_dict.update(data_dict)
        return jsonify(data)
    elif request.method == 'POST':
        print('Got in Post method')
        data = json.loads(request.data)
        try:
            title = data.get('title')
            description = data.get('description')
            status = data.get('status')
            new_task = Task(title=title, description=description, done=status)
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
