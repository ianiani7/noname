#주어진 기간동안의 주가및 거래량 데이터를 바탕으로 KOSPI200 종목의 거래대금 10분위별 투자전략을 백테스트 
# 1day 데이터 받고 정제하기  (kospi200구성종목 엑셀파일, KOSPI데이터 2개 엑셀파일 Python에서 가져오기 및 데이터 정리)

import pandas as pd 
import numpy as np 

data = pd.ExcelFile(r'C:\Users\InSeong\Desktop\DT\data\퀀트 2주차 프로젝트 참고자료(KOSPI200 구성종목).xlsx')
kospi200구성종목 = data.parse(0)
kospi200구성종목.index = kospi200구성종목.index.map(str)
hist_data = pd.ExcelFile(r'C:\Users\InSeong\Desktop\DT\data\퀀트 2주차 프로젝트 참고자료(KOSPI 데이터).xlsx')
hist_price = hist_data.parse('종가')
hist_amount= hist_data.parse('거래대금')

kospi200_list = [ i[:6] for i in kospi200구성종목['종목코드'] ] 
hist_price.index = hist_price.pop('일자')
hist_amount.index = hist_amount.pop('일자')
hist_price.index= hist_price.index.map(str)
hist_amount.index = hist_amount.index.map(str)
hist_price= hist_price.replace(0, np.nan) #0을 nan으로 바꾸고 drop
hist_amount= hist_amount.replace(0, np.nan)
hist_price = hist_price.dropna(how='all', axis=0)
hist_amount= hist_amount.dropna(how='all', axis=0)


#%% 2day : 특정일자의 kospi200종목들의 한달평균거래대금 dictionary 를 반환하는 함수만들기
#한달의 기준은 22영업일로 한다. 

def average_amount_1m(date): #date = '20220502'  문자형식
    date_location = hist_amount.index.get_loc(date)
    temp = hist_amount.iloc[date_location-22:date_location,:].mean()
    result = {}
    for i in temp.index:
        if i in kospi200_list:
            result[i] = temp[i]
    result = sorted(result.items(), key = lambda item: item[1])
    return result

#%% 3day : 특정일자 한달평균거래대금 하위 10%(20종목)에 대하여 동일가중 투자한 다음날 하루치 수익률 구하기 
date = '20220203' 
port_list = dict(average_amount_1m(date)[:20]).keys() #하위 20종목 티커 가져오기 

#수익률 dataframe 만들기
price_difference= hist_price.diff()
price_shift = hist_price.shift(1)
return_frame = price_difference/price_shift 

sum = 0 
count = 0 
returns_after_1day = return_frame.iloc[return_frame.index.get_loc(date)+1] # 다음날 kospi 모든종목 수익률 데이터가 찍힌다.
for i in returns_after_1day.index:
    if i in port_list:
        sum += returns_after_1day[i]
        count += 1 

print(sum/count)

#%% 4day : 특정일자, 거래대금 n분위 ( 1분위 ~ 10분위) 의 하루치 수익률을 구하는 함수 만들기 
price_difference= hist_price.diff()
price_shift = hist_price.shift(1)
return_frame = price_difference/price_shift 
return_frame = return_frame.fillna(0)

def return_on_amount_quintile( date, n ): # date 입력형식: '20220502' /n : 1~10 분위 
    port_list = dict(average_amount_1m(date)[20*(n-1):20*n]).keys() #하위 20종목 티커 가져오기 
    sum = 0 
    count = 0 
    returns_after_1day = return_frame.iloc[return_frame.index.get_loc(date)+1] # 다음날 kospi 모든종목 수익률 데이터가 찍힌다.
    for i in returns_after_1day.index:
        if i in port_list:
            sum += returns_after_1day[i]
            count += 1 
    return {'분위수': n , '평균수익률' :sum/count, '종목수' : count } 

#%% 5 day: 2021-07-01 ~ 2022-06-24 까지 거래대금분위별 투자전략의 결과를 dataframe에 기록하고 누적수익률을 시각화하여라 
start_index =  hist_price.index.get_loc('20220203' )
end_index =  hist_price.index.get_loc('20220624')

strategy_result = pd.DataFrame(index =hist_price.index[start_index:end_index+1])


for i in hist_price.index[start_index:end_index+1]:
    for j in range(1,11):
        strategy_result.loc[i,j] =  return_on_amount_quintile(i,j)['평균수익률']

cumulative_returns = np.cumprod(strategy_result+1)
cumulative_returns = (cumulative_returns -1)*100 #퍼센트 형태로 반환

import matplotlib.pyplot as plt
plt.plot(cumulative_returns)
plt.xticks(cumulative_returns.index[::22])
plt.legend(cumulative_returns.columns, loc= 'lower left' , fontsize= 6) 
plt.xlabel('Date')
plt.ylabel('Cumulative returns(%)')

#이런 투자 전략은 없지만 무지성 백테스트. 거래량 가장 큰 놈이 수익률 안좋음.