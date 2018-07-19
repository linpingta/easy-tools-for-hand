#-*- coding: utf-8 -*-
import requests
import pandas as pd
from bs4 import BeautifulSoup

# stock_id = '600520'
# query_url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/%s/ctrl/part/displaytype/4.phtml' % stock_id

# for i, df in enumerate(pd.read_html(query_url)):
        # df.to_csv('myfile_%s.csv' % i)

d = {
        u'财务摘要' : 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/%s/displaytype/4.phtml',
        u'资产负债表': 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/%s/ctrl/%s/displaytype/4.phtml',
        u'利润表': 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/%s/ctrl/%s/displaytype/4.phtml',
        u'现金流量表': 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/%s/ctrl/%s/displaytype/4.phtml'
    }

d_c_r = {
        u'财务摘要' : (2, 53, "FundHoldSharesTable"),
        u'资产负债表' : (5, 86, "BalanceSheetNewTable0"),
        u'利润表' : (5, 32, "ProfitStatementNewTable0"),
        u'现金流量表' : (5, 78, "ProfitStatementNewTable0"),
        }

def query_stock(stock_id, table_url, year, table_name):
    # query_url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/%s/ctrl/part/displaytype/4.phtml' % stock_id
    if year == -1:
        query_url = table_url % stock_id
    else:
        query_url = table_url % (stock_id, year) 
    print "query_url ", query_url

    (max_column, max_row, tag_name) = d_c_r[table_name]
    if int(year) == 2018:
        max_column = 2
    r = requests.get(query_url)
    print "cur stock %s" % stock_id
    if r.status_code == requests.codes.ok:
        r.encoding = 'gb2312'
        result = r.text.encode('utf-8')
        # print result
        # print r.encoding
        soup = BeautifulSoup(result, 'lxml')
        table = soup.find('table', {'id': tag_name})
        # print table
        new_table = pd.DataFrame(columns=range(0,max_column), index = range(max_row)) # I know the size 
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            # print "columns ", columns
            for column in columns:
                new_table.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            row_marker += 1
        stock_name = table.find_all('th')[0].get_text().split(' ')[0]
        # print new_table
        return new_table, stock_name


def main():
    stock_ids = []
    with open('stock_id', 'r') as fp:
        while 1:
            line = fp.readline()
            if not line.strip():
                break
            line = line.replace('\n', '')
            stock_ids.append(str(line.strip()))

    years = [2018,2017,2016,2015]
    # stock_ids = ['600519', '600520']
    # years = [2017]
    for table_name, table_url in d.iteritems():
        if table_name == u'财务摘要':
            writer = pd.ExcelWriter('stock_%s.xls' % table_name)
            for sheet_idx, stock_id in enumerate(stock_ids):
                query_table, stock_name = query_stock(stock_id, table_url, -1, table_name)
                stock_name = stock_name.replace('*', '')
                stock_name = stock_name.replace('(', '')
                stock_name = stock_name.replace(')', '')
                stock_name = stock_name.split(u'：')[0]
                query_table.to_excel(writer, '%s' % (stock_name))
            writer.save()
        else:
            for year in years:
                # stock_ids= ['600519', '600520', '600521' ]
                # print table_name, year, stock_ids
                # print table_name
                print year
                print stock_ids
                writer = pd.ExcelWriter('stock_%s_%s.xls' % (table_name, year) )
                for sheet_idx, stock_id in enumerate(stock_ids):
                    query_table, stock_name = query_stock(stock_id, table_url, year, table_name)
                    stock_name = stock_name.replace('*', '')
                    query_table.to_excel(writer, '%s' % (stock_name))
                writer.save()

if __name__ == '__main__':
    main()
