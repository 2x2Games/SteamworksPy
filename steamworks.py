#================================================
# Steamworks For Python
#================================================
from ctypes import *
import sys, os
import logging
from types import SimpleNamespace
logger = logging.getLogger(__name__)
#------------------------------------------------
# User Status
#------------------------------------------------
FriendFlags = {  # regular friend
    'None': 0x00,
    'Blocked': 0x01,
    'FriendshipRequested': 0x02,
    'Immediate': 0x04,
    'ClanMember': 0x08,
    'OnGameServer': 0x10,
    'RequestingFriendship': 0x80,
    'RequestingInfo': 0x100,
    'Ignored': 0x200,
    'IgnoredFriend': 0x400,
    'Suggested': 0x800,
    'All': 0xFFFF,
    }
#------------------------------------------------
# Workshop File Types
#------------------------------------------------
WorkshopFileType = {
    'Community': 0x00,			# normal Workshop item that can be subscribed to
    'Microtransaction': 0x01,	# Workshop item that is meant to be voted on for the purpose of selling in-game

    # NOTE: There are more workshop file types defined "in isteamremotestorage.h",
    # but we do not need them for now.
}
#------------------------------------------------
# Workshop Item States
#------------------------------------------------
WorkshopItemState = {
    "ItemStateNone":			0,	# item not tracked on client
    "ItemStateSubscribed":		1,	# current user is subscribed to this item. Not just cached.
    "ItemStateLegacyItem":		2,	# item was created with ISteamRemoteStorage
    "ItemStateInstalled":		4,	# item is installed and usable (but maybe out of date)
    "ItemStateNeedsUpdate":		8,	# items needs an update. Either because it's not installed yet or creator updated content
    "ItemStateDownloading":		16,	# item update is currently downloading
    "ItemStateDownloadPending":	32,	# DownloadItem() was called for this item, content isn't available until DownloadItemResult_t is fired
}
#------------------------------------------------
# Main Steam Class, obviously
#------------------------------------------------
class Steam:
    # Set some basic variables for the Steam class
    cdll = None
    warn = False
    # Initialize Steam
    @staticmethod
    def Init(dynamicLibDir):
        os.environ['LD_LIBRARY_PATH'] = dynamicLibDir
        # Loading SteamworksPy API for Linux
        if sys.platform == 'linux' or sys.platform == 'linux2':
            Steam.cdll = CDLL(os.path.join(dynamicLibDir, "SteamworksPy.so"))
            logger.info("SteamworksPy loaded for Linux")
        # Loading SteamworksPy API for Mac
        elif sys.platform == 'darwin':
            Steam.cdll = CDLL(os.path.join(dynamicLibDir, "SteamworksPy.dylib" ))
            logger.info("SteamworksPy loaded for Mac")
        # Loading SteamworksPy API for Windows
        elif sys.platform == 'win32':
            # Check Windows architecture
            Steam.cdll = CDLL(os.path.join(dynamicLibDir, "SteamworksPy.dll"))
            logger.info("SteamworksPy loaded for Windows")
        # Unrecognized platform, warn user, do not load Steam API
        else:
            logger.error("SteamworksPy failed to load (unsupported platform!)")
            Steam.warn = True
            return
        # Set restype for initialization
        Steam.cdll.IsSteamRunning.restype = c_bool
        # Check that Steam is running
        if Steam.cdll.IsSteamRunning():
            logger.info("Steam is running")
        else:
            logger.error("Steam is not running")
        # Boot up the Steam API
        if Steam.cdll.SteamInit() == 1:
            logger.info("Steamworks initialized!")
        else:
            logger.error("Steamworks failed to initialize!")
            Steam.warn = True
        #----------------------------------------
        # Restypes and Argtypes
        #----------------------------------------
        # Set restype for Apps functions
        Steam.cdll.HasOtherApp.restype = bool
        Steam.cdll.GetDlcCount.restype = int
        Steam.cdll.IsDlcInstalled.restype = bool
        Steam.cdll.IsAppInstalled.restype = bool
        Steam.cdll.GetCurrentGameLanguage.restype = c_char_p
        # Set restype for Friends functions
        Steam.cdll.GetFriendCount.restype = int
        Steam.cdll.GetFriendByIndex.restype = c_uint64
        Steam.cdll.GetPersonaName.restype = c_char_p
        Steam.cdll.GetPersonaState.restype = int
        Steam.cdll.GetFriendPersonaName.restype = c_char_p
        Steam.cdll.GetFriendPersonaName.argtypes = [c_uint64]
        Steam.cdll.SetRichPresence.restype = c_bool
        Steam.cdll.ClearRichPresence.restype = None
        Steam.cdll.InviteFriend.restype = None
        Steam.cdll.SetPlayedWith.restype = None
        Steam.cdll.ActivateGameOverlay.restype = None
        Steam.cdll.ActivateGameOverlay.argtypes = [c_char_p]
        Steam.cdll.ActivateGameOverlayToUser.restype = None
        Steam.cdll.ActivateGameOverlayToUser.argtypes = [c_char_p, c_uint32]
        Steam.cdll.ActivateGameOverlayToWebPage.restype = None
        Steam.cdll.ActivateGameOverlayToWebPage.argtypes = [c_char_p]
        Steam.cdll.ActivateGameOverlayToStore.restype = None
        Steam.cdll.ActivateGameOverlayToStore.argtypes = [c_uint32]
        Steam.cdll.ActivateGameOverlayInviteDialog.restype = None
        Steam.cdll.ActivateGameOverlayInviteDialog.argtypes = [c_uint64]
        # Set restype for Matchmaking
        Steam.cdll.CreateLobby.restype = None
        Steam.cdll.CreateLobby.argtypes = [c_uint64, c_uint64]
        Steam.cdll.JoinLobby.restype = None
        Steam.cdll.JoinLobby.argtypes = [c_uint64]
        Steam.cdll.LeaveLobby.restype = None
        Steam.cdll.LeaveLobby.argtypes = [c_uint64]
        Steam.cdll.InviteUserToLobby.restype = bool
        Steam.cdll.InviteUserToLobby.argtypes = [c_uint64, c_uint64]
        # Set restype for Music functions
        Steam.cdll.MusicIsEnabled.restype = bool
        Steam.cdll.MusicIsPlaying.restype = bool
        Steam.cdll.MusicGetVolume.restype = c_float
        Steam.cdll.MusicPause.restype = bool
        Steam.cdll.MusicPlay.restype = bool
        Steam.cdll.MusicPlayNext.restype = bool
        Steam.cdll.MusicPlayPrev.restype = bool
        Steam.cdll.MusicSetVolume.restype = c_float
        # Set restype for Screenshot functions
        Steam.cdll.TriggerScreenshot.restype = None
        Steam.cdll.SetScreenshotLocation.argtypes = [c_uint32, c_char_p]
        Steam.cdll.SetScreenshotLocation.restype = None
        # Set restype for User functions
        Steam.cdll.GetSteamID.restype = c_uint64
        Steam.cdll.GetPlayerSteamLevel.restype = int
        Steam.cdll.GetUserDataFolder.restype = c_char_p
        # Set restype for User Statistic functions
        Steam.cdll.GetAchievement.restype = bool
        Steam.cdll.IndicateAchievementProgress.restype = bool
        Steam.cdll.GetStatInt.restype = int
        Steam.cdll.GetStatFloat.restype = c_float
        Steam.cdll.GetGlobalStatInt.restype = c_uint64
        Steam.cdll.GetGlobalStatFloat.restype = c_double
        Steam.cdll.ResetAllStats.restype = bool
        Steam.cdll.RequestCurrentStats.restype = bool
        Steam.cdll.SetAchievement.restype = bool
        Steam.cdll.SetStatInt.restype = bool
        Steam.cdll.SetStatFloat.restype = bool
        Steam.cdll.StoreStats.restype = bool
        Steam.cdll.ClearAchievement.restype = bool
        Steam.cdll.Leaderboard_FindLeaderboard.restype = bool
        Steam.cdll.Leaderboard_FindLeaderboard.argtypes = [c_char_p]
        # Set restype for Utilities functions
        Steam.cdll.GetCurrentBatteryPower.restype = int
        Steam.cdll.GetIPCountry.restype = c_char_p
        Steam.cdll.GetSecondsSinceAppActive.restype = int
        Steam.cdll.GetSecondsSinceComputerActive.restype = int
        Steam.cdll.GetServerRealTime.restype = int
        Steam.cdll.IsOverlayEnabled.restype = bool
        Steam.cdll.IsSteamRunningInVR.restype = bool
        Steam.cdll.GetSteamUILanguage.restype = c_char_p
        Steam.cdll.GetAppID.restype = int
        Steam.cdll.SetOverlayNotificationPosition.restype = None
        # Set argtypes and restype for Workshop functions
        Steam.cdll.Workshop_StartItemUpdate.restype = c_uint64
        Steam.cdll.Workshop_SetItemTitle.restype = bool
        Steam.cdll.Workshop_SetItemTitle.argtypes = [c_uint64, c_char_p]
        Steam.cdll.Workshop_SetItemDescription.restype = bool
        Steam.cdll.Workshop_SetItemDescription.argtypes = [c_uint64, c_char_p]
        Steam.cdll.Workshop_SetItemUpdateLanguage.restype = bool
        Steam.cdll.Workshop_SetItemMetadata.restype = bool
        Steam.cdll.Workshop_SetItemVisibility.restype = bool
        Steam.cdll.Workshop_SetItemVisibility.argtypes = [c_uint64, c_int]
        Steam.cdll.Workshop_SetItemTags.restype = bool
        Steam.cdll.Workshop_SetItemContent.restype = bool
        Steam.cdll.Workshop_SetItemContent.argtypes = [c_uint64, c_char_p]
        Steam.cdll.Workshop_SetItemPreview.restype = bool
        Steam.cdll.Workshop_SetItemPreview.argtypes = [c_uint64, c_char_p]
        Steam.cdll.Workshop_SubmitItemUpdate.argtypes = [c_uint64, c_char_p]
        Steam.cdll.Workshop_GetNumSubscribedItems.restype = c_uint32
        Steam.cdll.Workshop_GetSubscribedItems.restype = c_uint32
        Steam.cdll.Workshop_GetSubscribedItems.argtypes = [POINTER(c_uint64), c_uint32]
        Steam.cdll.Workshop_GetItemState.restype = c_uint32
        Steam.cdll.Workshop_GetItemState.argtypes = [c_uint64]
        Steam.cdll.Workshop_GetItemInstallInfo.restype = bool
        Steam.cdll.Workshop_GetItemInstallInfo.argtypes = [c_uint64, POINTER(c_uint64), c_char_p, c_uint32,  POINTER(c_uint32)]
        Steam.cdll.Workshop_GetItemDownloadInfo.restype = bool
        Steam.cdll.Workshop_GetItemDownloadInfo.argtypes = [c_uint64, POINTER(c_uint64), POINTER(c_uint64)]
        Steam.cdll.Workshop_GetItemUpdateProgress.restype = c_int
        Steam.cdll.Workshop_GetItemUpdateProgress.argtypes = [c_uint64, POINTER(c_uint64), POINTER(c_uint64)]
        Steam.cdll.Workshop_DownloadItem.restype = bool
        Steam.cdll.Workshop_DownloadItem.argtypes = [c_uint64, c_bool]
    # Is Steam loaded
    @staticmethod
    def isSteamLoaded():
        return Steam.cdll and not Steam.warn
    # Running callbacks
    @staticmethod
    def RunCallbacks():
        if Steam.isSteamLoaded():
            Steam.cdll.RunCallbacks()
            return True
        return False
    # Shutdown
    @staticmethod
    def Shutdown():
        Steam.cdll.SteamShutdown()
#------------------------------------------------
# Class for Steam Apps
#------------------------------------------------
class SteamApps:
    # Check if the user has a given application/game
    @staticmethod
    def HasOtherApp(appID):
        if Steam.isSteamLoaded():
            return Steam.cdll.HasOtherApp(appID)
        return False
    # Get the number of DLC the user owns for a parent application/game
    @staticmethod
    def GetDlcCount():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetDlcCount()
        return 0
    # Check give the given DLC is installed, returns true/false
    @staticmethod
    def IsDlcInstalled(appID):
        if Steam.isSteamLoaded():
            return Steam.cdll.IsDlcInstalled(appID)
        return False
    # Check if given application/game is installed, not necessarily owned
    @staticmethod
    def IsAppInstalled(appID):
        if Steam.isSteamLoaded():
            return Steam.cdll.IsAppInstalled(appID)
        return False
    # Get the user's game language
    @staticmethod
    def GetCurrentGameLanguage():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetCurrentGameLanguage()
        return ""
#------------------------------------------------
# Class for Steam Friends
#------------------------------------------------
class SteamFriends:
    # Get number of friends user has
    @staticmethod
    def GetFriendCount(flag=FriendFlags['All']):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetFriendCount(flag)
        return 0
    # Get a friend by index
    @staticmethod
    def GetFriendByIndex(friendInt, flag=FriendFlags['All']):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetFriendByIndex(friendInt, flag)
        return 0
    # Get the user's Steam username
    @staticmethod
    def GetPlayerName():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetPersonaName()
        return ""
    # Get the user's state on Steam
    @staticmethod
    def GetPlayerState():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetPersonaState()
        return False
    # Get given friend's Steam username
    @staticmethod
    def GetFriendPersonaName(steamID):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetFriendPersonaName(steamID)
        return ""
    # Set the game information in Steam; used in 'View Game Info'
    @staticmethod
    def SetRichPresence(serverKey, serverValue):
        if Steam.isSteamLoaded():
            return Steam.cdll.SetRichPresence(serverKey, serverValue)
        return False
    # Clear the game information in Steam; used in 'View Game Info'
    @staticmethod
    def ClearRichPresence():
        if Steam.isSteamLoaded():
            Steam.cdll.ClearRichPresence()
            return True
        return False
    # Invite friend to current game/lobby
    @staticmethod
    def InviteFriend(steamID, connection):
        if Steam.isSteamLoaded():
            return Steam.cdll.InviteFriend(steamID, connection)
        return False
    # Set player as 'Played With' for game
    @staticmethod
    def SetPlayedWith(steamID):
        if Steam.isSteamLoaded():
            Steam.cdll.SetPlayedWith(steamID)
            return True
        return False
    # Activates the overlay with optional dialog to open the following: "Friends", "Community", "Players", "Settings", "OfficialGameGroup", "Stats", "Achievements", "LobbyInvite"
    @staticmethod
    def ActivateGameOverlay(dialog=''):
        if Steam.isSteamLoaded():
            Steam.cdll.ActivateGameOverlay(dialog.encode())
            return True
        return False
    # Activates the overlay to the following: "steamid", "chat", "jointrade", "stats", "achievements", "friendadd", "friendremove", "friendrequestaccept", "friendrequestignore"
    @staticmethod
    def ActivateGameOverlayToUser(url, steamID):
        if Steam.isSteamLoaded():
            Steam.cdll.ActivateGameOverlayToWebPage(url.encode(), steamID)
            return True
        return False
    # Activates the overlay with specified web address
    @staticmethod
    def ActivateGameOverlayToWebPage(url):
        if Steam.isSteamLoaded():
            Steam.cdll.ActivateGameOverlayToWebPage(url.encode())
            return True
        return False
    # Activates the overlay with the application/game Steam store page
    @staticmethod
    def ActivateGameOverlayToStore(appID):
        if Steam.isSteamLoaded():
            Steam.cdll.ActivateGameOverlayToWebPage(appID)
            return True
        return False
    # Activates game overlay to open the invite dialog. Invitations will be sent for the provided lobby
    @staticmethod
    def ActivateGameOverlayInviteDialog(steamID):
        if Steam.isSteamLoaded():
            Steam.cdll.ActivateGameOverlayToWebPage(steamID)
            return True
        return False

    class GameOverlayActivated_t(Structure):
        _fields_ = [
            ("active", c_uint8)
        ]
    GAME_OVERLAY_ACTIVATED_CALLBACK_TYPE = CFUNCTYPE(None, GameOverlayActivated_t)
    gameOverlayActivatedCallback = None

    @classmethod
    def SetGameOverlayActivatedCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.gameOverlayActivatedCallback = cls.GAME_OVERLAY_ACTIVATED_CALLBACK_TYPE(callback)
            Steam.cdll.Callbacks_SetGameOverlayActivatedCallback(cls.gameOverlayActivatedCallback)
            return True
        return False
#------------------------------------------------
# Class for Steam Matchmaking
#------------------------------------------------ 
class SteamMatchmaking:
    # Create a lobby on the Steam servers, if private the lobby will not be returned by any RequestLobbyList() call
    @staticmethod
    def CreateLobby(lobbyType, maxMembers):
        if Steam.isSteamLoaded():
            Steam.cdll.CreateLobby(lobbyType, maxMembers)
            return True
        return
    # Join an existing lobby
    @staticmethod
    def JoinLobby(lobbyID):
        if Steam.isSteamLoaded():
            Steam.cdll.JoinLobby(lobbyID)
            return True
        return False
    # Leave a lobby, this will take effect immediately on the client side, other users will be notified by LobbyChatUpdate_t callback
    @staticmethod
    def LeaveLobby(lobbyID):
        if Steam.isSteamLoaded():
            Steam.cdll.LeaveLobby(lobbyID)
            return True
        return False
    # Invite another user to the lobby, the target user will receive a LobbyInvite_t callback, will return true if the invite is successfully sent, whether or not the target responds
    @staticmethod
    def InviteUserToLobby(lobbyID, steamID):
        if Steam.isSteamLoaded():
            return Steam.cdll.InviteUserToLobby(lobbyID, steamID)
        return False
#------------------------------------------------
# Class for Steam Music
#------------------------------------------------
class SteamMusic:
    # Is Steam music enabled
    @staticmethod
    def MusicIsEnabled():
        if Steam.isSteamLoaded():
            return Steam.cdll.MusicIsEnabled()
        return False
    # Is Steam music playing something
    @staticmethod
    def MusicIsPlaying():
        if Steam.isSteamLoaded():
            return Steam.cdll.MusicIsPlaying()
        return False
    # Get the volume level of the music
    @staticmethod
    def MusicGetVolume():
        if Steam.isSteamLoaded():
            return Steam.cdll.MusicGetVolume()
        return 0
    # Pause whatever Steam music is playing
    @staticmethod
    def MusicPause():
        if Steam.isSteamLoaded():
            Steam.cdll.MusicPause()
            return True
        return False
    # Play current track/album
    @staticmethod
    def MusicPlay():
        if Steam.isSteamLoaded():
            Steam.cdll.MusicPlay()
            return True
        return False
    # Play next track/album
    @staticmethod
    def MusicPlayNext():
        if Steam.isSteamLoaded():
            Steam.cdll.MusicPlayNext()
            return True
        return False
    # Play previous track/album
    @staticmethod
    def MusicPlayPrev():
        if Steam.isSteamLoaded():
            Steam.cdll.MusicPlayPrev()
            return True
        return False
    # Set the volume of Steam music
    @staticmethod
    def MusicSetVolume(value):
        if Steam.isSteamLoaded():
            Steam.cdll.MusicSetVolume(value)
            return True
        return False
#------------------------------------------------
# Class for Steam Screenshots
#------------------------------------------------
class SteamScreenshots:
    # Causes Steam overlay to take a screenshot
    @staticmethod
    def TriggerScreenshot():
        if Steam.isSteamLoaded():
            Steam.cdll.TriggerScreenshot()
            return True

        return False

    @staticmethod
    def SetScreenshotLocation(hScreenshot, pchLocation):
        if Steam.isSteamLoaded():
            return Steam.cdll.SetScreenshotLocation(hScreenshot, pchLocation)
        return False

    class ScreenshotReady_t(Structure):
        _fields_ = [
            ("local", c_uint32),
            ("result", c_uint32),
        ]
    SCREENSHOT_READY_CALLBACK_TYPE = CFUNCTYPE(None, ScreenshotReady_t)
    screenshotReadyCallback = None

    @classmethod
    def SetScreenshotReadyCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.screenshotReadyCallback = cls.SCREENSHOT_READY_CALLBACK_TYPE(callback)
            Steam.cdll.Callbacks_SetScreenshotReadyCallback(cls.screenshotReadyCallback)
            return True

        return False
#------------------------------------------------
# Class for Steam Users
#------------------------------------------------
class SteamUser:
    # Get user's Steam ID
    @staticmethod
    def GetPlayerID():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetSteamID()
        return 0
    # Get the user's Steam level
    @staticmethod
    def GetPlayerSteamLevel():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetPlayerSteamLevel()
        return 0
    # Get the user's Steam installation path
    @staticmethod
    def GetUserDataFolder():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetUserDataFolder()
        return ""
    # Get the value of a float statistic
    @staticmethod
    def GetGobalStatFloat(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetGobalStatFloat(name)
        return 0.0
    # Get the value of an integer statistic
    @staticmethod
    def GetGlobalStatInt(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetGlobalStatInt(name)
        return 0

    @staticmethod
    def RequestGlobalStats(nHistoryDays):
        if Steam.isSteamLoaded():
            Steam.cdll.Stats_RequestGlobalStats(nHistoryDays)
            return True
        return False

    class UserStatsReceived_t(Structure):
        _fields_ = [
            ("game_id", c_uint64),
            ("result", c_uint32),
            ("steam_id_user", c_uint64),
        ]
    USER_STATS_RECEIVED_CALLBACK_TYPE = CFUNCTYPE(None, UserStatsReceived_t)
    userStatsReceivedCallback = None

    @classmethod
    def SetUserStatsReceivedCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.userStatsReceivedCallback = cls.USER_STATS_RECEIVED_CALLBACK_TYPE(callback)
            Steam.cdll.Callbacks_SetUserStatsReceivedCallback(cls.userStatsReceivedCallback)
            return True
        return False

    class GlobalStatsReceived_t(Structure):
        _fields_ = [
            ("game_id", c_uint64),
            ("result", c_uint32),
        ]
    GLOBAL_STATS_RECEIVED_CALLBACK_TYPE = CFUNCTYPE(None, GlobalStatsReceived_t)
    globalStatsReceivedCallback = None

    @classmethod
    def SetGlobalStatsReceivedCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.globalStatsReceivedCallback = cls.GLOBAL_STATS_RECEIVED_CALLBACK_TYPE(callback)
            Steam.cdll.Callbacks_SetGlobalStatsReceivedCallback(cls.globalStatsReceivedCallback)
            return True
        return False
#------------------------------------------------
# Class for Steam User Statistics
#------------------------------------------------
class SteamUserStats:
    # Return true/false if use has given achievement
    @staticmethod
    def GetAchievement(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetAchievement(name)
        return ""
    # Get the value of a float statistic
    @staticmethod
    def GetStatFloat(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetStatFloat(name)
        return 0.0
    # Get the value of a float statistic
    @staticmethod
    def IndicateAchievementProgress(name, nCurProgress, nMaxProgress):
        if Steam.isSteamLoaded():
            return Steam.cdll.IndicateAchievementProgress(name, nCurProgress, nMaxProgress)
        return 0
    # Get the value of an integer statistic
    @staticmethod
    def GetStatInt(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.GetStatInt(name)
        return 0
    # Reset all Steam statistics; optional to reset achievements
    @staticmethod
    def ResetAllStats(achievesToo):
        if Steam.isSteamLoaded():
            return Steam.cdll.ResetAllStats(achievesToo)
        return False
    # Request all statistics and achievements from Steam servers
    @staticmethod
    def RequestCurrentStats():
        if Steam.isSteamLoaded():
            return Steam.cdll.RequestCurrentStats()
        return False
    # Set a given achievement
    @staticmethod
    def SetAchievement(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.SetAchievement(name)
        return False
    # Set a statistic
    @staticmethod
    def SetStat(name, value):
        if Steam.isSteamLoaded():
            if isinstance(value, float):
                return Steam.cdll.SetStatFloat(name, value)
            elif isinstance(value, int):
                return Steam.cdll.SetStatInt(name, value)
            raise Exception("SteamUserStats: SetStat value can be only int or float.")
    # Store all statistics, and achievements, on Steam servers; must be called to "pop" achievements
    @staticmethod
    def StoreStats():
        if Steam.isSteamLoaded():
            return Steam.cdll.StoreStats()
        return False
    # Clears a given achievement
    @staticmethod
    def ClearAchievement(name):
        if Steam.isSteamLoaded():
            return Steam.cdll.ClearAchievement(name)
        return False
    # A class that describes Steam's LeaderboardFindResult_t C struct
    class FindLeaderboardResult_t(Structure):
        _fields_ = [
            ("leaderboard_handle", c_uint64),
            ("leaderboard_found", c_uint32)
        ]
    FIND_LEADERBORAD_RESULT_CALLBACK_TYPE = CFUNCTYPE(None, FindLeaderboardResult_t)
    findLeaderboardResultCallback = None

    @classmethod
    def SetFindLeaderboardResultCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.findLeaderboardResultCallback = cls.FIND_LEADERBORAD_RESULT_CALLBACK_TYPE (callback)
            Steam.cdll.Leaderboard_SetFindLeaderboardResultCallback(cls.findLeaderboardResultCallback)
            return True
        return False
    #
    # Find Leaderboard by name
    #
    # name -- The leaderboard name to search for
    # callback -- The function to call once the find returns a result
    @staticmethod
    def FindLeaderboard(name, callback = None):
        if Steam.isSteamLoaded():
            if callback is not None:
                SteamUserStats.SetFindLeaderboardResultCallback(callback)

            Steam.cdll.Leaderboard_FindLeaderboard(name.encode())
            return True
        return False
#------------------------------------------------
# Class for Steam Utilities
#------------------------------------------------
class SteamUtilities:
    # Get the amount of battery power, clearly for laptops
    @staticmethod
    def GetCurrentBatteryPower():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetCurrentBatteryPower()
        return 0
    # Get the user's country by IP
    @staticmethod
    def GetIPCountry():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetIPCountry()
        return ""
    # Returns seconds since application/game was started
    @staticmethod
    def GetSecondsSinceAppActive():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetSecondsSinceAppActive()
        return 0
    # Return seconds since computer was started
    @staticmethod
    def GetSecondsSinceComputerActive():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetSecondsSinceComputerActive()
        return 0
    # Get the actual time
    @staticmethod
    def GetServerRealTime():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetServerRealTime()
        return 0
    # Returns true/false if Steam overlay is enabled
    @staticmethod
    def IsOverlayEnabled():
        if Steam.isSteamLoaded():
            return Steam.cdll.IsOverlayEnabled()
        return False
    # Is Steam running in VR?
    @staticmethod
    def IsSteamRunningInVR():
        if Steam.isSteamLoaded():
            return Steam.cdll.IsSteamRunningInVR()
        return False
    # Get the Steam user interface language
    @staticmethod
    def GetSteamUILanguage():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetSteamUILanguage()
        return ""
    # Get the Steam ID of the running application/game
    @staticmethod
    def GetAppID():
        if Steam.isSteamLoaded():
            return Steam.cdll.GetAppID()
        return 0
    # Set the position where overlay shows notifications
    @staticmethod
    def SetOverlayNotificationPosition(pos):
        if Steam.isSteamLoaded():
            Steam.cdll.SetOverlayNotificationPosition(pos)
            return True
        return False
#------------------------------------------------
# Class for Steam Workshop
#------------------------------------------------
class SteamWorkshop:
    # A class that describes Steam's CreateItemResult_t C struct
    class CreateItemResult_t(Structure):
        _fields_ = [
            ("result", c_int),
            ("published_file_id", c_uint64),
            ("legal_accept_needed", c_bool)
        ]
    # A class that describes Steam's SubmitItemUpdateResult_t C struct
    class SubmitItemUpdateResult_t(Structure):
        _fields_ = [
            ("result", c_int),
            ("legal_accept_needed", c_bool),
            ("published_file_id", c_uint64),
        ]
    # A class that describes Steam's ItemInstalled_t C struct
    class ItemInstalled_t(Structure):
        _fields_ = [
            ("appId", c_uint32),
            ("published_file_id", c_uint64)
        ]
    # A class that describes Steam's DeleteItemResult_t C struct
    class DeleteItemResult_t(Structure):
        _fields_ = [
            ("result", c_uint32),
            ("published_file_id", c_uint64)
        ]
    # A class that describes Steam's DownloadItemResult_t C struct
    class DownloadItemResult_t(Structure):
        _fields_ = [
            ("app_id", c_uint32),
            ("published_file_id", c_uint64),
            ("result", c_uint32),
        ]
    # A class that describes Steam's SteamUGCDetails_t C struct
    class SteamUGCDetails_t(Structure):
        _fields_ = [
            ("published_file_id", c_uint64),
            ("result", c_uint32),
            ("file_type", c_uint32),
            ("creator_app_id", c_uint32),
            ("consumer_app_id", c_uint32),
            ("title", c_char * 129),
            ("description", c_char * 8000),
            ("steam_owner_id", c_uint64),
            ("time_created", c_uint32),
            ("time_updated", c_uint32),
            ("time_added_to_user_list", c_uint32),
            ("visibility", c_uint32),
            ("banned", c_bool),
            ("accepted_for_use", c_bool),
            ("tags_truncated", c_bool),
            ("tags", c_char * 1025),
            ("file", c_uint64),
            ("preview_file", c_uint64),
            ("file_name", c_char * 260),
            ("file_size", c_int32),
            ("preview_file_size", c_int32),
            ("url", c_char * 256),
            ("votes_up", c_uint32),
            ("voted_down", c_uint32),
            ("score", c_float),
            ("num_children", c_uint32),
        ]
    # We want to keep callbacks in the class scope, so that they don't get
    # garbage collected while we still need them.
    ITEM_CREATED_CALLBACK_TYPE = CFUNCTYPE(None, CreateItemResult_t)
    itemCreatedCallback = None

    ITEM_UPDATED_CALLBACK_TYPE = CFUNCTYPE(None, SubmitItemUpdateResult_t)
    itemUpdatedCallback = None

    ITEM_INSTALLED_CALLBACK_TYPE = CFUNCTYPE(None, ItemInstalled_t)
    itemInstalledCallback = None

    ITEM_DELETED_CALLBACK_TYPE = CFUNCTYPE(None, DeleteItemResult_t)
    itemDeletedCallback = None

    ITEM_DOWNLOADED_CALLBACK_TYPE = CFUNCTYPE(None, DownloadItemResult_t)
    itemDownloadedCallback = None

    QUERY_UGC_ITEM_CALLBACK_TYPE = CFUNCTYPE(None, SteamUGCDetails_t)
    queryUGCItemCallback = None
    #
    @classmethod
    def SetItemCreatedCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.itemCreatedCallback = cls.ITEM_CREATED_CALLBACK_TYPE(callback)
            Steam.cdll.Workshop_SetItemCreatedCallback(cls.itemCreatedCallback)
            return True
        return False
    #
    @classmethod
    def SetQueryUGCItemCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.queryUGCItemCallback = cls.QUERY_UGC_ITEM_CALLBACK_TYPE(callback)
            Steam.cdll.Workshop_SetSteamUGCDetailsCallback(cls.queryUGCItemCallback)
            return True
        return False
    #
    @classmethod
    def ClearSteamUGCDetailsCallback(cls):
        if Steam.isSteamLoaded():
            cls.queryUGCItemCallback = None
            Steam.cdll.Workshop_ClearSteamUGCDetailsCallback()
            return True
        return False
    #
    @classmethod
    def SetItemUpdatedCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.itemUpdatedCallback = cls.ITEM_UPDATED_CALLBACK_TYPE(callback)
            Steam.cdll.Workshop_SetItemUpdatedCallback(cls.itemUpdatedCallback)
            return True
        return False
    #
    @classmethod
    def SetItemInstalledCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.itemInstalledCallback = cls.ITEM_INSTALLED_CALLBACK_TYPE(callback)
            Steam.cdll.Workshop_SetItemInstalledCallback(cls.itemInstalledCallback)
            return True
        return False
    #
    @classmethod
    def ClearItemInstalledCallback(cls):
        if Steam.isSteamLoaded():
            cls.itemInstalledCallback = None
            Steam.cdll.Workshop_ClearItemInstalledCallback()
            return True
        return False
    #
    @classmethod
    def SetDeleteItemResultCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.itemDeletedCallback = cls.ITEM_DELETED_CALLBACK_TYPE(callback)
            Steam.cdll.Workshop_SetDeleteItemResultCallback(cls.itemDeletedCallback)
            return True
        return False
    #
    @classmethod
    def DownloadItem(cls, publishedFileId, highPriority):
        if Steam.isSteamLoaded():
            return Steam.cdll.Workshop_DownloadItem(publishedFileId, highPriority)
        return False
    #
    @classmethod
    def SetDownloadItemResultCallback(cls, callback):
        if Steam.isSteamLoaded():
            cls.itemDownloadedCallback = cls.ITEM_DOWNLOADED_CALLBACK_TYPE(callback)
            Steam.cdll.Workshop_SetDownloadItemResultCallback(cls.itemDownloadedCallback)
            return True
        return False
    #
    # Create a UGC (Workshop) item
    #
    # Arguments:
    # appId -- The app ID of the game on Steam.
    # Do not use the creation tool app ID if they are separate.
    #
    # filetype -- Can be a community file type or microtransactions.
    # Use predefined `WorkshopFileType` values.
    #
    # callback -- The function to call once the item creation is finished.
    @staticmethod
    def CreateItem(appId, filetype, callback=None):
        if Steam.isSteamLoaded():
            if callback is not None:
                SteamWorkshop.SetItemCreatedCallback(callback)

            Steam.cdll.Workshop_CreateItem(appId, filetype)
            return True
        return False
    #
    @staticmethod
    def QueryUGCItem(nPublishedFileID, callback):
        if Steam.isSteamLoaded():
            SteamWorkshop.SetQueryUGCItemCallback(callback)
            Steam.cdll.Workshop_QueryUGCItem(nPublishedFileID)
            return True
        return False
    # Start the item update process and receive an update handle.
    #
    # Arguments:
    # appId -- The app ID of the game on Steam.
    # Do not use the creation tool app ID if they are separate
    # publishedFileId -- The ID of the Workshop file you are updating
    #
    # Return value:
    # If sucessful: update handle - an ID of the current update transaction
    # Otherwise: False
    @staticmethod
    def StartItemUpdate(appId, publishedFileId):
        if Steam.isSteamLoaded():
            return Steam.cdll.Workshop_StartItemUpdate(appId, c_uint64(publishedFileId))
        return False
    # Set the title of a Workshop item
    #
    # Arguments:
    #
    # updateHandle -- the handle returned by 'StartItemUpdate'
    # title -- the desired title of the item.
    #
    # Return value:
    # True on succes,
    # False otherwise.
    @staticmethod
    def SetItemTitle(updateHandle, title):
        if Steam.isSteamLoaded():
            if len(title) > 128:
                logger.error("Your title is longer than 128 characters.")
                return False

            return Steam.cdll.Workshop_SetItemTitle(updateHandle, title.encode())
        return False
    # Set the description of a Workshop item
    #
    # Arguments:
    # updateHandle -- the handle returned by 'StartItemUpdate'
    # description -- the desired description of the item.
    #
    # Return value:
    # True on succes,
    # False otherwise.
    @staticmethod
    def SetItemDescription(updateHandle, description):
        if Steam.isSteamLoaded():
            if len(description) > 8000:
                logger.error("Your description is longer than 8000 characters.")
                return False

            return Steam.cdll.Workshop_SetItemDescription(updateHandle, description.encode())
        return False
    #
    @staticmethod
    def SetItemTags(updateHandle, *tags):
        if Steam.isSteamLoaded():
            arr = (c_char_p * len(tags))()
            arr[:] = [t.encode("utf-8") for t in tags]
            lib.external_C(len(L), arr)
            return Steam.cdll.Workshop_SetItemTags(updateHandle, arr, len(tags))
        return False
    # Set the directory containing the content you wish to upload to Workshop.
    #
    # Arguments:
    # updateHandle -- the handle returned by 'StartItemUpdate'
    # contentDirectory -- path to the directory containing the content of the workshop item.
    #
    # Return value:
    # True on succes,
    # False otherwise.
    @staticmethod
    def SetItemContent(updateHandle, contentDirectory):
        if Steam.isSteamLoaded():
            return Steam.cdll.Workshop_SetItemContent(updateHandle, contentDirectory.encode())
        return False
    # Set the preview image of the Workshop item.
    #
    # Arguments:
    # updateHandle -- the handle returned by 'StartItemUpdate'
    # previewImage -- path to the preview image file.
    #
    # Return value:
    # True on succes,
    # False otherwise.
    #
    @staticmethod
    def SetItemVisibility(updateHandle, visibility):
        if Steam.isSteamLoaded():
            return Steam.cdll.Workshop_SetItemVisibility(updateHandle, visibility)
        return False
    #
    # Submit the item update with the given handle to Steam.
    #
    # Arguments:
    # updateHandle -- the handle returned by 'StartItemUpdate'
    # changeNote -- a string containing change notes for the current update.
    @staticmethod
    def SubmitItemUpdate(updateHandle, changeNote="", callback=None):
        if Steam.isSteamLoaded():
            if callback is not None:
                SteamWorkshop.SetItemUpdatedCallback(callback)

            changeNote = changeNote.encode() if changeNote else c_char_p(0)
            Steam.cdll.Workshop_SubmitItemUpdate(updateHandle, changeNote)
            return True
        return False
    # Get the progress of an item update request.
    #
    # Argument:
    # updateHandle -- the handle returned by 'StartItemUpdate'
    #
    # Return Value:
    # On success: An object with the following attributes
    # -- 'itemUpdateStatus - a `WorkshopItemUpdateStatus` value describing the update status of the item
    # -- 'bytesProcessed' - amount of bytes processed
    # -- 'bytesTotal' - total amount of bytes to be processed
    # -- 'progress' - a value ranging from 0 to 1 representing update progress
    # Otherwise: False
    @staticmethod
    def GetItemUpdateProgress(updateHandle):
        if Steam.isSteamLoaded():
            pBytesProcessed = pointer(c_uint64(0))
            pBytesTotal = pointer(c_uint64(0))

            itemUpdateStatus = Steam.cdll.Workshop_GetItemUpdateProgress(updateHandle, pBytesProcessed, pBytesTotal)
            # Unlike for GetItemDownloadInfo, pBytesTotal should always be set here
            progress = pBytesProcessed.contents.value / pBytesTotal.contents.value if pBytesTotal.contents.value else 0

            return SimpleNamespace(
                item_update_status=itemUpdateStatus,
                bytes_processed=pBytesProcessed.contents.value,
                bytes_total=pBytesTotal.contents.value,
                progress=progress
            )
        return False
    # Get the total number of items the user is subscribed to for this game or application.
    #
    # Return value:
    # On success: The number of subscribed items,
    # Otherwise: False.
    @staticmethod
    def GetNumSubscribedItems():
        if Steam.isSteamLoaded():
            return Steam.cdll.Workshop_GetNumSubscribedItems()
        return False
    # Get a list of published file IDs that the user is subscribed to
    #
    # Arguments:
    # maxEntries -- the maximum number of entries to fetch. If omitted
    # the function will try to fetch as much items as the user is
    # subscribed to.
    #
    # Return Value:
    # On success: A list of published file IDs that the user is subscribed to.
    # Otherwise: False.
    @staticmethod
    def GetSubscribedItems(maxEntries=-1):
        if Steam.isSteamLoaded():
            if maxEntries < 0:
                maxEntries = SteamWorkshop.GetNumSubscribedItems()
            # Published file IDs are stored as uint64 values
            PublishedFileIdsArrayCType = c_uint64 * maxEntries
            pvecPublishedFileIds = PublishedFileIdsArrayCType()

            # TODO: We might need to add an exception check here to catch any errors while
            # writing to the 'pvecPublishedFileIds' array.
            numItems = Steam.cdll.Workshop_GetSubscribedItems(pvecPublishedFileIds, maxEntries)
            # According to steam's example, it is possible for numItems to be greater than maxEntries
            # so we crop.
            if numItems > maxEntries:
                numItems = maxEntries

            publishedFileIdsList = [pvecPublishedFileIds[i] for i in range(numItems)]
            return publishedFileIdsList
        return False
    # Get the current state of a workshop item.
    #
    # Arguments:
    # publishedFileId -- the id of the item whose state to check
    #
    # Return Value:
    # On success: A `WorkshopItemState` value describing the item state.
    # Otherwise: False
    @staticmethod
    def GetItemState(publishedFileId):
        if Steam.isSteamLoaded():
            return Steam.cdll.Workshop_GetItemState(publishedFileId)
        return False
    # Get info about an installed item
    #
    # Arguments:
    # publishedFileId -- the id of the item to look up,
    # maxFolderPathLength -- maximum length of the folder path in characters.
    #
    # Return Value:
    # If the item is installed: an object with the following attributes
    # -- 'sizeOnDisk'
    # -- 'folder'
    # -- 'timestamp'
    #
    # If the item is not installed, or the method fails it returns: False
    @staticmethod
    def GetItemInstallInfo(publishedFileId, maxFolderPathLength=1024):
        if Steam.isSteamLoaded():
            pSizeOnDisk = pointer(c_uint64(0))
            pTimestamp = pointer(c_uint32(0))
            pFolder = create_string_buffer(maxFolderPathLength)

            isInstalled = Steam.cdll.Workshop_GetItemInstallInfo(publishedFileId, pSizeOnDisk, pFolder, maxFolderPathLength, pTimestamp)

            if isInstalled:
                itemInfo = SimpleNamespace(
                    size_on_disk=pSizeOnDisk.contents.value,
                    folder=pFolder.value.decode(),
                    timestamp=pTimestamp.contents.value)

                return itemInfo
        return False
    # Get download info for a subscribed item
    #
    # Arguments:
    # publishedFileId -- the id of the item whose download info to look up
    #
    # Return Value:
    # If download information is available returns a SimpleNamespace with
    # the following attributes
    # -- 'bytes_downloaded'- the amount of downloaded bytes
    # -- 'bytes_total' - the total amounts of bytes an item has
    #
    # If download information or steamworks or not available,
    # returns False
    @staticmethod
    def GetItemDownloadInfo(publishedFileId):
        if Steam.isSteamLoaded():
            pBytesDownloaded = pointer(c_uint64(0))
            pBytesTotal = pointer(c_uint64(0))
            # NOTE: pBytesTotal will only be valid after the download has started.
            downloadInfoAvailable = Steam.cdll.Workshop_GetItemDownloadInfo(publishedFileId, pBytesDownloaded, pBytesTotal)
            if downloadInfoAvailable:
                bytesDownloaded = pBytesDownloaded.contents.value
                bytesTotal = pBytesTotal.contents.value
                progress = 0
                if bytesTotal > 0 and bytesDownloaded > 0:
                    progress = bytesDownloaded / bytesTotal
                downloadInfo = SimpleNamespace(
                    bytes_downloaded=bytesDownloaded,
                    bytes_total=bytesTotal,
                    progress=progress)
                return downloadInfo
        return False
