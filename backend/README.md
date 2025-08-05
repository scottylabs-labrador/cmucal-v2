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

## 3. Supabase
IF need to get the table schema from Supabase: in the terminal, run `sqlacodegen [SUPABASE_DB_URL from env file] --outfile models.py`
- comment out the `class Base` section in `models.py`
- add `from app.services.db import Base` to the top of `models.py`
- change all capitalized class names from plural to singular. i.e. class Events --> class Event. Don't change the lowercase names in quotes.

## 4. Course data
(ignore this unless told otherwise) IF need to scrape data from cmu schedule of classes
- first follow the instructions in the `rust` directory's README file. 
- Then, cd into the backend folder, and run `flask import-courses`

## Dev To-do
- remove `os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"` after flask app has been deployed. This is only for developmet environment.