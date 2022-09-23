# Librusik

Simple, fast, dark-themed Librus web client with some cool features.

Runnable even on RPi 1B.

![screenshot](https://gitlab.com/dani3l0/librusik/-/raw/stable/screenshots/librusik-2.png)

-----

## Features

### Librus:

- Grades (with Librus-independent average calculation)

- Timetable

- Messages (preview only)

- Presences & Absences (with frequency %% calculation)

- Exams

- School free days

- Teacher free days

- Parent-teacher conferences

- About school


### Client:

- Dark theme

- Cookies (Browser will remember you for 28 days)

- Grades cleanup (Removes subjects without grades from Grades page)

- Average predictor (Edit final grades in average screen to predict your final average)

- Cool countdown meters on home screen

- _Something happens at papieżowa_

-----

## Installation

This app __will not run on Windows__. And no support for it, ever.
I used Debian 11 (and previously 10) for a couple of years and everything was pretty fine.

__1. Install python3 dependencies (multiple ways to do it):__

- via pip:
```
pip install bs4 aiohttp cryptography
```

- or via distro packages:
```
apt install python3-bs4 python3-aiohttp python3-cryptography
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

Also, check [localhost:7777/panel](http://localhost:7777/panel) to manage your Librusik instance. Default user is `admin` and password is `admin` too.

-----

## Some other words

Because this was my first app written in Python, code quality is quite meh. Don't expect code to be super readable and flexible.

_It just works_
