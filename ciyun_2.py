import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np

path = r'C:/Users/hp/Desktop/233.txt'
font = r'C:\Windows\Fonts\simkai.TTF'

text = (open('C:/Users/hp/Desktop/233.txt', 'r', encoding='utf-8')).read()
cut = jieba.cut(text)  # 分词
string = ' '.join(cut)
print(len(string))
img = Image.open('F:/wu.png')  # 打开图片
img_array = np.array(img)  # 将图片装换为数组
stopword = ['xa0']  # 设置停止词，也就是你不想显示的词，这里这个词是我前期处理没处理好，你可以删掉他看看他的作用
wc = WordCloud(
    scale=4,
    background_color='white',
    max_words=400,
    width=1000,
    height=800,
    mask=img_array,
    font_path=font,
    stopwords=stopword
)
wc.generate_from_text(string)  # 绘制图片
plt.imshow(wc)
plt.axis('off')
plt.figure()
#plt.show()  # 显示图片
wc.to_file('F:/3.png')  # 保存图片
