import pandas as pd

def load_csv(csv_file, nrows=1 * 5000000):
    csv_dtype = {'reason': 'str'}
    # df = pd.read_csv(csv_file, delimiter=",", nrows=nrows, dtype=csv_dtype, quotechar='\'', escapechar="\\", skiprows=1,
    #                  names=['review_id', 'text', 'status', 'reason'])
    df = pd.read_csv(csv_file, delimiter=",", nrows=nrows, dtype=csv_dtype, quotechar="\"", escapechar="\\", skiprows=1,
                     names=['text'])
    df = df.dropna(subset=['text'])
    print(df.shape)
    # uncomment in case of original review file

    # df['reason'] = df[['reason']].fillna('-')
    # df = filter_regional_content(df)
    # df = filter_profane_content(df)
    df = df[['text']]
    reviews = list(df['text'])
    return reviews


def is_ne(reason, ne_reason):
    for res in ne_reason:
        if res in reason:
            return True
    return False


def filter_on_reason(df, ne_reason):
    df['ne_label'] = df.apply(lambda row: 1 if is_ne(row['reason'].lower(), ne_reason) else 0, axis=1)
    return df[df['ne_label'] == 1]


def filter_regional_content(df):
    ne_reason = ['contains non-english content', 'regional language review']
    return filter_on_reason(df, ne_reason)

def filter_profane_content(df):
    ne_reason = ['profane']
    return filter_on_reason(df, ne_reason)