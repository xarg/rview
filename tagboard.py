import requests
import os
import smtplib
import time
import traceback

hashtags =  {
        'gymglishparty': 'https://post-cache.tagboard.com/search/gymglishparty?count=50',
        'gymglish': 'https://post-cache.tagboard.com/search/gymglish?count=50'
}

old_path = "/tmp/tagboard-%s.json"

def main():
    while True:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls() 

            for hashtag, url in hashtags.items():
                old_tagboard = ""
                if os.path.exists(old_path % hashtag):
                    old_tagboard = open(old_path % hashtag).read()

                res = requests.get(url)
                                     
                if res.content != old_tagboard:
                    print "Changed!"
                    #send e-mail, save to disk
                    
                    #Next, log in to the server
                    server.login("plugaru@a9group.com", "septolete13")

                    #Send the mail
                    msg = "subject:New post in #{0}\r\n\r\n\r\nYo! There is a new post on tagboard here: https://tagboard.com/{0}/".format(hashtag) 
                    server.sendmail("alexandru@gymglish.com", "adsoullier+tagboard@gmail.com,alexandru+tagboard@gymglish.com,andrew.arnon+tagboard@gmail.com", msg) 
                    with open(old_path % hashtag, 'w') as fd:
                        fd.write(res.content)
        except:
            traceback.print_exc()
        finally:
            time.sleep(60)

if __name__ == "__main__":
    main()
