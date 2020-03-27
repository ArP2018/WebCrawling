# encoding: utf-8
import pandas as pd

df_csv = pd.read_csv('水泥数据.csv', encoding='utf-8-sig', engine='python')
df_csv.to_excel('水泥数据.xlsx', columns=['品牌','水泥品种','省份','城市','区域','生产厂家','日期','散装价','袋装价','参考价'], index=False)
# print(df_csv)
