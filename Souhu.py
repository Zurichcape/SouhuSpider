# -*- coding: utf-8 -*-
# 引入模拟浏览器框架支持库
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import os
import requests
# 引入ActionChains鼠标操作类支持库
from selenium.webdriver.common.action_chains import ActionChains
# xpath解析支持库
from lxml import etree
# 自定义的新闻结构体
from NewsInfo import NewsInfo
# 自定义解析html结构的实现类
from ParseNews import ParseNews
class ParseSohu(object):
    '''
    构造函数，初始化资源
    '''
    def __init__(self,url):
        self.url = url
        file_path = '搜狐'
        if (os.path.exists(file_path)):
            pass
        else:
            os.mkdir(file_path)
    def __getSouHuHtml(self,url):
        resHtml = ''
        #验证一下url是否正确
        if url and url != '' and url.startswith(r'http'):
            try:
                # browser = webdriver.Chrome()
                # browser.get(url)
                # resHtml = browser.page_source
                resHtml = requests.get(url,timeout=7)
            except Exception as ex:
                print(ex)
            finally:
                pass
            return resHtml
    def __parseNews(self):
        '''

        获取首页对应的分类页面信息，调用解析类进行爬取
        :param url:
        :return:
        '''
        resHtml = self.__getSouHuHtml(self.url)
        if not resHtml:
            print("解析内容出错")
            return
        soup = BeautifulSoup(resHtml.text,'lxml')
        catagories = soup.find_all('nav', attrs='nav area')
        news_catagories_list = []
        news_catagories_list.append(('搜狐首页',self.url))
        #获取首页对应的分类及相应的url
        for catagory in catagories:
            news_catagories = catagory.find_all('a')
            for news_catagory in news_catagories:
                if not re.match(r'http:', news_catagory.get('href')):
                    news_catagory_url = 'http:' + news_catagory.get('href')
                else:
                    news_catagory_url = news_catagory.get('href')
                news_catagory_name = news_catagory.text
                news_catagories_list.append((news_catagory_name, news_catagory_url))
        for element in news_catagories_list:
            print(element[0]+'\t正在爬取：请稍等...')
            parsenews = ParseNews()
            if not parsenews.parse(element):
                continue
    def run(self):
        self.__parseNews()
if __name__ == '__main__':
    ParseSohu('https://www.sohu.com//').run()