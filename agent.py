import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage

# LLM 추론 엔진으로 사용하여 어떤 작업을 수행할지, 해당 작업을 수행하는데 필요한 입력은 무엇인지 판단하는 모듈
from langgraph.prebuilt import create_react_agent 
import asyncio

load_dotenv()

# API KEYS
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM 구성 : GPT 모델 활용
openai_llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=OPENAI_KEY,
    temperature=0.7,
    max_completion_tokens=1024
)

# 검색 툴 구성
search_tool = TavilySearchResults(max_results=1)


# 프롬프트 구성
# system_prompt = """
# You are a helpful assistant that can search the web about law information. Please answer only legal-related questions.
# If the question is related to previous conversations, refer to that context in your response.
# If the question is not related to law, kindly remind the user that you can only answer legal questions.
# If a greeting is entered as a question, please respond in Korean with "반갑습니다. 어떤 법률을 알려드릴까요?"
# Only answer in Korean.
# """

system_prompt = """
    넌 최고의 노래 빨리 맞추기 장인이야. 넌 노래 제목을 맞추는 것 외의 대답은 할 수 없어
    만약 노래와 관련 없는 질문을 하면 무례한 말투로 노래 외의 질문은 모른다고 해줘
    노래에 대한 질문이나 가사의 일부를 받으면 넌 이어지는 가사 한줄로 답해준 후 답을 말해 주어야 해
    첫 만남 때는 "나는 노래맞추기 장인이야" 라고 해줘
"""



# agent 생성 부분을 try-catch 구문으로 예외처리
try :
    agent = create_react_agent( # LLM 모델 끌어다가 에이전트 만드는 파트인듯 ? create_react_agent 가지고 역할을 부여한 LLM 모델을 배정 하는 느낌으로다가
        model=openai_llm, # 
        tools=[search_tool],
        
        # 시스템 프롬프트(System Prompt), 즉 모델에게 "이런 식으로 행동하라"고 지시하는 초기 메시지 또는 설정값입니다.
        prompt=system_prompt
    )
except Exception as e :
    print(f'Agent 생성 중 오류 발생 : {str(e)}')


# 답변 히스토리 누적 함수
async def process_query(query, conversation_history):
    messages = [HumanMessage(content=system_prompt)] # HumanMessage에 content 를 담아 보내면 뭐가 리턴되는지 확인해봐야 될 듯
    
    # 기존 대화 내용 추가
    for msg in conversation_history :
        if isinstance(msg, tuple) : # 튜플인지 검사?
            messages.append(HumanMessage(content=msg[0]));
            messages.append(AIMessage(content=msg[1]));

    messages.append(HumanMessage(content=query))
    
    # 메세지 상태 선언(저장)
    state = {
        "messages":messages
    }
    
    response = await agent.ainvoke(state) # agent 실행 await 걸면 ainvoke 로 실행
    # ai_message = [message.content for message in response.get('messages', []) if isinstance(messages, AIMessage)] # 답변 추출
    ai_message = [message.content for message in response.get('messages', []) if isinstance(message, AIMessage)]
    
    # 답변을 conversation_history에 추가
    answer = ai_message[-1] if ai_message else "응답을 생성할 수 없습니다."
    conversation_history.append((query, answer))
    
    return answer
    

# 메인 함수
async def main():
    print("법률 관련 질문에 답변해 드립니다. 종료는 'q'를 입력해주세요 : ")
    
    # 대화기록 초기화
    conversation_history = []
    
    is_run = True
    # 대화 루프 시작
    while is_run :
        query = input('질문을 입력 하세요. : ')
        if query.lower() == 'q' :
            print("프로그램을 종료합니다.")
            is_run = False
            break
            
        # 답변처리
        response = await process_query(query, conversation_history)
        print(f"답변 : \n{response}")
        
        
        


print(__name__)

# 프로그램 실행
if __name__ == '__main__' : 
    import asyncio
    asyncio.run(main());
    
    
    