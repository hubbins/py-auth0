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

app = Flask(__name__)
oauth = OAuth(app)

load_dotenv()

auth0 = oauth.register(
    'auth0',
    client_id=f"{os.environ.get('CLIENT_ID')}",
    client_secret=f"{os.environ.get('CLIENT_SECRET')}",
    api_base_url=f"https://{os.environ.get('DOMAIN')}",
    access_token_url=f"https://{os.environ.get('DOMAIN')}/oauth/token",
    authorize_url=f"https://{os.environ.get('DOMAIN')}/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
)
