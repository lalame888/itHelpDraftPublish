![image](https://github.com/lalame888/itHelpDraftPublish/assets/43725404/94cd0bec-2d95-4650-a2c9-4534353e8a14)# itHelpDraftPublish
IT邦幫忙鐵人賽發文神器  
只要貼上登入token就可以檢視目前草稿的標題與數量  
並且可開關自動發文功能，每天於設定時間（預設為10:00:00，可以更動)自動貼一篇貼文  
避免失去挑戰資格  
若有串接line notify  
於發文後也會傳送line通知，或是程式崩潰時也會傳送通知  

設定步驟：
## Step1: 取得Cookie
  登入IT邦幫忙主頁 : https://ithelp.ithome.com.tw/  
  確定已經登入之後，按下F12，然後再重整一次    
  這時候點到F12中的網路，找到最上方的request  
  查看請求(request)的標頭Header中的 Cookie  
  ![取得cookie](https://raw.githubusercontent.com/lalame888/itHelpDraftPublish/master/%E5%8F%96%E5%BE%97cookie.png)
  就是圖片中反白的那一大塊  
  複製之後，把他貼到itHelpConfig.ini中  
  ![貼上cookie](https://github.com/lalame888/itHelpDraftPublish/blob/master/%E8%B2%BC%E4%B8%8Acookie.png?raw=true)
  (圖片中露出來的cookie是不同的登入帳號，所以內容長不一樣正常的，單純示範)  
  
## Step2: 設定 line notify token (可跳過）
  如果希望程式起動與發佈貼文之後可以透過line傳送訊息給自己  
  先進入到 https://notify-bot.line.me/zh_TW/
  然後登入之後，右上角名字選單點開，點擊「個人頁面」  
  ![line notify - 1](https://github.com/lalame888/itHelpDraftPublish/blob/master/lineNotify%20-1.png?raw=true)

  接著頁面來到最下方，點擊發行權杖 
  ![line notify - 2](https://github.com/lalame888/itHelpDraftPublish/blob/master/line%20notify-2.png?raw=true)

  接著輸入服務名字(看得懂是IT邦幫忙用的就好)
  下方可以選擇1v1的聊天，或是可以自己創一個群組，然後把notify機器人邀進那個群組
  ![line notify - 3](https://github.com/lalame888/itHelpDraftPublish/blob/master/line%20notify%20-3.png?raw=true)

  好了之後就會得到一組token，把token複製起來
  ![line notify - 4](https://github.com/lalame888/itHelpDraftPublish/blob/master/line%20notify%20-4.png?raw=true)
  (這個示範用的token我創完就刪掉了，所以露出來沒關係）

  把複製好的token，貼到itHelpConfig.ini中的line_token= 後方
  ![line notify - 5](https://github.com/lalame888/itHelpDraftPublish/blob/master/%E8%B2%BC%E4%B8%8Aline%20token.png?raw=true)

  之後的通知效果會像是：
  ![line notify - 6](https://github.com/lalame888/itHelpDraftPublish/blob/master/%E9%80%9A%E7%9F%A5%E7%9A%84%E6%A8%A3%E5%AD%90.png?raw=true)

## Step3: 安裝phthon、安裝需要的套件
### 在 Mac 上安裝 Python：
1. **前往官方網站**：
   - 開啟瀏覽器，前往 [Python 官方網站](https://www.python.org/)。
2. **下載 Python 安裝程式**：
   - 點擊首頁上的 "Downloads" 選項。
   - 會自動檢測你的作業系統，提供對應的安裝程式。選擇最新的 Python 版本，點進去後會看到不同的安裝程式選項。
3. **選擇安裝選項**：
   - 選擇符合你作業系統的安裝程式，通常會有 "macOS 64-bit installer" 的選項。
4. **執行安裝程式**：
   - 下載完安裝程式後，執行它。會開啟一個 Python 安裝器的視窗，記得勾選 "Add Python X.Y to PATH" 選項，這樣可以在終端機中直接運行 python。
5. **完成安裝**：
   - 完成安裝後，可以打開終端機（Terminal）並輸入 `python`，確認是否成功安裝。

### 在 Windows 上安裝 Python：
1. **前往官方網站**：
   - 開啟瀏覽器，前往 [Python 官方網站](https://www.python.org/)。
2. **下載 Python 安裝程式**：
   - 點擊首頁上的 "Downloads" 選項。
   - 會自動檢測你的作業系統，提供對應的安裝程式。選擇最新的 Python 版本，點進去後會看到不同的安裝程式選項。
3. **選擇安裝選項**：
   - 選擇符合你作業系統的安裝程式，通常會有 "Windows installer (64-bit)" 和 "Windows installer (32-bit)" 的選項。如果你的系統是 64 位元的，建議選擇 64 位元的版本。
4. **執行安裝程式**：
   - 下載完安裝程式後，執行它。勾選 "Add Python X.Y to PATH" 選項，這樣可以在命令提示字元（Command Prompt）中直接運行 python。
5. **完成安裝**：
   - 完成安裝後，可以打開命令提示字元（Command Prompt）並輸入 `python`，確認是否成功安裝。
### 安裝pip
在大多數情況下，安裝 Python 的同時也會自動安裝 pip。不過，如果你確定 pip 沒有安裝或者需要更新，你可以按照以下步驟來進行安裝：
### 使用 Python 的 get-pip.py 腳本（適用於所有作業系統）：
1. 首先，下載 `get-pip.py` 腳本。可以從 [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py) 連結進行下載。你可以在瀏覽器中開啟這個連結，然後將網頁另存為 `get-pip.py` 檔案。
2. 打開終端機或命令提示字元，進入到你下載 `get-pip.py` 檔案的目錄。
3. 在終端機中執行以下指令：
```bash
python3 get-pip.py
```
可以在終端機或命令提示字元中執行以下指令來檢查 pip 是否已成功安裝：
```bash
pip --version
```
如果成功安裝，將會顯示 pip 的版本號。

### 安裝需要的套件
以下是這個專案會用到的套件：
```bash
pip install requests
```
```bash
pip install schedule
```
```bash
pip install beautifulsoup4
```
## Step4: 開啟 & 運行
開啟終端機或是用VS Code等開啟專案資料夾
接著於終端機中輸入
```bash
python3 itHelp.py
```
![運行的樣子](https://github.com/lalame888/itHelpDraftPublish/blob/master/%E9%81%8B%E4%BD%9C%E7%9A%84%E6%A8%A3%E5%AD%90.png?raw=true)
如果有串接line的話就會同步收到通知

看起來卡在選單中，但背景還是有在運作，就把終端視窗開著



## 目前有幾個問題：
1. 尚未串接line bot等服務，無法透過line去傳送指令來操作  
2. 登入token需要事先在登入之後，用F12去取得並貼到config.ini上  
  原本也想要串登入去取得cookie，但目前不知道怎麼在成功post 登入api 後設置cookie  
3. 打包成單獨exe檔失敗
  目前使用`pyinstaller --onefile itHelp.py` 進行打包專案成單獨的執行檔卻一直失敗，將ini檔放在執行檔旁邊也是



