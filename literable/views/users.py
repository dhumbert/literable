import json
from functools import partial
from flask import render_template, request, redirect, url_for, flash, Response, abort
from flask.ext.login import login_required, current_user
from literable import app, model, content_type


@app.route("/ajax/users")
@content_type("application/json")
@login_required
def other_users():
    # todo fetch from DB and do not include self
    return json.dumps([{'id': 1, 'name': 'Devin'}])