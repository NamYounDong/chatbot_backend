from pydantic import BaseModel # 데이터 타입 정의 모듈
from typing import List, Dict # 타입 힌트 모듈
from fastapi import FastAPI, HTTPException # 웹 서버 모듈, 예외처리 모듈
from fastapi.middleware.cors import CORSMiddleware # 크로스 도메인 설정 모듈
from dotenv import load_dotenv
from agent import process_query # agent.py에서 가져오기

load_dotenv()

# 타입 정의
class ChatMessage(BaseModel) :
    role:str
    parts: List[Dict[str, str]]
    
class ChatRequest(BaseModel):
    contents:List[ChatMessage]
    
class ChatCandidate(BaseModel) :
    content:ChatMessage
    
class ChatResponse(BaseModel) :
    candidates:List[ChatCandidate]
    
app = FastAPI(title="법", description="법")

# CORS 미들웨어 설정
app.add_middleware (
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 유사하게 생겼는데 aysnc를 붙이네?
@app.get("/") # get 방식 / 접근
async def root() : 
    return {"message" : "법 채팅"}

# app.state는 FastAPI 애플리케이션에서 전역적으로 상태를 저장하고 관리할 수 있는 객체입니다. 주요 특징은 다음과 같습니다:
# 전역 상태 관리 : 애플리케이션 전체에서 공유되는 데이터를 저장할 수 있습니다
# 서버가 실행되는 동안 데이터가 유지됩니다
# Spring의 접근 세션과 같은 형태는 아닌듯 그냥 메모리에 올리는 느낌인 듯
app.state.conversation_history = [] # conversation_history 선언

@app.post("/chat", response_model=ChatResponse) # response_model=ChatResponse 리턴 형도 선언해줘야되나? 빼면 어떨지는 궁금한데 하기 귀찮네...
async def chat_endpoint(request: ChatRequest): # request: ChatRequest > 파라미터 전달 받을 객체 선언인듯 Spring @ModelAttribute XxxVo 와 유사한 것 같음 : 실제로 변수가 다른 파라미터 던지니까 405 에러 뿌림
    """법 상담"""
    try :
        # 기존대화 기록 가져오기
        conversation_history = app.state.conversation_history
        
        # 현재 사용자의 입력 메세지 가져오기
        current_user_message = request.contents[-1].parts[0].get("text", "") if request.contents else "" # 이건 문법이 아직도 잘 이해가 안가네 서순이 달라서 그런가? 외국어 듣는 기분임
        
        # AI 답변 생성 
        response = await process_query(current_user_message, conversation_history);
        
        # 응답 형식 구성 및 반환
        return ChatResponse(
            candidates=[
                ChatCandidate(
                    content=ChatMessage(
                        role="bot",
                        parts=[{"text":response}]    
                    )
                )
            ]
        )
    except Exception as e :
        raise HTTPException(status_code=500, detail=f"오류 발생 : {str(e)}")


# 프로그램 실행
if  __name__ == "__main__" :
    import uvicorn # 비동기 웹 서버 활용을 돕는 모듈
    
    # * 실행 방법 종류 : 아래 두 방법 모두 소스 수정 시 자동 반영(Reload)되므로 개발단계 실행 방법으로 보임.
    # 1. uvicorn 파일명(확장자제외):app --reload : 파이썬 실행? fast api 실행?
    # - 아래 소스로 작성
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # 2. python 파일명.확장자 : 파이썬 실행? fast api 실행?
    # - 아래 소스로 작성
    # uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    

