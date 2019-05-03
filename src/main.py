import requests, pprint, re
from re import findall


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
	page = open(path, 'r', encoding='utf-8') if use_utf8 else open(path, 'r')
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


if __name__ == '__main__':
	pp = pprint.PrettyPrinter(indent=2)

	# provided
	(diamonds, pendants) = (read_page(paths[0]), read_page(paths[1]))
	(audi, volvo) = (read_page(paths[2], True), read_page(paths[3], True))

	# chosen
	(tesla, nvidia) = (read_page(paths[4]), read_page(paths[5]))
	(bmwi3, arteon) = (read_page(paths[6]), read_page(paths[7]))


	# overstock
	print('--------------------------------')
	print('--- Diamonds | overstock.com ---')
	print('--------------------------------')
	pp.pprint(re_overstock(diamonds))
	print()

	print('--------------------------------')
	print('--- Pendants | overstock.com ---')
	print('--------------------------------')
	pp.pprint(re_overstock(pendants))
	print()


	# rtvslo
	print('--------------------------------')
	print('------- Audi | rtvslo.si -------')
	print('--------------------------------')
	pp.pprint(re_rtvslo(audi))
	print()

	print('--------------------------------')
	print('------ Volvo | rtvslo.si -------')
	print('--------------------------------')
	pp.pprint(re_rtvslo(volvo))
	print()


	# slotech
	print('--------------------------------')
	print('------ Tesla | slotech.com -----')
	print('--------------------------------')
	pp.pprint(re_slotech(tesla))
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
