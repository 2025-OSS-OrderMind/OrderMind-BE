import json
import pandas as pd
from libs.filtering_utils import *
from libs.preprocess_utils import processing_chatlog
from .test_json import my_json_2 as my_json
from collections import OrderedDict
import re

def build_nickname_order_map(df: pd.DataFrame) -> OrderedDict:
    """
    닉네임이 말한 4자리 숫자(주문번호)를 모두 수집하여,
    OrderedDict 로 반환.
    """
    nickname_map = OrderedDict()

    # 4자리 주문번호 패턴
    pattern = re.compile(r"\b(\d{4})\b")

    for idx, row in df.iterrows():
        nickname = row["닉네임"]
        message = row["채팅내용"]

        # 메시지에 있는 모든 4자리 번호 추출
        nums = pattern.findall(message)
        if not nums:
            continue

        # dict에 없으면 생성
        if nickname not in nickname_map:
            nickname_map[nickname] = []

        # 번호들을 append (중복 제거는 선택)
        for num in nums:
            if num not in nickname_map[nickname]:
                nickname_map[nickname].append(num)

    sorted_items = sorted(
        nickname_map.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    return OrderedDict(sorted_items)

def df_to_str(df: pd.DataFrame) -> str:
    lines = df.apply(lambda row: f"{row['날짜시간']} {row['닉네임']} : {row['채팅내용']}", axis=1)
    text = "\n".join(lines)
    return text



if __name__ == '__main__':

    # 위 JSON을 파싱, Dictionary와 배열로 구성되어 있음.
    parsed_json = json.loads(my_json)

    # items를 ["제품명:키워드", "제품명", ...] 으로 파싱.
    items_list = []
    items = parsed_json["items"]
    for item in items:

        item_str = item["name"]
        if (len(item["keywords"])):
            item_str += ":" + ', '.join(item["keywords"])
        
        items_list.append(item_str)
    # items 파싱 완료
    print('\n'.join(items_list))
    
    
    print('\033[96m' + 'items_list 테스트 출력' + '\033[0m', items_list, 
          '\033[96m' + '------------------------------------------------' + '\033[0m', sep='\n')


    email_address = parsed_json['email_address']

    print('\033[95m' + f'EMAIL: {email_address}' + '\033[0m')

    # 파싱한 날짜를 pandas용 Timestamp 객체로 만듦
    start = pd.to_datetime(parsed_json['date_range']['start'])
    end = pd.to_datetime(parsed_json['date_range']['end'])

    # 채팅 로그 파일 경로
    file_dir = 'test_data/Talk_2025.8.8 21_50-1.txt'

    # 채팅 로그로 DataFrame 생성
    df = processing_chatlog(file_dir)

    # 날짜 사이로 필터링
    root_df = filter_by_date_range(df, start, end)

    '''ID란 주문 번호로 쓰는 전화번호 뒤에 4자리 입니다.'''
    # 채팅내용에 ID가 등장하는 해당 채팅 데이터들만 필터링하여 가져옵니다.
    id_df = filter_by_4digit(root_df) 

    #ID가 등장한 채팅 데이터들 출력(임시값 이후 제거 예정)
    print('\033[93m' + '선택한 기간 동안 ID가 등장한 채팅 데이터들입니다.' + '\033[0m', id_df.head(5),
          '\033[93m' + '------------------------------------------------' + '\033[0m', sep='\n')
    
    
    id_list = id_df['채팅내용'].str.extractall(r'(\d{4})')[0].to_list() # ID 리스트를 뽑습니다.
    id_list = list(set(id_list)) # ID가 채팅내역에서 중복되어 나오기 때문에 set으로 감싸줍니다.
    
    print("고객 수: ", len(id_list))

    nickname_orders = build_nickname_order_map(root_df)

    for nick, order_list in nickname_orders.items():
        print(nick, "→", order_list)

    print(df_to_str( filter_by_nickname(root_df, '부끄러워하는 라이언')))

    print(df_to_str(filter_add_cancel_without_4digit(root_df)))

    '''
    for customer_id in id_list: # 사용자 주문번호 목록으로 for 문 시작
        customer_chat_df = filter_by_4digit(root_df, customer_id)

        users = list(set(customer_chat_df['닉네임'].unique()))
        if (len(users) > 1):
            print("해당 주문은 중복 번호가 의심되는 주문번호입니다.")
            print(users)
            print(customer_chat_df)
    

    for customer_id in id_list: # 사용자 주문번호 목록으로 for 문 시작

        customer_chat_df = filter_by_4digit(root_df, customer_id) # 해당 주문번호가 언급된 행만 필터링 한다.
        
        customer_chat_df = customer_chat_df[~customer_chat_df['processed']] # processed가 False인 것만 필터링한다.

        if customer_chat_df.empty: # DataFrame이 비어있으면
            continue

         # 필터링한 df에서 닉네임이 다른 게 있는지 검사하기 위해 닉네임 리스트를 뽑는다.
        users = list(set(customer_chat_df['닉네임'].unique()))

        if (len(users) > 1): # 닉네임 리스트가 1개 이상이면, 해다 주문번호를 여러 사람이 말했다는 것을 뜻하고 일일이 처리 해봐야 함.
            # 해당 주문은 중복 번호가 의심되는 주문번호입니다.

            is_sus = False  # AI로 풀기 복잡해지고, 주문번호 및 닉네임 중복 문제가 심각해지면 해당 플래그를 ON합니다.

            for user in users:  # 중복으로 의심되는 닉네임들로 for문을 돕니다.
                n_df = filter_by_nickname(root_df, user)
                
                n_df = n_df[~n_df['processed']]

                n_id_list = n_df['채팅내용'].str.extractall(r'(\d{4})')[0].to_list() # ID 리스트를 뽑습니다.
                n_id_list = list(set(n_id_list))

                if (len(n_id_list) > 1):
                    is_sus = True
                    break



                
                # ai
            print(users)
            print(customer_chat_df)


    '''




    