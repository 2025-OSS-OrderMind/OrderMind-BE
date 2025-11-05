import pandas as pd
import re

def filter_by_date_range(df:pd.DataFrame, start_time:pd.Timestamp, end_time:pd.Timestamp):
    mask = (df['날짜시간'] >= start_time) & (df['날짜시간'] <= end_time)
    return df.loc[mask]

def filter_by_nickname(df:pd.DataFrame, nickname:str) -> pd.DataFrame:
    return df.loc[df['닉네임'] == nickname]

def filter_by_4digit(df:pd.DataFrame, digit:str | int | None=None) -> pd.DataFrame:
    mask = df['채팅내용'].str.contains(r'\d{4}' if digit is None else str(digit), na=False)
    return df.loc[mask]