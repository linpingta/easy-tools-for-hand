#-*- coding: utf-8 -*-
import requests
import pandas as pd
from bs4 import BeautifulSoup

# stock_id = '600520'
# query_url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/%s/ctrl/part/displaytype/4.phtml' % stock_id

# for i, df in enumerate(pd.read_html(query_url)):
        # df.to_csv('myfile_%s.csv' % i)

def query_stock(stock_id):
    query_url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/%s/ctrl/part/displaytype/4.phtml' % stock_id
    r = requests.get(query_url)
    print "cur stock %s" % stock_id
    if r.status_code == requests.codes.ok:
        r.encoding = 'gb2312'
        result = r.text.encode('utf-8')
        # print result
        # print r.encoding
        soup = BeautifulSoup(result, 'lxml')
        table = soup.find('table', {'id': "ProfitStatementNewTable0"})
        # print table
        new_table = pd.DataFrame(columns=range(0,6), index = range(32)) # I know the size 
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                new_table.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            row_marker += 1
        stock_name = table.find_all('th')[0].get_text().split(' ')[0]
        return new_table, stock_name


def main():
    stock_ids= ['600519', '600520', '600521' ]
    writer = pd.ExcelWriter('stock_info.xls')
    for sheet_idx, stock_id in enumerate(stock_ids):
        query_table, stock_name = query_stock(stock_id)
        query_table.to_excel(writer, '%s' % (stock_name))
    writer.save()

if __name__ == '__main__':
    main()
