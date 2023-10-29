from decouple import config
import re

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from cs50 import SQL

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


db = SQL("sqlite:///froshims.db")

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
        sportDb = db.execute("SELECT sport FROM registrants WHERE name = ?", session.get("name"))

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
        isName = db.execute("SELECT name FROM registrants WHERE name= ?", name)
        print(isName)
        if isName is not None and isName != []:
            session["name"] = name
            return redirect("/")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

@app.route("/deregister", methods=["POST"])
def deregister():
    id = request.form.get("id")
    if id:
        db.execute("DELETE FROM registrants WHERE id = ?", id)
    return redirect("/registrants")

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
    
        db.execute("INSERT INTO registrants (name, sport) VALUES(?, ?)", name, sport)

        session["name"] = name
        session["sport"] = sport

        return redirect("/")
    
    return render_template("register.html", sports=SPORTS)

@app.route("/registrants")
def registrants():
    if not session.get("name") or session.get("name") != "Omoor":
        return redirect("/")
    
    registrants = db.execute("SELECT * FROM registrants")
    return render_template("registrants.html", registrants=registrants)