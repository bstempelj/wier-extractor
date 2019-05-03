import requests, pprint, re
from re import findall
from lxml import html
from io import StringIO
from bs4 import BeautifulSoup


paths = [
	'../pages/overstock.com/jewelry01.html',
	'../pages/overstock.com/jewelry02.html',
	'../pages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
	'../pages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html',
	'../pages/slo-tech.com/Musk zaradi afere s tvitom oglobljen z 20 milijoni dolarjev, odstopa kot prvi mož upravnega odbora @ Slo-Tech.htm',
	'../pages/slo-tech.com/Nvidia lansirala Geforce GTX 1650 @ Slo-Tech.htm',
	'../pages/avto.net/www.Avto.net  Največja ponudba BMW.htm',
	'../pages/avto.net/www.Avto.net  Največja ponudba Volkswagen.htm'
]


def read_page(path, use_utf8=False):
	page = open(path, 'r', encoding='ISO-8859-1') if use_utf8 else open(path, 'r')
	return page.read()


def remove_tags(text):
	tags_re = re.compile(r'<\/?\w+\s*.*?>', re.DOTALL)
	tags = tags_re.search(text)
	while tags is not None:
		text = text[:tags.start()] + text[tags.end():]
		tags = tags_re.search(text)
	return text


def re_rtvslo(site):
	author_re 		  = re.compile(r'<strong>(.*?)</strong>')
	published_time_re = re.compile(r'\d{1,2}\.\s*(januar|februar|marec|april|maj|junij|julij|avgust|september|oktober|november|december)\s*\d{4}\s*\w*\s*\d{2}:\d{2}')
	title_re 		  = re.compile(r'<h1>(.*?)</h1>')
	subtitle_re 	  = re.compile(r'<div class="subtitle">(.*?)</div>')
	lead_re 		  = re.compile(r'<p class="lead">(.*?)</p>')
	content_re 		  = re.compile(r'<article class="article">(.*?)</article>', re.DOTALL)
	text_re 		  = re.compile(r'<p[^>]*>(.*?)<\/p>', re.DOTALL)

	author 			  = author_re.search(site).group(1) # 1: match between tags
	published_time 	  = published_time_re.search(site).group()
	title 			  = title_re.search(site).group(1)
	subtitle 		  = subtitle_re.search(site).group(1)
	lead 			  = lead_re.search(site).group(1)

	# get only text from content
	content = content_re.search(site).group(1)
	content = ''.join(text_re.findall(content))
	content = remove_tags(content)

	json = {
		'author': author,
		'published_time': published_time,
		'title': title,
		'subtitle': subtitle,
		'lead': lead,
		'content': content
	}

	return json


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


def re_slotech(site):
	title_re = re.compile(r'<h3 itemprop="headline"><a href=".*" itemprop="name">(.*?)</a></h3>')
	author_re = re.compile(r'<span itemprop="name">(.*?)</span>')
	date_re = re.compile(r'\d{1,2}\.\s(jan|feb|mar|apr|maj|jun|jul|avg|sep|okt|nov|dec)\s\d{4}')
	time_re = re.compile(r'\d{2}:\d{2}')
	category_re = re.compile(r'itemprop="articleSection">(.*?)<\/a>')
	source_re = re.compile(r'<a\sclass="source".*?>(.*?)<\/a>')
	content_re = re.compile(r'>\s-\s(.*?)</div>', re.DOTALL)

	title = title_re.search(site).group(1)
	author = author_re.search(site).group(1)
	date = date_re.search(site).group()
	time = time_re.search(site).group()
	source = source_re.search(site).group(1)
	category = category_re.search(site).group(1)
	content = remove_tags(content_re.search(site).group(1)).replace('\n', ' ')

	json = {
		'title': title,
		'author': author,
		'date': date,
		'time': time,
		'source': source,
		'category': category,
		'content': content
	}

	return json


def xp_slotech(site):
	f = StringIO(site)
	tree = html.parse(f)
	time_re = re.compile(r'\d{2}:\d{2}')

	base_path = '//div[@id="content"]//article/'
	title_xp = tree.xpath(base_path + 'header/h3[@itemprop="headline"]/a/text()')[0]
	author_xp = tree.xpath(base_path + 'header/ul[@class="info"]//a[@itemprop="author"]/span/text()')[0]
	date_xp = tree.xpath(base_path + 'header/ul[@class="info"]//span[@class="date"]/time/a/text()')[0]

	time_tmp = tree.xpath(base_path + 'header/ul[@class="info"]//span[@class="date"]/time/text()')[0]
	time_xp = time_re.search(time_tmp).group()

	category_xp = tree.xpath(base_path + 'header/ul[@class="info"]/li[@class="categories"]/a/text()')[0]
	source_xp = tree.xpath(base_path + 'div[@itemprop="articleBody"]/a[1]/text()')[0]

	content_xp = "".join(tree.xpath(
		base_path + 'div[@itemprop="articleBody"]/text() | ' +
		base_path + 'div[@itemprop="articleBody"]/a[position()>1]/text()'))

	json = {
		'title': title_xp,
		'author': author_xp,
		'date': date_xp,
		'time': time_xp,
		'source': source_xp,
		'category': category_xp,
		'content': content_xp
	}

	return json



def re_avtonet(site):
	json = { 'cars': [] }

	carname_re = re.compile(r'<a\sclass="Adlink".*?>\n?<span>(.*?)</span>\n?</a>')
	carimg_re = re.compile(r'<div\sclass="ResultsAdPhotoTop">\n?\s*.*?<img\ssrc=\"(.*?)\"', re.DOTALL)
	price_re = re.compile(r'ResultsAdPrice[^>]+>.*?(?<!StaraCena\">)(\d{2}\.\d{3}\s€)', re.DOTALL)
	logo_re = re.compile(r'<div\sclass="ResultsAdLogo">\n?\s*.*?<img\ssrc=\"(.*?)\"', re.DOTALL)
	data_re = re.compile(r'<div\sclass="ResultsAdDataTop">.*?<ul>(.*?)</ul>', re.DOTALL)
	li_re = re.compile(r'<li>(.*?)</li>')

	carnames = carname_re.findall(site)
	carimgs = carimg_re.findall(site)
	logos = logo_re.findall(site)
	prices = price_re.findall(site)[:-1]
	data = []
	for match in data_re.finditer(site):
		di = match.group(1).replace('\n', '').strip()
		di = li_re.findall(di)
		data.append(di)

	for car in zip(carnames, carimgs, logos, prices, data):
		json['cars'].append({
			'name'  : car[0],
			'img'   : car[1],
			'logo'  : car[2],
			'price' : car[3],
			'data'  : car[4],
		})

	return json


def xp_overstock(site):
	f = StringIO(site)
	tree = html.parse(f)

	base_xPath = '//td[2][@valign="top"]'

	titles_list = tree.xpath(base_xPath + '/a/b/text()')
	contents_list = tree.xpath(base_xPath + '/table' + base_xPath + '/span[@class="normal"]/text()')
	listPrices_list = tree.xpath(base_xPath + '/table//td[1][@valign="top"]//tr[1]/td[2]/s/text()')
	prices_list = tree.xpath(base_xPath + '/table//td[1][@valign="top"]//tr[2]/td[2]/span/b/text()')
	tmp = tree.xpath(base_xPath + '/table//td[1][@valign="top"]//tr[3]/td[2]/span[@class="littleorange"]/text()')
	savePrices_list = [price.split(" ") for price in tmp]

	json = {'items': []}
	for item in zip(titles_list, contents_list, listPrices_list, prices_list, savePrices_list):
		json['items'].append({
			'title': item[0],
			'list_price': item[2],
			'price': item[3],
			'saving': item[4][0],
			'saving_percent': item[4][1],
			'content': item[1]
		})

	print(json)


if __name__ == '__main__':
	pp = pprint.PrettyPrinter(indent=2)

	# provided

	(diamonds, pendants) = (read_page(paths[0], True), read_page(paths[1], True))
	(audi, volvo) = (read_page(paths[2], True), read_page(paths[3], True))

	# chosen
	(tesla, nvidia) = (read_page(paths[4]), read_page(paths[5]))
	(bmwi3, arteon) = (read_page(paths[6]), read_page(paths[7]))


	# overstock
	print('--------------------------------')
	print('--- Diamonds | overstock.com ---')
	print('--------------------------------')
	pp.pprint(re_overstock(diamonds))
	pp.pprint(xp_overstock(diamonds))
	print()

	print('--------------------------------')
	print('--- Pendants | overstock.com ---')
	print('--------------------------------')
	pp.pprint(re_overstock(pendants))
	pp.pprint(re_overstock(diamonds))
	print()

	# rtvslo
	print('--------------------------------')
	print('------- Audi | rtvslo.si -------')
	print('--------------------------------')
	pp.pprint(re_rtvslo(audi))
	pp.pprint(xp_rtvslo(audi))

	print('--------------------------------')
	print('------ Volvo | rtvslo.si -------')
	print('--------------------------------')
	pp.pprint(re_rtvslo(volvo))
	pp.pprint(xp_rtvslo(volvo))
	print()


	# slotech
	print('--------------------------------')
	print('------ Tesla | slotech.com -----')
	print('--------------------------------')
	pp.pprint(re_slotech(tesla))
	pp.pprint(xp_slotech(tesla))
	print()

	print('--------------------------------')
	print('----- Nvidia | slotech.com -----')
	print('--------------------------------')
	pp.pprint(re_slotech(nvidia))


	# avtonet
	print('--------------------------------')
	print('------- BMW i3 | avto.net ------')
	print('--------------------------------')
	pp.pprint(re_avtonet(bmwi3))
	print()

	print('--------------------------------')
	print('------- Arteon | avto.net ------')
	print('--------------------------------')
	pp.pprint(re_avtonet(arteon))
