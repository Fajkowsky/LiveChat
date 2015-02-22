from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask.ext.wtf import Form
from flask.ext.mongoengine import MongoEngine, DoesNotExist
from flask.ext.login import LoginManager, login_user, login_required, logout_user, current_user
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
from wtforms import StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4

app = Flask(__name__)
app.config.from_object('config')

db = MongoEngine(app)

login_manager = LoginManager()
login_manager.login_view = "login_page"
login_manager.init_app(app)

socketio = SocketIO(app)


class User(db.Document):
    username = db.StringField(primary_key=True, required=True)
    password = db.StringField(required=True)
    user_contacts = db.ListField()
    status = db.BooleanField(default=True)
    description = db.StringField(default="")

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return unicode(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "{}".format(self.username)

    @staticmethod
    def get_user(username):
        try:
            user = User.objects.get(username=username)
        except DoesNotExist:
            return None
        return user

    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super(User, self).save(self, *args, **kwargs)


class PrivateChat(db.Document):
    users = db.ListField()
    chat_id = db.StringField()
    history = db.ListField()

    def save(self, *args, **kwargs):
        self.chat_id = uuid4().hex
        super(PrivateChat, self).save(self, *args, **kwargs)


class ChatRoom(db.Document):
    name = db.StringField(required=True)

    def __repr__(self):
        return "{}".format(self.name)


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired(), validators.length(min=3, max=8)])
    password = PasswordField('Password', [validators.DataRequired(), validators.length(min=5)])

    def validate(self):
        if super(LoginForm, self).validate():
            try:
                user = User.objects.get(username=self.username.data)
                if not user.check_password(self.password.data):
                    self.password.errors.append('Wrong password.')
                    return False
            except DoesNotExist:
                User(
                    username=self.username.data,
                    password=self.password.data
                ).save()
            return True


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


@app.route('/logout/', methods=['GET', ])
def logout():
    logout_user()
    return redirect(url_for('login_page'))


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
def get_avalible_users(username):
    try:
        user_contacts = User.objects.get(username=username).user_contacts
        users = User.objects(username__ne=username)
        data = [item.username for item in users if item.username not in user_contacts]
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


@app.errorhandler(404)
def error_handler(err):
    return redirect(url_for('login_page'))


@socketio.on('give_user')
def curr_user():
    if current_user.is_authenticated():
        data = {
            'username': current_user.username,
            'status': current_user.status,
            'description': current_user.description
        }
        emit('get_user', data)


@socketio.on('get_contacts')
def contacts():
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
def del_contact_user(data):
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
def send_room_message(message):
    data = {'user': message['username'], 'message': message['data']}
    try:
        chat = PrivateChat.objects.get(chat_id=message['room'])
        chat.update(push__history=data)
    except DoesNotExist:
        pass
    emit('msg', data, room=message['room'])


@socketio.on('status')
def status_update(data):
    user = User.objects(username=data['username'])
    user.update(set__status=data['status'])
    emit('update_status', {}, broadcast=True)


@socketio.on('description')
def description_update(data):
    user = User.objects(username=data['username'])
    user.update(set__description=data['description'])
    emit('update_status', {}, broadcast=True)


@socketio.on('create_private_chat')
def get_or_create_chat(data):
    users = sorted([data['username'], data['contact']])
    try:
        chat = PrivateChat.objects.get(users=users)
    except DoesNotExist:
        chat = PrivateChat(users=users)
        chat.save()
    join_room(chat.chat_id)
    emit('private_chat', {'data': chat})


if __name__ == '__main__':
    socketio.run(app)

