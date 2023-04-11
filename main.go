package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/lambda"
	"github.com/aws/aws-sdk-go-v2/service/lambda/types"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

var lambdaClient *lambda.Client
var s3Client *s3.Client

const (
	funcName     = "ccpproj-2"
	inputBucket  = "cse546proj3-input"
	outputBucket = "cse546proj3-output"
)

type S3Event struct {
	Detail struct {
		Bucket `json:"bucket"`
		Object `json:"object"`
	} `json:"detail"`
}

type Bucket struct {
	Name string `json:"name"`
}

type Object struct {
	Key string `json:"key"`
}

type Records struct {
	S3 `json:"s3"`
}

type Events struct {
	Recs []Records `json:"Records"`
}

func addAuth(handler http.HandlerFunc) http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		user, pass, ok := r.BasicAuth()
		if ok && user == "abc" && pass == "def" {
			handler.ServeHTTP(w, r)
			return
		}

		log.Println(user, pass)
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
	})
}

type S3 struct {
	Bucket `json:"bucket"`
	Object `json:"object"`
}

func Eventhandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var event S3Event

	data, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Println("Error occured while reading request body", err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	log.Println(string(data))

	if err := json.Unmarshal(data, &event); err != nil {
		log.Println("Error while decoding json data", err.Error())
		return
	}

	log.Printf("Received event Bucket: %s, Object: %s\n", event.Detail.Bucket.Name, event.Detail.Object.Key)

	if event.Detail.Bucket.Name == inputBucket {
		name := funcName
		data, err := json.Marshal(Events{
			Recs: []Records{
				{S3: S3{event.Detail.Bucket, event.Detail.Object}},
			},
		})

		if err != nil {
			log.Println("Unable to make json")
			w.WriteHeader(http.StatusInternalServerError)
			return
		}

		log.Println(string(data))
		params := lambda.InvokeInput{
			FunctionName:   &name,
			InvocationType: types.InvocationTypeEvent,
			Payload:        data,
		}

		if _, err := lambdaClient.Invoke(r.Context(), &params); err != nil {
			log.Println("Error while invoking lambda function", err.Error())
			w.WriteHeader(http.StatusInternalServerError)
			return
		}

		log.Println("Lambda invoked successfully!")
		w.WriteHeader(http.StatusOK)
	} else if event.Detail.Bucket.Name == outputBucket {
		res, err := s3Client.GetObject(r.Context(), &s3.GetObjectInput{
			Bucket: &event.Detail.Bucket.Name,
			Key:    &event.Detail.Object.Key,
		})
		if err != nil {
			log.Println("Error getting object from bucket")
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		defer res.Body.Close()

		var output []byte
		_, err = res.Body.Read(output)
		if err != nil {
			log.Println("Error reading s3 response body")
			w.WriteHeader(http.StatusInternalServerError)
			return
		}

		log.Printf("Output for image: %s is %s\n", event.Detail.Object.Key, string(output))
		w.WriteHeader(http.StatusOK)
	} else {
		w.WriteHeader(http.StatusBadRequest)
	}
}

func runServer(addr string, port int) {

	http.HandleFunc("/", addAuth(Eventhandler))

	log.Printf("starting server at %s:%d\n", addr, port)
	http.ListenAndServe(fmt.Sprintf("%s:%d", addr, port), nil)
}

func main() {
	var port int
	var addr string

	flag.IntVar(&port, "p", 12500, "Provide a port number")
	flag.StringVar(&addr, "addr", "0.0.0.0", "Provide an address to host server")
	flag.Parse()

	// aws config
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatalf("Unable to load SDK config %v\n", err)
	}

	lambdaClient = lambda.NewFromConfig(cfg)
	s3Client = s3.NewFromConfig(cfg)

	runServer(addr, port)
}
