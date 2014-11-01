from flask import render_template, request, redirect, flash
from flask.ext.login import login_user, logout_user
from literable import app, model


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = model.authenticate(request.form['username'], request.form['password'])
        if user:
            login_user(user, remember=True)
            url = request.form['next'] if 'next' in request.form else '/'
            return redirect(url)
        else:
            flash('Invalid login', 'error')
            return redirect('/login')
    return render_template('users/login.html', next=request.args.get('next'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/login')