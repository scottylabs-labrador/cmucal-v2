## Directions to run the backend
First, `cd` into the backend folder 

1. Virtual Environment
(ignore this step if already have venv) If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv.

    - Run the following command to activate venv.
        - macOS: `source venv/bin/activate`
        - windows: `venv\Scripts\activate`

    - Once activated, you can install dependencies, and save them by running `pip freeze > requirements.txt`

2. MongoDB (ignore this section for now)
    - need to run `mongod --dbpath /data/db` ?

3. To run the flask app: `python run.py`