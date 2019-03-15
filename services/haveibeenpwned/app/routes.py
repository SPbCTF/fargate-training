from flask import render_template, session, request, redirect, flash, url_for
from app import app
from app.models import User, Breach
from app.forms import LoginForm, RegistrationForm, AddPassword
from app.handlers import generate_password


@app.route("/")
@app.route("/index", methods=['GET', 'POST'])
def index():
    if 'username' in session:
        auth = True
    else:
        auth = False
    status = {
        "request": False,
        "status": False
    }
    res = []
    if request.method == 'POST':
        status["request"] = True
        account = request.form.get("Account", "")
        print("Requested account: " + account)
        res = Breach.check_account(account)
        if len(res) == 0:
            status["status"] = False
        else:
            status["status"] = True

    return render_template("index.html", status=status, passwords=res, auth=auth)

@app.route("/users")
def users():
    if 'username' in session:
        auth = True
    else:
        auth = False
    res = User().get_users()
    return render_template('users.html', users=res, auth=auth)

# @app.route("/breach")
# def breach():
#     if 'username' in session:
#         auth = True
#     else:
#         auth = False
#     res = Breach.get_breached_accounts()
#     return render_template('breach.html', emails=res, auth=auth)

@app.route("/logout")
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect('/index')

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect("/private")
    else:
        auth = False
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        check = User.check_user(username, password)
        if not check:
            flash("Invalid username or password")
            return redirect(url_for('login'))
        session['username'] = username
        next_page = request.args.get("next")
        print(session['username'])
        if not next_page:
            next_page = url_for("private")
        return redirect(next_page)
    return render_template('login.html', form=form, auth=auth)

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'username' in session:
        return redirect("/private")
    else:
        auth = False
    form = RegistrationForm()
    if request.method=="POST":
        if form.validate_on_submit():
            filled_form = {}
            for each in request.form:
                if not each=='csrf_token' or each=='submit':
                    filled_form [each] = request.form[each]
            filled_form ['password'] = generate_password(filled_form ['username'], filled_form ['email'])
            flash("Your login:password pair: ")
            flash(filled_form ['username']+" : "+filled_form ['password'])
            User.add_user(filled_form)
    return render_template('register.html', form=form, auth=auth)

@app.route("/private", methods=["GET", "POST"])
def private():
    if not 'username' in session:
        return redirect("/login")
    form = AddPassword()
    if form.validate_on_submit():
        account = form.account.data
        password = form.password.data
        if Breach.add_breach(account, password, session['username']):
            flash("Added successfully")
        else:
            flash("Some error occurred")
    accounts = Breach.get_submitted_breachs(session['username'])
    return render_template('private.html', form=form, auth=True, accounts=accounts)
