from flask import Flask, abort, render_template, redirect, url_for, request, make_response
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user
from urllib.parse import urlparse, urljoin
import requests, tableauserverclient as TSC
from secret import SECRET_KEY, TABLEAU_AUTH, USERS_LIST, PASSWORD_LOGIN
app = Flask(__name__)
app.secret_key = SECRET_KEY
login_manager = LoginManager(app)
users = USERS_LIST
password_login = PASSWORD_LOGIN

server = TSC.Server('http://10.0.55.1')
folder_path = "C:/Users/Administrator/Desktop/Flask-WebServer/static/images"

# Class User which extends UserMixin used to register users.5765
class User(UserMixin):
    # Constructor
    def __init__(self, user_id):
        self.id = user_id
        self.name = users[int(user_id)]

    def get(self, name):
        return users.index(name)
# Check if url to render is safe
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

# Route for handling the login page logic
# Checks if user exists and password matches
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if (request.method == 'POST'):
        if (request.form['username'] not in users or request.form['password'] != password_login):
            error = 'Invalid Credentials. Please try again.'
        else:
            user = User(users.index(request.form['username']))
            login_user(user)
            next = request.args.get('next')

            if not is_safe_url(next):
                return abort(400)

            resp = make_response(redirect('/homepage'))

            resp.set_cookie('username', request.form['username'])
            return resp
    return render_template('login.html', error=error)


# Used to by Flask to check which is the current logged user.
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Route to redirect - when the onload event occurs - to the login page directly
@app.route("/")
def hello():
    return redirect(url_for('login'))

@app.route("/homepage")
@login_required
def homepage(): #index with all the dashboards
    with server.auth.sign_in(TABLEAU_AUTH):
        workbooks, pagination_item = server.workbooks.get()
               
        wblist = [wb for wb in workbooks]
        for x in wblist:      
            server.workbooks.populate_preview_image(x)
            if x.project_name == "yourWorkspace":
                with open(folder_path  + "/{}.jpg".format(x.name), "wb") as img_file:   #generate thumbnails of all dashboards
                    img_file.write(x.preview_image)
    return render_template("select-dashboard.html")

@app.route("/dashboard")    #page of a single dashboard
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/logout')
def sign_out():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get_token')
def get_token():
    resp = make_response()

    token = requests.post("http://10.0.55.1/trusted?username=" + request.cookies.get("username"))
    if (token.status_code != 200 or token.text == '-1'): #200 = OK in HTTP requests
        return abort(400)

    resp.set_cookie("auth_token", token.text)
    return resp

if __name__ == "__main__":
    app.run(debug=True)
