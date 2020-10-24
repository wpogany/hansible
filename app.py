from flask import Flask, render_template, redirect, url_for, request, session, g
import users
import os
import subprocess

# 3.17.60.73

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Used for signing session cookie

user_list = [users.User1, users.User2, users.User3]


# This gets executed before any other view functions are executed
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # clear the users session if they try to login againß
        session.pop('user', None)
        username = request.form.get('user_name')
        passwd = request.form.get('user_password')
        for x in user_list:
            if x.username == username and x.password == passwd:
                # If the user is successfully authenticated then redirect to protected route. This
                session['user'] = username
                return redirect(url_for('protected', username=username))
        return render_template('index.html', auth_message='Invalid Credentials')
    return render_template('index.html')


@app.route('/protected/<username>')
def protected(username):
    if g.user:
        welcome_message = f"Welcome {username}!"
        return render_template('protected.html', user_message=welcome_message)
    return redirect(url_for('index'))


@app.route('/playbook1_1/', methods=['POST'])
def playbook1_1():
    if g.user:
        run_ansible = subprocess.run(["ansible-playbook", "/etc/ansible/vault/Dugout/dug_lock.yml",
                                      "--vault-password-file", "/etc/ansible/vault/ansible_playbook_pass.txt"])
        if run_ansible.returncode == 0:
            result = 'Playbook executed successfully'
        else:
            result = 'Something went wrong'
        return render_template('protected.html', user_message=result)
    else:
        return redirect(url_for('index'))


@app.route('/logout/', methods=['POST'])
def logout():
    if g.user:
        session.pop('user', None)
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
