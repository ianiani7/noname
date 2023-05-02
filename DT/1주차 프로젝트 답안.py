#%%데이터 가공 ~ googling도 보여주기.  

import pandas as pd

data = pd.ExcelFile(r"C:\Users\InSeong\Desktop\DT\data\1주차 프로젝트 참고자료.xlsx")
data = data.parse(0) #0--> n번째 sheet

data.index= data.pop(data.columns[0]) #pop을 하게 되면 값이 사라지며 인덱스로 들어감
data = data.drop(index="Date")
data.columns=data.iloc[0,:]
data.index.names = ['Date']
data = data.iloc[1:,:]

#%% 일단 생략
import numpy as np
#수익률 Dataframe 만들기 (로그수익률)
# log(x) = (x-1)-(x-1)^2 + ...
# log(a/b) = (a/b-1) +... = (a-b)/b
log_frame = np.log(data.astype(float))  # ~ test is an object dtype array, Try test.values.astype(float) error에 대한 googling도 보여주기.  
return_frame = log_frame.diff()
return_frame = return_frame.dropna()

#%%
#일반적인 수익률 Frame 만들기  - net return
price_difference= data.diff() #data.diff() --> 밑 행 - 위 행
price_shift = data.shift(1) #한칸 밀기
return_frame = price_difference/price_shift 
return_frame = return_frame.dropna()

#%% 일자를 받아서 해당일자의 종목-수익률 dictionary 구성 
import datetime
date_for_research  = input("원하시는 날짜를 적어주세요 ex.2022-05-27 : ")
date_for_research = datetime.datetime.strptime(date_for_research, '%Y-%m-%d')
daily_return = dict(return_frame.loc[date_for_research,:])
#%% dictionary의 메소드 구글링 보여주기  https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
'''' 구글링 잘 해서 복붙하기'''
sorted_dict = sorted(daily_return.items(), key = lambda item: item[1])
winner = dict(sorted_dict[-10:])
loser = dict(sorted_dict[:10])

#%% 주간, 월간, 연간 수익률과 변동성 구하기 from return_frame
# 주간 5영업일, 월간 22영업일, 연간 252영업일로 계산하자 
# 마지막 날 기준 누적수익률

기준일자인덱스 = return_frame.index.get_loc(date_for_research) #2022-05-27의 인덱스 찾기
week_ago = return_frame.index[기준일자인덱스-5]
month_ago = return_frame.index[기준일자인덱스-22]
year_ago = return_frame.index[기준일자인덱스-252]

'''수익률 계산. ex) 0.3/0.2/0.4 3일치의 수익률 --> (1.3*1.2*1.4) - 1
cumprod --> 누적해서 곱함
'''
weekly_ret = (return_frame.iloc[기준일자인덱스-4:기준일자인덱스+1,:]+1).cumprod().iloc[-1,:]-1
monthly_ret = (return_frame.iloc[기준일자인덱스-21:기준일자인덱스+1,:]+1).cumprod().iloc[-1,:]-1
yearly_ret = (return_frame.iloc[기준일자인덱스-251:기준일자인덱스+1,:]+1).cumprod().iloc[-1,:]-1
std_dev= return_frame.iloc[기준일자인덱스-251:,:].std()*np.sqrt(252)
''''일간 --> N(daily return,sigma^2) 연간 --> N(annual return, 252*sigma^2)'''

#%% winner, loser 테이블 만들기 

winner_table = pd.DataFrame(index =["주간수익률","월간수익률","연간수익률","연간변동성"],columns=winner.keys())
loser_table = pd.DataFrame(index =["주간수익률","월간수익률","연간수익률","연간변동성"],columns=loser.keys())

for i in winner_table.columns:
    winner_table.loc["주간수익률",i] = weekly_ret[i]
    winner_table.loc["월간수익률",i] = monthly_ret[i]
    winner_table.loc["연간수익률",i] = yearly_ret[i]
    winner_table.loc["연간변동성",i] = std_dev[i]

for i in loser_table.columns:
    loser_table.loc["주간수익률",i] = weekly_ret[i]
    loser_table.loc["월간수익률",i] = monthly_ret[i]
    loser_table.loc["연간수익률",i] = yearly_ret[i]
    loser_table.loc["연간변동성",i] = std_dev[i]

#여러 데이터 프레임 시트안에 넣기 (구글링 안하면 못함)
writer = pd.ExcelWriter(r"C:\Users\InSeong\Desktop\DT\Assignment\lastprice_for_project1_result.xlsx", engine='xlsxwriter')
winner_table.to_excel(writer, sheet_name='Winner')
loser_table.to_excel(writer, sheet_name='Loser')
writer.close()
writer.save()
