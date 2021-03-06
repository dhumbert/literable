import json
from functools import partial
from flask import render_template, request, redirect, url_for, flash, Response, abort
from flask.ext.login import login_required, current_user
from literable import app, model, content_type


@app.route("/ajax/users")
@content_type("application/json")
@login_required
def other_users():
    users = []
    for u in model.get_users():
        users.append({'id': u.id, 'name': u.username})

    return json.dumps(users)
