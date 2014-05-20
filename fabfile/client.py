""" Quicktext.io flask app """

from fabric.api import *
from fabric.contrib.files import exists

from fabtools import require, cron, files

@task
@roles('client')
def packages():
    """ Install packages needed for the client """
    
    # Require some Debian/Ubuntu packages
    require.deb.packages([
        'fswebcam',
        'python-virtualenv'
    ])

@task
@roles('client')
def install():
    execute(packages)
    home = "/home/%s/rview" % env.user

    if not exists("rview"):
        run("mkdir rview")

    with cd("rview"):
        run("virtualenv .")
        put("client/tasks.py", home)
        with prefix("source bin/activate"):
            run("pip install requests invoke")

    require.supervisor.process('rview_client',
        command='%s/bin/inv start -p bigpasswordWow' % home,
        directory=home,
        user=env.user,
        stopsignal='INT',
        stdout_logfile='%s/supervisor-rview.log' % home,
    )


@task
@roles('client')
def restart():
    """ Start the client (begin timelapse) """
    home = "/home/%s/rview" % env.user

    with cd("rview"):
        put("client/tasks.py", home)
    sudo("supervisorctl restart rview_client")
    

@task
@roles('client')
def stop():
    """ Start the client (begin timelapse) """
    sudo("supervisorctl stop rview_client")
 
