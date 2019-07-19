# n100m-reviews
DS hackathon

### Setup Instructions

1. Clone git repo

2. ``$ pip install -requirements.txt``

3. Copy model binary to models folder in repo (or change MODELPATH in webapp/config.py)

4. cd into webapp, run 
```$ python app.py```


###  For testing API:

POST call to http://localhost:5000/api/language/

```Content-Type: application/json```

Request body will be 
```json
{
    "entityText" : "<review>",
    "threshold" :  50
}
```