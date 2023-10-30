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
        sportDb = cursor.execute("SELECT sport FROM registrants WHERE name = ?", (session.get("name"),))
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
        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        isName = cursor.execute("SELECT name FROM registrants WHERE name= ?", (name,))
        conn.close()
        print(isName)
        if isName is not None and isName != []:
            session["name"] = name
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
        email= request.form.get("email")
        sport = request.form.get("sport")

        if not name or sport not in SPORTS:
            return render_template("failure.html")
    
        message = Message("you are registered!", recipients=[email])
        mail.send(message)
        conn = sqlite3.connect('froshims.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registrants (name, sport) VALUES(?, ?)", (name, sport, ))
        conn.commit()
        conn.close()
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
    