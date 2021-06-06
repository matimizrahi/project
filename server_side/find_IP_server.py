import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import netifaces
import socket
from sqlalchemy import Column, Integer, String


# השרת ניגש למאגר המידע, שולף את המידע הרלוונטי ומחזיר למשתמש

# finds server's IP address and returns it
def ip4_addresses():
    for iface in netifaces.interfaces():
        iface_details = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in iface_details:
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


class User(db.Model):
    __table_name__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)  # can't have the same username therefore it's unique
    password = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False)
    ip = Column(String(32), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.name}', '{self.email}', '{self.ip}')"


class UserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'password', 'email', 'ip')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Active(db.Model):
    __table_name__ = 'Active'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)  # can't have the same username therefore it's unique
    ip = Column(String(32), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.name}', '{self.ip}')"


class ActiveUserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'ip')


active_user_schema = ActiveUserSchema()
active_users_schema = ActiveUserSchema(many=True)


class Call(db.Model):  # call other side
    __table_name__ = 'Call'
    id = Column(Integer, primary_key=True, autoincrement=True)
    src = Column(String(32), unique=True, nullable=False)  # the name of the src caller is unique
    operation = Column(String(32), nullable=False)
    dst = Column(String(32), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.src}', '{self.operation}', '{self.dst}')"


class CallSchema(ma.Schema):
    class Meta:
        fields = ('src', 'operation', 'dst')


call_schema = CallSchema()
calls_schema = CallSchema(many=True)


def ip_in_Active(ip):
    name = Active.query.filter_by(ip=ip).first().name
    call_src = Call.query.filter_by(src=name).first()
    call_dst = Call.query.filter_by(dst=name).first()
    # if the clients just ended the call they wont be on the call table
    if call_src:
        db.session.delete(call_src)
        a = Active.query.filter_by(ip=ip).first()
        if a:
            db.session.delete(a)
            db.session.commit()
    elif call_dst:
        db.session.delete(call_dst)
        a = Active.query.filter_by(ip=ip).first()
        if a:
            db.session.delete(a)
            db.session.commit()


@app.route('/left')
def user_left():
    if request.method == 'GET':
        user_name = request.form.get("name")
        a = Active.query.filter_by(name=user_name).first()
        if a:
            db.session.delete(a)
            db.session.commit()
        call_src = Call.query.filter_by(src=user_name).first()
        call_dst = Call.query.filter_by(dst=user_name).first()
        if call_src:
            db.session.delete(call_src)
            db.session.commit()
        if call_dst:
            db.session.delete(call_dst)
            db.session.commit()
        return jsonify('True')


@app.route('/user_list')
def user_list():
    if request.method == 'GET':
        results = db.session.query(User.name).all()
        user_names = [u.name for u in results]
        return jsonify(user_names)


@app.route('/active_user_list')
def active_user_list():
    if request.method == 'GET':
        if db.session.query(Active).first:
            results = db.session.query(Active.name).all()
            user_names = [u.name for u in results]
            return jsonify(user_names)
        return jsonify(False)


@app.route('/call_list')
def is_in_call(src):
    if request.method == 'GET':
        result = 'False'
        user_info = Call.query.filter_by(src=src).first()
        if user_info:
            result = "True"
        return jsonify(result)


@app.route('/get_ip', methods=['GET'])
def get_ip():
    if request.method == 'GET':
        user_name = request.form.get("name")
        table = request.form.get("table")
        result = ""
        if table == "Active":
            user_info = Active.query.filter_by(name=user_name).first()
        else:
            user_info = User.query.filter_by(name=user_name).first()
        if user_info:
            result = user_info.ip
        return jsonify(result)


@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        user_name = request.form.get("name")
        password = request.form.get("password")
        if Active.query.filter_by(name=user_name).first():
            return jsonify('already_conn')
        result = 'False'
        user_info = User.query.filter_by(name=user_name, password=password).first()
        if user_info:
            result = "True"
            user_info.ip = request.remote_addr  # updates the user's ip to it's current one
            db.session.add(Active(name=user_name, ip=user_info.ip))
            db.session.commit()
        return jsonify(result)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        user_name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")
        ip = request.remote_addr
        result = 'False'
        user_info = User.query.filter_by(name=user_name).first()
        # checks if name already exist
        if not user_info:
            new_user = User(name=user_name, password=password, email=email, ip=ip)
            db.session.add(new_user)
            db.session.commit()
            result = 'True'
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
            if row.operation == 'dialing':
                row.operation = op
                db.session.commit()
                result = 'True'
        return jsonify(result)


@app.route('/stop', methods=['DELETE'])
def stop():
    if request.method == 'DELETE':
        name = request.form.get("name")
        op = request.form.get("operation")
        result = "empty"

        if op == 'dialing':
            row = Call.query.filter_by(src=name).first()
            if not row:
                row = Call.query.filter_by(dst=name).first()
            if row:
                db.session.delete(row)
                db.session.commit()
                result = 'dialing stopped'
        else:  # call
            row = Call.query.filter_by(src=name).first()
            if not row:
                row = Call.query.filter_by(dst=name).first()
            if row:
                db.session.delete(row)
                db.session.commit()
                result = 'call stopped'
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
            result = "True"
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

        # check if being ringing; 'dialing'
        elif dst and not src:
            row = Call.query.filter_by(dst=dst).first()
            if row:
                result = row.src
        return jsonify(result)


if __name__ == '__main__':
    # db.create_all()  # to create the tables- not necessary if database.db id downloaded
    IPs = ip4_addresses()
    print(f'Server started!')
    print(f'IPv4 : {IPs}')
    print(f'hostname : {socket.gethostname()}')
    db.session.query(Call).delete()  # because if a client stopped the program while calling someone he is still
    db.session.query(Active).delete()  # because if a client stopped the program while calling someone he is still
    # calling according to the call table
    db.session.commit()
    print("deleted prior information in Call table")
    app.run(debug=False, host='0.0.0.0', port=5000)  # debug=False- if I have any errors they won't come up
