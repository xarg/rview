""" Quicktext.io flask app """

from fabric.api import *
from fabric.contrib.files import exists

from fabtools import require, cron, files


import os

from fabric.api import *
from fabtools import require

@task
def setup():
    require.user(
        'rview',
        create_home=True,
        shell='/bin/bash',
        ssh_public_keys=[os.path.expanduser('~/.ssh/id_rsa.pub')]
    )
    require.sudoer('rview')

@task
@roles('server')
def packages():
    """ Install packages needed for the client """

    # Require some Debian/Ubuntu packages
    require.deb.packages([
        'ffmpeg',
        'mencoder',
        'python-virtualenv',
        'python-opencv',
        'golang'
    ])

@task
@roles('server')
def install():
    execute(packages)
    home = "/home/%s/rview" % env.user

    if not exists("rview"):
        run("mkdir rview")

    with cd("rview"):
        put("app.go", home)
        put("encoder/tasks.py", home)
        run("virtualenv --system-site-packages .")
        run("bin/pip install invoke python-dateutil")
        run("wget https://raw.githubusercontent.com/Itseez/opencv/master/data/haarcascades/haarcascade_frontalface_alt.xml")

    require.supervisor.process('rview_server',
        command='go run %s/app.go' % home,
        directory=home,
        user=env.user,
        stopsignal='INT',
        stopasgroup=True,
        stdout_logfile='%s/supervisor-rview_server.log' % home,
    )

    require.supervisor.process('rview_encoder',
        command='%s/bin/inv encode' % home,
        directory=home,
        user=env.user,
        stopsignal='INT',
        stdout_logfile='%s/supervisor-rview_encoder.log' % home,
    )
@task
@roles('server')
def tagboard():
    home = "/home/%s/rview" % env.user
    put("tagboard.py", home)

    require.supervisor.process('tagboard',
        command='%s/bin/python tagboard.py' % home,
        directory=home,
        user=env.user,
        stopsignal='INT',
        stdout_logfile='%s/supervisor-tagboard.log' % home,
    )
    sudo("supervisorctl restart tagboard")

@task
@roles('server')
def nginx():
    """ Install and configure nginx

    """
    home='/home/%s/rview' % env.user
    template = open(os.path.dirname(__file__) + '/rview.io').read()

    # special conf for vagrant (no ssl)
    site = 'rview.io'
    require.nginx.site(site,
        template_contents=template,
        server_alias="www.%s" % site,
        docroot=home,
        port='8000',
    )


@task
@roles('server')
def restart():
    """ Restart app.go """
    home = "/home/%s/rview" % env.user

    with cd("rview"):
        put("app.go", home)
        put("encoder/tasks.py", home)

    sudo("supervisorctl restart rview_encoder")
    sudo("supervisorctl restart rview_server")


@task
@roles('server')
def stop():
    """ Stop """
    sudo("supervisorctl stop rview_encoder")
    sudo("supervisorctl stop rview_server")

