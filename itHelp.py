import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode, quote, quote_plus
from datetime import datetime
import schedule
import time
import threading
from configparser import ConfigParser

config = ConfigParser()
config.read('itHelpConfig.ini')
cookie_value = config.get('Settings', 'cookie_value')
lineToken = config.get('Settings', 'line_token')
stop_event = threading.Event()

# 建立session
def getSession(cookie_value):
    session = requests.Session()
    # 設定 User-Agent 標頭
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    # 將 Cookie 存儲在 Session 中
    session.headers.update(headers)
    session.cookies['Cookie'] = cookie_value
    return session
session = getSession(cookie_value)

def is_valid_time(input_str):
    try:
        datetime.strptime(input_str, '%H:%M:%S') # 以24小時制的格式進行解析
        return True
    except ValueError:
        return False

# 取得IT邦幫忙的網站內容
def scrape_website(url, method = 'GET', data = {}, session = session):
    if method.upper() == 'GET':
        response = session.get(url)
    else :
        response = session.post(url, data=data, json=data)
    # 檢查請求的回應
    if response.status_code == 200:
        # 處理回應內容
        return (response.text)
    else:
        raise Exception(f'請求失敗，狀態碼：{response.status_code}, 錯誤訊息：{response.text}')

#發送到line通知    
def line_notifiy(message):
    try:
        url = 'https://notify-api.line.me/api/notify'
        data = { 'message': message }
        lineSession = getSession('')
        lineSession.headers = {"Authorization": f"Bearer {lineToken}"}
        lineSession.headers.update(lineSession.headers)
        scrape_website(url, 'POST', data, lineSession)
    except Exception as error:
        print(f'串接line失敗 : error')

def no_longin_alter():
    line_notifiy('目前登入Tonke過期，請重新設定Token')


# 取得使用者id
def getUser():
    isLogin = False
    name = ''
    id = ''
    url = 'https://ithelp.ithome.com.tw/'
    page_content = scrape_website(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    account = soup.find('a', {'id': 'account'})
    if account :
        isLogin = True
        name = account['data-account']
        href = account['href']
        id = re.search(r'users/(\d+)', href).group(1)
    return { 'isLogin': isLogin, 'name': name , 'id': id }


# 取得草稿列表 Array<{link:string, text: string, id:string}>
def getArticlesList(userId):
    url = f'https://ithelp.ithome.com.tw/users/{userId}/articles'
    page_content = scrape_website(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    div_elements = soup.find_all('div', class_='qa-list profile-list')

    if div_elements:
        # 遍歷所有找到的元素，並處理它們
        # 使用列表推導式篩選出包含 <span class="title-badge title-badge--draft"> 的 <div> 元素
        filtered_div_elements = [div_element for div_element in div_elements if div_element.find('span', class_='title-badge title-badge--draft')]
        # 檢查篩選後的結果
        results = []  # 創建一個空的物件陣列來存儲結果
        if filtered_div_elements:
            for  list_element in filtered_div_elements:
                title_link = list_element.find('a', class_='qa-list__title-link')
                link = title_link.get('href').strip()
                text = title_link.text.strip()
                id = re.search(r'articles/(\d+)', link).group(1)
                result_dict = {'link': link, 'text': text, 'id': id}
                results.append(result_dict)
        results.reverse()
        return results
    else:
        return []

# 取得文章的發文token
def getDraftContent(id):
    url = f'https://ithelp.ithome.com.tw/articles/{id}/draft'
    page_content = scrape_website(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    input_element = soup.find('input', {'name': '_token'})
    if input_element == None:
        raise Exception(f'發文token取得失敗')
    token = input_element['value']
    subject = soup.find('input', {'name': 'subject'})['value']
    description =  soup.find('textarea', {'name': 'description'}).text
    tag_elements = soup.find('select', {'name': 'tags[]'}).find_all('option', selected='selected')
    tags = [option.text for option in tag_elements]
    return { 
            'token': token,
            'description': description,
            'subject': subject,
            'tags': tags
        }

def showList(list):
    for index, element in enumerate(list, start=1):
        print(f"{index}. {element['text']}")

def publish(id):
    global session
    draftContent = getDraftContent(id)
    url = f'https://ithelp.ithome.com.tw/articles/{id}/publish'

    newHeaders = session.headers
    newHeaders['X-Csrf-Token'] = draftContent['token']
    newHeaders['Referer'] = url
    newHeaders['Origin'] = 'https://ithelp.ithome.com.tw'
    session.headers.update(newHeaders)

    data = {'_token': draftContent['token'],
         'group': 'tech',
         '_method': 'PUT',
         'subject': draftContent['subject'],
         'description': draftContent['description'],
        }
    # 將tags[]的值編碼
    encoded_data = urlencode(data)
    tags =  '&'.join([f'tags%5B%5D={t}' for t in draftContent['tags']])
    encoded_data  = encoded_data + '&' + tags
    return scrape_website(url, 'POST', encoded_data)

def showDraft(userId):
    draftList = getArticlesList(userId)
    length = len(draftList)
    print(f'＊以下是目前尚未發布的草稿文章列表: 共 {length} 篇＊')

    showList(draftList)
    print('')

def login(loginId, ps):
    # 去登入看看
    global session
    global cookie_value
    url = 'https://member.ithome.com.tw/login'
    loingPage = scrape_website(url)
    soup = BeautifulSoup(loingPage, 'html.parser')
    token = soup.find('input', {'name': '_token'})['value']

    newHeaders = session.headers
    newHeaders['X-Csrf-Token'] = token
    newHeaders['Referer'] = url
    newHeaders['Origin'] = 'https://member.ithome.com.tw'
    # 將 Cookie 存儲在 Session 中
    session.headers.update(newHeaders)
    data = {'_token': token, 'account': loginId, 'password': ps}
    response = session.post(url, data=data)
     # 檢查請求的回應
    if response.status_code == 200:
        # 處理回應內容
        # if (response.cookies):
        #     RequestsCookieJar = response.cookies.values()
        #     cookie_value = RequestsCookieJar[0]
        #     session = getSession(cookie_value)
        #     print(f'設定cookie_value = {cookie_value}')
        print (response.text)
    else:
        raise Exception(f'請求失敗，狀態碼：{response.status_code}, 錯誤訊息：{response.text}')

def postLast(userId):
    draftList = getArticlesList(userId)
    if len(draftList) > 0 :
        postId = draftList[0]['id']
        postName = draftList[0]['text']
        publish(postId)
        message = f'已發布文章！ 文章名稱: {postName} ; id: {postId}'
        line_notifiy(message)
        print(message)
        showDraft(userId)
    else: 
        message = '發文失敗，目前無草稿文章'
        line_notifiy(message)
        print(message) 

def chiosePost(userId):
    draftList = getArticlesList(userId)
    print('目前的草稿文章清單：')
    showList(draftList)
    while True:
        try:
            postIndex = input("請選擇要發布的文章編號，或是exit離開: ")
            if postIndex == 'exit':
                break
            elif int(postIndex) <= len(draftList):
                publish(draftList[postIndex - 1])
                break
            else :
                print('輸入無效，請重新選擇')
        except Exception as error:
            print('輸入無效，請重新選擇')

def autoPostFunction(open, time, userId):
    schedule.cancel_job(postLast)
    if open:
        schedule.every().day.at(time).do(postLast, userId)
        line_notifiy(f'開啟自動發文，時間為{time}')
    else:
        line_notifiy(f'關閉自動發文功能')


def run_schedule():
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)
        # print('check!')

def main():
    autoPost = True
    autoPostTime = '10:00:00'
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    line_notifiy(f'\n啟動IT邦幫忙自動發文神器\n自動發文設定為: {"開，設定時間為每日 " + autoPostTime if autoPost else "關"}')
    user = getUser()
    if user['isLogin']:
        userName = user['name']
        line_notifiy(f'目前登入帳號為: {userName}')
    try:
        while True :
                user = getUser()
                userId = user['id']
                userName = user['name']
                schedule.cancel_job(no_longin_alter)
                if user['isLogin']:
                    print(f'目前登入帳號: {userName}')
                    message = f'自動發文設定為: {"開，設定時間為每日 " + autoPostTime if autoPost else "關"}'
                    print(message)
                    print("--------- 選單 ---------")
                    print("1. 檢視未發布草稿文章列表")
                    print('2. 發布最早儲存的草稿')
                    print("3. 選擇文章發布")
                    print(f'4. {"關閉" if autoPost else "開啟"} 自動定時發布')
                    print("5. 修改每日定時發布時間")


                    print("或是輸入 exit 關閉離開")
                    print("")
                    choice = input("請輸入您的選擇：")
                        # 根據使用者的選擇執行相應的操作
                    if choice == "1":
                        showDraft(userId)
                    elif choice == "2":
                        postLast(userId)          
                    elif choice == "3":
                        chiosePost(userId)
                    elif choice == '4':
                        autoPost = not autoPost
                        autoPostFunction(autoPost, autoPostTime, userId)
                    elif choice == '5':
                        print(f'目前設定時間為每日 {autoPostTime}')
                        while True:  
                            if autoPost:
                                time_str = input("請輸入時間（格式為HH:MM:SS），或是exit取消：")
                                if time_str == 'exit':
                                    break
                                if is_valid_time(time_str):
                                    autoPostTime = datetime.strptime(time_str, '%H:%M:%S').strftime('%H:%M:%S') # 以24小時制的格式進行解析
                                    autoPostFunction(True, autoPostTime, userId)
                                    print(f'已設定為{autoPostTime}')
                                    break
                                else:
                                    print(f"{time_str} 不是有效的時間格式")
                            else:
                                newInput = input('目前尚未開啟自動發文，是否要先開啟？(y/n)')
                                if (newInput.upper() == 'Y'):
                                    autoPost = True
                                    autoPostFunction(True, autoPostTime, userId)
                                else:
                                    print('退出時間設定')
                                    break
                    elif choice == "exit":
                        print("ㄅㄅ！")
                        break  # 選擇離開時結束循環
                    else:
                        print("無效的選擇，請重新輸入。")
                    print('')
                else:
                    schedule.every(30).minutes.do(no_longin_alter)
                    loginId = input("目前登入cookie無效，請重新輸入登入帳號: ")
                    ps = input("請輸入密碼:")
                    print('登入中...')
                    login(loginId, ps)
    except Exception as error:
        line_notifiy(f'發生錯誤意外關閉: {error}')
        print(error)
        stop_event.set()
    stop_event.set()
    schedule_thread.join()
    line_notifiy('關閉IT邦幫忙發文神器')


main()

# 作者： 一宵三筵 (lalame888)
