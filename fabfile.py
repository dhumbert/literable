from fabric.api import *


remote_dir_to_backup = '/var/www/seshat/seshat/static/uploads/'
local_backup_dir = '/Users/dhumbert/Dropbox/Books/seshatBackup/'


def deploy(demo=False):
    path = '/var/www/seshat' if not demo else '/var/www/seshat_demo'
    app = 'seshat' if not demo else 'seshat_demo'

    sudo("stop {0}".format(app))
    with cd(path):
        run('git pull')
        run('. venv/bin/activate && pip install -r requirements.txt')
        run('. venv/bin/activate && python manage.py migrate upgrade head')
    sudo("start {0}".format(app))


def backup_locally():
    """Backup ebook and cover files from remote host to local"""
    local('rsync -r -a -v -e "ssh -l %s" --delete %s:"%s" "%s"' % (env.user, env.host, remote_dir_to_backup, local_backup_dir))


def restore_demo():
    """Restore demo data"""
    local('source setdbenv && psql -h localhost -d seshat_demo -U seshat_demo -a -f demo/demo.sql')
    local('rm -rf seshat/static/uploads')
    local('cp -R demo/uploads seshat/static')