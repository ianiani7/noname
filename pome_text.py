import pandas as pd
import glob
import numpy as np
from datetime import date

file_format = "csv" # .csv .xlsx
file_path = r"C:\Users\InSeong\Desktop\Coding\pome\data" # 파일경로
file_list = glob.glob(f"{file_path}/*{file_format}")

rd_apps = pd.read_csv(file_list[0])

rd_apps2 = rd_apps[['Install Time', 'Media Source' ,'Campaign', 'Country Code', 'Adset','Ad']]

#날짜형식 변경
rd_apps2['Install Time'] = rd_apps2['Install Time'].str.slice(0,10)


country_upper = ['PH', 'TH' , 'ID', 'VN']
country_lower = ['ph', 'th' , 'id', 'vn']

#틱톡 변경
for i, j in zip(country_upper,country_lower):
    rd_apps2.loc[(rd_apps2['Campaign'] == 'restricted') & (rd_apps2['Country Code']== i), 'Campaign'] = 'mintakr_app_aos_ua_tiktok_appinstall_install_{}_230428'.format(j)

#메타 변경
for i, j in zip(country_upper,country_lower):
    rd_apps2.loc[(rd_apps2['Media Source'] == 'restricted') & (rd_apps2['Country Code']== i), 'Campaign'] = 'mintakr_app_aos_ua_meta_advantage+_install_{}_230428'.format(j)

#TNK 변경
for i, j in zip(country_upper,country_lower):
    rd_apps2.loc[(rd_apps2['Campaign'] == 'TNK_AOS_{}_CPE'.format(i)), 'Campaign'] = 'mintakr_app_aos_ua_tnk_rcpi_install_{}_230428'.format(j)


#피벗테이블
rd_apps2['개수'] = 1
rd_apps2 = rd_apps2.fillna(0)
pivot_apps = pd.pivot_table(rd_apps2, index = ['Install Time', 'Media Source' , 'Campaign', 'Adset','Ad'], values = '개수', aggfunc = 'sum')

#출력
pivot_apps = pivot_apps.reset_index()
pivot_apps = pivot_apps.replace(0, np.NaN)
pivot_apps.to_csv( r"C:\Users\InSeong\Desktop\Coding\pome\apps_pome_{}.csv".format(date.today().strftime("%Y-%m-%d")),index=False, encoding='utf-8-sig')

