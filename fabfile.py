from fabric.api import *


remote_dir_to_backup = '/var/www/seshat/seshat/static/uploads/'
local_backup_dir = '/Users/dhumbert/Dropbox/Books/seshatBackup/'


def deploy():
    sudo('stop seshat')
    with cd('/var/www/seshat'):
        run('git pull')
        run('. venv/bin/activate && pip install -r requirements.txt')
        run('. venv/bin/activate && python manage.py migrate upgrade head')
    sudo('start seshat')


def backup_locally():
    """Backup ebook and cover files from remote host to local"""
    local('rsync -r -a -v -e "ssh -l %s" --delete %s:"%s" "%s"' % (env.user, env.host, remote_dir_to_backup, local_backup_dir))
