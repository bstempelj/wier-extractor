import requests
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
	for title in findall('<a href="(.*)"><b>(.*)</b></a><br>', site):
		print(title[1])


if __name__ == '__main__':
	(diamonds, pendants) = (read_page(paths[0]), read_page(paths[1]))
	(audi, volvo) = (read_page(paths[2], True), read_page(paths[3], True))

	# overstock
	regex(diamonds)
	regex(pendants)


	# rtvslo

