from flask import Flask , render_template , redirect , request ,url_for , flash , session
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import ForeignKey
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///notes.db"
app.config["SECRET_KEY"]= "rehman69"
db = SQLAlchemy(app)

class Notes(db.Model):
    id = db.Column(db.Integer , primary_key =True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text(500), nullable=False)
    created_at = db.Column(db.DateTime , default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class User(db.Model):
    id =db.Column(db.Integer , primary_key= True)
    username = db.Column(db.String , nullable = False , unique= True)
    password = db.Column(db.String , nullable = False)
    notes = db.relationship("Notes", backref="owner")




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login" , methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user =User.query.filter_by(username = username).first()
    if not user:
        flash ("User Does not exists")
        return redirect(url_for("home"))

    if password == user.password:
        session["username"]= username
        return redirect(url_for("dashboard"))
    return ("Invalid password")
    



@app.route("/signup-pg")
def signup_pg():
    return render_template("signup.html")


@app.route("/signup" , methods=["POST"])
def signup():
    username = request.form["sname"]
    password = request.form["spass"]
    existing_user = User.query.filter_by(username = username).first()
    if existing_user:
        flash ("Username Already Exists")
        return redirect(url_for("home"))
    new_user = User(username= username, password = password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("home"))
    username = session["username"]
    user = User.query.filter_by(username = username).first()
    notes = Notes.query.filter_by(user_id=user.id).all()
    return render_template("dashboard.html" , username=username , notes= notes)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/add-notes" , methods=["POST"])
def add_note():
    if "username" not in session:
        return redirect(url_for("home"))
    username = session["username"]
    user = User.query.filter_by(username = username).first()
    title = request.form["title"]
    content= request.form["content"]
    note = Notes(title=title , content = content , user_id = user.id)
    db.session.add(note)
    db.session.commit()
    flash("Notes Added")
    return redirect("/dashboard")


@app.route("/delete-note/<int:id>" , methods=["POST"])
def delete_note(id):
    note =Notes.query.get(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/update-note/<int:id>" , methods=["POST"])
def update_note(id):
    note = Notes.query.get(id)
    if not note:
        flash("Note not found!")
        return redirect("/dashboard")

    
    note.title = request.form["updated_title"]
    note.content = request.form["updated_content"]
    db.session.commit()
    return redirect("/dashboard")




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
