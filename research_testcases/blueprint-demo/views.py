from flask import Blueprint, request, render_template

bp = Blueprint('auth',__name__)

# Attack Payload : curl 'http://localhost:5000/login-bp-request?name=Mansi<script>alert(1)</script>'
@bp.route('/login-bp-request')
def login():
    return render_template('login.html')

