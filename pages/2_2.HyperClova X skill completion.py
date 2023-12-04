import streamlit as st
import httpx
import json

BASE_URL = "https://clovastudio.stream.ntruss.com"

## Functions
def clear_chat():
    if "messages" in st.session_state:
        st.session_state.messages = []
        print(st.session_state.messages)

def query_model(query: str, full_response: str):
    header = {
            "X-NCP-CLOVASTUDIO-API-KEY": st.session_state.clovastudio_api_key,
            "X-NCP-APIGW-API-KEY": st.session_state.apigw_api_key,
            'Accept': 'text/event-stream',
            "Content-Type": "application/json"
        }
    data = {
        "query": query
    }
    with httpx.stream(method="POST", 
                    url=f"{BASE_URL}/testapp/v1/skillsets/{st.session_state.skillset_id}/versions/{st.session_state.skillset_version}/final-answer", 
                    json=data,
                    headers=header, 
                    timeout=120) as res:
        for line in res.iter_lines():
            print(line)
            if line.startswith('event:planning'):
                full_response += "플래닝 중..."
                message_placeholder.markdown(full_response + "▌")
                full_response += "\n\n"
                message_placeholder.markdown(full_response)

            if line.startswith('data:{"selectedSkill"'):
                split_line = line.split("data:")
                line_json = json.loads(split_line[1])
                full_response += f'{line_json["selectedSkill"]} 사용 예정'
                message_placeholder.markdown(full_response + "▌")
                full_response += "\n\n"
                message_placeholder.markdown(full_response)

            if line.startswith('event:cot'):
                full_response += "cot 진행중"
                message_placeholder.markdown(full_response + "▌")
                full_response += "\n\n"
                message_placeholder.markdown(full_response)

            if line.startswith('data:{"finalAnswer"'):
                split_line = line.split("data:")
                line_json = json.loads(split_line[1])
                full_response += line_json["finalAnswer"]
                message_placeholder.markdown(full_response + "▌")
                full_response += "\n\n"
                message_placeholder.markdown(full_response)

            if line.startswith('data:{"data":"[DONE]"}'):
                split_line = line.split("data:")
                full_response += "답변 종료"
                message_placeholder.markdown(full_response + "▌")
                full_response += "\n\n"
                message_placeholder.markdown(full_response)

        message_placeholder.markdown(full_response)
        return full_response

#####################################

st.set_page_config(page_title="Hyper Clova X", page_icon="")

## Sidebars
st.sidebar.header("HCX Config")
st.sidebar.button("Reset", type="primary", on_click=clear_chat)
st.session_state['clovastudio_api_key'] = st.sidebar.text_input("CLOVASTUDIO-API-KEY", type="password", value="")
st.session_state['apigw_api_key'] = st.sidebar.text_input("APIGW-API-KEY", type="password", value="")
#add_model_name = st.sidebar.text_input("Model name", key="hcx_model_name", value="HCX-002")
st.session_state['skillset_id'] = st.sidebar.text_input("skillset-id 입력",  type="default", value="")
st.session_state['skillset_version'] = st.sidebar.text_input("skillset 버전 입력", type="default", value="")
    
## Body
st.markdown("# HCX Chat Completion")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        print(prompt)
        #print(message_placeholder)
        full_response = query_model(query=prompt, full_response=full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    # print(st.session_state.stop_token)
    print(st.session_state.messages)
