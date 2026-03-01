from colorama import Fore, Style, init
import configparser
from datetime import datetime, timezone
from pprint import pprint
from pypresence import Presence 
from pypresence.types import StatusDisplayType
import re
import requests
import time
import os.path
import time
import warnings
from allSystems import consoleIcons
import traceback

init(autoreset=True)

def getData(url):
    response = requests.get(url, headers={'Accept-Charset': 'utf-8', 'charset': 'utf-8'})
    if response.status_code == 200:
        return response.json()
    else:
        print(Fore.RED + f"Failed to fetch data from {url}, status code: {response.status_code}")
        return None

def getUserProfile(api_key, username):
    data = getData(f"https://retroachievements.org/API/API_GetUserProfile.php?y={api_key}&u={username}")
    return data

def getUserRecentlyPlayedGame(api_key, username, number_of_results):
    data = getData(f"https://retroachievements.org/API/API_GetUserRecentlyPlayedGames.php?y={api_key}&u={username}&c={number_of_results}")
    return data[0]

def getGameInfoAndUserProgress(api_key, username, game_id):
    data = getData(f"https://retroachievements.org/API/API_GetGameInfoAndUserProgress.php?y={api_key}&u={username}&g={game_id}")
    return data

# This function returns a list [totalAchievementsAchieved, totalAchievements]. Both of these are progression type and one win condition achievement.
def getBeatenAchievements(gameInfoAndUserProgress):
    totalProgressionAchievements = 0
    totalWinConditionAchievements = 0
    totalProgressionAchieved = 0
    totalWinConditionAchieved = 0
    winConditionAchieved = 0

    for achievement in gameInfoAndUserProgress['Achievements'].values():
        if(achievement['Type'] == "progression"):
            totalProgressionAchievements += 1 # Counts the total number of progression achievements
            if 'DateEarned' in achievement:
                totalProgressionAchieved += 1 # Counts the total number of progression achievements achieved
        elif(achievement['Type'] == "win_condition"):
            totalWinConditionAchievements += 1 # Counts the total number of win condition achievements
            if 'DateEarned' in achievement:
                totalWinConditionAchieved += 1 # Counts the total number of win condition achievements achieved

    if totalWinConditionAchieved > 0:
        winConditionAchieved = 1
    else:
        winConditionAchieved = 0

    totalAchievements = totalProgressionAchievements + 1 # Adds 1 since the game is considered beaten if the user have just at least 1 win condition achievement
    totalAchievementsAchieved = totalProgressionAchieved + winConditionAchieved
    
    return [totalAchievementsAchieved, totalAchievements]


def timeDifferenceFromNow(timeStamp):
    current_time = datetime.now(timezone.utc)
    target_time = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    differenceInMinutes = abs((target_time - current_time).total_seconds() / 60)
    return int(differenceInMinutes)

def isDiscordRPCAvailable(RPC):
    try:
        RPC.connect()
        RPC.close()
        print(Fore.GREEN + "Discord RPC is available.")
        return True
    except:
        print(Fore.RED + "Discord RPC is not available.")
        return False

def clampState(presence, story):
    msg = f"{presence}{story}"
    if len(msg) > 128:
        msg = presence
        if len(msg) > 128:
            msg = presence.split(",", 1)[0]
            if len(msg) > 128:
                msg = ""
    try:
        return msg.decode("utf-8", errors="replace")
    except:
        return msg

def updatePresence(RPC, userProfile, recentlyPlayedGame, isDisplayUsername, start_time, gameBeatenAchievements):
    button1Link = None
    gameCompletionPercentage = int((recentlyPlayedGame['NumAchieved'] / recentlyPlayedGame['NumPossibleAchievements']) * 100)
    gameBeatenPercentage = int((gameBeatenAchievements[0] / gameBeatenAchievements[1]) * 100)
    largeImageHoverText = f"{recentlyPlayedGame['NumAchieved']} of {recentlyPlayedGame['NumPossibleAchievements']} achieved🏆| {gameCompletionPercentage} %"
    storyProgressText = f" | Story Progress: {gameBeatenPercentage} %"

    if(isDisplayUsername):
        button1Link = {"label": "Visit Profile 👤", "url": f"https://retroachievements.org/user/{userProfile['User']}"}
    else:
        button1Link = {"label": "What is RetroAchievements❓", "url": "https://retroachievements.org"}
    
    button2Link = {"label": "Game Info 🎮", "url": f"https://retroachievements.org/game/{recentlyPlayedGame['GameID']}"}

    if gameBeatenPercentage == 0:
        storyProgressText = ""
    
    try:
        msg = clampState(userProfile['RichPresenceMsg'].encode('utf-8'), storyProgressText.encode('utf-8'))        
        RPC.update(
            name = recentlyPlayedGame['Title'],
            status_display_type = StatusDisplayType.NAME,
            details = "Playing on AYN Thor",
            state = msg,
            start = start_time,
            large_image = f"https://media.retroachievements.org{recentlyPlayedGame['ImageIcon']}",
            large_text = largeImageHoverText,
            small_image = consoleIcons.get(recentlyPlayedGame['ConsoleID']),
            small_text = recentlyPlayedGame['ConsoleName'],
            buttons = [button1Link, button2Link]
        )
    except Exception as e:
        date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        print(Fore.RED + f"{date_time} - Failed to update presence: {e}")
        print(Fore.RED + f"{date_time} - Name: {recentlyPlayedGame['Title'].encode('utf-8')}, state: {msg.encode('utf-8')}")
        print(traceback.format_exc())
        print(Fore.CYAN + "Waiting for Discord RPC availability...")
        while(isDiscordRPCAvailable(RPC) == False):
            time.sleep(10)
        RPC.connect()
        print(Fore.CYAN + "Reconnected!")
        pass
        

def setup_config():
    config_file = open("config.ini","w")
    usr = ""
    api = ""

    if not os.getenv('RETROACHIEVEMENTS_USERNAME'):
        print(f'Enter RetroAchievements username: ')
        usr = str(input())
    if not os.getenv('RETROACHIEVEMENTS_API_KEY'):
        print(f'Enter RetroAchievements api_key: ')
        api = str(input())

    data = f"""
[DISCORD]
username = {usr}
api_key = {api}

[SETTINGS]
# If set to True, the username will be displayed in the presence. If False, the username won't be displayed.
displayUsername = True

# This is the time in minutes after which the presence will be cleared after you quit playing.
# Increase the number if your game device has an unstable internet connection. (This is to prevent the presence from being cleared when you're still playing)
timeoutInMinutes = 3

# This is the time in seconds after which the presence will be updated
refreshRateInSeconds = 30
    """

    config_file.write(data)
    config_file.close()

def main():
    # GLOBAL SET
    isRPCRunning = False

    # print(Fore.YELLOW + "HOW TO USE:\n1. Open Discord app.\n2. Run this script.\nDiscord app should be running first before this script.\n")

    if(os.path.exists('config.ini') == False):
        print(Fore.YELLOW + f"Config file not found. Running first time setup...")
        setup_config()

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    username = os.getenv('RETROACHIEVEMENTS_USERNAME', config.get('DISCORD', 'username'))
    api_key = os.getenv('RETROACHIEVEMENTS_API_KEY', config.get('DISCORD', 'api_key'))
    isDisplayUsername = config.getboolean('SETTINGS', 'displayUsername')
    timeoutInMinutes = config.getint('SETTINGS', 'timeoutInMinutes')
    refreshRateInSeconds = config.getint('SETTINGS', 'refreshRateInSeconds')

    client_id = os.getenv('DISCORD_CLIENT_ID', "1320752097989234869")

    RPC = Presence(client_id)
    print(Fore.CYAN + "Waiting for Discord RPC availability...")

    while(isDiscordRPCAvailable(RPC) == False):
        #print(Fore.RED + "Retrying in 10 seconds...")
        time.sleep(10)

    time.sleep(5)
    RPC.connect()

    print(Fore.MAGENTA + "Connected!")

    print("Timeout in minutes: ", timeoutInMinutes)
    print("Refresh rate in seconds: ", refreshRateInSeconds)
    
    start_time = int(time.time())

    while True:
        warnings.filterwarnings("ignore")

        try:
            # For getting the recently played game
            recentlyPlayedGame = getUserRecentlyPlayedGame(api_key, username, 1)
            # print(recentlyPlayedGame)
            if(timeDifferenceFromNow(recentlyPlayedGame['LastPlayed']) < timeoutInMinutes):
                # print("Present")
                # For getting the rich presence message
                userProfile = getUserProfile(api_key, username)
                # print(userProfile)
                # Getting achievements data
                gameInfoAndUserProgress = getGameInfoAndUserProgress(api_key, username, recentlyPlayedGame['GameID'])
                # print(gameInfoAndUserProgress)
                gameBeatenAchievements = getBeatenAchievements(gameInfoAndUserProgress)
                if(isRPCRunning == False):
                    start_time = int(time.time())
                updatePresence(RPC, userProfile, recentlyPlayedGame, isDisplayUsername, start_time, gameBeatenAchievements)
                isRPCRunning = True
            else:
                # print("Not present")
                RPC.clear()
                isRPCRunning = False
        except Exception as e:
            date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            print(Fore.RED + f"{date_time} - Error during presence update: {e}")
            print(Fore.RED + f"{date_time} - Rich presence msg: {userProfile['RichPresenceMsg'].encode('utf-8')}")
            print(traceback.format_exc())
            isRPCRunning = False
            print(Fore.CYAN + "Rechecking Discord RPC availability...")
            while(isDiscordRPCAvailable(RPC) == False):
                #print(Fore.RED + "Retrying in 10 seconds...")
                time.sleep(10)
            RPC.connect()
            RPC.clear()
            isRPCRunning = False
            print(Fore.CYAN + "Reconnected to Discord RPC!")

        time.sleep(refreshRateInSeconds)
        
if __name__ == "__main__":
    main()
