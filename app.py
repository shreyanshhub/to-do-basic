from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite3"
app.config["SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS"] = False
app.secret_key = "todo"

db =  SQLAlchemy(app)

class User(db.Model):

    id = db.Column("id",db.Integer,primary_key=True)
    username = db.Column("username",db.String(100))
    password = db.Column("password",db.String(100))
    notes = db.relationship("Note",backref="user")

    def __init__(self,username,password):

        self.username = username
        self.password = password

class Note(db.Model):

    id = db.Column("id",db.Integer,primary_key=True)
    note_id = db.Column("note_id",db.Integer,db.ForeignKey("user.id"))
    notes = db.Column("notes",db.String(10000))


@app.route("/",methods=["GET","POST"])
def home():
    return render_template("home.html")


@app.route("/dashboard",methods=["GET","POST"])
def dashboard():

    if "username" in session:
        username = session["username"]
        user = User.query.filter_by(username=username).first()
        return render_template("index.html",user=user)

    else:

        return redirect(url_for("home"))

@app.route("/add_task/",methods=["GET","POST"])
def add_task():

    if request.method == "POST":

        notes = request.form["notes"]
        username = session["username"]

        user = User.query.filter_by(username=username).first()

        note = Note(notes=notes,user=user)

        db.session.add(note)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("add.html")

@app.route("/register",methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user:
            flash("Username already exists")
            return render_template("register.html")

        else:

            user = User(username=username,password=password)

            flash("User registered successfully")
            db.session.add(user)
            db.session.commit()

            return redirect(url_for("login"))

    if "username" in session:
        flash("User already logged in")
        return redirect(url_for("dashboard"))

    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username,password=password)

        if user:
            session["username"] = username
            flash("User logged in successfully")

            return redirect(url_for("dashboard"))

        else:

            flash("Incorrect username or password")

            return render_template("login.html")


    if "username" in session:
        flash("User already logged in")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout",methods=["GET","POST"])
def logout():

    if "username" in session:

        session.pop("username",None)
        return redirect(url_for("home"))

    return redirect(url_for("home"))


@app.route("/delete_task/<id>",methods=["GET","POST"])
def delete_note(id):

    if request.method == "POST":

        username = session["username"]
        user = User.query.filter_by(username=username).first()
        note = Note.query.filter_by(id=id,user=user).first()

        db.session.delete(note)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("delete.html")


if __name__ == "__main__":

    with app.app_context():

        db.create_all()
        app.run(debug=True)
