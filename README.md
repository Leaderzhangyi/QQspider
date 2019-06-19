
![GitHub stars](https://img.shields.io/github/stars/Leaderzhangyi/QQspider.svg?style=social) 
![](https://img.shields.io/badge/python-3.6-brightgreen.svg)
![](https://img.shields.io/badge/platform-Windows%7CLinux%7CmacOS-660066.svg)



# QQspider
利用python爬取好友说说并分析

  看了网上的许多博客，基本上都是一个样，基本的知识也没详细解释，我这次也想跟大家仔细分析一下，自己还是要有一定爬虫基础，**本人技术有限，如果本文哪有错误或不够准确的地方，还望大牛们指点ヾ(๑╹◡╹)ﾉ"**
  
  ----
  
###  **一、环境配置：**
* **Python 3.6**
* selenium (<font color=#FF0000>注意:</font>先配置好自己浏览器的驱动，下载地址看下面) 
* pymysql
* re
* requests

点击下载chrome的---->[Chrome_webdriver]( http://chromedriver.storage.googleapis.com/index.html)
点击下载Firefox的---->[Firefox_webdriver](https://github.com/mozilla/geckodriver/releases/)
点击下载IE的---->[IE_webdriver](http://selenium-release.storage.googleapis.com/index.html)

先来张效果图看看效果
[![ki2cDJ.md.png](https://s2.ax1x.com/2019/01/21/ki2cDJ.md.png)](https://imgchr.com/i/ki2cDJ)

### 二、思路：
 作为一个菜鸡学了一点爬虫，就想做一个好友的说说分析，最开始我以为这个爬虫很简单几十行就可以搞定，然而忽略了一些东西。。。。（先卖个关子）
 
 -------
 
 先说说整个过程的想法：
![kFAq54.png](https://s2.ax1x.com/2019/01/22/kFAq54.png)
 看起来是不是很简单？（手动dog）那现在我们就来按步骤操作一下
 #### 1.找到包含好友的QQ信息的url（这里也有两种方法）

* **法一**：
先点开好友这一栏,通过亲密度的排行来获取，这里我们点开F12，选中Network
一般这种信息都在XHR或者JS类型里面，大家可以在这里面找找，通过一会的寻找我们就发现friend_ship开头这xhr里面的items_list就包含了好友的QQ号和姓名，但是此方法获取的qq不全，只是大部分的qq
![kFEYMq.png](https://s2.ax1x.com/2019/01/22/kFEYMq.png)
![kFE4Fe.png](https://s2.ax1x.com/2019/01/22/kFE4Fe.png)
* **法二：**
点击页面最上面的设置按钮，滑动可见好友，通过js的结果分析，随着下滑请求的url的页数都在变化，我们只要每次修改下页数的参数就可以获取所有好友的QQ，这个方法可以获取所有的好友的qq，但对于qq好友很少的朋友来说，此方法不适用
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf4uq01yvj30eo05zweo.jpg)
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf4uq5xnnj30q40bxdij.jpg)
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf4upza7gj30hp03naa7.jpg)


 #### 2.找到包含好友的说说的url
 
我们先随便点进一个好友的空间进行分析
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf57oz5pxj30sn06v0y0.jpg)
点进去过后，我们F12 进行分析，发现一页最多存20条说说，以此我们可以通过说说总数（re提取）来算出一共有多少页，然后通过构造url来获取
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf5d51ntwj30pe0le412.jpg)

---------



**通过以上的分析过后我们开始获取url：**

我们先看看获取qq的第一种方法的url：
> 
> https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?uin=你的QQ号&do=1&rd=0.55484478707938&fupdate=1&clean=1&g_tk=1376935160&qzonetoken=6e4e0b063e3f00421d98df35b330c8bb2158bb8697e5dc7a85a65b379407706960f0b1c422f9a26879&g_tk=1376935160

我们分析一下这里面**每次登录都在变**的参数 
* g_tk        （空间加密算法）
* qzonetoken  （空间源码里面的参数）

那这两个参数我们要怎么获取呢？为什么每次登录这两个参数的都在变呢？

我们首先先要了解一下---->[**cookie**](https://baike.baidu.com/item/cookie/1119?fr=aladdin)
在看看[**session**](https://baike.baidu.com/item/session/479100)的基本概念

快速查看 cookies 的方法：按F12进入浏览器的开发者模式——console——在命令行输入`javascript:alert(document.cookie)`，再回车即可看见

所以我们登录过后，每次都访问url的时候都要保持着参数不变，也就是说cookie不能变
每次都要是<font color=##FF0000>同一个cookie</font>(**就相当于每次都是以你的身份保持着登录状态去访问他人空间**)，否则就会出现以下情况↓
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf61qzu1pj30tg0f8mxj.jpg)

----

理解好以上的几个问题过后，问题就解决了一大部分了
接着我们分析g_tk参数，在自己qq空间主页 F12  点JS类型文件，找到以下文件,查看Preview部分，分析一下其中的代码
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf67ysgc2j30t60evmz5.jpg)
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf67ysb8ej30o10icgmw.jpg)

<del>其实这个程序的意思，</del>    还是直接上代码吧
```python

def get_tk(cookie):
    hashes = 5381       
    for i in cookie['p_skey']:    #提取cookie中p_skey每个字母
        hashes += (hashes << 5) + ord(i)  #加密过程,ord()将 字符转化为ASCII码
                                  # << 二进制 左移运算 左移几位就相当于乘以2的几次方
    return hashes & 2147483647  #二进制 与运算
    # 比如  2&3 转为二进制  10&11
	#   都是1结果为1，否则为0   
	#    所以二进制算出来是  10   返回2
	#   还不懂的朋友，还是自行Baidu吧
```
随着我们分析第二个参数**qzonetoken**  
这个参数很好获取，在我们空间主页右键查看网页源代码,Ctrl+F查找下可以找到，之后我们可以通过正则提取
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzf6v66w82j30zy03kjrz.jpg)
ok，理解了上面的全部，基本就完成了80%了，接下来我们开始代码实现

### 三、代码实现：
先导入第三方库
```python
import re, requests
import time, pymysql

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
```
1. 首先是登录，我们这里用selenium模拟浏览器实现
```python

def login():
    driver = webdriver.Chrome()  # 传入浏览器对象
    wait = WebDriverWait(driver, 5)  # 显式等待
    driver.get('https://qzone.qq.com/')
    driver.switch_to_frame('login_frame')       #切换到登录窗口
    input = wait.until(EC.presence_of_element_located((By.ID, 'switcher_plogin')))# 显式等待 找到账号密码登录按钮
    time.sleep(1)
    input.click()     # 交互点击
    driver.find_element_by_id('u').clear()  #清空里面的内容
    driver.find_element_by_id('u').send_keys('your_qq')   #传入你的QQ
    time.sleep(3)
    driver.find_element_by_id('p').clear()   
    driver.find_element_by_id('p').send_keys('your_password')  #传入你的密码
    button = driver.find_element_by_id('login_button')   #找到登录按钮
    time.sleep(3)  
    button.click()
    time.sleep(1)
    driver.switch_to.default_content()  # 将frame重新定位回来，不然后续会出错
    return driver

```
2. 通过传回来的driver对象获取网页源代码和cookies

通过源代码获取qzonetoken参数
```python
	def get_qzonetoken(html):
    paa = re.compile(r'window\.g_qzonetoken = \(function\(\)\{ try\{return "(.*?)";\} catch\(e\)', re.S)
    res = re.findall(paa, html)[0]  # 因为返回的是列表形式，所以只取第一个元素
    return res
```
注意：`driver.get_cookies()`获取的cookies是散的，所以要进行以下操作：

```python
def get_tk(cookie):  #加密过程
    hashes = 5381
    for i in cookie['p_skey']:
        hashes += (hashes << 5) + ord(i)
    return hashes & 2147483647
    
  cookies = driver.get_cookies()
	 for item in cookies:
        cookie[item['name']] = item['value']   #将对应表达联系起来 
         #  上一步不懂的可以把 cookies的值输出来看一下
    g_tk = get_tk(cookie)
```
3.将cookies传给requests,以保证都是在登录状态（<font color=#FF0000>**最关键**</font>）
```python
def back_session(driver):
    mysession = requests.session()  #  建立一个session对话
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
    c = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True) 
     # 将字典转化为cookiejar形式
    mysession.headers = headers  # 请求头，防止反爬
    mysession.cookies.update(c)  # 更新cookies
    return mysession   # 返回带cookies的requests
```
4. 存入MySQL

```python 
connection = pymysql.connect(host='your_host', port=3306, user='你的账户', passwd='你的密码', db='your_database')
connection.autocommit(True)   #开启自动提交 不然每次执行

def save_mysql(say, stime, QQ, connection):  #这里我存入说说、说说时间、qq号
    stime = str(stime)
    content = str(say)
    QQ = str(QQ)
    sql = 'insert into qq values ("{}","{}","{}")'.format(content, stime, QQ)
    connection.query(sql)
#  数据库建表的时候  一定要把字符集改成utf8

```
看看效果图，爬了40多分钟，四万多条数据，有点<del>小慢。。。</del>，很慢。大家可以尝试下多线程爬取
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzfbtje5nzj30u009e3z4.jpg)


----
 
完成以上步骤之后整个框架就都搭好了，其余数据的提取大家就先自己完成了吧（本文最后会给出GitHub地址），也希望大家看思路过后，自己操作，不仅仅是**copy、paste and run**


导出某个好友的数据库，用Notepad++过滤一些数据后，通过词云分析
```python
import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np

path = r'your_data.text_path'
font = r'C:\Windows\Fonts\simkai.TTF'  #  字体path

text = (open('C:/Users/hp/Desktop/233.txt', 'r', encoding='utf-8')).read() # 如果是中文的话encoding换成utf8
cut = jieba.cut(text)  # 分词
string = ' '.join(cut)
print(len(string))
img = Image.open('your_photo_path')  # 打开图片
img_array = np.array(img)  # 将图片装换为数组
stopword = ['xa0']  # 设置停止词，也就是你不想显示的词，这里这个词是我前期处理没处理好，你可以删掉他看看他的作用
wc = WordCloud(
    scale=4,  #清晰度
    background_color='white',  #背景颜色
    max_words=400,    #最多单词
    width=1000,				
    height=800,
    mask=img_array,
    font_path=font,
    stopwords=stopword   # 停用词
)
wc.generate_from_text(string)  # 绘制图片
plt.imshow(wc)
plt.axis('off')
plt.figure()
#plt.show()  # 显示图片
wc.to_file('F:/3.png')  # 保存图片


```
最后我么就分析到以下图片，字越大说明出现次数最多
![](http://ww1.sinaimg.cn/large/006pybPDgy1fzfbyjdgg4j32w41xgb2a.jpg)

最后贴上我的代码链接 https://github.com/Leaderzhangyi/QQspider 希望大家能够共同改进
