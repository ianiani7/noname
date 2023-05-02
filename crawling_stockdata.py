import pandas as pd
import numpy as np
from pykrx import stock
import time

#추출 날짜 리스트 생성
start_date = '20230420' #형식 = yyyymmdd
end_date = '20230501'
date_range = pd.date_range(start_date,end_date)
#해당 data_range를 통하여 pykrx 인풋으로 사용할 수 있는 문자열형태로 반환
datelist = []
for date in date_range:
    datelist.append(date.strftime("%Y%m%d"))


#설정한 기간의 코스피 데이터 불러오기
#한 번에 많은 종목을 조회하면 ip가 차단될 수 있기에 time.sleep()으로 시간차 둬야
df_kospi = pd.DataFrame()
for d in datelist:
    df = stock.get_market_ohlcv(d, market= "KOSPI")
    df = df.assign(일자=d)
    #dataframe 합치기 
    df_kospi = pd.concat([df_kospi, df], axis=0)
    time.sleep(1)
    print(d)
df_kospi = df_kospi.assign(티커 = df_kospi.index)
#휴일 제거
df_kospi = df_kospi.replace(0, np.NaN)
df_kospi = df_kospi.dropna(subset=['시가'])


#특정 시점 KOSPI100 종가 불러오기
#참조 https://github.com/sharebook-kr/pykrx
ks100date = '20230502' #형식 = yyyymmdd
list_ks100 = stock.get_index_portfolio_deposit_file("1034",ks100date)
#KOSPI100 종목에 맞는 데이터만 추출
df_ks100 = df_kospi[df_kospi['티커'].isin(list_ks100)]
df_ks100 = df_ks100.pivot(index= '일자', columns='티커',values='종가')

#엑셀 추출
address = r'C:\Users\dana\Desktop\stock' #저장경로
df_ks100.to_csv(path_or_buf = address+'\stockprice.csv', encoding = 'utf-8-sig')

