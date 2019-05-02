import requests, pprint, re
from re import findall
from lxml import html
from io import StringIO
from bs4 import BeautifulSoup


paths = [
	'../pages/overstock.com/jewelry01.html',
	'../pages/overstock.com/jewelry02.html',
	'../pages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
	'../pages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html'
]


def read_page(path, use_utf8=False):
	page = open(path, 'r', encoding='ISO-8859-1') if use_utf8 else open(path, 'r')
	return page.read()


def re_rtvslo(site):
	author_re 		  = re.compile(r'<strong>(.*?)</strong>')
	published_time_re = re.compile(r'\d{1,2}\.\s*(januar|februar|marec|april|maj|junij|julij|avgust|september|oktober|november|december)\s*\d{4}\s*\w*\s*\d{2}:\d{2}')
	title_re 		  = re.compile(r'<h1>(.*?)</h1>')
	subtitle_re 	  = re.compile(r'<div class="subtitle">(.*?)</div>')
	lead_re 		  = re.compile(r'<p class="lead">(.*?)</p>')
	content_re 		  = re.compile(r'<article class="article">(.*?)</article>', re.DOTALL)
	text_re 		  = re.compile(r'<p[^>]*>(.*?)<\/p>', re.DOTALL)
	tags_re 		  = re.compile(r'<\/?\w+\s*.*?>', re.DOTALL)

	author 			  = author_re.search(site).group(1) # 1: match between tags
	published_time 	  = published_time_re.search(site).group()
	title 			  = title_re.search(site).group(1)
	subtitle 		  = subtitle_re.search(site).group(1)
	lead 			  = lead_re.search(site).group(1)

	# get only text from content
	content = content_re.search(site).group(1)
	content = text_re.findall(content)
	content = ''.join(content)

	# remove all tags from content
	tags = tags_re.search(content)
	while tags is not None:
		content = content[:tags.start()] + content[tags.end():]
		tags = tags_re.search(content)

	json = {
		'author': author,
		'published_time': published_time,
		'title': title,
		'subtitle': subtitle,
		'lead': lead,
		'content': content
	}

	return json


def xp_rtvslo(site):
	f = StringIO(site)
	tree = html.parse(f)
	author_xp = tree.xpath('//div[@class="author-name"]/text()')[0]
	published_time_xp = tree.xpath('//div[@class="publish-meta"]/text()')[0].strip()
	title_xp = tree.xpath('//header[@class="article-header"]/h1/text()')[0].strip()
	subtitle_xp = tree.xpath('//header[@class="article-header"]/div[@class="subtitle"]/text()')[0].strip()
	lead_xp = tree.xpath('//header[@class="article-header"]/p[@class="lead"]/text()')[0].strip()
	content_xp = ''.join(tree.xpath('//div[@class="article-body"]/article[@class="article"]/p/text()'))

	print(content_xp)

	json_xp = {
		'author': author_xp,
		'published_time': published_time_xp,
		'title': title_xp,
		'subtitle': subtitle_xp,
		'lead': lead_xp,
		'content': content_xp
	}

	return json_xp


def re_overstock(site):
	json = { 'items': [] }

	money_re 	  = r'([$]\s*[0-9.,]+)'
	perct_re 	  = r'(\d+%)'
	title_re 	  = r'<a href="(.*)"><b>(.*)</b></a><br>'
	price_re 	  = r'<span class="bigred"><b>{}</b></span>'.format(money_re)
	list_price_re = r'<s>{}</s>'.format(money_re)
	saving_re 	  = r'{}\s*\({}\)'.format(money_re, perct_re)
	content_re	  = re.compile(r'<span class="normal">(.*?)<br>', re.DOTALL)

	titles 		  = [t[1] for t in findall(title_re, site)]
	list_prices   = findall(list_price_re, site)
	prices 		  = findall(price_re, site)
	savings 	  = findall(saving_re, site)
	content		  = content_re.findall(site)

	for item in zip(titles, list_prices, prices, savings, content):
		json['items'].append({
			'title': item[0],
			'list_price': item[1],
			'price': item[2],
			'saving': item[3][0],
			'saving_percent': item[3][1],
			'content': item[4]
		})

	return json


if __name__ == '__main__':
	pp = pprint.PrettyPrinter(indent=2)

	(diamonds, pendants) = (read_page(paths[0], True), read_page(paths[1], True))
	(audi, volvo) = (read_page(paths[2], True), read_page(paths[3], True))

	# overstock
	print('--------------------------------')
	print('--- Diamonds | overstock.com ---')
	print('--------------------------------')
	#pp.pprint(re_overstock(diamonds))
	print()

	print('--------------------------------')
	print('--- Pendants | overstock.com ---')
	print('--------------------------------')
	#pp.pprint(re_overstock(pendants))
	print()

	# rtvslo
	print('--------------------------------')
	print('------- Audi | rtvslo.si -------')
	print('--------------------------------')
	pp.pprint(re_rtvslo(audi))
	pp.pprint(xp_rtvslo(audi))
	print()so

	print('--------------------------------')
	print('------ Volvo | rtvslo.si -------')
	print('--------------------------------')
	#pp.pprint(re_rtvslo(volvo))
