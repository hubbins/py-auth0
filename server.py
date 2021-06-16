from functools import wraps
import json
from os import environ as env
import os
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

load_dotenv()

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = f"{os.environ.get('SECRET_KEY')}"
oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    client_id=f"{os.environ.get('CLIENT_ID')}",
    client_secret=f"{os.environ.get('CLIENT_SECRET')}",
    api_base_url=f"https://{os.environ.get('DOMAIN')}",
    access_token_url=f"https://{os.environ.get('DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.environ.get('DOMAIN')}/authorize",
    client_kwargs={
        "scope": "openid profile email",
    },
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    access_token = auth0.token.get("access_token")
    id_token = auth0.token.get("id_token")

    session["access_token"] = access_token
    session["id_token"] = id_token

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://localhost:3000/callback',
        audience=os.environ.get("AUDIENCE"))

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': f"{os.environ.get('CLIENT_ID')}"}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))
