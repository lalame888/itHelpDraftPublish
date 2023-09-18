from datetime import datetime
import schedule
import time
import threading
import utils as module

cookie_value = 'your cookie'
stop_event = threading.Event()

def is_valid_time(input_str):
    try:
        datetime.strptime(input_str, '%H:%M:%S') # 以24小時制的格式進行解析
        return True
    except ValueError:
        return False

def no_login_alter():
    module.line_notify('目前登入Token過期，請重新設定Token')

def showList(list):
    for index, element in enumerate(list, start=1):
        print(f"{index}. {element['text']}")

def showDraft(session):
    draftList = module.getArticlesList(session)
    length = len(draftList)
    print(f'＊以下是目前尚未發布的草稿文章列表: 共 {length} 篇＊')

    showList(draftList)
    print('')

def postLast(session):
    draftList = module.getArticlesList(session)
    if len(draftList) > 0 :
        postId = draftList[0]['id']
        module.publish(session, postId)
        showDraft(session)
    else: 
        message = '發文失敗，目前無草稿文章'
        module.line_notify(message)
        print(message) 

def chosePost(session):
    draftList = module.getArticlesList(session)
    print('目前的草稿文章清單：')
    showList(draftList)
    while True:
        try:
            postIndex = input("請選擇要發布的文章編號，或是exit離開: ")
            if postIndex == 'exit':
                break
            elif int(postIndex) <= len(draftList):
                module.publish(session, draftList[int(postIndex) - 1]['id'])
                break
            else :
                print('輸入無效，請重新選擇')
        except Exception as error:
            print(error)
            print('發生錯誤，請重新選擇')

def autoPostFunction(open, time, session):
    schedule.cancel_job(postLast)
    if open:
        schedule.every().day.at(time).do(postLast, session)
        module.line_notify(f'開啟自動發文，時間為{time}')
    else:
        module.line_notify(f'關閉自動發文功能')


def run_schedule():
    while not stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)
        # print('check!')

def main():
    global cookie_value
    autoPost = False
    autoPostTime = '10:00:00'
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    session = module.getSession(cookie_value)
    module.line_notify(f'\n啟動IT邦幫忙自動發文神器\n自動發文設定為: {"開，設定時間為每日 " + autoPostTime if autoPost else "關"}')
    user = module.getUser(session)
    if user != None:
        userName = user['name']
        module.line_notify(f'目前登入帳號為: {userName}')
    try:
        while True :
            session = module.getSession(cookie_value)
            user = module.getUser(session)
            schedule.cancel_job(no_login_alter)
            if user != None:
                userName = user['name']
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
                    showDraft(session)
                elif choice == "2":
                    postLast(session)          
                elif choice == "3":
                    chosePost(session)
                elif choice == '4':
                    autoPost = not autoPost
                    autoPostFunction(autoPost, autoPostTime, session)
                elif choice == '5':
                    print(f'目前設定時間為每日 {autoPostTime}')
                    while True:  
                        if autoPost:
                            time_str = input("請輸入時間（格式為HH:MM:SS），或是exit取消：")
                            if time_str == 'exit':
                                break
                            if is_valid_time(time_str):
                                autoPostTime = datetime.strptime(time_str, '%H:%M:%S').strftime('%H:%M:%S') # 以24小時制的格式進行解析
                                autoPostFunction(True, autoPostTime, session)
                                print(f'已設定為{autoPostTime}')
                                break
                            else:
                                print(f"{time_str} 不是有效的時間格式")
                        else:
                            newInput = input('目前尚未開啟自動發文，是否要先開啟？(y/n)')
                            if (newInput.upper() == 'Y'):
                                autoPost = True
                                autoPostFunction(True, autoPostTime, session)
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
                schedule.every(30).minutes.do(no_login_alter)
                loginId = input("目前登入cookie無效，請重新輸入登入帳號: ")
                ps = input("請輸入密碼:")
                print('登入中...')
                cookie_value = module.login(loginId, ps)
    except Exception as error:
            module.line_notify(f'發生錯誤意外關閉: {error}')
            print(error)
            stop_event.set()
    stop_event.set()
    schedule_thread.join()
    module.line_notify('關閉IT邦幫忙發文神器')


main()

# 作者： 一宵三筵 (lalame888)
