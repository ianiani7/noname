import pandas as pd
from glob import glob


#csv파일 통합하기
address = r'C:\Users\dana\Desktop\stock'

file_names = glob(address+'\*.csv') #폴더 내의 모든 csv파일 목록을 불러온다
total = pd.DataFrame()

for file_name in file_names:
    temp = pd.read_csv(file_name,index_col='일자' ,encoding='utf-8') 
    total = pd.concat([total, temp])

