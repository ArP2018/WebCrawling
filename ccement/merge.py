import os

import pandas as pd

dfs = []
for f in os.listdir('.'):
    if '.txt' in f:
        df = pd.read_csv(f, sep='\t', engine='python', encoding='utf-8',)
        dfs.append(df)

# df_01 = pd.read_csv('output_河南_许昌.txt', sep='\t', engine='python', encoding='utf-8',)
# df_02 = pd.read_csv('output_河南_郑州.txt', sep='\t', engine='python', encoding='utf-8',)
# df_03 = pd.read_csv('output_辽宁_大连.txt', sep='\t', engine='python', encoding='utf-8')

df = pd.concat(dfs, ignore_index=True)
df.to_csv('水泥数据.csv', sep=',', encoding='utf-8', index=False,)
# print(df)
