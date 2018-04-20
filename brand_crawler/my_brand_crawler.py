#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import re
from bs4 import BeautifulSoup, SoupStrainer


def parse_basic_page(basic_link):
    brand_link_dict = {}

    requests_session = requests.Session()
    params = {}
    response = requests_session.request(
        'GET',
        basic_link,
        params = params
    )
    if response.status_code == 200:
        content = response.content
        print "get basic page success"
        soup = BeautifulSoup(content, 'html.parser')
        for href in soup.find_all('a'):
            try:
                link = href['href']
                brand = href.string
                if link and brand:
#                    print brand_name, link
                    brand_link_dict[str(brand)] = link
            except Exception as e:
                print e
                continue

        #links_to_brand = SoupStrainer('a', href=re.compile('brand.ppsj.com.cn/'))
#        for tag in BeautifulSoup(content, parse_only=links_to_brand):
#            print tag
#            print tag['href']
#            print type(tag)

    else:
        print "get basic page fail"
    return brand_link_dict

def parse_brand_page(link):
    brand_names = []
    requests_session = requests.Session()
    params = {}
    response = requests_session.request(
        'GET',
        link,
        params = params
    )
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        for href in soup.find_all('a'):
            try:
                link = href['href']
                if href.get('class'):
                    continue
                if 'http' not in link or 'ppsj.com' not in link:
                    continue
                brand_name = href.string
                if not brand_name or brand_name.strip() == 'NEXT':
                    continue
                if brand_name in brand_names:
                    continue
                brand_names.append(brand_name)
                #print brand_name
            except Exception as e:
                continue
    else:
        print "get basic page fail"
    return brand_names

def main():
    # 获取品牌名及品牌链接
    basic_link = 'http://brand.ppsj.com.cn/'
    brand_link_dict = parse_basic_page(basic_link)

    # 访问具体页面获取品牌词表
    for brand, link in brand_link_dict.iteritems():
        try:
            print "brand ", brand, link
            brand_names = parse_brand_page(link)
            with open("data/brand_%s" % brand, 'w') as fp:
                for brand_name in brand_names:
                    fp.write('%s\n' % brand_name)
            #break
        except Exception as e:
            print e


if __name__ == '__main__':
    main()
