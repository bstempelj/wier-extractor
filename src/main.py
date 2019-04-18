import requests, pprint
from re import findall


paths = [
	'../pages/overstock.com/jewelry01.html',
	'../pages/overstock.com/jewelry02.html',
	'../pages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
	'../pages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html'
]


def read_page(path, use_utf8=False):
	if use_utf8:
		return open(path, 'r', encoding='utf-8').read()
	return open(path, 'r').read()


def regex(site):
	json = {
		'items': []
	}

	titles = [t[1] for t in findall('<a href="(.*)"><b>(.*)</b></a><br>', site)]
	list_prices = [lp for lp in findall('<s>(.*)</s>', site)]
	prices = [p for p in findall('<span class="bigred"><b>(.*)</b></span>', site)]

	for item in zip(titles, list_prices, prices):
		json['items'].append({
			'title': item[0],
			'list_price': item[1],
			'price': item[2]
		})

	return json


if __name__ == '__main__':
	pp = pprint.PrettyPrinter(indent=2)

	(diamonds, pendants) = (read_page(paths[0]), read_page(paths[1]))
	# (audi, volvo) = (read_page(paths[2], True), read_page(paths[3], True))

	# overstock
	print('--------------------------------')
	print('--- Diamonds | overstock.com ---')
	print('--------------------------------')
	pp.pprint(regex(diamonds))
	print()

	print('--------------------------------')
	print('--- Pendants | overstock.com ---')
	print('--------------------------------')
	pp.pprint(regex(pendants))


	# rtvslo

