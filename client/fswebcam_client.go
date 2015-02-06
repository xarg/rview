package main

import (
	"bytes"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"time"
)

const (
	URL      = "http://rview.io/upload"
	INTERVAL = time.Second * 60
	PASSWORD = "bigpasswordWow"
)

func uploadFiles() {

}

func main() {
	// create a dir to store the images

	user, _ := os.Hostname()
	err := os.MkdirAll("photos", 0777)
	if err != nil {
		log.Fatal(err)
	}

	for {
		imageName := fmt.Sprintf("photos/%s.jpg", time.Now().UTC())
		cmd := exec.Command("fswebcam --no-banner -r 1920x1089 ", imageName)
		err = cmd.Run()
		if err != nil {
			log.Print(err)
		}

		uploadFiles()
	}
}
