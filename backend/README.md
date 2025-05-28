## Directions to run the backend
First, `cd` into the backend folder 

## 1. Virtual Environment
(ignore this step if already have venv) If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv.


- Next, run the following command to activate venv
    - macOS: `source venv/bin/activate`
    - windows: `venv\Scripts\activate`

- Once activated, you can install dependencies by `pip install -r requirements.txt`, and save them by running `pip freeze > requirements.txt`
- If you encounter an error with psycogp2, run `brew install postgresql` first.

## 2. Flask app
Open a terminal (in the backend folder with virtual environment), run `python run.py` to start the Flask app.

## Dev To-do
- remove `os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"` after flask app has been deployed. This is only for developmet environment.