from . import app, models
from flask import render_template, abort, request, jsonify, redirect
from datetime import datetime, timedelta
from flask_login import current_user, login_user


@app.route("/")
def index():
    return render_template("login.html", chatrooms=models.ChatRoom.objects().all())


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        if (email is None) or (password is None):
            return redirect("/register")

        newUser = models.User(email=email)
        newUser.setPassword(password)
        newUser.save()
        return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    if (email is None) or (password is None):
        return redirect("/")

    userObject: models.User = models.User.objects(email=email).first()
    if userObject is None:
        return redirect("/")

    if userObject.checkPassword(password):
        login_user(userObject)
        return redirect("/chatroom_list")
    else:
        return redirect("/")

@app.route("/chatroom_list")
def chatroomList():
    if current_user.is_authenticated:
        return render_template("chatroom_list.html", chatrooms=models.ChatRoom.objects().all())
    else:
        abort(400)


@app.route("/chat/<room_code>")
def chatroom(room_code):
    if current_user.is_authenticated:
        thisChatroom = models.ChatRoom.objects(code=room_code).first()
        if thisChatroom is None:
            abort(404)

        return render_template("chatroom.html", chatroom=thisChatroom)
    else:
        abort(400)

@app.route("/get_latest_messages/<room_code>")
def getLatestMessages(room_code):
    if current_user.is_authenticated:
        thisChatroom = models.ChatRoom.objects(code=room_code).first()
        if thisChatroom is None:
            abort(404)

        lastRequestTimestamp = request.args.get("last_poll")
        if lastRequestTimestamp is None:
            abort(500, "No timestamp!")

        lastRequest = datetime.fromtimestamp(float(lastRequestTimestamp)) - timedelta(seconds=1)
        messages = models.Chat.objects(chatroom=thisChatroom).order_by("-timeSent").all().limit(10)
        raw = list()
        for message in messages:
            raw.append({
                "message_id": str(message.id),
                "type": message.type,
                "user": message.user.email,
                "text": message.text
            })
        raw.reverse()
        return jsonify(raw)
    else:
        abort(400)


@app.route("/new_chat", methods=["GET", "POST"])
def newChat():
    if current_user.is_authenticated:
        if request.method == "GET":
            return render_template("new_chat.html")
        else:
            friendlyName = request.form.get("name")
            roomCode = request.form.get("room_code")
            if (friendlyName is None) or (roomCode is None):
                return redirect("/new_chat")

            newChatroom = models.ChatRoom(
                friendlyName=friendlyName,
                code=roomCode
            )
            newChatroom.save()
            return redirect("/chatroom_list")
    else:
        abort(400)


@app.route("/send_chat/<room_code>", methods=["POST"])
def send_chat(room_code):
    print(request.data)
    if current_user.is_authenticated:
        thisChatroom = models.ChatRoom.objects(code=room_code).first()
        if thisChatroom is None:
            abort(404)

        currentUser = models.User.objects(id=str(current_user.get_id())).first()
        newChat = models.Chat(
            user=currentUser,
            chatroom=thisChatroom,
            type="text",
            text=request.args.get("message"),
            image=None
        )
        newChat.save()
        return "Success"
    else:
        abort(400)

