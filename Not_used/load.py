import pandas as pd
import dtale

file_path = '../data/raw/imdb_datasets/title.basics.tsv'
pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.width', 1000) # prevent columns from wrapping

df = pd.read_csv(file_path, sep='\t', nrows=1)
print(df)

d = dtale.show(df, subprocess=False)
d.open_browser()