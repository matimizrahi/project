import requests


HOST_IP = input('enter host IP: ')
MAIN_SERVER_PORT = 5000
MAIN_SERVER_URL = f'http://{HOST_IP}:{MAIN_SERVER_PORT}'


def user_left(name):
    data = {'name': name}
    r = requests.get(MAIN_SERVER_URL + '/left', data=data)


# if call not rejected returns True
def not_rejected(src, dst):
    data = {'src': src, 'dst': dst}
    r = requests.get(MAIN_SERVER_URL + '/check', data=data)
    return r.json()


# registered users
def user_lists():
    print("slient-servre")
    r = requests.get(MAIN_SERVER_URL + '/user_list')
    return r.json()  # r.status_code


# active users- to display on main page
def active_user_lists():
    r = requests.get(MAIN_SERVER_URL + '/active_user_list')
    return r.json()


def is_in_call():
    r = requests.get(MAIN_SERVER_URL + '/call_list')
    return r.json()


# returns ip or 0 if user doesnt exist
def get_user_ip(name, table):
    data = {'name': name, 'table': table}
    r = requests.get(MAIN_SERVER_URL + '/get_ip', data=data)
    return r.json()


# return true if name exists in table
def is_user(name, table):
    if get_user_ip(name, table):
        return True
    return False


# login
def login(name, password):
    data = {'name': name, 'password': password}
    r = requests.get(MAIN_SERVER_URL + '/login', data=data)
    if r.json() == 'True':
        print(name, " logged in")
        return 'True'
    elif r.json() == 'already_conn':
        return 'already_conn'
    return 'False'


# register
def register(name, password, email):
    data = {'name': name, 'password': password, 'email': email}
    r = requests.post(MAIN_SERVER_URL + '/register', data=data)
    if r.json() == 'True':
        print(name, " registered")
        return True
    return False


# post dialing
def call(src, dst):
    new_call = {'src': src, 'operation': 'dialing', 'dst': dst}
    r = requests.post(MAIN_SERVER_URL + '/call', data=new_call)
    if r.json() == 'True':
        return True
    return False


# change from dialing to call
def accept(src, dst):
    new_call = {'src': src, 'operation': 'call', 'dst': dst}
    r = requests.put(MAIN_SERVER_URL + '/accept', data=new_call)
    return r.json()


# check if a user is ringing
def look_for_call(dst):
    check_call = {'operation': 'dialing', 'dst': dst}
    r = requests.get(MAIN_SERVER_URL + '/check', data=check_call)
    return r.json()


# returns name of dialing user
def get_src_name(dst):
    name = look_for_call(dst)
    if name:
        return name


# check if call accepted or if call still alive
def is_in_call(name):
    data = {'name': name}
    r = requests.get(MAIN_SERVER_URL + '/check', data=data)
    return r.json()


# when dialing
def stop(name, operation):
    msg = {'name': name, 'operation': operation}
    r = requests.delete(MAIN_SERVER_URL + "/stop", data=msg)
    return r.json()

