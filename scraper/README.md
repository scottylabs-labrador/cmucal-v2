To use, first create a virtual environment: `python3 -m venv <myenvname>`

Then activate it:

On windows: `.\env\Scripts\activate.bat`
On mac: `source venv/bin/activate`

Then install needed packages: `pip3 install -r requirements.txt`

Then create a file `config.ini` that contains the link to the MONGO database in the format seen in `config.ini.example`.

Then launch the scraper: `python3 main.py`

--------

Updates for the future:
- fix peertutoring cause they switched from the login method to SSO one, breaking the whole scraper...
- improve the Handshake/TC mechanisms to automatically update login cookie information cause it is static at the moment
- might need to abstract "resource_source" out of each scraper file so it's not one to one (i.e. one scraper file like OfficeHoursScraper can query 5 different google calendars, and write to 5 different resource sources. this would
involve updating the update_database function slightly )
- more office hours
- write a backend in flask that connects with mongo and returns a list of events given filters (will also expand out reoccurring events for whole semester)