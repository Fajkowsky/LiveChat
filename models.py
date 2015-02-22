from app import db
from flask.ext.mongoengine import DoesNotExist
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4


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