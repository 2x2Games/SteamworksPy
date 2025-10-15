//===============================================
//  STEAMWORKS FOR PYTHON
//===============================================
//-----------------------------------------------
// Modify SW_PY based on operating system and include the proper Steamworks API file
//-----------------------------------------------
#if defined( _WIN32 )
	#include "steam\steam_api.h"
	#include "steam\isteamfriends.h"
	#include <iostream> 
	#define SW_PY extern "C" __declspec(dllexport)
#elif defined( __APPLE__ )
	#include "steam/steam_api.h"
	#include "TargetConditionals.h"
	#define SW_PY extern "C" __attribute__ ((visibility("default")))
#elif defined( __linux__ )
	#include "steam/steam_api.h"
	#define SW_PY extern "C" __attribute__ ((visibility("default")))
#else
	#error "Unsupported platform"
#endif
//-----------------------------------------------
// Definitions
//-----------------------------------------------
//#define IS_INIT_SUCCESS
#define IS_VALID
#define OFFLINE 0
#define ONLINE 1
#define BUSY 2
#define AWAY 3
#define SNOOZE 4
#define LF_TRADE
#define LF_PLAY
#define STATE_MAX
#define NOT_OFFLINE 8
#define ALL 9
#define TOP_LEFT 0
#define TOP_RIGHT 1
#define BOT_LEFT 2
#define BOT_RIGHT 3
#define OK 0
#define FAILED 1
#define ERR_NO_CLIENT 2
#define ERR_NO_CONNECTION 3
#define AVATAR_SMALL 0
#define AVATAR_MEDIUM 1
#define AVATAR_LARGE 2
#define GLOBAL 0
#define GLOBAL_AROUND_USER 1
#define FRIENDS 2
#define USERS 3
#define LOBBY_OK 0
#define LOBBY_NO_CONNECTION 1
#define LOBBY_TIMEOUT 2
#define LOBBY_FAIL 3
#define LOBBY_ACCESS_DENIED 4
#define LOBBY_LIMIT_EXCEEDED 5
#define PRIVATE 0
#define FRIENDS_ONLY 1
#define PUBLIC 2
#define INVISIBLE 3
#define LOBBY_KEY_LENGTH 255
#define UGC_MAX_TITLE_CHARS 128
#define UGC_MAX_DESC_CHARS 8000
#define UGC_MAX_METADATA_CHARS 5000
#define UGC_ITEM_COMMUNITY 0
#define UGC_ITEM_MICROTRANSACTION 1
#define UGC_STATE_NONE 0
#define UGC_STATE_SUBSCRIBED 1
#define UGC_STATE_LEGACY 2
#define UGC_STATE_INSTALLED 4
#define UGC_STATE_UPDATE 8
#define UGC_STATE_DOWNLOADING 16
#define UGC_STATE_PENDING 32
#define STATUS_INVALID 0
#define STATUS_PREPARING_CONFIG 1
#define STATUS_PREPARING_CONTENT 2
#define STATUS_UPLOADING_CONTENT 3
#define STATUS_UPLOADING_PREVIEW 4
#define STATUS_COMMITTING_CHANGES 5
typedef void(*CreateItemResultCallback_t) (CreateItemResult_t);
typedef void(*SubmitItemUpdateResultCallback_t) (SubmitItemUpdateResult_t);
typedef void(*ItemInstalledCallback_t) (ItemInstalled_t);
typedef void(*LeaderboardFindResultCallback_t) (LeaderboardFindResult_t);
typedef void(*GameOverlayActivatedCallback_t) (GameOverlayActivated_t);
typedef void(*ScreenshotReadyCallback_t) (ScreenshotReady_t);
typedef void(*UserStatsReceivedCallback_t) (UserStatsReceived_t);
typedef void(*GlobalStatsReceivedCallback_t) (GlobalStatsReceived_t);
typedef void(*DeleteItemResultCallback_t) (DeleteItemResult_t);
typedef void(*DownloadItemResultCallback_t) (DownloadItemResult_t);
typedef void(*SteamUGCDetailsCallback_t) (SteamUGCDetails_t);
//-----------------------------------------------
// Workshop Class
//-----------------------------------------------
class Workshop
{
public:
	CreateItemResultCallback_t _pyItemCreatedCallback;
	SubmitItemUpdateResultCallback_t _pyItemUpdatedCallback;
	ItemInstalledCallback_t _pyItemInstalledCallback;
	SteamUGCDetailsCallback_t _pySteamUGCDetailsCallback;

	CCallResult<Workshop, CreateItemResult_t> _itemCreatedCallback;
	CCallResult<Workshop, SubmitItemUpdateResult_t> _itemUpdatedCallback;
	CCallResult<Workshop, SteamUGCQueryCompleted_t> _queryCompletedCallback;

	CCallback<Workshop, ItemInstalled_t> _itemInstalledCallback;

	Workshop() : _itemInstalledCallback(this, &Workshop::OnItemInstalled) {}

	void SetItemCreatedCallback(CreateItemResultCallback_t callback){
		_pyItemCreatedCallback = callback;
	}
	void SetItemUpdatedCallback(SubmitItemUpdateResultCallback_t callback){
		_pyItemUpdatedCallback = callback;
	}

	void SetItemInstalledCallback(ItemInstalledCallback_t callback){
		_pyItemInstalledCallback = callback;
	}
	void ClearItemInstallCallback(){
		_pyItemInstalledCallback = nullptr;
	}

	void SetSteamUGCDetailsCallback(SteamUGCDetailsCallback_t callback) {
		_pySteamUGCDetailsCallback = callback;
	}
	void ClearSteamUGCDetailsCallback() {
		_pySteamUGCDetailsCallback = nullptr;
	}

	void CreateItem(AppId_t consumerAppId, EWorkshopFileType fileType){
		//TODO: Check if fileType is a valid value?
		const SteamAPICall_t createItemCall = SteamUGC()->CreateItem(consumerAppId, fileType);
		_itemCreatedCallback.Set(createItemCall, this, &Workshop::OnWorkshopItemCreated);
	}
	void SubmitItemUpdate(UGCUpdateHandle_t updateHandle, const char *pChangeNote){
		const SteamAPICall_t submitItemUpdateCall = SteamUGC()->SubmitItemUpdate(updateHandle, pChangeNote);
		_itemUpdatedCallback.Set(submitItemUpdateCall, this, &Workshop::OnItemUpdateSubmitted);
	}

	void QueryUGCItem(PublishedFileId_t nPublishedFileID) {
		const UGCQueryHandle_t handle = SteamUGC()->CreateQueryUGCDetailsRequest(&nPublishedFileID, 1);
		const SteamAPICall_t sendQueryCall = SteamUGC()->SendQueryUGCRequest(handle);
		_queryCompletedCallback.Set(sendQueryCall, this, &Workshop::OnSteamUGCQueryCompleted);
	}

private:
	void OnWorkshopItemCreated(CreateItemResult_t *createItemResult, bool bIOFailure) {
		if(_pyItemCreatedCallback != nullptr && !bIOFailure) {
			_pyItemCreatedCallback(*createItemResult);
		}
	}
	void OnItemUpdateSubmitted(SubmitItemUpdateResult_t *submitItemUpdateResult, bool bIOFailure) {
		if(_pyItemUpdatedCallback != nullptr && !bIOFailure) {
			_pyItemUpdatedCallback(*submitItemUpdateResult);
		}
	}
	void OnItemInstalled(ItemInstalled_t *itemInstalledResult) {
		if(_pyItemInstalledCallback != nullptr && itemInstalledResult->m_unAppID == SteamUtils()->GetAppID()) {
			_pyItemInstalledCallback(*itemInstalledResult);
		}
	}
	void OnSteamUGCQueryCompleted(SteamUGCQueryCompleted_t *pCallback, bool bIOFailure) {
		if (pCallback->m_eResult == k_EResultOK && !bIOFailure) {
			SteamUGCDetails_t details;
			if (SteamUGC()->GetQueryUGCResult(pCallback->m_handle, 0, &details)) {
				_pySteamUGCDetailsCallback(details);
			}
		}

		ClearSteamUGCDetailsCallback();
		SteamUGC()->ReleaseQueryUGCRequest(pCallback->m_handle);
	}
};

static Workshop workshop;
//-----------------------------------------------
// Leaderboard Class
//-----------------------------------------------
class Leaderboard
{
public:
	LeaderboardFindResultCallback_t _pyLeaderboardFindResultCallback;

	CCallResult<Leaderboard, LeaderboardFindResult_t> _leaderboardFindResultCallback;

	void SetLeaderboardFindResultCallback(LeaderboardFindResultCallback_t callback){
		_pyLeaderboardFindResultCallback = callback;
	}
	void FindLeaderboard(const char *pchLeaderboardName){
		SteamAPICall_t leaderboardFindResultCall = SteamUserStats()->FindLeaderboard(pchLeaderboardName);
		_leaderboardFindResultCallback.Set(leaderboardFindResultCall, this, &Leaderboard::OnLeaderboardFindResult);
	}
private:
	void OnLeaderboardFindResult(LeaderboardFindResult_t *leaderboardFindResult, bool bIOFailure) {
		if(_pyLeaderboardFindResultCallback != nullptr && !bIOFailure) {
			_pyLeaderboardFindResultCallback(*leaderboardFindResult);
		}
	}
};
static Leaderboard leaderboard;
//-----------------------------------------------
// Callbacks class
//-----------------------------------------------
class SteamCallbacks
{
public:
	void SetGameOverlayActivatedCallback(GameOverlayActivatedCallback_t callback) {
		_pyGameOverlayActivatedCallback = callback;
	}

	void SetScreenshotReadyCallback(ScreenshotReadyCallback_t callback) {
		_pyScreenshotReadyCallback = callback;
	}

	void SetUserStatsReceivedCallback(UserStatsReceivedCallback_t callback) {
		_pyUserStatsReceivedCallback = callback;
	}

	void SetGlobalStatsReceivedCallback(GlobalStatsReceivedCallback_t callback) {
		_pyGlobalStatsReceivedCallback = callback;
	}

	void SetDeleteItemResultCallback(DeleteItemResultCallback_t callback) {
		_pyDeleteItemResultCallback = callback;
	}

	void SetDownloadItemResultCallback(DownloadItemResultCallback_t callback) {
		_pyDownloadItemResultCallback = callback;
	}

	void RequestGlobalStats(int nHistoryDays) {
		const SteamAPICall_t hSteamAPICall = SteamUserStats()->RequestGlobalStats(nHistoryDays);
		_RequestGlobalStatsCallResult.Set(hSteamAPICall, this, &SteamCallbacks::OnGlobalStatsReceived);
	}

	void DeleteItem(PublishedFileId_t nPublishedFileID) {
		const SteamAPICall_t hSteamAPICall = SteamUGC()->DeleteItem(nPublishedFileID);
		_DeleteItemResult.Set(hSteamAPICall, this, &SteamCallbacks::OnItemDeleted);
	}

	bool DownloadItem(PublishedFileId_t nPublishedFileID, bool bHighPriority) {
		return SteamUGC()->DownloadItem(nPublishedFileID, bHighPriority);
	}

private:
	CCallResult< SteamCallbacks, GlobalStatsReceived_t > _RequestGlobalStatsCallResult;
	CCallResult< SteamCallbacks, DeleteItemResult_t > _DeleteItemResult;

	STEAM_CALLBACK(SteamCallbacks, OnGameOverlayActivated, GameOverlayActivated_t);
	STEAM_CALLBACK(SteamCallbacks, OnScreenshotReady, ScreenshotReady_t);
	STEAM_CALLBACK(SteamCallbacks, OnUserStatsReceived, UserStatsReceived_t);
	STEAM_CALLBACK(SteamCallbacks, OnUserStatsStored, UserStatsStored_t);
	STEAM_CALLBACK(SteamCallbacks, OnItemDownloaded, DownloadItemResult_t);

	GameOverlayActivatedCallback_t _pyGameOverlayActivatedCallback = nullptr;
	ScreenshotReadyCallback_t _pyScreenshotReadyCallback = nullptr;
	UserStatsReceivedCallback_t _pyUserStatsReceivedCallback = nullptr;
	GlobalStatsReceivedCallback_t _pyGlobalStatsReceivedCallback = nullptr;
	DeleteItemResultCallback_t _pyDeleteItemResultCallback = nullptr;
	DownloadItemResultCallback_t _pyDownloadItemResultCallback = nullptr;

	void OnGlobalStatsReceived(GlobalStatsReceived_t *pCallback, bool bIOFailure) {
		if (_pyGlobalStatsReceivedCallback != nullptr && !bIOFailure && pCallback->m_eResult == k_EResultOK && SteamUtils()->GetAppID() == pCallback->m_nGameID) {
			_pyGlobalStatsReceivedCallback(*pCallback);
		}
	}

	void OnItemDeleted(DeleteItemResult_t *pCallback, bool bIOFailure) {
		if (_pyDeleteItemResultCallback != nullptr && !bIOFailure && pCallback->m_eResult == k_EResultOK) {
			_pyDeleteItemResultCallback(*pCallback);
		}
	}
};

void SteamCallbacks::OnGameOverlayActivated(GameOverlayActivated_t *pCallback) {
	if (_pyGameOverlayActivatedCallback != nullptr) {
		_pyGameOverlayActivatedCallback(*pCallback);
	}
}

void SteamCallbacks::OnScreenshotReady(ScreenshotReady_t *pCallback) {
	if (_pyScreenshotReadyCallback != nullptr && pCallback->m_eResult == k_EResultOK) {
		_pyScreenshotReadyCallback(*pCallback);
	}
}

void SteamCallbacks::OnUserStatsReceived(UserStatsReceived_t *pCallback) {
	if (_pyUserStatsReceivedCallback != nullptr && SteamUtils()->GetAppID() == pCallback->m_nGameID && pCallback->m_eResult == k_EResultOK) {
      _pyUserStatsReceivedCallback(*pCallback);
	}
}

void SteamCallbacks::OnUserStatsStored(UserStatsStored_t *pCallback) {
  const uint64 appID = SteamUtils()->GetAppID();
  if(pCallback->m_nGameID == appID && pCallback->m_eResult == k_EResultInvalidParam) {
    // One or more stats we set broke a constraint. They've been reverted,
    // and we should re-iterate the values now to keep in sync.
    // Fake up a callback here so that we re-load the values.
    UserStatsReceived_t callback;
    callback.m_eResult = k_EResultOK;
    callback.m_nGameID = appID;
    OnUserStatsReceived(&callback);
  }
}

void SteamCallbacks::OnItemDownloaded(DownloadItemResult_t *pCallback) {
	if (_pyDownloadItemResultCallback != nullptr && pCallback->m_unAppID == SteamUtils()->GetAppID() && pCallback->m_eResult == k_EResultOK) {
		_pyDownloadItemResultCallback(*pCallback);
	}
}

static SteamCallbacks callbacks;


SW_PY void Callbacks_SetGameOverlayActivatedCallback(GameOverlayActivatedCallback_t callback) {
	callbacks.SetGameOverlayActivatedCallback(callback);
}
SW_PY void Callbacks_SetScreenshotReadyCallback(ScreenshotReadyCallback_t callback) {
	callbacks.SetScreenshotReadyCallback(callback);
}
SW_PY void Callbacks_SetUserStatsReceivedCallback(UserStatsReceivedCallback_t callback) {
	callbacks.SetUserStatsReceivedCallback(callback);
}
SW_PY void Callbacks_SetGlobalStatsReceivedCallback(GlobalStatsReceivedCallback_t callback) {
	callbacks.SetGlobalStatsReceivedCallback(callback);
}
SW_PY void Stats_RequestGlobalStats(int nHistoryDays) {
	callbacks.RequestGlobalStats(nHistoryDays);
}
SW_PY void Workshop_DeleteItem(PublishedFileId_t nPublishedFileID) {
	callbacks.DeleteItem(nPublishedFileID);
}
SW_PY void Workshop_SetDeleteItemResultCallback(DeleteItemResultCallback_t callback) {
	callbacks.SetDeleteItemResultCallback(callback);
}
SW_PY bool Workshop_DownloadItem(PublishedFileId_t nPublishedFileID, bool bHighPriority) {
	return callbacks.DownloadItem(nPublishedFileID, bHighPriority);
}
SW_PY void Workshop_SetDownloadItemResultCallback(DownloadItemResultCallback_t callback) {
	callbacks.SetDownloadItemResultCallback(callback);
}


//-----------------------------------------------
// Steamworks functions
//-----------------------------------------------
SW_PY bool SteamInit(){
	return SteamAPI_Init();
}
SW_PY void SteamShutdown() {
  SteamAPI_Shutdown();
}
// Returns true/false if Steam is running
SW_PY bool IsSteamRunning(void){
	return SteamAPI_IsSteamRunning();
}
CSteamID CreateSteamID(uint32 steamID, int accountType){
	CSteamID cSteamID;
	if(accountType < 0 || accountType >= k_EAccountTypeMax){
		accountType = 1;
	}
	cSteamID.Set(steamID, EUniverse(k_EUniversePublic), EAccountType(accountType));
	return cSteamID;
}
// Callbacks
SW_PY void RunCallbacks(){
	SteamAPI_RunCallbacks();
}
//-----------------------------------------------
// Steam Apps
//-----------------------------------------------
SW_PY int HasOtherApp(int32 value){
	if(SteamApps() == NULL){
		return false;
	}
	return SteamApps()->BIsSubscribedApp((AppId_t)value);
}
SW_PY int GetDlcCount(){
	if(SteamApps() == NULL){
		return 0;
	}
	return SteamApps()->GetDLCCount();
}
SW_PY bool IsDlcInstalled(int32 value){
	if(SteamApps() == NULL){
		return false;
	}
	return SteamApps()->BIsDlcInstalled(value);
}
SW_PY bool IsAppInstalled(int32 value){
	if(SteamApps() == NULL){
		return false;
	}
	return SteamApps()->BIsAppInstalled((AppId_t)value);
}
SW_PY const char* GetCurrentGameLanguage(){
	if(SteamApps() == NULL){
		return "None";
	}
	return SteamApps()->GetCurrentGameLanguage();
}
//-----------------------------------------------
// Steam Friends
//-----------------------------------------------
SW_PY int GetFriendCount(int flag){
	if(SteamFriends() == NULL){
		return 0;
	}
	return SteamFriends()->GetFriendCount(flag);
}
SW_PY uint64 GetFriendByIndex(int thisFriend){
	CSteamID friendID = SteamFriends()->GetFriendByIndex(thisFriend, 0xFFFF);
	return friendID.ConvertToUint64();
}
SW_PY const char* GetPersonaName(){
	if(SteamFriends() == NULL){
		return "";
	}
	return SteamFriends()->GetPersonaName();
}
SW_PY int GetPersonaState(){
	if(SteamFriends() == NULL){
		return 0;
	}
	return SteamFriends()->GetPersonaState();
}
SW_PY const char* GetFriendPersonaName(int steamID){
	if(SteamFriends() != NULL && steamID > 0){
		// Add 1 here to prevent error
		CSteamID friendID = CreateSteamID(steamID, 1);
		bool isDataLoading = SteamFriends()->RequestUserInformation(friendID, true);
		if(!isDataLoading){
			return SteamFriends()->GetFriendPersonaName(friendID);
		}
	}
	return "";
}
SW_PY bool SetRichPresence(const char *serverKey, const char *serverValue){
	if(SteamFriends() == NULL){
		return false;
	}
	return SteamFriends()->SetRichPresence(serverKey, serverValue);
}
SW_PY void ClearRichPresence(){
	if(SteamFriends() == NULL){
		return;
	}
	SteamFriends()->ClearRichPresence();
}
SW_PY void InviteFriend(int steamID, const char* conString){
	if(SteamFriends() == NULL){
		return;
	}
	CSteamID friendID = CreateSteamID(steamID, 1);
	SteamFriends()->InviteUserToGame(friendID, conString);
}
SW_PY void SetPlayedWith(int steamID){
	if(SteamFriends() == NULL){
		return;
	}
	CSteamID friendID = CreateSteamID(steamID, 1);
	SteamFriends()->SetPlayedWith(friendID);
}
// SW_PY GetRecentPlayers
// SW_PY GetFriendAvatar
// SW_PY DrawAvatar
SW_PY void ActivateGameOverlay(const char* name){
	if(SteamFriends() == NULL){
		return;
	}
	SteamFriends()->ActivateGameOverlay(name);	
}
SW_PY void ActivateGameOverlayToUser(const char* url, int steamID){
	if(SteamFriends() == NULL){
		return;
	}
	CSteamID overlayUserID = CreateSteamID(steamID, 1);
	SteamFriends()->ActivateGameOverlayToUser(url, overlayUserID);
}
SW_PY void ActivateGameOverlayToWebPage(const char* url){
	if(SteamFriends() == NULL){
		return;
	}
	SteamFriends()->ActivateGameOverlayToWebPage(url);
}
SW_PY void ActivateGameOverlayToStore(int app_id){
	if(SteamFriends() == NULL){
		return;
	}
	SteamFriends()->ActivateGameOverlayToStore(AppId_t(app_id), EOverlayToStoreFlag(0));
}
SW_PY void ActivateGameOverlayInviteDialog(int steamID){
	if(SteamFriends() == NULL){
		return;
	}
	CSteamID lobbyID = CreateSteamID(steamID, 1);
	SteamFriends()->ActivateGameOverlayInviteDialog(lobbyID);
}
//-----------------------------------------------
// Steam Matchmaking
//-----------------------------------------------
SW_PY void CreateLobby(int lobbyType, int cMaxMembers){
	if(SteamMatchmaking() == NULL){
		return;
	}
	ELobbyType eLobbyType;
	// Convert the lobby type back over
	if(lobbyType == PRIVATE){
		eLobbyType = k_ELobbyTypePrivate;
	}
	else if(lobbyType == FRIENDS_ONLY){
		eLobbyType = k_ELobbyTypeFriendsOnly;
	}
	else if(lobbyType == PUBLIC){
		eLobbyType = k_ELobbyTypePublic;	
	}
	else{
		eLobbyType = k_ELobbyTypeInvisible;
	}
	SteamMatchmaking()->CreateLobby(eLobbyType, cMaxMembers);
}
SW_PY void JoinLobby(int steamIDLobby){
	if(SteamMatchmaking() == NULL){
		return;
	}
	CSteamID lobbyID = CreateSteamID(steamIDLobby, 1);
	SteamMatchmaking()->JoinLobby(lobbyID);
}
SW_PY void LeaveLobby(int steamIDLobby){
	if(SteamMatchmaking() == NULL){
		return;
	}
	CSteamID lobbyID = CreateSteamID(steamIDLobby, 1);
	return SteamMatchmaking()->LeaveLobby(lobbyID);
}
SW_PY bool InviteUserToLobby(int steamIDLobby, int steamIDInvitee){
	if(SteamMatchmaking() == NULL){
		return 0;
	}
	CSteamID lobbyID = CreateSteamID(steamIDLobby, 1);
	CSteamID inviteeID = CreateSteamID(steamIDInvitee, 1);
	return SteamMatchmaking()->InviteUserToLobby(lobbyID, inviteeID);
}
//-----------------------------------------------
// Steam Music
//-----------------------------------------------
SW_PY bool MusicIsEnabled(){
	if(SteamMusic() == NULL){
		return false;
	}
	return SteamMusic()->BIsEnabled();
}
SW_PY bool MusicIsPlaying(){
	if(SteamMusic() == NULL){
		return false;
	}
	return SteamMusic()->BIsPlaying();
}
SW_PY float MusicGetVolume(){
	if(SteamMusic() == NULL){
		return 0;
	}
	return SteamMusic()->GetVolume();
}
SW_PY void MusicPause(){
	if(SteamMusic() == NULL){
		return;
	}
	return SteamMusic()->Pause();
}
SW_PY void MusicPlay(){
	if(SteamMusic() == NULL){
		return;
	}
	return SteamMusic()->Play();
}
SW_PY void MusicPlayNext(){
	if(SteamMusic() == NULL){
		return;
	}
	return SteamMusic()->PlayNext();
}
SW_PY void MusicPlayPrev(){
	if(SteamMusic() == NULL){
		return;
	}
	return SteamMusic()->PlayPrevious();
}
SW_PY void MusicSetVolume(float value){
	if(SteamMusic() == NULL){
		return;
	}
	return SteamMusic()->SetVolume(value);
}
//-----------------------------------------------
// Steam Screenshots
//-----------------------------------------------
SW_PY void TriggerScreenshot(){
	if(SteamScreenshots() == NULL){
		return;
	}
	SteamScreenshots()->TriggerScreenshot();
}
SW_PY bool SetScreenshotLocation(ScreenshotHandle hScreenshot, const char *pchLocation) {
	if (SteamScreenshots() == NULL) {
		return false;
	}
	return SteamScreenshots()->SetLocation(hScreenshot, pchLocation);
}
//-----------------------------------------------
// Steam User
//-----------------------------------------------
SW_PY uint64 GetSteamID(){
	if(SteamUser() == NULL){
		return 0;
	}
	CSteamID steamID = SteamUser()->GetSteamID();
	return steamID.ConvertToUint64();
}
SW_PY int GetPlayerSteamLevel(){
	if(SteamUser() == NULL){
		return 0;
	}
	return SteamUser()->GetPlayerSteamLevel(); 
}
SW_PY const char* GetUserDataFolder(){
	if(SteamUser() == NULL){
		return "";
	}
	const int cubBuffer = 256;
	char *pchBuffer = new char[cubBuffer];
	SteamUser()->GetUserDataFolder((char*)pchBuffer, cubBuffer);
	char *data_path = pchBuffer;
	delete pchBuffer;
	return data_path;
}
//-----------------------------------------------
// Steam User Stats
//-----------------------------------------------
SW_PY bool ClearAchievement(const char* name){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->ClearAchievement(name);
}
SW_PY bool IndicateAchievementProgress(const char *name, uint32 nCurProgress, uint32 nMaxProgress){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->IndicateAchievementProgress(name, nCurProgress, nMaxProgress);
}
SW_PY bool GetAchievement(const char* name) {
	if (SteamUser() == NULL) {
		return false;
	}
	bool achieved = false;
	SteamUserStats()->GetAchievement(name, &achieved);
	return achieved;
}
SW_PY float GetStatFloat(const char* name){
	if(SteamUser() == NULL){
		return 0;
	}
	float statval = 0;
	SteamUserStats()->GetStat(name, &statval);
	return statval;
}
SW_PY int32 GetStatInt(const char* name){
	if(SteamUser() == NULL){
		return 0;
	}
	int32 statval = 0;
	SteamUserStats()->GetStat(name, &statval);
	return statval;
}
SW_PY double GetGlobalStatFloat(const char* name) {
	if (SteamUser() == NULL) {
		return 0;
	}
	double statval = 0;
	SteamUserStats()->GetGlobalStat(name, &statval);
	return statval;
}
SW_PY int64 GetGlobalStatInt(const char* name) {
	if (SteamUser() == NULL) {
		return 0;
	}
	int64 statval = 0;
	SteamUserStats()->GetGlobalStat(name, &statval);
	return statval;
}
SW_PY bool ResetAllStats(bool achievesToo){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->ResetAllStats(achievesToo);
}
SW_PY bool RequestCurrentStats(){
	if(SteamUser() == NULL || SteamUserStats() == NULL || !SteamUser()->BLoggedOn()){
		return false;
	}
	return SteamUserStats()->RequestCurrentStats();
}
SW_PY bool SetAchievement(const char* name){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->SetAchievement(name);
}
SW_PY bool SetStatFloat(const char* name, float value){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->SetStat(name, value);
}
SW_PY bool SetStatInt(const char* name, int32 value){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->SetStat(name, value);
}
SW_PY bool StoreStats(){
	if(SteamUser() == NULL){
		return false;
	}
	return SteamUserStats()->StoreStats();
}
//SW_PY const char* GetLeaderboardName()
//SW_PY int GetLeaderboardEntryCount()
//SW_PY void DownloadLeaderboardEntries()
//SW_PY void DownloadLeaderboardEntriesForUsers()
//SW_PY void UploadLeaderboardScore()
//SW_PY void GetDownloadLeaderboardEntry()
//SW_PY void UpdateLeaderboardHandle()
//SW_PY uint64 GetLeaderboardHandle()
//SW_PY void GetLeaderBoardEntries()
//-----------------------------------------------
// Steam Utilities
//-----------------------------------------------
SW_PY uint8 GetCurrentBatteryPower(){
	if(SteamUtils() == NULL){
		return 0;
	}
	return SteamUtils()->GetCurrentBatteryPower();
}
SW_PY bool GetEnteredGamepadTextInput(char* buffer, uint32 length){
    if(SteamUtils() == NULL){
        return false;
    }

    return SteamUtils()->GetEnteredGamepadTextInput(buffer, length);
}
SW_PY uint32 GetEnteredGamepadTextLength(){
	if(SteamUtils() == NULL){
		return 0;
	}
	return SteamUtils()->GetEnteredGamepadTextLength();
}
SW_PY const char* GetIPCountry(){
	if(SteamUtils() == NULL){
		return "None";
	}
	return SteamUtils()->GetIPCountry();
}
SW_PY uint32 GetSecondsSinceAppActive(){
	if(SteamUtils() == NULL){
		return 0;
	}
	return SteamUtils()->GetSecondsSinceAppActive();
}
SW_PY uint32 GetSecondsSinceComputerActive(){
	if(SteamUtils() == NULL){
		return 0;
	}
	return SteamUtils()->GetSecondsSinceComputerActive();
}
SW_PY uint32 GetServerRealTime(){
	if(SteamUtils() == NULL){
		return 0;
	}
	return SteamUtils()->GetServerRealTime();
}
SW_PY bool IsOverlayEnabled(){
	if(SteamUtils() == NULL){
		return false;
	}
	return SteamUtils()->IsOverlayEnabled();
}
SW_PY bool IsSteamInBigPictureMode() {
    if (SteamUtils() == NULL) {
        return false;
    }
    return SteamUtils()->IsSteamInBigPictureMode();
}
SW_PY bool IsSteamRunningInVR(){
	if(SteamUtils() == NULL){
		return false;
	}
	return SteamUtils()->IsSteamRunningInVR();
}
SW_PY bool IsSteamRunningOnSteamDeck(){
	if(SteamUtils() == NULL){
		return false;
	}
	return SteamUtils()->IsSteamRunningOnSteamDeck();
}
SW_PY const char* GetSteamUILanguage(){
	if(SteamUtils() == NULL){
		return "None";
	}
	return SteamUtils()->GetSteamUILanguage();
}
SW_PY uint32 GetAppID(){
	if(SteamUtils() == NULL){
		return 0;
	}
	return SteamUtils()->GetAppID();
}
SW_PY void SetOverlayNotificationPosition(int pos){
	if((pos < 0) || (pos > 3) || (SteamUtils() == NULL)){
		return;
	}
	SteamUtils()->SetOverlayNotificationPosition(ENotificationPosition(pos));
}
SW_PY bool ShowGamepadTextInput(int inputMode, int lineInputMode, const char *description, uint32 maxText,
                                const char *presetText) {
    if (SteamUtils() == NULL) {
        return false;
    }
    // Convert modes
    EGamepadTextInputMode mode;
    if (inputMode == 0) {
        mode = k_EGamepadTextInputModeNormal;
    } else {
        mode = k_EGamepadTextInputModePassword;
    }
    EGamepadTextInputLineMode lineMode;
    if (lineInputMode == 0) {
        lineMode = k_EGamepadTextInputLineModeSingleLine;
    } else {
        lineMode = k_EGamepadTextInputLineModeMultipleLines;
    }
    return SteamUtils()->ShowGamepadTextInput(mode, lineMode, description, maxText, presetText);
}
//-----------------------------------------------
// Steam Workshop
//-----------------------------------------------
SW_PY void Workshop_SetItemCreatedCallback(CreateItemResultCallback_t callback){
	if(SteamUGC() == NULL){
		return;
	}
	workshop.SetItemCreatedCallback(callback);
}
SW_PY void Workshop_CreateItem(AppId_t consumerAppId, EWorkshopFileType fileType){
	if(SteamUGC() == NULL){
		return;
	}
	workshop.CreateItem(consumerAppId, fileType);
}
SW_PY void Workshop_QueryUGCItem(PublishedFileId_t nPublishedFileID) {
	if (SteamUGC() == NULL) {
		return;
	}
	workshop.QueryUGCItem(nPublishedFileID);
}
SW_PY UGCUpdateHandle_t Workshop_StartItemUpdate(AppId_t consumerAppId, PublishedFileId_t publishedFileId){
	return SteamUGC()->StartItemUpdate(consumerAppId, publishedFileId);
}
SW_PY bool Workshop_SetItemTitle(UGCUpdateHandle_t updateHandle, const char *pTitle){
	if(SteamUGC() == NULL){
		return false;
	}
	if (strlen(pTitle) > UGC_MAX_TITLE_CHARS){
		printf("Title cannot have more than %d ASCII characters. Title not set.", UGC_MAX_TITLE_CHARS);
		return false;
	}
	return SteamUGC()->SetItemTitle(updateHandle, pTitle);
}
SW_PY bool Workshop_SetItemDescription(UGCUpdateHandle_t updateHandle, const char *pDescription){
	if(SteamUGC() == NULL){
		return false;
	}
	if (strlen(pDescription) > UGC_MAX_DESC_CHARS){
		printf("Description cannot have more than %d ASCII characters. Description not set.", UGC_MAX_DESC_CHARS);
		return false;
	}
	return SteamUGC()->SetItemDescription(updateHandle, pDescription);
}
SW_PY bool Workshop_SetItemUpdateLanguage(UGCUpdateHandle_t updateHandle, const char *pLanguage){
	if(SteamUGC() == NULL){
		return false;
	}
	return SteamUGC()->SetItemUpdateLanguage(updateHandle, pLanguage);
}
SW_PY bool Workshop_SetItemMetadata(UGCUpdateHandle_t updateHandle, const char *pMetadata){
	if(SteamUGC() == NULL){
		return false;
	}
	if (strlen(pMetadata) > UGC_MAX_METADATA_CHARS){
		printf("Metadata cannot have more than %d ASCII characters. Metadata not set.", UGC_MAX_METADATA_CHARS);
	}
	return SteamUGC()->SetItemMetadata(updateHandle, pMetadata);
}
SW_PY bool Workshop_SetItemVisibility(UGCUpdateHandle_t updateHandle, int visibility){
	if(SteamUGC() == NULL){
		return false;
	}
	return SteamUGC()->SetItemVisibility(updateHandle, static_cast<ERemoteStoragePublishedFileVisibility>(visibility));
}

SW_PY bool Workshop_SetItemTags(UGCUpdateHandle_t updateHandle, const char ** stringArray, const int32 stringCount){
	if(SteamUGC() == NULL){
		return false;
	}
	const SteamParamStringArray_t tags = { stringArray, stringCount };	
	return SteamUGC()->SetItemTags(updateHandle, &tags);
}
SW_PY bool Workshop_SetItemContent(UGCUpdateHandle_t updateHandle, const char *pContentFolder){
	if(SteamUGC() == NULL){
		return false;
	}
	return SteamUGC()->SetItemContent(updateHandle, pContentFolder);
}
SW_PY bool Workshop_SetItemPreview(UGCUpdateHandle_t updateHandle, const char *pPreviewFile){
	if(SteamUGC() == NULL){
		return false;
	}
	return SteamUGC()->SetItemPreview(updateHandle, pPreviewFile);
}
SW_PY void Workshop_SetItemUpdatedCallback(SubmitItemUpdateResultCallback_t callback){
	if(SteamUGC() == NULL){
		return;
	}
	workshop.SetItemUpdatedCallback(callback);
}
SW_PY void Workshop_SubmitItemUpdate(UGCUpdateHandle_t updateHandle, const char *pChangeNote){
	if(SteamUGC() == NULL){
		return;
	}
	workshop.SubmitItemUpdate(updateHandle, pChangeNote);
}
SW_PY int Workshop_GetItemUpdateProgress(UGCUpdateHandle_t handle, uint64 *punBytesProcessed, uint64* punBytesTotal){
	return static_cast<int>(SteamUGC()->GetItemUpdateProgress(handle, punBytesProcessed, punBytesTotal));;
}
SW_PY uint32 Workshop_GetNumSubscribedItems() {
  if(SteamUGC() == NULL){
    return 0;
  }
  return SteamUGC()->GetNumSubscribedItems();
}
SW_PY uint32 Workshop_GetSubscribedItems(PublishedFileId_t* pvecPublishedFileID, uint32 maxEntries){
	if(SteamUGC() == NULL){
		return 0;
	}
	return SteamUGC()->GetSubscribedItems(pvecPublishedFileID, maxEntries);
}
SW_PY uint32 Workshop_GetItemState(PublishedFileId_t publishedFileID){
	if(SteamUGC() == NULL){
		return 0;
	}
	return SteamUGC()->GetItemState(publishedFileID);
}
SW_PY void Workshop_SetItemInstalledCallback(ItemInstalledCallback_t callback){
	if(SteamUGC() == NULL){
		return;
	}
	workshop.SetItemInstalledCallback(callback);
}
SW_PY void Workshop_ClearItemInstalledCallback(){
	if(SteamUGC() == NULL){
		return;
	}
	workshop.ClearItemInstallCallback();
}

SW_PY void Workshop_SetSteamUGCDetailsCallback(SteamUGCDetailsCallback_t callback) {
	if (SteamUGC() == NULL) {
		return;
	}
	workshop.SetSteamUGCDetailsCallback(callback);
}
SW_PY void Workshop_ClearSteamUGCDetailsCallback() {
	if (SteamUGC() == NULL) {
		return;
	}
	workshop.ClearSteamUGCDetailsCallback();
}

SW_PY bool Workshop_GetItemInstallInfo(PublishedFileId_t nPublishedFileID, uint64 *punSizeOnDisk, char *pchFolder, uint32 cchFolderSize, uint32 *punTimeStamp){
	if(SteamUGC() == NULL){
		return false;
	}
	return SteamUGC()->GetItemInstallInfo(nPublishedFileID, punSizeOnDisk, pchFolder, cchFolderSize, punTimeStamp);
}
SW_PY bool Workshop_GetItemDownloadInfo(PublishedFileId_t publishedFileID, uint64 *punBytesDownloaded, uint64 *punBytesTotal){
	if(SteamUGC() == NULL){
		return false;
	}
	return SteamUGC()->GetItemDownloadInfo(publishedFileID, punBytesDownloaded, punBytesTotal);
}
//-----------------------------------------------
// Steam Leaderboard
//-----------------------------------------------
SW_PY void Leaderboard_SetFindLeaderboardResultCallback(LeaderboardFindResultCallback_t callback){
	if(SteamUserStats() == NULL){
		return;
	}
	leaderboard.SetLeaderboardFindResultCallback(callback);
}
SW_PY void Leaderboard_FindLeaderboard(const char *pchLeaderboardName){
	if(SteamUserStats() == NULL){
		return;
	}
	leaderboard.FindLeaderboard(pchLeaderboardName);
}
