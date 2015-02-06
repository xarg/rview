import time
import os
import socket
from datetime import datetime

import requests
from invoke import run, task

PHOTOS = "photos"

@task
def start(ctype="cam", url="http://rview.io/upload", username=socket.gethostname(), password='', interval=60, directory=PHOTOS):
    """Start timelapse
    
    `interval` - in seconds 

    """
    if ctype == 'cam':
        cmd = "fswebcam --no-banner -r 1920x1080 %s"
    elif ctype == 'still':
        cmd = "raspistill --rotation 270 -o %s"
    
    while True:
        files = {}
        try:
            run("mkdir -p photos")
            imagename = os.path.join(directory, "%s.jpg" % datetime.utcnow().isoformat())
            run(cmd % imagename)

            count = 0
            for imagefile in os.listdir(directory):
                files[imagefile] = open(os.path.join(directory, imagefile), "rb")
                print("Uploading %s" % imagefile)
                count += 1
                if count == 20: # don't try to upload many files at one time
                    break

            res = requests.post(url, files=files, auth=(username, password))
            if res.status_code != 200:
                print res
            else:
                for filename, fd in files.copy().items():
                    fd.close()
                    os.unlink(os.path.join(directory, filename))
                    del files[filename]
        finally:
            for filename, fd in files.items():
                fd.close()
            time.sleep(interval)
