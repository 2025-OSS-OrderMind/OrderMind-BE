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

def filter_add_cancel_without_4digit(df: pd.DataFrame) -> pd.DataFrame:
    """
    채팅내용에 '추가' 또는 '취소'가 포함되어 있고,
    4자리 숫자가 없는 행만 필터링하여 반환
    """
    msg = df['채팅내용']

    # '추가' 또는 '취소' 포함
    contains_add_cancel = msg.str.contains(r"(추가|취소)", regex=True)

    # 4자리 숫자 없음
    no_4digit = ~msg.str.contains(r"\b\d{4}\b", regex=True)

    mask = contains_add_cancel & no_4digit
    return df.loc[mask]