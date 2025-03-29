cd into the backend folder 

1. Virtual Environment
(ignore this step if already have venv) If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv.

- Run the following command to activate venv
    - macOS: `source venv/bin/activate`
    - windows: `venv\Scripts\activate`

- Once activated, you can install dependencies, and save them by running `pip freeze > requirements.txt`

2. MongoDB
- Use the following code to get access to mongodb if having trouble.
    - `from app.services.db import mongo`
    - `db = mongo.cx["CMUCal"]`

3. ngrok
- Uses ngrok expose Flask server publicly, i.e. allows the server to receive webhooks from external services directly on the local machine for testing. 
- Ignore the following directions if you don't need access to clerk webhook: 
    - Create an account on ngrok, then run this in a separate terminal from the python app. You need both terminals (ngrok and the python app) open. 
    - `ngrok http --url=foxhound-true-finally.ngrok-free.app 5001`