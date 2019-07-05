# -*- coding: utf-8 -*-
import scrapy


class BlogSpiderSpider(scrapy.Spider):
	name = 'blog_spider'
	allowed_domains = ['http://woodenrobot.me']
	start_urls = ['http://woodenrobot.me/']

	def parse(self, response):
		titles = response.xpath('//a[@class="post-title-link"]/text()').extract()
		for title in titles:
			print(">>"*3 + title.strip())
