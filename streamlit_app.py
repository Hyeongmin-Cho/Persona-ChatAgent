import streamlit as st
import uuid
from src.graph.graph import get_persona_graph
from langchain_core.messages import HumanMessage
import api_keys


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [] # [{"role": "...", "content": "..."}, ...]
    
    if "persona_graph" not in st.session_state:
        st.session_state.persona_graph = get_persona_graph()
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = uuid.uuid4()
    
    if "profile" not in st.session_state:
        st.session_state.profile = None


def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("User").write(message["content"])
        else:
            st.chat_message("Assistant").write(message["content"])


def process_message(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    display_messages()
    
    assistant_response = st.chat_message("Assistant").empty()
    
    config = {"configurable": {"thread_id": st.session_state.thread_id}} # LangGraph MemorySaver 설정
    
    with st.spinner("생각 중..."):
        final_response = None
        for event in st.session_state.persona_graph.stream({"messages": [HumanMessage(content=user_input)]}, config):
            for value in event.values():
                final_response = value["messages"][-1].content
                if profile := value.get("profile", None):
                    st.session_state.profile = profile
    
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    assistant_response.markdown(final_response)
    

def main():
    st.title("Persona ChatAgent")
    init_session_state()
    
    with st.sidebar: # 사이드바 선언
        st.header("설정")
        
        if st.button("대화 초기화"): # 대화 초기화
            st.session_state.messages = []
            st.session_state.profile = None
            st.session_state.thread_id = f"thread_{uuid.uuid4()}"
            # st.session_state.person_graph = get_persona_graph()
            st.rerun()

        if st.session_state.profile: # 설정된 프로필 정보 출력
            st.header("캐릭터 정보")
            st.write(f"캐릭터: {st.session_state.profile.get('character_name', '정보 없음')}")
            st.write(f"세계관: {st.session_state.profile.get('universe', '정보 없음')}")
            st.write(f"요구사항: {st.session_state.profile.get('requirements', '정보 없음')}")
            st.write(f"사용자명: {st.session_state.profile.get('user_name', '정보 없음')}")
    
    display_messages()
    
    # 대화 시작
    user_input = st.chat_input("메시지를 입력하세요...")
    if user_input:
        process_message(user_input)


if __name__ == "__main__":
    main()
