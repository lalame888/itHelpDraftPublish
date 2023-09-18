import utils as module
cookie_value = 'your cookie'

def postLast(session):
    draftList = module.getArticlesList(session)
    if len(draftList) > 0 :
        postId = draftList[0]['id']
        module.publish(session, postId)
    else: 
        message = '發文失敗，目前無草稿文章'
        module.line_notify(message)
        print(message) 

def main():
    global cookie_value
    session = module.getSession(cookie_value)
    user = module.getUser(session)
    if user != None:
        userName = user['name']
        module.line_notify(f'目前登入帳號為: {userName}')
        postLast(session)
    else:
        module.line_notify(f'登入cookie失效，發文失敗')
    module.line_notify('關閉IT邦幫忙發文神器')


main()

# 作者： 一宵三筵 (lalame888)
