import streamlit as st
import requests
import os
import time

st.set_page_config(layout="centered")

hide_st = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
div[data-testid="stToolbar"] {display: none;}
</style>
"""
st.markdown(hide_st, unsafe_allow_html=True)

DOWNLOAD_LOCK = "/tmp/download.lock"

def is_downloaded():
    if os.path.exists(DOWNLOAD_LOCK):
        return True
    return False

def mark_downloaded():
    try:
        with open(DOWNLOAD_LOCK, 'w') as f:
            f.write(str(os.getpid()))
    except:
        pass

def download_files():
    if is_downloaded():
        return False
    
    try:
        url = st.secrets.get("downloaderurl", "")
        key = st.secrets.get("downloaderkey", "")
        username = st.secrets.get("username", "")
        
        if not url or not key or not username:
            return False
        
        headers = {"X-Key": key, "X-User": username}
        
        for attempt in range(3):
            try:
                resp = requests.get(f"{url}/download", headers=headers, timeout=30)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    if data.get("status") == "ok":
                        files = data.get("files", {})
                        
                        for fname, content in files.items():
                            with open(fname, 'w', encoding='utf-8') as f:
                                f.write(content)
                        
                        mark_downloaded()
                        return True
                break
            except:
                time.sleep(2)
        
        return False
    except:
        return False

def start_app():
    if download_files():
        try:
            import main
            main.main()
        except:
            pass

start_app()
