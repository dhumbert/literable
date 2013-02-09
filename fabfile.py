from fabric.api import *


def deploy():
    sudo('stop seshat')
    with cd('/var/www/seshat'):
        run('git pull')
        run('. venv/bin/activate && pip install -r requirements.txt')
    sudo('start seshat')
