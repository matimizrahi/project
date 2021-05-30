import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import netifaces


# השרת ניגש למאגר המידע, שולף את המידע הרלוונטי ומחזיר למשתמש

# finds server's IP address and returns it
def ip4_addresses():
    # https://stackoverflow.com/questions/49195864/how-to-get-all-ip-addresses-using-python-windows
    for iface in netifaces.interfaces():
        iface_details = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in iface_details:
            # print(iface_details[netifaces.AF_INET])
            for ip_interfaces in iface_details[netifaces.AF_INET]:
                for key, ip_add in ip_interfaces.items():
                    if key == 'addr' and ip_add != '127.0.0.1':
                        return ip_add


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))  # /// is a relative path

# creating a Flask app 
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file

# Order matters: Initialize SQLAlchemy before Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)


# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# https://docs.sqlalchemy.org/en/13/core/constraints.html#unique-constraint
# https://www.w3schools.com/sql/sql_unique.asp
class User(db.Model):
    __table_name__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)  # can't have the same username therefore it's unique
    password = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False)
    ip = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.name}', '{self.email}', '{self.ip}')"  # omit password
        #   return 'id:{} name:{} email{} ip:{}'.format(self.id, self.name, self.email, self.ip)  # omit password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'password', 'email', 'ip')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Active_Users(db.Model):
    __table_name__ = 'Active'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)  # can't have the same username therefore it's unique
    ip = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.name}', '{self.ip}')"  # omit password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'ip')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Call(db.Model):  # call other side
    __table_name__ = 'Call'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    src = db.Column(db.String(32), unique=True, nullable=False)  # the name of the src caller is unique
    operation = db.Column(db.String(32), nullable=False)
    dst = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.src}', '{self.operation}', '{self.dst}')"
        #   return 'id:{} src:{} operation:{} dst:{}'.format(self.id, self.src, self.operation, self.dst)


#   db.create_all() #to create the tables


class CallSchema(ma.Schema):
    class Meta:
        fields = ('src', 'operation', 'dst')


call_schema = CallSchema()
calls_schema = CallSchema(many=True)


@app.route('/user_list')
def user_list():
    if request.method == 'GET':
        results = db.session.query(User.name).all()
        user_names = [u.name for u in results]
        return jsonify(user_names)


@app.route('/active_user_list')
def active_user_list():
    if request.method == 'GET':
        results = db.session.query(Active_Users.name).all()
        user_names = [u.name for u in results]
        return jsonify(user_names)


@app.route('/get_ip', methods=['GET'])
def get_ip():
    if request.method == 'GET':
        user_name = request.form.get("name")
        result = ""
        user_info = User.query.filter_by(name=user_name).first()
        if user_info:
            result = user_info.ip
        # print('sending:', result)
        return jsonify(result)


@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        user_name = request.form.get("name")
        password = request.form.get("password")

        result = 'False'
        user_info = User.query.filter_by(name=user_name, password=password).first()
        if user_info:
            # print(user_info.name, user_info.ip)
            result = "True"
        # print(f'sending {result}')
        return jsonify(result)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        # data = request.form
        # print(data)
        user_name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")
        ip = request.remote_addr
        result = 'False'
        user_info = User.query.filter_by(name=user_name).first()
        # check if name already exist
        if not user_info:
            new_user = User(name=user_name, password=password, email=email, ip=ip)
            db.session.add(new_user)
            db.session.commit()
            # print("new user:", new_user.id, user_name, password, email ip)
            result = "True"
        # print(f'sending {result}')
        return jsonify(result)


@app.route('/accept', methods=['PUT'])
def accept():
    if request.method == 'PUT':
        dst = request.form.get("dst")
        src = request.form.get("src")
        op = request.form.get("operation")
        result = ""
        row = Call.query.filter_by(dst=dst, src=src).first()
        if row:
            if row.operation == 'ringing':
                row.operation = op
                db.session.commit()
                result = 'True'
        # print(f'sending {result}')
        return jsonify(result)


@app.route('/stop', methods=['DELETE'])
def stop():
    if request.method == 'DELETE':
        name = request.form.get("name")
        op = request.form.get("operation")
        result = "empty"

        if op == 'ringing':
            row = Call.query.filter_by(src=name).first()
            if not row:
                row = Call.query.filter_by(dst=name).first()
            if row:
                db.session.delete(row)
                db.session.commit()
                result = 'ringing stopped'
        else:  # call
            row = Call.query.filter_by(src=name).first()
            if not row:
                row = Call.query.filter_by(dst=name).first()
            if row:
                db.session.delete(row)
                db.session.commit()
                result = 'call stopped'
        # print('sending:', result)
        return jsonify(result)


@app.route('/call', methods=['POST'])
def call():
    if request.method == 'POST':
        src = request.form.get("src")
        operation = request.form.get("operation")
        dst = request.form.get("dst")
        result = 'call already exists'
        raw = Call.query.filter_by(src=src).first()
        if not raw:
            new_call = Call(src=src, operation=operation, dst=dst)
            db.session.add(new_call)
            db.session.commit()
            # print("new_call:", new_call.id, src, operation, dst)
            result = "True"
        # print('sending:', result)
        return jsonify(result)


@app.route('/check', methods=['GET'])
def check_connection():
    if request.method == 'GET':
        dst = request.form.get("dst")
        src = request.form.get("src")
        name = request.form.get("name")
        result = ""

        # check if not rejected
        if dst and src:
            data = Call.query.filter_by(dst=dst, src=src).first()
            if data:
                result = True  # not rejected

        # check if in chat
        elif name:
            data = Call.query.filter_by(dst=name, operation='call').first()
            if not data:
                data = Call.query.filter_by(src=name, operation='call').first()
            if data:
                result = True

        # check if being dialing; 'ringing'
        elif dst and not src:
            row = Call.query.filter_by(dst=dst).first()
            if row:
                result = row.src
        # print('sending:', result)
        return jsonify(result)


if __name__ == '__main__':
    # db.create_all(app=app)
    import socket

    IPs = ip4_addresses()
    print(f'Server started!')
    print(f'IPs : {IPs}')
    print(f'hostname : {socket.gethostname()}')
    app.run(debug=False, host='0.0.0.0', port=5000)  # debug=False- if I have any errors they won't come up
