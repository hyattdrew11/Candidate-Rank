#!
from flask import Flask
from flask import render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask import Flask
from redis import Redis
import rq

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_pyfile('config.py')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)

DB_URL = app.config['DB_URL']

# REDIS IMPLEMENTAIOTN NAMESPACE
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('tasks', connection=app.redis)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/home')
def index():
    return render_template('index.html', title='Home',)

from server.api.auth import mod
app.register_blueprint(mod, url_prefix="/api/auth")

from server.api.dashboard import mod
app.register_blueprint(mod, url_prefix="/api/dashboard")

from server.api.organization import mod
app.register_blueprint(mod, url_prefix="/api/organization")

from server.api.candidate import mod
app.register_blueprint(mod, url_prefix="/api/candidate")

from server.api.survey import mod
app.register_blueprint(mod, url_prefix="/api/survey")


