package main

import (
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path"
	"strings"
)

// Returns the username and password provided in the request's
// Authorization header, if the request uses HTTP Basic Authentication.
// (See RFC 2617, Section 2)
func basicAuth(r *http.Request) (username string, password string, err error) {
	auth := r.Header.Get("Authorization")
	if auth == "" {
		return "", "", errors.New("no Authorization header")
	}
	return parseBasicAuth(auth)
}

// Parses an HTTP Basic Authentication string.
// "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==" returns ("Aladdin", "open sesame", nil).
func parseBasicAuth(auth string) (username, password string, err error) {
	s1 := strings.SplitN(auth, " ", 2)
	if len(s1) != 2 {
		return "", "", errors.New("failed to parse authentication string")
	}
	if s1[0] != "Basic" {
		return "", "", fmt.Errorf("authorization scheme is %v, not Basic", s1[0])
	}
	c, err := base64.StdEncoding.DecodeString(s1[1])
	if err != nil {
		return "", "", errors.New("failed to parse base64 basic credentials")
	}
	s2 := strings.SplitN(string(c), ":", 2)
	if len(s2) != 2 {
		return "", "", errors.New("failed to parse basic credentials")
	}
	return s2[0], s2[1], nil
}

//uploadHandler - used
func uploadHandler(w http.ResponseWriter, r *http.Request) {
	username, password, err := basicAuth(r)

	if err != nil {
		http.Error(w, err.Error(), http.StatusForbidden)
		return
	}

	if password != "bigpasswordWow" {
		http.Error(w, "Incorrect password", http.StatusForbidden)
		return
	}

	switch r.Method {
	//GET displays the upload form.
	case "GET":
		fmt.Fprintf(w, "Upload something!")

		//POST takes the uploaded file(s) and saves it to disk.
	case "POST":
		//get the multipart reader for the request.
		reader, err := r.MultipartReader()

		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		//copy each part to destination.
		for {
			part, err := reader.NextPart()
			if err == io.EOF {
				break
			}

			//if part.FileName() is empty, skip this iteration.
			if part.FileName() == "" {
				continue
			}

			// some cleanup
			targetDir := strings.Replace(username, "/", "", -1)
			targetDir = path.Clean(targetDir)
			cwd, _ := os.Getwd()
			targetDir = path.Join(cwd, "static", targetDir)

			err = os.MkdirAll(targetDir, 0777)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			// filename cleanup
			fileName := part.FileName()
			fileName = strings.Replace(fileName, "/", "", -1)
			fileName = path.Clean(fileName)

			targetPath := path.Join(targetDir, fileName)

			dst, err := os.Create(targetPath)
			defer dst.Close()

			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			if _, err := io.Copy(dst, part); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			log.Printf("Saved: %s\n", fileName)
		}
		//display success message.
		fmt.Fprintf(w, "Upload succesful.")
	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
	}
}

var addr = flag.String("addr", ":8000", "http service address")

func main() {
	flag.Parse()

	http.HandleFunc("/upload", uploadHandler)
	log.Println("Listening on", *addr)
	http.ListenAndServe(*addr, nil)
}
