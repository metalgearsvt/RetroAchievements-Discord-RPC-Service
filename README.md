# My changes
- Fixed issues where the RA presence message can exceed the Discord presence limit, and will attempt to truncate first.
- Changed the presence to show the game title as what you are playing.
- Changed to also include "Playing on AYN Thor"
- Will always run, and exit after not seeing you play for 4 min+.
- Added timestamps to logging.
- Added some logging.
- Added better crash handling and API calls as to not hammer the RA servers as much.

# RetroAchievements Discord Presence: Improved Improved
## Features:
- The game icon is displayed on the Discord's RP.
- The console currently being played is also displayed.
- Hovering over the game icon displays the user's overall achievements status about the current game. _(e.g "31 of 138 achieved | 22 %")_
- Displays the user's story progress percentage at the last part of the rich presence message about the current game. _(e.g "...some rich presence message | Story Progress: 48 %")_  
- A first button that redirects to the user's RA profile. _(Don't worry, I made an option to turn this off)_
- If the username display is turned off, the first button will have the link of the RetroAchievements website instead.
- A second button that redirects to the current game info inside the RetroAchievements website. 
- Discord's Rich Presence will get cleared after you stopped playing for 5 minutes (default). _(You can modify this duration inside the `config.ini` file)_
- Optimized game title.
- Optimized game status.
<hr>

## Instructions (Running it as a Python file)
1. Install Python. _(It works currently at version 3.13.1)_
2. Run `cmd` and ensure that python is installed correctly by entering this command `py --version`.
3. Run the command, `py -m pip install -r requirements.txt`. Make sure that you're running this command in this directory.
4. Open Discord App. (_NOTE: Discord App should always be opened first before running the `run.bat` file._)
5. Go to Discord > User Settings > Activity Privacy. Toggle on `Share your detected activity with others.`
6. Run the `run.bat` file, enter your credentials, `username` and `api key` from RetroAchievements.

Note: You may alternatively store your credentials via environment variables `RETROACHIEVEMENTS_USERNAME` and `RETROACHIEVEMENTS_API_KEY`. If set, they will be used by default.

After running the `run.bat` file, a `config.ini` file will be created in the same directory. The credentials that you've submitted are stored in this config file.

### If you want to run the presence in the background:
1. Use NSSM to install as a service.

### How to turn off username display?
1. If ever you don't want your username to have a redirection button on your Discord RP, just edit the `config.ini` file and modify the value inside the `displayUsername` to `False`. By default, this is `True`. _Notice the capital letters in the True and False as wrong cases may result to an error._
2. Save the changes you made, close the `run.bat` file, and open it again to reflect changes.

All the configurations inside the `config.ini` file can be modified based on your preferences. Just make sure to follow the proper syntax to avoid errors. 

### Things to keep in mind:
- Always open the Discord App first before running the script or the exe file.
- Restart the Rich Presence from running when switching accounts or reopening the Discord App.
