import os
from os import listdir
from os.path import join
import time
import traceback
import logging

from invoke import run, task
import dateutil.parser
import cv2

logging.basicConfig()
logger = logging.getLogger("tasks")

MEDIA_PATH = join(os.path.dirname(__file__), "static")
ENCONDE_CMD = "mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 %(options)s -o %(out)s.avi -mf type=jpeg:fps=%(fps)d mf://@frames.txt"

def sort_by_date(filename):
    datestr, ext = os.path.splitext(os.path.basename(filename))
    return dateutil.parser.parse(datestr)

def detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("./haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.1, 6, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img 

def blur(rects, img, dst):
    result_image = img.copy()

    for x1, y1, x2, y2 in rects:
        # Get the origin co-ordinates and the length and width till where the face extends
        # get the rectangle img around all the faces
        #cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)

        sub_face = img[y1:y2, x1:x2]

        # apply a gaussian blur on this new recangle image
        sub_face = cv2.medianBlur(sub_face, 53)

        # merge this blurry rectangle to our final image
        result_image[y1:y1+sub_face.shape[0], x1:x1+sub_face.shape[1]] = sub_face
    cv2.imwrite(dst, result_image); 

def modify(src, dst):
    """ Given a source and a destination image path try to blur using opencv"""
    run("cp %s %s" % (src, dst))

    #rects, img = detect(src) 
    #blur(rects, img, dst)

@task
def encode():
    """ Create a timelapse """

    stream_path = join(MEDIA_PATH, "streams")
    if not os.path.exists(stream_path):
        os.makedirs(stream_path)

    # where the modified pictures are
    modified_path = join(MEDIA_PATH, "_modified")
    if not os.path.exists(modified_path):
        os.makedirs(modified_path) 

    while True:
        try:
            for stream in listdir(MEDIA_PATH):
                # create stream path if it doesn't exist yet
                if stream != "streams" and stream != '_modified':
                    modified_stream = join(modified_path, stream) 
                    if not os.path.exists(modified_stream):
                        os.makedirs(modified_stream)
                    modified_images = listdir(modified_stream) 

                    image_dir = join(MEDIA_PATH, stream)
                    for image in listdir(image_dir):
                        original_image_path = join(image_dir, image)
                        modified_image_path = join(modified_stream, image)
                        if image not in modified_images:
                            # modify image with copy
                            modify(original_image_path, modified_image_path)

                    photos = listdir(modified_stream)
                    photos = [join(modified_stream, p) for p in photos]
                    photos = sorted(photos, key=sort_by_date)
                    with open("frames.txt", "w+") as fd:
                        fd.write("\n".join(photos))
                    output_path = join(stream_path, stream)
                    options = ""
                    if stream == 'iphone4s':
                        options = "-flip"
                    encode_cmd = ENCONDE_CMD % {
                        'fps': 24,
                        'out': output_path,
                        'options': options
                    }
                    run(encode_cmd)
        except Exception as e:
            traceback.print_exc()
        finally:
            time.sleep(90)
