# Librusik

Simple, fast, dark-themed Librus web client with some cool features.


### Features

##### Librus:

- Grades (with Librus-independent average calculation)

- Timetable

- Messages (preview only)

- Presences & Absences (with frequency %% calculation)

- Exams

- School free days

- Teacher free days

- Parent-teacher conferences

- About school


##### Client:

- Dark theme

- Cookies (Browser will remember you for 28 days)

- Grades cleanup (Removes subjects without grades from Grades page)

- Average predictor (Edit final grades in average screen to predict your final average)

- Cool countdown meters on home screen

- _Something happens at papieżowa_


### Installation

This app __will not run on Windows__. And no support for it, ever.
I used Debian 11 (and previously 10) for a couple of years and it was pretty stable.

1. Install python3 dependencies (via pip or distro packages):
```
bs4 aiohttp cryptography
```

2. Clone the repo:
```
git clone https://gitlab.com/dani3l0/librusik Librusik
cd Librusik
```

3. And, finally run it:
```
python3 librusik.py
```

4. Done! Librusik is now running at localhost:7777.


### Configuration

Edit `config.json` file and adjust your preferences.

Also, check localhost:7777 to manage your Librusik instance. Default user is `admin` and password is `admin` too.



