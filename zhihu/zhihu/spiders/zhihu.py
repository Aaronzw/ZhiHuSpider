import scrapy
import re
from zhihu.items import ZhihuItem


class ZhiHuSpider(scrapy.Spider):

    name = "zhihu"
    start_urls = ['https://zhihu.com']
    allowed_domains = ['www.zhihu.com']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 ('
                      'KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
        'Referer': 'http://www.zhihu.com/',
    }

    post_data = {
        'password': 'passssssss',
        'captcha_type': 'cn',
        'email': '123456789@qq.com'
    }

    def start_requests(self):
        yield scrapy.Request('https://www.zhihu.com', headers=self.headers, callback=self.login_zhihu)

    def login_zhihu(self, response):
        xsrf = re.findall(r'name="_xsrf" value="(.*?)"', response.text)[0]
        self.headers['X-Xsrftoken'] = xsrf
        times = re.findall(r'<script type="text/json" class="json-inline" data-n'
                           r'ame="ga_vars">{"user_created":0,"now":(\d+),', response.text)[0]
        captcha_url = 'https://zhihu.com' + 'captcha.gif?r=' + times + '&type=login&lang=cn'
        yield scrapy.Request(captcha_url, headers=self.headers, callback=self.veri_captcha)

    def veri_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        loca1 = input('input the loca 1:')
        loca2 = input('input the loca 2:')
        captcha = self.location(loca1, loca2)
        self.post_data['captcha'] = captcha
        post_url = 'https://www.zhihu.com/login/email'
        yield scrapy.FormRequest(post_url, formdata=self.post_data, headers=self.headers, callback=self.login_success)

    def location(self, a, b):
        a = 20 * int(a) +2
        if b != 0:
            b = 20 * int(b) +2
            captcha = "{\"img_size\":[200,44],\"input_points\":[[%s,26.45],[%s,29.45]]}" %(int(a),int(b))
        else:
            captcha = "{\"img_size\":[200,44],\"input_points\":[[%s,26.45]]}" % a
        return captcha

    def login_success(self, response):
        if 'err' in response.text:
            pass
        else:
            yield scrapy.Request('https://www.zhihu.com', headers=self.headers)

    def parse(self, response):
        item = ZhihuItem()
        patt = r'<meta itemprop="name" content="(.*?)"/>'
        articles = re.findall(patt, response.text)
        for a in articles:
            item['title'] = a
            yield item

