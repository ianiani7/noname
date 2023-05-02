import xlwings

def excel_editing():
    #xlwings 통해 Workbook 호출
    wb = xlwings.Book(r"C:\Users\InSeong\Desktop\DT\data\testxlwings.xlsm").caller()
    sheet = wb.sheets[0]
    sheet["A1"].value = "커리어하이"
    sheet["A2"].value = "안녕하세요"
#%%
import xlwings
def breaking_news(): #3강의 네이버뉴스 속보 응용 
    #xlwings 통해 Workbook 호출
    wb = xlwings.Book(r"C:\Users\InSeong\Desktop\DT\data\testxlwings.xlsm").caller()
    sheet = wb.sheets[0]
    import requests
    from bs4 import BeautifulSoup
    webpage = requests.get("https://finance.naver.com/news/news_list.naver\
                           ?mode=LSS2D&section_id=101&section_id2=258")
    soup = BeautifulSoup(webpage.content, "html.parser")
    for index, i in enumerate(soup.dd.find_all('a')):
        sheet["B"+str(index+1)].value = i.text
        