import requests
import re
from bs4 import BeautifulSoup
import summary as ausu

stops=[]
# 讀取停用詞表
with open("C:\\Users\\ACER\\Desktop\\AutoSummary\\stopWordList.txt", 'r', encoding="utf-8-sig") as f:
    for line in f.readlines():
        stops.append(line.strip())

def get_news_content(link):
    # 發送請求獲取新聞頁面內容
    response = requests.get(link)
    # 如果請求成功
    if response.status_code == 200:
        # 解析新聞頁面內容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到新聞內容所在的元素
        content_element = soup.find('div', class_='article-content__paragraph')
        # 如果找到內容元素
        if content_element:
            # 獲取新聞內容並去除多餘空格和換行符
            news_content = re.sub(r'\s+', ' ', content_element.text)
            return news_content
    else:
        print(f'無法從 {link} 獲取新聞內容。狀態碼: {response.status_code}')
        return "無"

def scrape_udn_news(url):
    news_contents=[]
    i=1
    # 發送請求獲取網頁內容
    response = requests.get(url)
    # 如果請求成功
    news_content = ''
    if response.status_code == 200:
        # 解析網頁內容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到所有新聞標題的容器
        news_containers = soup.find_all('div', class_='story-list__text')
        # 遍歷所有新聞容器
        for container in news_containers:
            # 獲取新聞標題
            title_element = container.find('h2')
            # 確保找到標題元素
            if title_element:
                title = title_element.text.strip()
                # 獲取新聞連結
                link = container.find('a')['href']
                # 如果連結不是完整的 URL（缺少協議部分），則添加協議部分
                if not link.startswith('http'):
                    link = 'https://udn.com' + link
                # 獲取新聞內容
                
                news_content =get_news_content(link)
                if news_content!=None:
                    summarized_content = summarize_content(news_content)
                    if summarized_content!="":
                        print("處理第",str(i),"則新聞")
                        print("標題：",title)
                    # 將標題和摘要內容添加到列表中
                        news_contents.append({'title': title, 'summary': summarized_content})
                        i+=1
    else:
        print(f'無法獲取網頁內容。狀態碼: {response.status_code}')
    return news_contents



def summarize_content(content):
    # 將內容分割成句子
    sentences, indexs = ausu.split_sentence(content)
    # 獲得句子的TF-IDF矩陣
    tfidf = ausu.get_tfidf_matrix(sentences, stops)
    # 根據詞語重要性獲得句子權重
    word_weight = ausu.get_sentence_with_words_weight(tfidf)
    # 根據句子位置獲得句子權重
    posi_weight = ausu.get_sentence_with_position_weight(sentences)
    # 計算句子間的相似度權重
    scores = ausu.get_similarity_weight(tfidf)
    # 根據權重進行句子排序
    sort_weight = ausu.ranking_base_on_weigth(word_weight, posi_weight, scores, feature_weight=[1, 1, 1])
    # 獲得摘要
    summar = ausu.get_summarization(indexs, sort_weight, topK_ratio=0.3)
    return summar


url = 'https://udn.com/news/breaknews/1'
news = scrape_udn_news(url)

# 打印每篇新聞的標題和摘要內容
for idx, item in enumerate(news, 1):
    print(f'新聞{idx}：')
    print(f'標題：{item["title"]}')
    print(f'摘要：{item["summary"]}')
    print('-' * 50)