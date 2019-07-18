import pandas as pd

csv_file = 'rw.csv'
csv_dtype = {'reason': 'str'}
nrows = 1 * 5000000

df = pd.read_csv(csv_file, delimiter=",", nrows=nrows, dtype=csv_dtype, quotechar='\'', escapechar="\\", skiprows=1, names=['review_id','text','status','reason'])
df = df.dropna(subset=['text'])

df['reason'] = df[['reason']].fillna('-')

# ne_reason = ['contains non-english content', 'regional language review']
ne_reason = ['profane']
def is_ne(reason):
   for res in ne_reason:
       if res in reason: return True
   return False

df['ne_label'] = df.apply(lambda row: 1 if is_ne(row['reason'].lower()) else 0, axis=1)
df = df[df['ne_label'] == 1]