from flask import Flask, request, render_template, session, g
from functools import wraps
import os



app = Flask(__name__)
app.secret_key = os.urandom(24)


# Attack Payload : curl 'http://localhost:5000/login-request-obj?username=mansi&password=sheth<script>alert(1)</script>'
# Template, gets  reference to request object directly
@app.route('/login-request-obj')
def login():
    user_name = request.args['username']
    password = request.args['password']
    return render_template("login.html")

# Attack Payload  : curl 'http://localhost:5000/login-parameter-passing?username=mansi&password=sheth<script>alert(1)</script>'
# Individual parameters  passed to template
@app.route('/login-parameter-passing')
def login1():
    user_name =  request.args['username']
    password = request.args['password']
    clean_data = 'admin'
    return render_template("login1.html",user_name = user_name, password = password, clean_data = clean_data)

# Attack Payload: curl 'http://localhost:5000/login-pojo?username=mansi&password=sheth<script>alert(1)</script>'
# POJO kinds being passed to template file... Common pattern once we start dealing with models.
@app.route('/login-pojo')
def login2():
    creds  = credentials(request.args['username'],request.args['password'],'clean_data')
    return render_template('login2.html',creds=creds)

def template_login(template):
    return render_template(template)


# Attack payload : curl 'http://localhost:5000/login-function?username=mansi&password=sheth<script>alert(1)</script>'
@app.route('/login-function')
def login3():
    return template_login('login4.html')

def template_or_json(template=None):
    """"Return a dict from your view and this will either
    pass it to a template or render json. Use like:

    @template_or_json('template.html')
    """
    def decorated(f):
        @wraps(f)
        def decorated_fn(*args, **kwargs):
            ctx = f(*args, **kwargs)
            return render_template(template, **ctx)
        return decorated_fn
    return decorated


# Attack Payload: curl 'http://localhost:5000/login-decorator?username=mansi&password=sheth<script>alert(1)</script>'
# Template called thru  decorator. Someone  reason  below order of decoraters  is super important
@app.route('/login-decorator')
@template_or_json('login5.html')
def login4():
    return {'username' : request.args['username']} # CWEID 80

#Attack Payload: curl 'http://localhost:5000/login-session-obj?username=sheth<script>alert(1)</script>'
@app.route('/login-session-obj')
def login5():
    session["user_name"] = request.args['username'] # tainted data
    session['admin'] = 'admin' # clean data
    return render_template('login6.html')

# Attack Payload : curl 'http://localhost:5000/login-global-object?username=sheth<script>alert(1)</script>'
@app.route('/login-global-object')
def login6():
    g.setdefault('username', request.args['username']) # Tainted data
    g.setdefault('admin', 'admin') ## Clean data set in global object
    return render_template('login7.html')

class credentials:
    username = ''
    password = ''
    clean_data = ''

    def __init__(self, username: str, password: str, clean_data : str):
        self.username = username
        self.password  = password
        self.clean_data = clean_data
