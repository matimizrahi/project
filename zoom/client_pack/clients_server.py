import requests
import time

HOST_IP = '10.0.0.31'
#   HOST_IP = input('please enter host IP')
MAIN_SERVER_IP = 5000
MAIN_SERVER_URL = f'http://{HOST_IP}:{MAIN_SERVER_IP}'


# server's ip and port
def print_info():
    print(f'server ip = {HOST_IP}')
    print(f'server port = {MAIN_SERVER_IP}')


print_info()


# if call not rejected returns True
def not_rejected(src, dst):
    data = {'src': src, 'dst': dst}
    r = requests.get(MAIN_SERVER_URL + '/check', data=data)
    return r.json()


# registered users
def user_lists():
    r = requests.get(MAIN_SERVER_URL + '/user_list')
    return r.json()  # r.status_code


'''
# registered users
def active_user_lists():
    r = requests.get(MAIN_SERVER_URL + '/active_user_list')
    return r.json()  # r.status_code
'''


# returns ip or 0 if user doesnt exist
def get_user_ip(name):
    data = {'name': name}
    r = requests.get(MAIN_SERVER_URL + '/get_ip', data=data)
    return r.json()  # r.status_code


# return true if user exists
def is_user(name):
    if get_user_ip(name):
        return True
    return False


# login
def login(name, password):
    data = {'name': name, 'password': password}
    r = requests.get(MAIN_SERVER_URL + '/login', data=data)
    if r.json() == 'True':
        return True
    return False


# register
def register(name, password, email):
    data = {'name': name, 'password': password, 'email': email}
    r = requests.post(MAIN_SERVER_URL + '/register', data=data)
    # print(r.json())
    if r.json() == 'True':
        return True
    return False


# post ringing
def call(src, dst):
    print("call: src->", src, "   <-dst->", dst)
    new_call = {'src': src, 'operation': 'ringing', 'dst': dst}
    r = requests.post(MAIN_SERVER_URL + '/call', data=new_call)
    # print(r.json())  # r.status_code
    if r.json() == 'True':
        return True
    return False


# change from ringing to call
def accept(src, dst):
    print("accept: src->", src, "   <-dst->", dst)
    new_call = {'src': src, 'operation': 'call', 'dst': dst}
    r = requests.put(MAIN_SERVER_URL + '/accept', data=new_call)
    return r.json()
    # print(r.json())  # r.status_code


# check if a user is dialing
def look_for_call(dst):
    print("look for call: dst->", dst)
    check_call = {'operation': 'ringing', 'dst': dst}
    r = requests.get(MAIN_SERVER_URL + '/check', data=check_call)
    return r.json()  # returns src or ""


# returns name of ringing user
def get_src_name(dst):
    print("der_src_name: dst->", dst)
    name = look_for_call(dst)
    if name:
        return name


# check if call accepted or if call still alive
def is_in_call(name):
    print("is_in_call: name->", name)
    data = {'name': name}
    r = requests.get(MAIN_SERVER_URL + '/check', data=data)
    return r.json()


# when ringing
def stop(name, operation):
    print("stop: name->", name, "   <-op->", operation)
    msg = {'name': name, 'operation': operation}
    r = requests.delete(MAIN_SERVER_URL + "/stop", data=msg)
    # print(r.json())
    return r.json()  # r.status_code


if __name__ == '__main__':
    my_name = ''
    print('Users List')
    print(*user_lists(), sep='\n')
    while True:
        if look_for_call(my_name):
            break
    user = get_src_name(my_name)
    print(user)
    accept(my_name, user)

    time.sleep(7)
    stop(my_name, 'call')
