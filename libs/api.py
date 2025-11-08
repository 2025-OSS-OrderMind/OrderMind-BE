from openai import OpenAI
import requests

#---------------------예시값----------------------
# LM Studio가 제공하는 로컬 서버 주소
LM_STUDIO_URL = "http://localhost:1234/v1" #예시: 실제 주소로 변경
# API 키
API_KEY = "not-needed"
#--------------------------------------------------


def call_local_ai_server(LM_STUDIO_URL:str, API_KEY:str, prompt_text:str)-> str | None:
    """
    LM Studio 서버에 OpenAI 규격의 Chat Completion 요청을 보내고
    결과 문자열을 파싱하여 반환합니다.
    """
    # LM Studio 서버 주소 + OpenAI Chat Completion 
    full_url = f"{LM_STUDIO_URL}/chat/completions"
    
    #HTTP 헤더 설정 (인증 및 데이터 형식)
    headers = {
        "Authorization": f"Bearer {API_KEY}", #Bearer로 뒤의 값이 토큰임을 인식
        "Content-Type": "application/json" # JSON 형식 데이터 전송
    }

    data = {
        "model": "gemma-3-1b-it", # LM Studio에 로드된 모델 이름으로 변경 
        "messages": [
            {"role": "user", "content": prompt_text} #생성한 주체, 내용
        ],
        "temperature": 0.7, #창의성 조절(0~1)
        "max_tokens": 512 #생성할 최대 토큰 수(변경가능)
    }

    print(f"로컬 서버({LM_STUDIO_URL})에 요청 중...")
    
    try:
        # POST 요청 전송
        response = requests.post(full_url, headers=headers, json=data)
        
        # HTTP 응답 코드가 200 (성공)이 아니면 예외 발생
        response.raise_for_status() 
        
        # 응답 받은 JSON 데이터를 파이썬 딕셔너리로 변환
        response_json = response.json()


        ai_response_string = response_json['choices'][0]['message']['content']
        
        return ai_response_string

    # --- 예외 처리 ---
    except requests.exceptions.RequestException as e:  #api 통신 오류 
        print(f"\n--- API 통신 오류 발생 ---")
        return None
    except KeyError:
        print(f"\n--- 응답 파싱 오류 발생 ---")
        return None




# --- 함수 사용 예시 -----------------
user_prompt = input("AI에게 보낼 프롬프트를 입력하세요: ")
result = call_local_ai_server(LM_STUDIO_URL, API_KEY, user_prompt)

if result: #결과가 None이 아닐 경우
    print("\n--- 로컬 서버 응답 문자열 ---")
    print(result)
#--------------------------------------