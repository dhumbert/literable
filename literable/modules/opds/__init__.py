from flask import Blueprint

opds_module = Blueprint('opds', __name__, template_folder='templates')


import views

