import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode
from configparser import ConfigParser

config = ConfigParser()
config.read('itHelpConfig.ini')
lineToken = config.get('Settings', 'line_token')

# 建立session
def getSession(cookie_value = ''):
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

# 發出request取得網站內容或回應
def scrape_website(session, url, method = 'GET', data = {}):
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
def line_notify(message):
    try:
        url = 'https://notify-api.line.me/api/notify'
        data = { 'message': message }
        lineSession = getSession('')
        lineSession.headers = {"Authorization": f"Bearer {lineToken}"}
        lineSession.headers.update(lineSession.headers)
        scrape_website(lineSession, url, 'POST', data)
    except Exception as error:
        print(f'串接line失敗 : {error}')


# 取得使用者{id: string, name: string} | None 
def getUser(session):
    url = 'https://ithelp.ithome.com.tw/'
    page_content = scrape_website(session, url)
    soup = BeautifulSoup(page_content, 'html.parser')
    account = soup.find('a', {'id': 'account'})
    if account :
        name = account['data-account']
        href = account['href']
        id = re.search(r'users/(\d+)', href).group(1)
        return { 'name': name , 'id': id }
    else:
        return None
def editDraft(session, articlesId, Content):
    draftContent = getDraftContent(session, articlesId)
    url = f'https://ithelp.ithome.com.tw/articles/{articlesId}/draft'
    token = draftContent['token']
    newHeaders = session.headers
    newHeaders['X-Csrf-Token'] = token
    newHeaders['Origin'] = 'https://ithelp.ithome.com.tw'
    session.headers.update(newHeaders)
    subject = Content['subject']
    data = {'_token': token,
         'group': 'tech',
         '_method': 'PUT',
         'subject': subject,
         'description': Content['description'],
         'tags[]': Content['tags'],
        }
    # 將tags[]的值編碼
    encoded_data = urlencode(data, doseq=True)
    scrape_website(session, url, 'POST', encoded_data)


# 取得草稿列表 Array<{link:string, text: string, id:string}>
def getArticlesList(session):
    user = getUser(session)
    if user == None:
        raise Exception('登入狀態過期，無法取得文章列表')
    userId = user['id']
    url = f'https://ithelp.ithome.com.tw/users/{userId}/articles'

    page_content = scrape_website(session, url)
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

# 取得指定草稿文章的資料內容
def getDraftContent(session, articlesId):
    url = f'https://ithelp.ithome.com.tw/articles/{articlesId}/draft'
    page_content = scrape_website(session, url)
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

def publish(session, articlesId):
    draftContent = getDraftContent(session, articlesId)
    url = f'https://ithelp.ithome.com.tw/articles/{articlesId}/publish'

    newHeaders = session.headers
    newHeaders['X-Csrf-Token'] = draftContent['token']
    newHeaders['Origin'] = 'https://ithelp.ithome.com.tw'
    session.headers.update(newHeaders)
    subject = draftContent['subject']
    data = {'_token': draftContent['token'],
         'group': 'tech',
         '_method': 'PUT',
         'subject': subject,
         'description': draftContent['description'],
         'tags[]': draftContent['tags'],
        }
    # 將tags[]的值編碼
    encoded_data = urlencode(data, doseq=True)
    scrape_website(session, url, 'POST', encoded_data)
    message = f'已發布文章！ 文章名稱: {subject} ; id: {articlesId}'
    line_notify(message)
    print(message)


def login(loginId, ps):
    # 去登入看看
    session = getSession()
    url = 'https://member.ithome.com.tw/login'
    loginPage = scrape_website(session, url)
    soup = BeautifulSoup(loginPage, 'html.parser')
    token = soup.find('input', {'name': '_token'})['value']

    newHeaders = session.headers
    newHeaders['X-Csrf-Token'] = token
    newHeaders['Origin'] = 'https://member.ithome.com.tw'
    # 將 Cookie 存儲在 Session 中
    session.headers.update(newHeaders)
    data = {'_token': token, 'account': loginId, 'password': ps}
    response = session.post(url, data=data)
     # 檢查請求的回應
    if response.status_code == 200:
        # 處理回應內容
        if (response.cookies):
            cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
            cookie_string = '; '.join([f'{key}={value}' for key, value in cookie_dict.items()])
            return cookie_string
    else:
        raise Exception(f'請求失敗，狀態碼：{response.status_code}, 錯誤訊息：{response.text}')


# 作者： 一宵三筵 (lalame888)
