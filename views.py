from flask import render_template, redirect, url_for, jsonify, request
from app import app, login_manager, socketio
from forms import LoginForm
from models import User, ChatRoom, PrivateChat
from flask.ext.mongoengine import DoesNotExist
from flask.ext.socketio import emit, join_room, leave_room
from flask.ext.login import login_user, login_required, logout_user, current_user


@login_manager.user_loader
def load_user(username):
    return User.get_user(username)


@app.route('/', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated():
        return redirect(url_for('communicator'))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.objects.get(username=login_form.username.data)
        login_user(user)
        return redirect(url_for('communicator'))
    return render_template('login.html', form=login_form)


@app.route('/communicator/', methods=['GET', ])
@login_required
def communicator():
    chat_rooms = ChatRoom.objects
    return render_template(
        'communicator.html',
        rooms=chat_rooms,
        logged_user=current_user
    )


@app.route('/contact/<string:username>/', methods=['GET', ])
def get_available_users(username):
    try:
        user_contacts = User.objects.get(username=username).user_contacts
        users = User.objects(username__ne=username)
        data = [user.username for user in users if user.username not in user_contacts]
        return jsonify(data=data)

    except DoesNotExist:
        return jsonify(data=[])


@app.route('/contact/', methods=['POST', ])
def save_contact():
    if current_user.is_authenticated():
        try:
            user = User.objects.get(username=current_user.username)
            new_user = request.json['username']
            if not new_user in user.user_contacts:
                user.update(push__user_contacts=new_user)
        except DoesNotExist:
            return jsonify(error='User not exists.')
        return jsonify(info='User added.')
    return jsonify(error='User not logged-in.')


@app.route('/logout/', methods=['GET', ])
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.errorhandler(404)
def error_handler(err):
    return redirect(url_for('login_page'))


# SOCKETIO
@socketio.on('give_user')
def give_user():
    if current_user.is_authenticated():
        data = {
            'username': current_user.username,
            'status': current_user.status,
            'description': current_user.description
        }
        emit('get_user', data)


@socketio.on('get_contacts')
def get_contacts():
    fields = [
        'username',
        'user_contacts',
        'status',
        'description'
    ]

    contact_list = [
        item for item in User.objects().only(*fields)
        if item.username in current_user.user_contacts
    ]
    emit('give_contacts', {'data': contact_list})


@socketio.on('del_user')
def del_user(data):
    user = User.objects(username=data['username'])
    user.update(pull__user_contacts=data['del'])


@socketio.on('join')
def join(message):
    join_room(message['room'])
    emit('my response', {"room": message['room']})


@socketio.on('leave')
def leave(message):
    leave_room(message['room'])
    emit('my response', {"room": message['room']})


@socketio.on('room_msg')
def room_msg(message):
    data = {'user': message['username'], 'message': message['data']}
    try:
        chat = PrivateChat.objects.get(chat_id=message['room'])
        chat.update(push__history=data)
    except DoesNotExist:
        pass
    emit('msg', data, room=message['room'])


@socketio.on('status')
def status(data):
    user = User.objects(username=data['username'])
    user.update(set__status=data['status'])
    emit('update_status', {}, broadcast=True)


@socketio.on('description')
def description(data):
    user = User.objects(username=data['username'])
    user.update(set__description=data['description'])
    emit('update_status', {}, broadcast=True)


@socketio.on('create_private_chat')
def create_private_chat(data):
    users = sorted([data['username'], data['contact']])
    try:
        chat = PrivateChat.objects.get(users=users)
    except DoesNotExist:
        chat = PrivateChat(users=users)
        chat.save()
    join_room(chat.chat_id)
    emit('private_chat', {'data': chat})
