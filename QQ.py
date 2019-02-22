import re, requests
import time, pymysql

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='zhangyi')
connection.autocommit(True)


def login():
    driver = webdriver.Chrome()  # 传入浏览器对象
    wait = WebDriverWait(driver, 5)  # 显式等待
    driver.get('https://qzone.qq.com/')
    driver.switch_to_frame('login_frame')
    input = wait.until(EC.presence_of_element_located((By.ID, 'switcher_plogin')))
    time.sleep(1)
    input.click()
    driver.find_element_by_id('u').clear()
    driver.find_element_by_id('u').send_keys('your_qq')   # 改QQ
    time.sleep(3)
    driver.find_element_by_id('p').clear()
    driver.find_element_by_id('p').send_keys('your_pwd') # 改 密码
    button = driver.find_element_by_id('login_button')
    time.sleep(3)
    button.click()
    time.sleep(1)
    driver.switch_to.default_content()  # 将frame重新定位回来
    return driver


def get_tk(cookie):
    hashes = 5381
    for i in cookie['p_skey']:
        hashes += (hashes << 5) + ord(i)

    return hashes & 2147483647


def back_session(driver):
    mysession = requests.session()
    cookies = driver.get_cookies()
    cookie = {}
    for item in cookies:
        cookie[item['name']] = item['value']
    headers = {
        'authority': 'user.qzone.qq.com',
        'referer': 'https://qzone.qq.com/',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'
    }
    # print("back_session函数")
    c = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
    mysession.headers = headers
    mysession.cookies.update(c)
    return mysession


def get_QQ(g_tk, mysession, qzonetoken):
    friendlist = []
    url = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?uin=your_qq&do=1&rd=0.08392787628241383&fupdate=1&clean=1&g_tk=' + str(
        g_tk) + '&qzonetoken=' + str(qzonetoken) + '&g_tk=' + str(g_tk)   # url 里面 uin里面加自己的qq
    r = mysession.get(url)
    html = r.text
    paa = re.compile(r'"uin":(.*?),', re.S)
    friendlist = re.findall(paa, html)
    return friendlist


def save_mysql(say, stime, QQ, connection):
    stime = str(stime)
    content = str(say)
    QQ = str(QQ)

    sql = 'insert into qq values ("{}","{}","{}")'.format(content, stime, QQ)
    connection.query(sql)


def spider(g_tk, mysession, qzonetoken, QQ):
    page = 0
    url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=' + str(
        QQ) + '&inCharset=utf-8&outCharset=utf-8&hostUin=' + str(
        QQ) + '&notice=0&sort=0&pos=0&num=20&cgi_host=http%3A%2F%2Ftaotao.qq.com%2Fcgi-bin%2Femotion_cgi_msglist_v6' \
              '&code_version=1&format=jsonp&need_private_comment=1&g_tk=' + str(
        g_tk) + '&qzonetoken=' + str(qzonetoken)
    say = r'"certified".*?"conlist":(.*?),'  # 说说匹配
    stime = r'"certified".*?"createTime":"(.*?)"'  # 时间匹配
    snum = r'"total":(.*?),'  # 说说总数匹配
    r = mysession.get(url)
    shuo_html = r.text
    shuo_num = re.compile(snum).findall(shuo_html)[0]  # 说说总数
    saylist = re.compile(say, re.S).findall(shuo_html)  # 说说内容

    if len(saylist) == 0:
        print("该好友说说为0或你已被禁止访问！")
        return False

    if int(shuo_num) % 20 == 0:
        page = int(shuo_num) / 20

    else:
        page = int(shuo_num) / 20 + 1
    page = int(page)
    print("总页数为" + str(page))
    for i in range(0, int(page)):
        pos = i * 20
        try:
            s_url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=' + str(
                QQ) + '&inCharset=utf-8&outCharset=utf-8&hostUin=' + str(
                QQ) + '&notice=0&sort=0&pos=' + str(
                pos) + '&num=20&cgi_host=http%3A%2F%2Ftaotao.qq.com%2Fcgi-bin%2Femotion_cgi_msglist_v6' \
                       '&code_version=1&format=jsonp&need_private_comment=1&g_tk=' + str(
                g_tk) + '&qzonetoken=' + str(qzonetoken)
            new_html = mysession.get(s_url).text
            saylist = re.compile(say, re.S).findall(new_html)
            timelist = re.compile(stime, re.S).findall(new_html)
            print("正在获取第" + str(i + 1) + "页数据....")
            # saylist = [item.replace('[{"con":', '') for item in saylist]

            for s, t in zip(saylist, timelist):
                try:
                    if s == "null":
                        continue
                    s = s.replace('[{"con":', '')[1:-1]
                    save_mysql(s, t, QQ, connection)
                except Exception as e:
                    print("此条数据出错，无法插入！")

        except:
            print("第" + str(i + 1) + "页获取失败！")


def get_qzonetoken(html):
    paa = re.compile(r'window\.g_qzonetoken = \(function\(\)\{ try\{return "(.*?)";\} catch\(e\)', re.S)
    res = re.findall(paa, html)[0]  # 因为返回的是列表形式，所以只取第一个元素
    return res


def main():
    driver = login()
    cookies = driver.get_cookies()
    html = driver.page_source
    qzonetoken = get_qzonetoken(html)
    # print(cookies)
    cookie = {}
    for item in cookies:
        cookie[item['name']] = item['value']
    g_tk = get_tk(cookie)
    mysession = back_session(driver)
    driver.close()
    friendlist = get_QQ(g_tk, mysession, qzonetoken)
    for i in range(len(friendlist)):
        print("现在正在爬取---" + friendlist[i] + "---的说说......")
        try:
            spider(g_tk, mysession, qzonetoken, friendlist[i])
            print("**************" + str(friendlist[i]) + "的说说爬取成功**************")
            print("\n\n")
            time.sleep(5)


        except Exception as e:
            print("该好友空间出现问题，跳过.....~.~")
            print("\n\n")
        time.sleep(3)


if __name__ == '__main__':
    begin = time.time()
    main()
    connection.close()
    end = time.time()
    cu = end - begin
    print("一共耗时：{:.2f}".format(cu))
