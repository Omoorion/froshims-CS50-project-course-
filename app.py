import sqlite3
from decouple import config
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message

app = Flask(__name__)

#alternatively can be done with os.environ["VALUE"]:
app.config["MAIL_DEFAULT_SENDER"] = str(config('EMAIL'))
app.config["MAIL_PASSWORD"] = str(config('PASS'))
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = str(config('EMAIL'))
mail = Mail(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

SPORTS = [
    "Basketball",
    "Football",
    "Soccer",
    "Ultimate Frisbee",
]

@app.route("/")
def index():
    if not session.get("name"):
        return redirect("/login")
    if not session.get("sport"):
        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        sportDb = cursor.execute("SELECT sport FROM registrants WHERE name = ? AND id = ?", (session.get("name"), session.get("id")))
        conn.close()
        sportValue = ""
        for sport in SPORTS:
            if sport in str(sportDb):
                sportValue = sport
                break
        session["sport"] = sportValue
        
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        print(name + " " + password)

        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT name, id FROM registrants WHERE name=? AND password=?;", (name, password, ))
        isName = ""
        isId = ""
        isAll = cursor.fetchall()
        if(isAll != []):
            print("true")
            isName = isAll[0][0]
            print(isName)
            isId = isAll[0][1]
            print(isId)
        conn.close()
        print("false")

        if isName != "" and isId != "":
            session["name"] = isName
            session["id"] = isId
            return redirect("/")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        email= request.form.get("email")
        sport = request.form.get("sport")

        if not name or not password or not email or sport not in SPORTS:
            return render_template("failure.html")
    
        message = Message("you are registered!", recipients=[email])
        mail.send(message)
        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registrants (name, password, sport) VALUES(?, ?, ?)", (name, password, sport, ))
        conn.commit()
        cursor.execute("SELECT id FROM registrants WHERE name = ? AND password = ?", (name, password, ))
        id = cursor.fetchall()[0][0]
        conn.close()
        session["id"] = id
        session["name"] = name
        session["sport"] = sport

        return redirect("/")
    
    return render_template("register.html", sports=SPORTS)

@app.route("/deregister", methods=["POST"])
def deregister():
    id = request.form.get("id")
    print(id)
    if id:
        print("id exists")
        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrants WHERE id = ?;", (id,))
        conn.commit()
        conn.close()

    return redirect("/registrants")

@app.route("/registrants")
def registrants():
    if not session.get("name") or session.get("name") != "Omoor":
        return redirect("/")
    conn = sqlite3.connect('froshims.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrants")
    columns = [column[0] for column in cursor.description]
    registrants = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return render_template("registrants.html", registrants=registrants)

@app.route("/update", methods=["GET", "POST"])
def update():
    if not session.get("id") or session.get("id") == "":
        return redirect("/login")

    if request.method == "POST":
        
        name = request.form.get("name")
        password = request.form.get("password")
        sport = request.form.get("sport")
        email = request.form.get("email")

        if not name or not password or sport not in SPORTS:
            return render_template("failure.html")

        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE registrants SET name='?', password='?', sport='?' WHERE id='?';",(name, password, sport, session.get("id"), ))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("SQLite error:", e)

        if email and email != "":
            message = Message("you updated your account!", recipients=[email])
            mail.send(message)

        session["name"] = name
        session["sport"] = sport

        return redirect("/")
    
    return render_template("update.html", sports=SPORTS)

@app.route("/search")
def search():
    conn = sqlite3.connect('froshims.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrants WHERE name LIKE ?", ('%' + request.args.get('q') + '%',))
    columns = [column[0] for column in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    registrants=str(jsonify(data).data)[2:-3]
    return registrants

@app.route("/autosearch")
def autosearch():
    return render_template("autosearch.html")
    