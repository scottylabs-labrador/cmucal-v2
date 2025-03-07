cd into the backend folder 

1. Virtual Environment
If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv (ignore this step if already have venv).

Run the following command to activate venv
macOS: `source venv/bin/activate`
windows: `venv\Scripts\activate`

Once activated, you can install dependencies, and save them by running `pip freeze > requirements.txt`

2. MongoDB
need to run `mongod --dbpath /data/db` ?