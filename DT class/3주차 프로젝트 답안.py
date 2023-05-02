# 1
# date list 뽑기 
import pandas as pd
import datetime
today = datetime.datetime.today()
today_str = datetime.datetime.strftime(today, '%m/%d/%y')
date_range = pd.date_range(start='8/1/2022',end = '8/15/2022') # 2022/1/1~ 오늘까지 전체일자 뽑기 

datelist = [] 
for date in date_range:
    datelist.append(date.strftime("%Y%m%d"))
    
# pykrx에서 데이터 받기
import time
from pykrx import stock
res = pd.DataFrame()
for d in datelist:
    df = stock.get_market_ohlcv(d, market= "KOSPI")
    df = df.assign(일자=d) #날짜 컬럼 추가
    #dataframe 합치기 
    res = pd.concat([res, df], axis=0)
    time.sleep(1)
    print(d)
res = res.assign(티커 = res.index) #그냥 인덱스 복사

# 내가 원하는 자료만 추출해서 새로운 dataframe 만들기
# row-column 정리하기 + 휴일은 nan처리해서 dropna / how = all 옵션 -> 모든 데이터가 nan이어야 drop
import numpy as np 
kospi_hist_price = ((res.pivot(index= '일자', columns='티커',values='종가')).replace(0,np.nan)).dropna(how="all",axis=0)
kospi_hist_trading_amount = ((res.pivot(index= '일자', columns='티커',values='거래대금')).replace(0,np.nan)).dropna(how="all",axis=0)

#%% 
#2-1) historical 적재 
import sqlite3
conn = sqlite3.connect(r"C:\Users\InSeong\Desktop\DT\data\projectoring.db", isolation_level=None)
c = conn.cursor()
# c.execute("DROP TABLE KOSPI_LASTPRICE")
# c.execute("DROP TABLE KOSPI_TA")

c.execute("CREATE TABLE KOSPI_LASTPRICE \
    (TICKER text, DATE text, LASTPRICE integer )") #종가
c.execute("CREATE TABLE KOSPI_TA \
    (TICKER text, DATE text, TRADINGAMOUNT integer )") #거래량

#적재할 형식으로 데이터 가공
input_data1 , input_data2 = [] , []
for i in range(len(res.index)): #정제하기 전 데이터로 적재하는 게 편함
    temp1 = res.iloc[i,[-1,-2,-6]].tolist()
    temp2 = res.iloc[i,[-1,-2,-4]].tolist()
    temp1[-1] = int(temp1[-1]) #종가 int로
    temp2[-1] = int( temp2[-1]) #거래대금 int로
    input_data1.append(tuple(temp1))
    input_data2.append(tuple(temp2))
    print(i)

input_data1 = tuple(input_data1)
input_data2 = tuple(input_data2)
c.executemany("INSERT INTO KOSPI_LASTPRICE(TICKER, DATE, LASTPRICE) VALUES(?,?,?)", input_data1)
c.executemany("INSERT INTO KOSPI_TA (TICKER, DATE, TRADINGAMOUNT) VALUES(?,?,?)", input_data2)
c.close()
conn.close()
#%%
#2-2 적재함수 - 해당 날짜의 데이터를 DB로 적재하는 함수 작성
import datetime
def kospidata_to_DB(date =datetime.datetime.today() ): #default today날짜
    import sqlite3
    from pykrx import stock
    conn = sqlite3.connect(r"C:\Users\InSeong\Desktop\DT\data\projectoring.db", isolation_level=None)
    c = conn.cursor()
    today_str = datetime.datetime.strftime(date, "%Y%m%d")
    today_table = stock.get_market_ohlcv(today_str, market= "KOSPI")
    today_table = today_table.assign(일자=today_str,티커 = today_table.index)
    input_data1_ , input_data2_ = [] , []
    for i in range(len(today_table.index)):
        temp1_ = today_table.iloc[i,[-1,-2,-6]].tolist()
        temp2_ = today_table.iloc[i,[-1,-2,-4]].tolist()
        temp1_[-1] = int(temp1_[-1]) 
        temp2_[-1] = int(temp2_[-1])
        input_data1_.append(tuple(temp1_))
        input_data2_.append(tuple(temp2_))
    input_data1_ = tuple(input_data1_)
    input_data2_ = tuple(input_data2_)
    c.executemany("INSERT INTO KOSPI_LASTPRICE(TICKER, DATE, LASTPRICE) VALUES(?,?,?)", input_data1_)
    c.executemany("INSERT INTO KOSPI_TA (TICKER, DATE, TRADINGAMOUNT) VALUES(?,?,?)", input_data2_)
    print("DB insert 완료")
    c.close()
    conn.close()
    return 0
#%%
#3 거래대금20위 공시자료찾기 
import pandas as pd
import datetime

def 상위거래대금20종목공시크롤링():
    today = datetime.datetime.today()
    today_str =datetime.datetime.strftime(today, '%Y%m%d')
    today_table_ = stock.get_market_ohlcv(today_str, market= "KOSPI")
    today_table_ = today_table_.sort_values(by=['거래대금'],ascending=False) #dataframe 거래대금 내림차순 정렬
    tickers_best20 = today_table_.index[:20] #거래대금 상위 20 thicker 추출
    
    
    #2강 강의자료 그대로.
    from xml.etree.ElementTree import parse 
    xmlTree= parse(r"C:\Users\InSeong\Desktop\DT\data\CORPCODE.xml")
    root = xmlTree.getroot()
    temp_list = root.findall('list')
    list_for_df = [] 
    for i in range(0,len(temp_list)):
        temp = temp_list[i]
        list_for_df.append([temp.findtext('corp_code'),temp.findtext('corp_name')\
                            ,temp.findtext('stock_code'),temp.findtext('modify_date')])
    corp_code_df = pd.DataFrame(list_for_df,columns = ['corp_code','corp_name','stock_code','modify_date'])
    
    #최종 티커(상위 20개 종목),종목명,corpcode를 넣는다. 
    final_list = corp_code_df[corp_code_df['stock_code'].isin(tickers_best20)]
    
    import requests
    from bs4 import BeautifulSoup
    
    key = "79b2ff92ec43f1f81057939df2485f517e72603c"
    url = 	"https://opendart.fss.or.kr/api/list.xml"
    
    result = pd.DataFrame(columns=['종목명','거래대금','공시제목','공시링크'])
    cnt = 1 #공시수 담을것
    for i in final_list.index:
        params = {'crtfc_key':key, 'bgn_de' : today_str , 'end_de':today_str,\
                  'page_no' :1 ,'page_count':100,'corp_code':final_list.loc[i,'corp_code']}
        #url에 요청인자 추가해서 컨텐츠 내려받기 (UTF-8형식 변환해서)
        response = requests.get(url, params=params).content.decode('UTF-8')
        #받은 컨텐츠를 html으로 parsing 
        html = BeautifulSoup(response,'html.parser')
        #html 파일에서 list 태그 가져오기 
        res = html.findAll('list')
    
        for j in res:
            result.loc[cnt,:] = [final_list.loc[i,'corp_name'] , today_table_.loc[final_list.loc[i,'stock_code'],'거래대금'],\
                                 j.report_nm.text , "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="+j.rcept_no.text]
            cnt +=1 
    return result
#%%
#4 거래대금20위 네이버 종목 뉴스기사 가져오기 
def 상위거래대금20종목네이버뉴스크롤링():
    today = datetime.datetime.today()
    today_str = datetime.datetime.strftime(today, '%Y%m%d')
    today_table_ = stock.get_market_ohlcv(today_str, market= "KOSPI")
    today_table_ = today_table_.sort_values(by=['거래대금'],ascending=False)
    tickers_best20 = today_table_.index[:20]
    
    
    #2강 강의자료 그대로.
    from xml.etree.ElementTree import parse 
    xmlTree= parse(r'C:\Users\InSeong\Desktop\DT\data\CORPCODE.xml')
    root = xmlTree.getroot()
    temp_list = root.findall('list')
    list_for_df = [] 
    for i in range(0,len(temp_list)):
        temp = temp_list[i]
        list_for_df.append([temp.findtext('corp_code'),temp.findtext('corp_name')\
                            ,temp.findtext('stock_code'),temp.findtext('modify_date')])
    corp_code_df = pd.DataFrame(list_for_df,columns = ['corp_code','corp_name','stock_code','modify_date'])
    
    #최종 티커,종목명,corpcode를 박아넣는다. 
    final_list = corp_code_df[corp_code_df['stock_code'].isin(tickers_best20)]

    import urllib
    import requests
    from bs4 import BeautifulSoup
    
    today_str2 = datetime.datetime.strftime(today, '%Y-%m-%d')
    result =  pd.DataFrame(columns=['종목명','거래대금','기사제목','기사링크'])
    cnt = 1 #기사갯수 담기
    for q in final_list['corp_name']:
        q_enc = urllib.parse.quote_plus(q,encoding='euc-kr')
        webpage = requests.get("https://finance.naver.com/news/news_search.naver?q="+q_enc\
                               +'&sm=title.basic&pd=1&stDateStart='+today_str2+'&stDateEnd='+today_str2)
        soup = BeautifulSoup(webpage.content, "html.parser")
        elem_news = soup.select_one('div.newsSchResult dl.newsList')
        elem_news()
        elems_sub= elem_news.select('.articleSubject')
        
        for i in elems_sub:
            기사제목 = i.text.strip()
            기사article_id = i.a.get('href')
            티커명 = final_list[final_list['corp_name']==q].iloc[0,2]
            result.loc[cnt,:] = [q , today_table_.loc[티커명,'거래대금'],\
                     기사제목 ,"https://finance.naver.com"+기사article_id]
            cnt +=1 
    return result 
