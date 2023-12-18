import streamlit as st
import httpx
import json

BASE_URL = "https://clovastudio.stream.ntruss.com"
DEFALT_MODEL = ["HCX-002"]
DEFAULT_STOP_TOKEN = "<END>"
DEFAULT_PROMPT = """"""

## Functions
def clear_chat():
    if "messages" in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": st.session_state.system_prompt})
    
def default_model(model_name, full_response, message_placeholder):
    header = {
            "X-NCP-CLOVASTUDIO-API-KEY": st.session_state.clovastudio_api_key,
            "X-NCP-APIGW-API-KEY": st.session_state.apigw_api_key,
            'Accept': 'text/event-stream',
            "Content-Type": "application/json"
        }
    data = {
        "messages" : st.session_state.messages,
        "maxTokens": st.session_state["slider_max_token"],
        "topK": st.session_state["slider_top_k"],
        "topP": st.session_state["slider_top_p"],
        "repeatPenalty": st.session_state["slider_repeatPenalty"],
        "tempreature": st.session_state["slider_temparature"]
    }

    with httpx.stream(method="POST", 
                    url=f"{BASE_URL}/testapp/v1/chat-completions/{model_name}", 
                    json=data,
                    headers=header, 
                    timeout=120) as res:
        for line in res.iter_lines():
            if line.startswith("data:"):
                split_line = line.split("data:")
                line_json = json.loads(split_line[1])
                if "stopReason" in line_json and line_json["stopReason"] == None:
                    full_response += line_json["message"]["content"]
                    message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        return full_response

def tuning_model(model_name, full_response, message_placeholder):
    header = {
            "X-NCP-CLOVASTUDIO-API-KEY": st.session_state.clovastudio_api_key,
            "X-NCP-APIGW-API-KEY": st.session_state.apigw_api_key,
            'Accept': 'text/event-stream',
            "Content-Type": "application/json"
        }
    data = {
        "messages" : st.session_state.messages,
        "maxTokens": st.session_state["slider_max_token"],
        "topK": st.session_state["slider_top_k"],
        "topP": st.session_state["slider_top_p"],
        "repeatPenalty": st.session_state["slider_repeatPenalty"],
        "tempreature": st.session_state["slider_temparature"],
        'stopBefore': str(st.session_state.stop_token).split(",") if len(str(st.session_state.stop_token)) > 0 else []
    }

    with httpx.stream(method="POST", 
                    url=f"{BASE_URL}/v2/tasks/{model_name}/chat-completions", 
                    json=data,
                    headers=header, 
                    timeout=120) as res:
        for line in res.iter_lines():
            if line.startswith("data:"):
                split_line = line.split("data:")
                line_json = json.loads(split_line[1])
                if "stopReason" in line_json and line_json["stopReason"] == None:
                    full_response += line_json["message"]["content"]
                    message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        return full_response


# def sliding_window(model_name):
#     print(st.session_state.messages)
#     header = {
#             "X-NCP-CLOVASTUDIO-API-KEY": st.session_state.clovastudio_api_key,
#             "X-NCP-APIGW-API-KEY": st.session_state.apigw_api_key,
#             "Content-Type": "application/json"
#         }
#     data = {
#         "messages" : st.session_state.messages,
#         "maxTokens": 4000,
#     }
#     print(f"{BASE_URL}/testapp/v1/api-tools/sliding/chat-messages/{model_name}/{st.session_state['sliding_window']}")
#     res = httpx.post(url=f"{BASE_URL}/testapp/v1/api-tools/sliding/chat-messages/{model_name}/{st.session_state['sliding_window']}", 
#                     json=data,
#                     headers=header, 
#                     timeout=120)
#     print(res.json())
#####################################

st.set_page_config(page_title="Hyper Clova X", page_icon="")

## Sidebars
st.sidebar.header("HCX Config")
st.sidebar.button("Reset", type="primary", on_click=clear_chat)
st.session_state['clovastudio_api_key'] = st.sidebar.text_input("X-NCP-CLOVASTUDIO-API-KEY", key="hcx_api_key", type="password", value="")
st.session_state['apigw_api_key'] = st.sidebar.text_input("X-NCP-APIGW-API-KEY", key="hcx_api_secret", type="password", value="")
st.session_state['sliding_window'] = st.sidebar.text_input("SLIDING-WINDOW-KEY", key="hcx_sliding_window", type="password", value="")
st.session_state['model_name'] = st.sidebar.text_input("Model name", key="hcx_model_name", value="HCX-002")
st.session_state['system_prompt'] = st.sidebar.text_area(label="System prompt", key="hcx_system_prompt", value=DEFAULT_PROMPT)
st.session_state["stop_token"] = st.sidebar.text_area(label="Stop Token / 공백이 없는 쉼표로 구분", value=DEFAULT_STOP_TOKEN)
st.session_state["slider_repeatPenalty"] = st.sidebar.slider(
    label='Repeat penalty',
    min_value=0.0,
    max_value=10.0,
    value=5.0
)
st.session_state["slider_temparature"] = st.sidebar.slider(
    label="Temparature",
    min_value=0.0,
    max_value=1.0,
    value=0.5
)
st.session_state["slider_top_p"] = st.sidebar.slider(
    label="Top P",
    min_value=0.0,
    max_value=1.0,
    value=0.8
)
st.session_state["slider_top_k"] = st.sidebar.slider(
    label="Top K",
    min_value=0,
    max_value=128,
    value=0
)
st.session_state["slider_max_token"]= st.sidebar.slider(
    label="Max Token",
    min_value=0,
    max_value=4000,
    value=300
)

    
## Body
st.markdown("# HCX Chat Completion")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": st.session_state.system_prompt})
else:
    st.session_state.messages[0]["content"] = st.session_state.system_prompt

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
        if st.session_state.model_name in DEFALT_MODEL:
            full_response = default_model(model_name=st.session_state.model_name, full_response=full_response, message_placeholder=message_placeholder)
        else :
            full_response = tuning_model(model_name=st.session_state.model_name, full_response=full_response, message_placeholder=message_placeholder)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    print(st.session_state.messages)