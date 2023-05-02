import pandas as pd
import datetime
from pykrx import stock
import time
import numpy as np 
import sqlite3
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import urllib
import requests
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
import smtplib
from email.mime.text import MIMEText 
smtp_info = dict({"smtp_server" : "smtp.naver.com", # SMTP 서버 주소
                  "smtp_user_id" : "pride0404@naver.com", #개인 이메일주소
                  "smtp_user_pw" : "p4613404@" , #naver 비밀번호
                  "smtp_port" : 587}) # SMTP 서버 포트

path = r"C:\Users\InSeong\Desktop\DT\최종 프로젝트"

today = datetime.datetime.today()
oneyear_ago = datetime.datetime.today()-datetime.timedelta(365)

#%%

#1년간의 날짜들 문자열을string으로 반환 
def datelist_oneyear():
    today_str = datetime.datetime.strftime(today, '%m/%d/%y')
    oneyear_ago_str = datetime.datetime.strftime(oneyear_ago, '%m/%d/%y')
    #최근 1년간의 daterange 반환
    date_range = pd.date_range(start=oneyear_ago_str,end = today_str) 
    #해당 data_range를 통하여 pykrx 인풋으로 사용할 수 있는 문자열형태로 반환
    datelist = [] 
    for date in date_range:
        datelist.append(date.strftime("%Y%m%d"))
    return datelist


# pykrx에서 1년 누적 KOSPI 종가 데이터 받는 함수 (시간소요!!)
def get_historical_data(): 
    datelist = datelist_oneyear()
    res = pd.DataFrame()
    for d in datelist:
        df = stock.get_market_ohlcv(d, market= "KOSPI")
        df = df.assign(일자=d)
        #dataframe 합치기 
        res = pd.concat([res, df], axis=0)
        time.sleep(1)
        print(d)
    res = res.assign(티커 = res.index)
    # row-column 정리하기 + 휴일은 nan처리해서 dropna (how = all)
    return res 


# pykrx에서 특정일자 KOSPI 종가 데이터 받는 함수 / 아무인풋 입력안하면 당일 
#date = Y/m/d형식
def get_someday_data(datestr =today.strftime("%Y%m%d") ): #datestr= "2022/08/18"
    df = stock.get_market_ohlcv(datestr, market= "KOSPI")
    df = df.assign(일자=datestr)
    df = df.assign(티커 = df.index)
    return df



#pykrx 결과물을 바로 DB 적재하는 형태로서 input에는 pykrx 함수결과 자체가 들어간다. 
#사용예시 
#DB_saving_price(get_someday_data()) :하루치 데이터 받기
#DB_saving_price(get_historical_data()) : 오늘까지 누적 1년 (장시간 소요) 
def DB_saving_price(pykrx_get_function): #input에는 pykrx 함수결과 자체가 들어간다. 
    res =pykrx_get_function
    conn = sqlite3.connect(path+r"\lowvolfund.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS KOSPI_LASTPRICE  \
    (TICKER text, DATE text, LASTPRICE integer )")
    input_data = []
    for i in range(len(res.index)):
        temp = res.iloc[i,[-1,-2,-6]].tolist()
        temp[-1] = int(temp[-1]) 
        input_data.append(tuple(temp))
    input_data = tuple(input_data)
    c.executemany("INSERT INTO KOSPI_LASTPRICE(TICKER, DATE, LASTPRICE) VALUES(?,?,?)", input_data)
    c.close()
    conn.close()
    print("DB save가 완료되었습니다.")
    return 0


#DB에 저장된 종가들중 최근1년치를 가져온다. 
def DB_parsing_for_1year():
    conn = sqlite3.connect(path+r"\lowvolfund.db", isolation_level=None)
    c = conn.cursor()
    res = pd.read_sql_query("select * from KOSPI_LASTPRICE",conn)
    datelist = datelist_oneyear()
    res = res[res['DATE'].isin(datelist)] #1년치 로드
    res = ((res.pivot(index= 'DATE', columns='TICKER',values='LASTPRICE')).replace(0,np.nan)).dropna(how="all",axis=0)
    c.close()
    conn.close()
    return res 


#특정일자의 투자유니버스 구하는 함수 - KOSPI200종목 불러오기
#date = ymd형식 ex '20230125'
def get_universe(특정일자): 
    return stock.get_index_portfolio_deposit_file("1028",date=특정일자) #1028이면 kospi200 

#공분산행렬을 넣으면 최소변동성을 가지는 weights와, 목표변동성을 반환하여준다.
def get_weights_for_lowvol(cov): 
    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1}) #제약조건: weight의 합은 1 
    bnds = [(0,1)]*len(cov) #각 성분들의 바운더리를 설정합니다. (공매도 허용시 [-1,1])
    w = np.ones(len(cov))/len(cov) # weight의 초기값(임의의 값 설정해도 관계X)
    var = lambda w: w.dot(cov.dot(w.T)) #분산을 구하는 목적함수 
    return [ minimize(var, w,method='SLSQP', bounds = bnds , constraints = cons)['x'],\
            minimize(var, w,method='SLSQP', bounds = bnds , constraints = cons)['fun']]


#특정일자의 포트폴리오 구하기
#date = ymd형식 ex '20230125'
def get_final_port(date):
    historical_data = DB_parsing_for_1year()
    historical_in_kospi200 = historical_data[get_universe(date)].dropna(axis=1)
    index = historical_in_kospi200.index.get_loc(date) #date가 몇번째 자리에 오는지 확인
    data = historical_in_kospi200.iloc[max(0,index-252): index,:] # 최근 1년간의 데이터만 자르기 
    ret_matrix = data.diff()/data.shift(1) #수익률프레임만들기
    ret_matrix = ret_matrix.dropna()
    cov = np.cov(ret_matrix.T) #공분산행렬구하기
    minimize_information = get_weights_for_lowvol(cov) #공분산행렬을 이용하여 최저 vol을 만드는 weight구하기 
    weights , target_vol = minimize_information[0] , np.sqrt(minimize_information[1]*252) 
    port_dict = {}
    for ind, i in enumerate(ret_matrix.columns):
        port_dict[i] = weights[ind]
    return [port_dict, target_vol]

#비중상위20종목 네이버뉴스 긁어오기 
#date = ymd형식 ex '20230125'
def today_news(date):
    
    port = get_final_port(date)
    sorted_dict =  dict(sorted(port[0].items(), key=lambda item: item[1] , reverse=True))
    ticker_list = list( sorted_dict.keys())[:20]
    day = date[:4]+"-"+date[4:6]+"-"+date[6:]
    result =  pd.DataFrame(columns=['종목명','비중','기사제목','기사링크'])
    cnt = 1
    for ticker in ticker_list:
        종목명= stock.get_market_ticker_name(ticker)

        q_enc = urllib.parse.quote_plus(종목명,encoding='euc-kr')
        webpage = requests.get("https://finance.naver.com/news/news_search.naver?q="+q_enc\
                               +'&sm=title.basic&pd=1&stDateStart='+day+'&stDateEnd='+day)
        soup = BeautifulSoup(webpage.content, "html.parser")
        elem_news = soup.select_one('div.newsSchResult dl.newsList')
        elem_news()
        elems_sub= elem_news.select('.articleSubject')
        
        for i in elems_sub:
            기사제목 = i.text.strip()
            기사article_id = i.a.get('href')
            비중 = sorted_dict[ticker]
            result.loc[cnt,:] = [종목명, 비중,\
                     기사제목 ,"https://finance.naver.com"+기사article_id]
            cnt +=1 
    return result 

#date = ymd형식 ex '20230125'
def get_gongsi(date):
    from xml.etree.ElementTree import parse 
    port= get_final_port(date)
    sorted_dict =  dict(sorted(port[0].items(), key=lambda item: item[1] , reverse=True))
    ticker_list = list( sorted_dict.keys())[:20]

    xmlTree= parse(path+r"\CORPCODE.xml")
    root = xmlTree.getroot()
    temp_list = root.findall('list')
    list_for_df = [] 
    for i in range(0,len(temp_list)):
        temp = temp_list[i]
        list_for_df.append([temp.findtext('corp_code'),temp.findtext('corp_name')\
                            ,temp.findtext('stock_code'),temp.findtext('modify_date')])
    corp_code_df = pd.DataFrame(list_for_df,columns = ['corp_code','corp_name','stock_code','modify_date'])
    
    #최종 티커,종목명,corpcode를 박아넣는다. 
    final_list = corp_code_df[corp_code_df['stock_code'].isin(ticker_list)]
    
    key = "9bf24eec2edf273a28b3d7157010ced7abd8fe65"
    url = 	"https://opendart.fss.or.kr/api/list.xml"
    
    result = pd.DataFrame(columns=['종목명','비중','공시제목','공시링크'])
    cnt = 1 #공시수 담을것
    for i in final_list.index:
        params = {'crtfc_key':key, 'bgn_de' : date , 'end_de':date,\
                  'page_no' :1 ,'page_count':100,'corp_code':final_list.loc[i,'corp_code']}
        #url에 요청인자 추가해서 컨텐츠 내려받기 (UTF-8형식 변환해서)
        response = requests.get(url, params=params).content.decode('UTF-8')
        #받은 컨텐츠를 html으로 parsing 
        html = BeautifulSoup(response,'html.parser')
        #html 파일에서 list 태그 가져오기 
        res = html.findAll('list')
        
        비중 = sorted_dict[final_list.loc[i,"stock_code"]]
    
        for j in res:
            result.loc[cnt,:] = [final_list.loc[i,'corp_name'] , 비중,\
                                 j.report_nm.text , "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="+j.rcept_no.text]
            cnt +=1 
    return result 

#엑셀 자료 생성 
#date = ymd형식 ex '20230125'
def get_excel( date =datetime.datetime.strftime(today, '%Y%m%d') ):
    port= get_final_port(date)
    sorted_dict =  dict(sorted(port[0].items(), key=lambda item: item[1] , reverse=True))
    temp = pd.DataFrame(sorted_dict,index=["비중"]).T
    for i in temp.index:
        temp.loc[i,"종목명"] = stock.get_market_ticker_name(i)
    news = today_news(date)
    gonsi = get_gongsi(date)
    writer = pd.ExcelWriter(path+r"\today_lowvolfund_{}".format(date)+".xlsx", engine='xlsxwriter')
    temp.to_excel(writer, sheet_name='펀드비중')
    pd.DataFrame(port[1],index=["목표변동성"],columns=["수치"]).to_excel(writer, sheet_name='목표변동성')
    pd.DataFrame(news).to_excel(writer, sheet_name='비중Top20 뉴스')
    pd.DataFrame(gonsi).to_excel(writer, sheet_name='비중Top20 공시')
    writer.save()
    return 0

def send_email(date =datetime.datetime.strftime(today, '%Y%m%d') ):
    multi = MIMEMultipart(_subtype='mixed') #최종적으로 누적해서 담을 MIME객체생성
    #파일(이미지)을 읽어서 MIMEbase에 담는다. 이후 multi 객체에 누적시킨다.
    with open(path+r'\today_lowvolfund_{}.xlsx'.format(date), 'rb') as fp:
        msg = MIMEBase('application',  _subtype='octect-stream')
        msg.set_payload(fp.read())
        encoders.encode_base64(msg)
    #보낼 파일명에 확장자를 붙혀서 수신자의 조회가 용이하게 합니다.
    # 'Content-Disposition', 'attachment' : 첨부파일을 첨부하게 하는 명령어 
    msg.add_header('Content-Disposition', 'attachment', filename='금일펀드정보_{}.xlsx'.format(date))
    multi.attach(msg)
    
    #이메일 내용 텍스트를 담은 MIMEText도 multi 객체에 누적시킨다.
    메일내용 = '안녕하십니까. xx자산운용 xx대리입니다. {}일자 저변동성펀드 정보 엑셀첨부드립니다. 감사합니다. '.format(date)
    multi.attach(MIMEText(_text = 메일내용, _charset = "utf-8") )
    #이하는 위와 같이 MIME객체를 가지고 송수신자를 결정하여 메일을 보낸다.
    multi['subject'] = "저변동성펀드정보" 
    multi['from'] = smtp_info["smtp_user_id"]
    multi['to'] = "pride0404@naver.com"
    server = smtplib.SMTP(smtp_info["smtp_server"], smtp_info["smtp_port"])
    server.starttls()
    server.login(smtp_info["smtp_user_id"], smtp_info["smtp_user_pw"])
    server.sendmail(multi['from'], multi['to'], multi.as_string())
    return 0 




