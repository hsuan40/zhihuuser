# -*- coding: utf-8 -*-
#import scrapy
from scrapy import Request,Spider
from zhihuuser.items import UserItem
import json

headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'authorization':'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
}


class ZhihuSpider(Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    #第一步：找一個起始用戶(勇哥)
    #第二步：構造取得特定user關注人列表的通用url結構
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    start_user = 'tianshansoft'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics' #查詢參數

    #第三步：構造取得特定user基本資料頁面資訊的通用url結構
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics' #查詢參數


    #第二步勇哥的個人訊息及第三步勇哥關注人列表的請求
    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query), callback=self.parse_user, headers=headers)
        yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20 ), callback=self.parse_follows, headers=headers)

    def parse_user(self,response):
        #print(response.text) #為json格式
        result = json.loads(response.text)
        item= UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field]=result.get(field)
        yield item  #把字典形式訊息保存下來


    #解析user關注人頁面,取得關注人名稱並構造關注人url,翻頁及再遞迴取得資料
    def parse_follows(self,response):
        #print(response.text)
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),self.parse_user, headers=headers)

        #翻頁，取得下一分頁連結
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.parse_follows,headers=headers) #自己調用自己，形成翻頁





