import scrapy
# from scrapy_splash import SplashRequest
import re
import json
from scrapy.http.headers import Headers
import base64
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy import Spider

class amazon(scrapy.Spider):
    name = "amazon"
    index = 2
    data = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(amazon, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        urls = ['https://www.amazon.in/s?k=nike+shoes&ref=nb_sb_noss']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if self.index > 7:
            return
        # print(str(response.body.decode("utf-8")))
        body = Selector(text=response.text)
        products = body.css('span.rush-component div.s-result-list div.s-result-item')
        # body.css('span.rush-component div.a-section span.celwidget div.a-section div.a-text-center ul.a-pagination li.a-disabled:nth-child(2)')
        for product in products:
            url = response.urljoin(product.css('div.sg-col-inner span.celwidget div div div:nth-child(3) h2 a::attr(href)').extract_first())
            image = response.urljoin(product.css('div.sg-col-inner span.celwidget div div div:nth-child(2) div span a div img::attr(src)').extract_first())
            title = product.css('div.sg-col-inner span.celwidget div div div:nth-child(3) h2 a span::text').extract_first()
            price = product.css('div.sg-col-inner span.celwidget div div div:nth-child(5) div div a span span.a-offscreen::text').extract_first()
            ratings = product.css('div.sg-col-inner span.celwidget div div div:nth-child(4) div span:nth-child(1) span.a-declarative a.a-declarative i.a-icon-star-small span.a-icon-alt::text').extract_first()
            mrp = product.css('div.sg-col-inner span.celwidget div div div:nth-child(5) div div a span.a-text-price span.a-offscreen::text').extract_first()
            savings = product.css('div.sg-col-inner span.celwidget div div div:nth-child(5) div div span:nth-child(2)::text').extract_first()

            print("URL :"+str(url)+"\nImage :"+str(image)+"\nTitle :"+str(title)+"\nPrice :"+str(price)+"\nRatings :"+str(ratings)+"\nMRP :"+str(mrp)+"\nSavings :"+str(savings)+"\n\n")
            self.data.append(
            {
            "url": str(url),
            "title": str(title).strip(),
            "image": str(image),
            "price": str(price).strip(),
            "ratings": str(ratings).strip(),
            "mrp":str(mrp).strip(),
            "discounts": str(savings).strip()})

        yield scrapy.Request(url='https://www.amazon.in/s?k=nike+shoes&page='+str(self.index)+'&ref=sr_pg_'+str(self.index), callback=self.parse)
        self.index += 1

    def spider_closed(self, spider):
        with open('products_amazon_new.json', 'w') as file:
            for d in self.data:
                json.dump({"url": d["url"], "title": d["title"], "image": d["image"], "price": d["price"], "mrp": d["mrp"], "ratings": d["ratings"], "discounts": d["discounts"]}, file)
                file.write(",\n")


class ajio(scrapy.Spider):
    name = "ajio"
    totalPages = 0
    ajioData = list()
    #https://www.ajio.com/api/search?fields=SITE&currentPage=1&pageSize=45&format=json&query=Nike%20T%20shirt%3Arelevance%3ANike%20T%20shirt&sortBy=relevance&text=Nike%20T-shirt&gridColumns=3&advfilter=true

    #https://www.ajio.com/api/search?fields=SITE&currentPage=1&pageSize=45&format=json&query=Nike%20Shoes%3Arelevance%3ANike%20Shoes&sortBy=relevance&text=Nike%20Shoes&gridColumns=3&advfilter=true

    # {"code":"460345198004",
    # "couponStatus":"Coupon Applicable",
    # "fnlColorVariantData":{"brandName":"NIKE","maxQuantity":0,"outfitPictureURL":"https://assets.ajio.com/medias/sys_master/root/h18/hb9/13223223885854/-286Wx359H-460345198-black-OUTFIT.jpg","allPromotions":false,"colorGroup":"460345198_black","sizeFlag":false},
    # "images":[
    # {"altText":"NIKE Black Lace-Ups Downshifter 9 Lace-Up Sports Shoes","format":"product","imageType":"PRIMARY","url":"https://assets.ajio.com/medias/sys_master/root/had/ha8/13223225327646/nike_black_lace-ups_downshifter_9_lace-up_sports_shoes.jpg"},{"altText":"NIKE Black Lace-Ups Downshifter 9 Lace-Up Sports Shoes","format":"mobileProductListingImage","imageType":"PRIMARY","url":"https://assets.ajio.com/medias/sys_master/root/hd0/ha7/13223226114078/nike_black_lace-ups_downshifter_9_lace-up_sports_shoes.jpg"},{"altText":"NIKE Black Lace-Ups Downshifter 9 Lace-Up Sports Shoes","format":"productGrid3ListingImage","imageType":"PRIMARY","url":"https://assets.ajio.com/medias/sys_master/root/hcd/h19/13223225262110/nike_black_lace-ups_downshifter_9_lace-up_sports_shoes.jpg"}
    # ],
    # "fnlProductData":{"returnWindow":0,"toggleOn":"TOGGLE_ON_MODEL","planningCategory":"Footwear"},
    # "discountPercent":"30% off",
    # "price":{"currencyIso":"INR","priceType":"BUY","formattedValue":"Rs. 2,797.00","displayformattedValue":"Rs. 2,797","value":2797},
    # "wasPriceData":{"currencyIso":"INR","priceType":"BUY","formattedValue":"Rs. 3,995.00","displayformattedValue":"Rs. 3,995","value":3995},"name":"Downshifter 9 Lace-Up Sports Shoes",
    # "volumePricesFlag":false,
    # "url":"/nike-downshifter-9-lace-up-sports-shoes/p/460345198_black"}

    def start_requests(self):
        urls = ['https://www.ajio.com/api/search?fields=SITE&currentPage=1&pageSize=45&format=json&query=Nike%20Shoes%3Arelevance%3ANike%20Shoes&sortBy=relevance&text=Nike%20Shoes&gridColumns=3&advfilter=true']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_result)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ajio, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse_result(self, response):
        #pagination totalPages
        data = json.loads(response.body_as_unicode())['products']
        self.totalPages = json.loads(response.body_as_unicode())['pagination']['totalPages']
        for details in data:
            if 'discountPercent' in details.keys():
                discountPercent = details['discountPercent']
            else:
                discountPercent = None
            self.ajioData.append({'url': str(response.urljoin(details['url'])), 'title': str(details['name']), 'price': str(details['price']['value']), 'image': str(details['images'][0]['url']), 'mrp': str(details['wasPriceData']['value']), 'discounts': str(discountPercent)})

        for i in range(2, int(self.totalPages)):
            nextURL = 'https://www.ajio.com/api/search?fields=SITE&currentPage='+str(i)+'&pageSize=45&format=json&query=Nike%20Shoes%3Arelevance%3ANike%20Shoes&sortBy=relevance&text=Nike%20Shoes&gridColumns=3&advfilter=true'
            yield scrapy.Request(url=nextURL, callback=self.parse_result)

    # def parse(self, response):
    #     data = json.loads(response.body_as_unicode())['products']
    #     for details in data:
    #         self.ajioData.append({'title': details['name'], 'price': details['price']['formattedValue'], 'image_url': details['images'][0]['url']})

    def spider_closed(self, spider):
        with open('products_ajio_new.json', 'w') as file:
            for details in self.ajioData:
                json.dump({'url': details['url'], 'title': details['title'], 'price': details['price'], 'image': details['image'], 'mrp': details['mrp'], 'discounts': details['discounts']}, file)
                file.write(',\n')
