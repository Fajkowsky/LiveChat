from models import User

from wtforms import StringField, PasswordField, validators
from flask.ext.mongoengine import DoesNotExist
from flask.ext.wtf import Form


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