from fabric.api import *


remote_dir_to_backup = '/srv/literable/literable/static/uploads/'
local_backup_dir = '/Users/dhumbert/Dropbox/Books/literableBackup/'


def deploy(demo=False):
    path = '/srv/literable' if not demo else '/srv/demo'
    app = 'literable' if not demo else 'demo'

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
    local('source setdbenv && psql -h localhost -d literable_demo -U literable_demo -a -f demo/demo.sql', shell='/bin/bash')
    local('rm -rf literable/static/uploads')
    local('cp -R demo/uploads literable/static')