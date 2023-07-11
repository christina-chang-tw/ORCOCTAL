import numpy as np
import pandas as pd
from lib.csv_operations import export_csv

data1 = (1539.9999999999998,

1540.0049999999997,

1540.0099999999998,

1540.0149999999999,

1540.0199999999998,

1540.0249999999999,

1540.0299999999997,

1540.0349999999996,

1540.0399999999997)

data2 = (1539.9999999999998,

1540.0049999999997,

1540.0099999999998,

1540.0149999999999,

1540.0199999999998,

1540.0249999999999,

1540.0299999999997,

1540.0349999999996,

1540.0399999999997)

data3 = (1539.9999999999998,

1540.0049999999997,

1540.0099999999998,

1540.0149999999999,

1540.0199999999998,

1540.0249999999999,

1540.0299999999997,

1540.0349999999996,

1540.0399999999997)

df = pd.DataFrame()
df["1"] = data1
df["2"] = data2
df["3"] = data3

print(df.eq(df.iloc[:, 0], axis=0).all(axis=1).all(axis=0))
print(df.iloc[:,1])