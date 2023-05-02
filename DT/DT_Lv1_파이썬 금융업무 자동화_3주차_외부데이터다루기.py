#yfinance 
import yfinance as yf ##설치필요 pip install yfinance 

#티커등록
AAPL = yf.Ticker("AAPL")
#주식정보
AAPL.info
#historical 데이터 확인1
hist = AAPL.history(period="max")
#historical 데이터 확인2
hist_data =yf.download('AAPL',start = '2000-01-01')

#배당과 액면분할등의 기업action확인
AAPL.actions
#배당데이터 확인
AAPL.dividends
# 액면병합분할 데이터 확인
AAPL.splits
#재무데이터확인
AAPL.financials
AAPL.quarterly_financials

#대차대조표 확인
bs = AAPL.balance_sheet
qbs = AAPL.quarterly_balance_sheet

# 현금흐름 확인
AAPL.cashflow
AAPL.quarterly_cashflow

#Earning데이터확인
AAPL.earnings
AAPL.quarterly_earnings

# 향후 옵션만기일 가져오기 
AAPL.options

# 특정 만기에 대한 옵션시장데이터 제공 
opt = AAPL.option_chain('2023-02-10')
# data available via: opt.calls, opt.puts

# 복수 티커 등록 ( tickers 변수확인 )
tickers = yf.Tickers('msft aapl goog')
msft_info = tickers.tickers['MSFT'].info
aapl_hist = tickers.tickers['AAPL'].history(period="1mo")
#복수기업 historical데이터 받기 (상위 티커를 사용하지 않는다.)
hist_data = yf.download(['msft','aapl','goog'], start="2021-04-10",\
                        end="2022-05-30",group_by='ticker')

#%%yahoo_fin : yfinance와 공통된 종가및 재무데이터는 생략
from yahoo_fin.stock_info import *
# stat : 현재 기준 해당 기업의 베타, 이동평균, 재무데이터 등을 제공 
stats = get_stats('nflx')
# statvaluation : stat데이터로 계산된 다양한 비율 데이터제공 (PER,PBR등)
stats_valuation= get_stats_valuation('nflx')
# 선물 최근종가데이터
futures = get_futures()
# 실시간데이터 제공
liveprice = get_live_price('nflx')
# 티커들고오기 True를 붙힐시 각 티커별 기업 정보를 확인가능 
tickers = tickers_nasdaq()
nasdaq_table = tickers_nasdaq(True)
tickers = tickers_dow()
dow_table = tickers_dow(True)
tickers = tickers_sp500()
tickers_sp500(True)


#%%pykrx 한국종목이면 여기서 가져오는게 편하다 https://github.com/sharebook-kr/pykrx
# KRX API활용 
from pykrx import stock
#특정시점 상장종목 가져오기
# KOSPI/KOSDAQ/KONEX 종목코드 조회, 날짜생략시 가장최근일자 적용, market생략시 KOSPI적용
tickers = stock.get_market_ticker_list('2000-01-01' , market='KOSPI')

#티커로 종목명 가져오기 
print(stock.get_market_ticker_name(tickers[0]))

#get_market_ohlcv : 시계열 시장데이터 가져오기 시가,저가,종가,고가,거래량 
df = stock.get_market_ohlcv("20220101","20220628","005930")
#frequency 추가 :d,y,m 가능 
df = stock.get_market_ohlcv("20220101","20220628","005930","m")
#수정주가버전으로 가져오기 
df = stock.get_market_ohlcv("20220101","20220628","005930" ,adjusted=True)
#특정일자의 코스피 전종목의 정보가져오기 
df = stock.get_market_ohlcv("20210122", market= "KOSPI")

#일자간격 사이의 변동폭 전체 조회 (코스피) 
df= stock.get_market_price_change("20180301", "20180320")
#특정시점의 투자지표 확인 
df = stock.get_market_fundamental("20210108")

#특정시점의 시가총액가져오기 
df = stock.get_market_cap("20220628")

#공매도 잔고 가져오기 
df = stock.get_shorting_status_by_date("20220101", "20220628", "005930")

#ETF 티커리스트 반환 
tickers = stock.get_etf_ticker_list("20220628")

#ETF용 시계열데이터 
df= stock.get_etf_ohlcv_by_date("20220101", "20220628", "292340")

#PDF 확인용 
df = stock.get_etf_portfolio_deposit_file("152100")

#괴리율 확인 
df = stock.get_etf_price_deviation("20200101", "20200401", "295820")
#%% 여러종목가져오기 : 트래픽초과가능성 있으므로 time.sleep 모듈 사용. 시간 간격 두면서 for문 돌림
import time
import pandas as pd
stock_code = stock.get_market_ticker_list() 
# stock_code = ['005930','000660']
res = pd.DataFrame()
for ticker in stock_code[:4]:
    df = stock.get_market_ohlcv_by_date(fromdate="20100101", todate="20220628", ticker=ticker)
    #df.assign: 컬럼을 추가하고 특징 추가하기 (아래예시)
    #tempdf= pd.DataFrame(index=[1])
    #tempdf=tempdf.assign(a='a')
    df = df.assign(종목코드=ticker, 종목명=stock.get_market_ticker_name(ticker))
    #dataframe 합치기 
    res = pd.concat([res, df], axis=0)
    time.sleep(1)
res
#%% pandas_datareader 살펴보기 
import pandas_datareader.data as pdr

df_pdr = pdr.DataReader('000660', 'naver', start='2010-01-01', end='2022-06-28')
df_pdr = pdr.DataReader('000660.KS', 'yahoo', start='2010-01-01', end='2022-06-28')






#%% Dart API 활용하여 금감원 데이터 가져오기 
#종목코드 모두 가져오기 
KEY =  "79b2ff92ec43f1f81057939df2485f517e72603c"

from xml.etree.ElementTree import parse #xml 파싱하는 모듈
import pandas as pd 

#받은 xml파일을 parsing 
xmlTree= parse(r'C:\Users\InSeong\Desktop\DT\data\CORPCODE.xml')
# get_root = 최상위루트를 지정 
root = xmlTree.getroot()
#루트에서 각 list태그들 전부 가져오기  
temp_list = root.findall('list')

list_for_df = [] 

# stock_code는 상장사만 있습니다. 
for i in range(0,len(temp_list)):
    temp = temp_list[i]
    list_for_df.append([temp.findtext('corp_code'),temp.findtext('corp_name')\
                        ,temp.findtext('stock_code'),temp.findtext('modify_date')])

corp_code_df = pd.DataFrame(list_for_df,columns = ['corp_code','corp_name','stock_code','modify_date'])
corp_code_df.to_excel(r'C:\Users\InSeong\Desktop\DT\data\CORPCODE.xlsx')
#%% 주요사항보고 공시 리스트 가져오기 -함수구성
#https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001
 
from bs4 import BeautifulSoup #html 웹문서를 파싱하고 조회하는 모듈 
import requests #url 호출하는 모듈 (요청인자의 경우 params뒤에 요청인자 dictionary를 추가한다.)


def get_search(bgn_de, end_de, page_no, page_count,pblntf_ty = "B"):
    key = "79b2ff92ec43f1f81057939df2485f517e72603c"
    url = 	"https://opendart.fss.or.kr/api/list.xml"
    params = {'crtfc_key':key, 'bgn_de' : bgn_de , 'end_de':end_de,\
              'page_no' :page_no, 'page_count':page_count,'pblntf_ty':pblntf_ty}
    #url에 요청인자 추가해서 컨텐츠 내려받기 (UTF-8형식 변환해서)
    response = requests.get(url, params=params).content.decode('UTF-8')
    #받은 컨텐츠를 html으로 parsing 
    html = BeautifulSoup(response,'html.parser')
    #html 파일에서 list 태그 가져오기 
    res = html.findAll('list')
    return res
#%% 주요사항보고 공시 리스트 가져오기 - 결과 출력
from datetime import datetime as dt 
today = dt.today() #20220704
today_str= today.strftime('%Y%m%d')#원하는문자열로 변경  
today_str= '20220704'
# 오늘공시되는 주요사항보고서, 100개씩 한페이지에 검색할때 첫번째페이지 내용정리 및 저장
# 아래 rcept_nm (공시접수번호) 는 개별 공시내용 링크를 만드는데에 용이하다. 

result = get_search(today_str, today_str,1, 100) 
list_for_df = [] 
for i in result:
    print(i.corp_code.text , i.flr_nm.text, i.report_nm.text, i.rcept_no.text )
    list_for_df.append([i.corp_code.text , i.flr_nm.text, i.report_nm.text,\
                        "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="+i.rcept_no.text])

rcept_df = pd.DataFrame(list_for_df,columns=['회사코드','회사명','공시내용','공시링크'])
rcept_df.to_excel(r'C:\Users\sangu\Desktop\커리어하이\3강_첨부자료\공시내용정리.xlsx')

#%% 받은공시리스트중 유상증자결정된 회사( 초록뱀컴퍼니 00349811)에 대하여 상세 내용 크롤링.
#https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020023 유상증자 개발가이드 참조 
#개발가이드에 없는 내용은 https://dart.fss.or.kr/dsaf001/main.do?rcpNo=접수번호 형식으로 직접 공시에 접근해야함.

def get_pifricDecsn_details(corp_code,bgn_de,end_de):
    url = "https://opendart.fss.or.kr/api/piicDecsn.xml"
    key = "79b2ff92ec43f1f81057939df2485f517e72603c"
    params = {'crtfc_key':key, 'bgn_de' : bgn_de , 'end_de':end_de,'corp_code':corp_code}
    response = requests.get(url, params=params).content.decode('UTF-8')
    html = BeautifulSoup(response,'html.parser')
    
    res_dict = {"회사명": html.corp_name.text\
                ,"신주수(보통)": html.nstk_ostk_cnt.text\
                ,"신주수(기타)": html.nstk_estk_cnt.text\
                , "주당액면가":html.fv_ps.text\
                , "증자전 발행주식총수(보통)":html.bfic_tisstk_ostk.text \
                , "증자전 발행주식총수(기타)":html.bfic_tisstk_estk.text \
                , "증자방식":html.ic_mthn.text}
    return res_dict

#결과출력 (최초공시일자를 기준으로 가져오므로 bgn_de를 여유있게 두었음.)
print(get_pifricDecsn_details('00349811','20220601','20220708'))

#%%네이버 뉴스 크롤링 

#네이버 금융뉴스 실시간 속보 크롤링
import requests #url 호출
from bs4 import BeautifulSoup
webpage = requests.get("https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258")
soup = BeautifulSoup(webpage.content, "html.parser")

#크롤링결과물(html) 보기 
print(soup)

#dd태그만 찾기 (모든 dd태그를 가져온다.)
print(soup.dd)
print(len(soup.dd)) #article subject와 articleSummary가 전부포함
#dd태그안에 a태그 전부 들고오기 
print(soup.dd.find_all('a')) 

#a태그 안의 text 들고오기 
for i in soup.dd.find_all('a'):
    print(i.text)

#%%
# 특정종목(진에어) 뉴스기사 가져오기 

import urllib #한글 인코딩 과정
q='진에어' 
q_enc = urllib.parse.quote_plus(q,encoding='euc-kr') 
print(q_enc)
webpage = requests.get("https://finance.naver.com/news/news_search.naver?q="+q_enc)
soup = BeautifulSoup(webpage.content, "html.parser")
print(soup)

# 웹사이트 방문후 https://finance.naver.com/news/news_search.naver?q=%C1%F8%BF%A1%BE%EE
# 도구 > 개발자도구 > Elements 들어가서 구성확인및 태그찾기 

elem_news = soup.select_one('dl.newsList') #div내 클래스 하나만 .으로 접근 
elems_sub= elem_news.select('.articleSubject') #클래스 내 클래스 .으로 접근
elems_summary= elem_news.select('.articleSummary') #클래스 내 클래스 .으로 접근


for i in elems_sub:
    print(i.text)
for i in elems_sub:
    print(i.text.strip())

#%%디테일한 조건하에 뉴스기사 가져오기 
# 제목에서만 종목명적용 + 시작날짜 끝날짜
# https://finance.naver.com/news/news_search.naver?rcdate=&q=%BB%EF%BC%BA%C0%FC%C0%DA 
# &x=16&y=18&sm=title.basic&pd=1&stDateStart=2022-05-31&stDateEnd=2022-05-31
# x,y,pd의 경우 데이터에 영향을 주는 변수가 아니므로, 생략해도 된다. 

q='sk하이닉스' #바꿔쓰면 다가져와짐 
q_enc = urllib.parse.quote_plus(q,encoding='euc-kr')
webpage = requests.get("https://finance.naver.com/news/news_search.naver?q="+q_enc\
                       +'&sm=title.basic&pd=1&stDateStart=2022-07-07&stDateEnd=2022-07-08')
soup = BeautifulSoup(webpage.content, "html.parser")
elem_news = soup.select_one('div.newsSchResult dl.newsList')
elem_news()
elems_sub= elem_news.select('.articleSubject')
elems_summary= elem_news.select('.articleSummary')

print(elems_sub) #제목들 다 가져오기 
print(elems_summary) #기사 summary 다 가져오기 
#%%
import re
#기사의 화이트스페이스 정리방법: 정규식 (re 모듈)
#( 참고사이트 : https://cosmosproject.tistory.com/180 )
print(elems_sub[0]) #예시 제목
print(elems_summary[0]) #예시 summary
for ii,i in enumerate(elems_sub):
    #.strip() : 양옆에 공백과 띄어쓰기 제거 
    print(i.text.strip() )
     #\s(띄어쓰기 공백)가 2회부터 무한대까지 반복되는것을 모두 제거
    print(re.sub('\s{2,}','',elems_summary[ii].text.strip()))
    #print(elems_summary[ii].text.strip()) #제거전 버전 

#%% href(reference)를 통해 기사내용 가져오기 
print(elems_sub[0]) #제목구성요소 분석
print(elems_sub[0].a.get('href')) #제목의 reference 가져오기 
url_temp = "https://finance.naver.com"+elems_sub[0].a.get('href')
webpage = requests.get(url_temp)
soup = BeautifulSoup(webpage.content, "html") #lxml로 돌려라는 경고문이 뜨기도한다. 
contents = soup.select_one('div.articleCont').text.strip()
