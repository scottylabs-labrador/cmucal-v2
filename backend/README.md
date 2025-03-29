## Directions to run the backend
First, `cd` into the backend folder 

## 1. Virtual Environment
(ignore this step if already have venv) If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv.


- Next, run the following command to activate venv
    - macOS: `source venv/bin/activate`
    - windows: `venv\Scripts\activate`

- Once activated, you can install dependencies by `pip install -r requirements.txt`, and save them by running `pip freeze > requirements.txt`

## 2. MongoDB
- Use the following code to get access to mongodb if having trouble.
    - `from app.services.db import mongo`
    - `db = mongo.cx["CMUCal"]`

## 3. Flask app
Open a terminal (in the backend folder with virtual environment), run `python run.py` to start the Flask app.

## 4. ngrok
(Ignore this section if you don't need access to clerk webhook)
- Uses ngrok expose Flask server publicly, i.e. allows the server to receive webhooks from external services directly on the local machine for testing. 
    - Create an account on ngrok, then run this in a separate terminal from the python app. You need both terminals (ngrok and the python app) open. 
    - `ngrok http --url=foxhound-true-finally.ngrok-free.app 5001`

