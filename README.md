<img src="screenshots/librusik.png" alt="Status" width="600"/>

## Features

### Librus Synergia:

📋 Grades (with independent average calculation - works even if school has disabled it)

🗓️ Timetable

✉️ Messages (with downloading attachments) (outgoing messages are unsupported)

✅ Presences & Absences (with per-semester per-subject frequency %% calculation)

✏️ Exams

🏠 School free days

🧑‍🏫 Teacher free days

👪 Parent-teacher conferences

🏫 About school


### Client (Librusik UI):

🌙 Dark theme

🍪 Cookies (you won't be logged out each time you close the browser)

🧹 Grades cleanup (removes subjects without grades from Grades page)

🔮 Average predictor (edit final grades in average screen to predict your final average)

⌛ Cool countdown meters on home screen

🎉 Party mode

✨ ...and many more!

-----

## Installation

This app __will not run on Windows__. And no support for it, ever.
I used Debian 11 (and previously 10) for a couple of years and everything was pretty fine.

__1. Install required dependencies:__

- via pip:
```
pip install -r requirements.txt
```


__2. Clone the repo:__
```
git clone https://gitlab.com/dani3l0/librusik Librusik
cd Librusik
```

__3. And, finally run it:__
```
python3 librusik.py
```

__4. Done! Librusik is now running at [localhost:7777](http://localhost:7777).__

-----

## Configuration

Edit `config.json` file and adjust your preferences.

You may also want to set up your custom encryption key (which encrypts our Librus Synergia passwords). Please run `generate_random_key.py` and paste the new key into `fernet.key`. Don't forget to `chmod 400 fernet.key`. 

You can use [localhost:7777/panel](http://localhost:7777/panel) to manage your Librusik instance. Default user is `admin` and password is `admin`.

-----

## Some other words

Because this was my first app written in Python, code quality is quite meh. Don't expect code to be super readable and flexible.

_It just works_
