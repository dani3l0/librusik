<img src="screenshots/librusik.png" alt="Preview photo" width="600"/>

**As I am graduating from school this year, after May 2023 I will lose access to Librus.**

## Features

### Librus Synergia:

📋 Grades (with independent average calculation - works even if school has disabled it)

🗓️ Timetable

✉️ Messages (with downloading attachments) (outgoing messages are unsupported)

✅ Presences & Absences (with per-semester per-subject frequency %% calculation)

✏️ Exams (with countdown to next one)

🏠 School free days (with countdown to next holiday)

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

**WARNING:** If you update your existing Librusik installation be careful, as our pseudo-database structure might change. Missing database entries will lead to app crash. So, **always do a backup before updating.**. Config changes won't crash the app.

__1. Clone the repo:__
```
git clone https://gitlab.com/dani3l0/librusik Librusik
cd Librusik
```

__2. Install required dependencies:__

```
pip install -r requirements.txt
```

__3. And, finally run it:__
```
python3 librusik.py
```

__4. Done! Librusik is now running at [localhost:7777](http://localhost:7777).__

-----

## Configuration

Librusik will generate `data` dir upon its first boot. You can edit `data/config.json` file and adjust the preferences to your liking. Some of them can be set from Panel.

Go to [localhost:7777/panel](http://localhost:7777/panel) to manage your Librusik instance. Default user is `admin` and password is `admin`.

**Config keys explained:**

`enable_registration` - enable registration of new users

`max_users` - how many users can be registered on your instance

`name` - an username required to log into Panel

`passwd` - SHA-256 hashed password for Panel

`port` - HTTP port Librusik is listening on

`subdirectory` - an absolute path for running under reverse proxy (like nginx), I guess it's still broken

`readable_db` - if set to `true`, database contents will be stored as multi-line, human-readable JSON (results will appear upon first database change)

`ssl` - whether to enable HTTPS or not

`pubkey` - path to public key used for HTTPS

`privkey` - path to private key used for HTTPS

`contact_uri` - URI (a link) where user can contact with you. As it's passed directly to `a` HTML element, values can be like `mailto:`, `tel:`, `https://`, `tg://`, `mumble://` etc. This will be shown in About page and Tiers (if enabled)

`enable_tiers` - when `true`, Librusik will show a special UI for managing available features for each user.

`tiers_text` - a bottom text shown below tier list in _Settings -> Upgrade tier_.

`tiers_requirements` - a list of requirements for each tier. Those will be shown under _Settings -> Upgrade tier_.

`debug` - enables/disables some verbose information (like aiohttp exceptions) and stuff related to debugging.


-----

## Tiers

Tiers is a per-user feature management system that can be used to prevent random people from using your instance. Well, I'm not sure why did I implement this.

With this, users can be classed in a different categories:

- `DEMO` - Default for new users. Has access to all features available in `PRO` for 7 days. After this period, all features become unavailable and tier upgrade is required to continue using Librusik.

- `FREE` - all basic features are available like grades, timetable, free days etc. It has no time limit.

- `PLUS` - includes some extra features, like per-subject average calculation, countdowns in Exams & Free days and a possibility to list & read messages.

- `PRO` - has access to all implemented features available in Librusik. Those include final average calculation, AttendancesExtendedUI and message attachments.

-----

## Querying the API

In `tools` dir there is a `dump_full_api.py` file. It queries the whole Librus API and saves all the available data to local JSON file. Kinda helpful for further development or some research.

-----

## Reporting a bug

Feel free to open new issues when something doesn't work or you want to ask for new features/improvements.

If you encounter a bug, remember to attach some logs (exception traceback or just a detailed description).

**After May 2023, only merge requests will be accepted.**

-----

## Some other words

Because this was my first app written in Python, code is a terrible mess. Don't expect it to be super readable and flexible.

_It just works_ (It actually worked since 2020 xD)
