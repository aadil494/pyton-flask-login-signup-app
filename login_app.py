"""
Simple login mechanism implemented with Flask and Flask-Sqlalchemy
1. Create new user 
2. Authenticate user
3. Send authorized user to home page

"""
import flask
import os
from flask_sqlalchemy import sqlalchemy, SQLAlchemy



# dbname here
db_name = "auth.db"

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# SECRET_KEY required for session, flash and Flask Sqlalchemy to work
app.config['SECRET_KEY'] = 'configure strong secret key here'

db = SQLAlchemy(app)


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '' % self.username


def create_db():
    """ # Execute this first time to create new db in current directory. """
    db.create_all()


@app.route("/signup/", methods=["GET", "POST"])
def signup():
    """
    Implements signup functionality. Allows username and password for new user.
    Stores username and password inside database.
    Username should to be unique else raises sqlalchemy.exc.IntegrityError.
    """

    if flask.request.method == "POST": #checks if the request method is post 
        username = flask.request.form['username'] #fetches the username
        password = flask.request.form['password'] #fetches the password

        if not (username and password): #checks if username or password is empty
            flask.flash("Username or Password Fields cannot be empty")
            return flask.redirect(flask.url_for('signup')) 
        else:
            username = username.strip() #strip spaces from username
            password = password.strip() #strip spaces from password

        new_user = User(username=username, password=password) #create a user object
        db.session.add(new_user) # add user object to the db

        try:
            db.session.commit() # commit the changes
        except sqlalchemy.exc.IntegrityError: # This will check if the username already exists in the db
            flask.flash(f"Username {username} is not available.")
            return flask.redirect(flask.url_for('signup'))

        flask.flash("Congrats !! User account has been created.")
        return flask.redirect(flask.url_for("login"))

    return flask.render_template("signup.html") 


@app.route("/", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
    """
    Provides login functionality by rendering login form on get request.
   
    """

    if flask.request.method == "POST": # checks if the method is post
        username = flask.request.form['username'] #fetches the username
        password = flask.request.form['password'] #fetches the password

        if not (username and password):
            flask.flash("Username or Password fields cannot be empty.")
            return flask.redirect(flask.url_for('login'))
        else:
            username = username.strip()
            password = password.strip()

        user = User.query.filter_by(username=username).first() # checks if the username exists in db

        if user and user.password == password: # checks the username and password 
            flask.session[username] = True
            return flask.redirect(flask.url_for("user_home", username=username))
        else:
            flask.flash("Invalid username or password.")

    return flask.render_template("login_form.html")


@app.route("/user/<username>/")
def user_home(username):
    """
    Home page for Logged in users.

    """
    if not flask.session.get(username):
        flask.abort(401)
  
    return flask.render_template("user_home.html", username=username)
@app.route("/explore/<username>/", methods=["GET", "POST"])
def explore(username):

    if not flask.session.get(username):
        flask.abort(401)
  
    return flask.render_template("explore.html", username=username)

@app.route("/logout/<username>")
def logout(username):
    """ Logout user and redirect to login page with success message."""
    flask.session.pop(username, None)
    flask.flash("successfully logged out.")
    return flask.redirect(flask.url_for('login'))


if __name__ == "__main__":
	if not os.path.isfile(f"./{db_name}"):
		create_db()
	app.run(port=5000, debug=True)
