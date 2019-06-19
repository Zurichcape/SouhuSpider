from lxml import etree
import os
import time
import re
import requests
from bs4 import BeautifulSoup
from NewsInfo import NewsInfo
from selenium import webdriver
class ParseNews:
    def __pathCheck(self,file_path):
        if (os.path.exists(file_path)):
            return False
        else:
            os.mkdir(file_path)
            return True
    def parse(self, element):
        dir_name = './搜狐/' + element[0]
        if (os.path.exists(dir_name)):
            pass
        else:
            os.mkdir(dir_name)
        # 这两个网页的新闻标签布局是相同的
        if (element[0] == '新闻' or element[0] == '搜狐首页'):
            #新闻和首页爬取
            self.__parseNews(element, dir_name)
        elif element[0] == '体育':
            #体育类爬取
            self.__parseSports(element, dir_name)
        else:
            #其他爬取
            self.__parseOthers(element,dir_name)

    #    解析首页
    #
    def __getSouHuHtml(self, url):
        resHtml = ''
        # 验证一下url是否正确
        if url and url != '' and url.startswith(r'http'):
            try:
                resHtml = requests.get(url,timeout=7)
            except Exception as ex:
                print(ex)
            finally:
              pass
        return resHtml

    #在使用新闻标题做文件夹和文件名时只保留中文
    def __normalizeDir(self,dir_name):
        try:
            n_dir_name = ''
            dirName = re.findall(u"[\u4e00-\u9fa5]+", dir_name)
            for element in dirName:
                n_dir_name += element
            return n_dir_name
        except BaseException as err:
            print(dir_name)
            print('*', str(err))
    def __parseFunction(self,dir_name,newsInfo,news_html,news_url):
        # 解析新闻正文网页
        news_soup = BeautifulSoup(news_html.text, 'html.parser')
        error_urls = []
        if len(news_soup.find_all('body',attrs='article-page')) == 0:
            if newsInfo.category == '搜狐首页' or newsInfo.category == '新闻' or newsInfo.category == '体育':
                print('error_url', news_url)
                pass
            else:
                element = (newsInfo.category,news_url)
                # self.__parseOthers(element,dir_name)
                error_urls.append(news_url)
                return False
        newsInfo.title = news_soup.find_all('h1')
        if newsInfo.title:
            newsInfo.title = news_soup.find_all('h1')[0].text.strip()
        else:
            newsInfo.title = ''
        file_path = dir_name + '/' + self.__normalizeDir(newsInfo.title)
        self.__pathCheck(file_path)
        newsInfo.publish_time = news_soup.find_all(class_='time')
        newsInfo.author = news_soup.find_all('h4')
        if newsInfo.publish_time:
            newsInfo.publish_time = newsInfo.publish_time[0].text.strip()
        else:
            newsInfo.publish_time = ''
        if newsInfo.author:
            newsInfo.author = newsInfo.author[0].text.strip()
        else:
            newsInfo.author = ''
        try:
            article = news_soup.find('article', attrs='article')
        except Exception as err:
            print('***' + str(err))
            print('Error is getting: ', newsInfo.title, '***', newsInfo.detail_link, '***', newsInfo.publish_time,
                  '***', newsInfo.author,
                  '***', newsInfo.text)
            return False
        newsInfo.imgurl = []
        newsInfo.text = ''
        if article:
            passages = article.find_all('p')
            for passage in passages:
                # 文本信息
                newsInfo.text += passage.text + '\n'
                # 图片信息
                if passage.find('img'):
                    img = passage.find('img')
                    # 规范化图片的url
                    if re.match(r'http:', img.get('src')):
                        news_img = img.get('src')
                    else:
                        news_img = 'http:' + img.get('src')
                    try:
                        pic = requests.get(news_img, timeout=7)
                    except BaseException:
                        print('错误，当前图片无法下载')
                        continue
                    newsInfo.imgurl.append(news_img)
                    img_path = file_path + '//' + news_img.split('/', 5)[5].split('.')[0] + '.jpeg'
                    fp = open(img_path, 'wb')
                    fp.write(pic.content)
                    fp.close()
            # print(newsInfo.text)
            print('分类：{}\n标题：{}\n发布时间：{}\n作者：{}\n图片数：{}\n新闻地址：{}\n'.format(newsInfo.category, newsInfo.title,
                                                                           newsInfo.publish_time,
                                                                           newsInfo.author.strip(),
                                                                           newsInfo.imgurl.__len__(),
                                                                           newsInfo.detail_link))
            file_path = file_path + '\\' + self.__normalizeDir(newsInfo.title) + '.txt'
            file = open(file_path, 'w', encoding='utf-8')
            file.write('标题：{}\n作者：{}\n发布时间：{}\n原文地址：{}\n正文：{}\n'.format(newsInfo.title, newsInfo.author, newsInfo.publish_time,newsInfo.detail_link, newsInfo.text))
            file.close()
        return True
    # 解析搜狐新闻和搜狐首页
    def __parseNews(self, element,dir_name):
        html = self.__getSouHuHtml(element[1])
        if html == '':
            print('解析网页失败')
        soup = BeautifulSoup(html.text, 'lxml')
        news_list = soup.find_all('div', attrs='list16')  # 得到包含所有新闻信息的bs4对象
        for news in news_list:
            newsInfo = NewsInfo()
            newsInfo.category = element[0]
            news_contents = news.find_all('a')
            for news_content in news_contents:
                newsInfo.detail_link = news_content.get('href')
                if not re.match(r'http:', newsInfo.detail_link):
                    newsInfo.detail_link = 'https:' + newsInfo.detail_link  # 保证网页链接的正确性
                else:
                    pass
                news_html = self.__getSouHuHtml(newsInfo.detail_link)
                if news_html == '':
                    continue
                if not self.__parseFunction(dir_name,newsInfo,news_html,newsInfo.detail_link):
                    continue
        print(element[0]+'\t抓取完毕')
        # return newsInfo
    #爬取搜狐体育
    def __parseSports(self,element,dir_name):
        html = self.__getSouHuHtml(element[1])
        if html == '':
            print('解析网页失败')
            return False
        html = etree.HTML(html.text)
        url = html.xpath('//div[@class="s-one_center"]//a/@href')
        url1 = html.xpath('//div[@class="clear"]//ul//li/a/@href')
        for e in url1:
            url.append(e)
        for news_url in url:
            newsInfo = NewsInfo()
            newsInfo.category = element[0]
            if not re.match(r'http',news_url):
                news_url = 'https:' + news_url
            newsInfo.detail_link = news_url
            html = self.__getSouHuHtml(news_url)
            if html == '':
                print('解析网页失败')
                continue
            if not self.__parseFunction(dir_name, newsInfo, html,news_url):
                continue
        print(element[0] + '\t抓取完毕')
    #其他分类页
    def __parseOthers(self,element,dir_name):
        driver = webdriver.Firefox()
        driver.get(element[1])
        time.sleep(3)
        # 逐渐滚动浏览器窗口，令ajax逐渐加载
        for i in range(0, 10):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            i += 1
            time.sleep(4)
        html = driver.page_source
        driver.quit()
        if html == '':
            print('解析网页失败')
            return False
        soup = BeautifulSoup(html,'lxml')
        urls = soup.find_all('a')
        urls1 = set()
        newsInfo = NewsInfo()
        newsInfo.category = element[0]
        for news_url in urls:
            news_url = news_url.get('href')
            if type(news_url) is not str:
                continue
            if not re.match(r'//www', news_url):
                if re.match(r'http', news_url):
                    pass
                else:
                    continue
            else:
                news_url = r'http:'+news_url
            urls1.add(news_url)
        #失败次数过多，直接放弃该网页的爬取，我这儿没线程，所以设置的阈值较小，为了节省时间
        counter_i = 0
        for news_url in urls1:
            if(counter_i>3):
                return False
            newsInfo.detail_link = news_url
            html = self.__getSouHuHtml(news_url)
            if html == '':
                print('解析网页失败')
                counter_i+=1
                continue
            if not self.__parseFunction(dir_name, newsInfo, html, news_url):
                continue
        print(element[0] + '\t抓取完毕')








