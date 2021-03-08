import pandas as pd
from hansard import DATE_FORMAT
from datetime import datetime


df = pd.read_csv('data/officeholdings.csv', sep=',')
df = df.astype({'oh_id': int})
df.set_index('oh_id', inplace=True)
df['start_date'] = pd.to_datetime(df['start_date'], format=DATE_FORMAT)
df = df[df['start_date'] < datetime(year=1910, month=1, day=1)]
df['estimated_start_date'] = df['estimated_start_date'].fillna(value=0)
df['estimated_end_date'] = df['estimated_end_date'].fillna(value=0)
df['in_cabinet'] = df['in_cabinet'].fillna(value=0)
df = df.astype({'estimated_end_date': int, 'estimated_start_date': int, 'in_cabinet': int})

df.to_csv('data/officeholdings.csv', sep=',')
