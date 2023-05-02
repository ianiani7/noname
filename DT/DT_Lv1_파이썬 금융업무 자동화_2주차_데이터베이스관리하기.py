#sqlite3

# 준비물 DB Browser for SQLite https://sqlitebrowser.org 의 Portable App

import sqlite3
print(sqlite3.version)
print(sqlite3.sqlite_version)
#%%  DB작업 순서  (일반적인경우 )
conn = sqlite3.connect(r"C:\Users\InSeong\Desktop\DT\Testdb\test.db") #DB연결 ( DB가 없을경우 생성됨 )
c = conn.cursor()  # 커서획득
c.execute("CREATE TABLE test_table_1 (test text)") #쿼리작업
conn.commit() #commit : 쿼리작업내용 DB에 적용 ( isolation_level = None으로 자동 커밋가능 )
c.close() #커서닫기
conn.close() #DB연결해제 

#%%
# DB생성 (오토 커밋)
conn = sqlite3.connect(r"C:\Users\InSeong\Desktop\DT\Testdb\test.db", isolation_level=None) #isolationlevel>>자동커밋
#isolation 없으면 conn.commit() 필요 
c = conn.cursor() # 커서 획득 (파일을 읽고 쓰는 주체)
#%% 테이블 생성 (데이터 타입은 TEST, NUMERIC, INTEGER, REAL, BLOB 등)
c.execute("CREATE TABLE IF NOT EXISTS KOSPI200 \
    (tickers text PRIMARY KEY, full_name text, market_cap integer , Lastprice integer)")
    
#%% 테이블 삭제 
c.execute("DROP TABLE KOSPI200")

#%% 데이터 삽입 방법 1 기본 
c.execute("INSERT INTO KOSPI200 \
    VALUES('005930 KS Equity', '삼성전자', 354605083,59500)")
#%% 데이터 삽입 방법 2 튜플로 넣어주기 
c.execute("INSERT INTO KOSPI200(tickers, full_name, market_cap, Lastprice) \
    VALUES(?,?,?,?)", \
    ('000660 KS Equity', 'sk하이닉스', 69378625,95500))
    
#%% 여러개 넣어주기 
test_tuple = (
    ('373220 KS Equity', 'LG에너지솔루션',96057000,410500 ),
    ('207940 KS Equity', '삼성바이오로직스',58006810,815000))
c.executemany("INSERT INTO KOSPI200(tickers, full_name, market_cap, Lastprice) VALUES(?,?,?,?)", test_tuple)
#%% 데이터 삭제 
c.execute("DELETE FROM KOSPI200 WHERE tickers='005930 KS Equity'")
#%%
c.execute("DELETE FROM KOSPI200") #KOSPI200 테이블 초기화 
import pandas as pd 
data = pd.ExcelFile(r"C:\Users\InSeong\Desktop\DT\data\KOSPI 2000 구성종목.xlsx")
data = data.parse(0)
input_data = [] 
for i in data.index:
    temp = data.loc[i,["종목코드","종목명","상장시가총액","종가"]].tolist()
    temp[2:] = list(map(int, temp[2:])) #숫자형변환이 되어야한다. 특수상황 
    input_data.append(tuple(temp))
input_data = tuple(input_data)
c.executemany("INSERT INTO KOSPI200(tickers, full_name, market_cap, Lastprice) VALUES(?,?,?,?)", input_data)

#%%
#데이터 불러오기 
c.execute("SELECT * FROM KOSPI200")
print(c.fetchone())
print(c.fetchone()) #부를때마다 커서가 이동해함 
print(c.fetchone()) #부를때마다 커서가 이동해함 
print(c.fetchone()) #부를때마다 커서가 이동해함 
#%% 데이터 전부 불러보기 
c.execute("SELECT * FROM KOSPI200")
print(c.fetchall())
#%% 데이터 불러서 정리하기 
c.execute("SELECT * FROM KOSPI200")
for row in c.fetchall():
    print(row)
#%% pandas로 데이터 끌어오는 방식 
import pandas as pd 
temp_table = pd.read_sql_query("select * from KOSPI200",conn)

#%% 원하는 필드만 가져오기 
c.execute("SELECT tickers FROM KOSPI200")
print(c.fetchall())

c.execute("SELECT K.tickers 티커 FROM KOSPI200 as K")
ticker_table = pd.read_sql_query("SELECT K.tickers 티커 FROM KOSPI200 as K",conn)
#%%데이터 조회 쿼리 'SELECT FROM WHERE (GROUP BY HAVING ORDER BY) ' 
#방법 1-1 일반 쿼리형 
c.execute("SELECT * FROM KOSPI200 WHERE tickers = '005930 KS Equity'")
print( c.fetchall())
#%%
#방법 1-2 튜플활용 
param1 = ('005930 KS Equity',)
c.execute("SELECT * FROM KOSPI200 WHERE tickers = ? ",param1)
print( c.fetchall())
#%% 
# 방법 2-1 정규식 활용 문자 string 
param2 = '005930 KS Equity'
c.execute("SELECT * FROM KOSPI200 WHERE tickers='%s'" % param2)  # %s %d %f # 예시 :print("안녕하세요 %s" %'키키키')
print('param2', c.fetchone())
print('param2', c.fetchall())
#%% 방법2-2정규식 활용 문자 float
param2 =95500
c.execute("SELECT * FROM KOSPI200 WHERE Lastprice='%f'" % param2)  # %s %d %f
print('param2', c.fetchone())
print('param2', c.fetchall())

#%%
# 방법 3 딕셔너리 활용 
c.execute("SELECT * FROM KOSPI200 WHERE tickers=:삼전", {"삼전": '005930 KS Equity'})
print('param3', c.fetchone())
print('param3', c.fetchall())
#%%
# 방법 4 복수가져오기 
param4 = ('005930 KS Equity', '000660 KS Equity')
c.execute('SELECT * FROM KOSPI200 WHERE tickers IN(?,?)', param4)
print('param4', c.fetchall())

#%%
# 방법 5
c.execute("SELECT * FROM KOSPI200 WHERE tickers In('%s','%s')" % ('005930 KS Equity', '000660 KS Equity'))
print('param5', c.fetchall())
#%%
# 일반적인 쿼리사용 시총 1조 이상 
c.execute("SELECT * FROM KOSPI200 WHERE market_cap>10000000 ")
print(c.fetchall())

# 시총 1조이상기업 데이터프레임으로 들고오기 
temp_table = pd.read_sql_query("SELECT * FROM KOSPI200 WHERE market_cap>10000000 ",conn)

#%% 데이터 수정하기 
#방법 1
c.execute("UPDATE KOSPI200 SET full_name='SAMSUNG_ELECTRONICS' WHERE tickers='005930 KS Equity'")
# 방법 2
c.execute("UPDATE KOSPI200 SET full_name=? WHERE tickers=?", ('LG_ENERGYSOLUTION', '373220 KS Equity'))
# 확인
c.execute("SELECT * FROM KOSPI200")
print(c.fetchone())
print(c.fetchone()) #부를때마다 커서가 이동해함 
    
#%% 데이터삭제하기
#방법1( 여러티커)
c.execute("DELETE FROM KOSPI200 WHERE tickers IN ('005930 KS Equity','373220 KS Equity')")
#방법2(숫자 필터링 )
c.execute("DELETE FROM KOSPI200 WHERE market_cap>10000000")
#%%
# 연결해제
# 연결해제 하지않은채로 db파일을 이동해본다. 옮겨지지 않을것이다. 
c.close()
conn.close()
#에러문구 
c.execute('SELECT * FROM KOSPI200')
#%% DB 백업하기 
conn = sqlite3.connect(r"C:\Users\sangu\Desktop\커리어하이\2강_첨부자료\test.db", isolation_level=None)
c = conn.cursor()
#DB백업 하기. 해당DB를 재구성할 수 있는 sql문이 완성된다. 
#해당 sql을 메모장으로 들고와 실행해보자. 백업 데이터를 만들어내는 쿼리가 들어있다. 
# 해당 쿼리를 새로운 DB에서 SQL실행을 해보자 . 데이터가 복원이 된다.

# conn.iterdump() 살펴보기   
with conn:
    for line in conn.iterdump():
        print(line)
#%%
with conn:
    with open(r"C:\Users\sangu\Desktop\커리어하이\2강_첨부자료\dump.sql", 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)


