import mongoengine
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from uuid import uuid4
from flask_login import UserMixin
from . import login


@login.user_loader
def user_loader(id):
    return User.objects(id=id).first()


def generate_token():
    return str(uuid4())


class User(mongoengine.Document, UserMixin):
    email = mongoengine.EmailField(required=True)
    passwordHash = mongoengine.StringField(required=True)

    def checkPassword(self, password):
        return check_password_hash(self.passwordHash, password)

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)


class ChatRoom(mongoengine.Document):
    friendlyName = mongoengine.StringField(required=True)
    code = mongoengine.StringField(required=True)


class UserChatRoomRegistration(mongoengine.Document):
    user = mongoengine.ReferenceField(User, required=True)
    chatroom = mongoengine.ReferenceField(ChatRoom, required=True)


class Image(mongoengine.Document):
    file = mongoengine.ImageField(required=True)


class Chat(mongoengine.Document):
    chatroom = mongoengine.ReferenceField(ChatRoom, required=True)
    user = mongoengine.ReferenceField(User, required=True)
    type = mongoengine.StringField(required=True, default="text")
    image = mongoengine.ReferenceField(Image, required=False, default=None)
    text = mongoengine.StringField(required=True, default=None)
    timeSent = mongoengine.DateTimeField(required=True, default=datetime.utcnow)
