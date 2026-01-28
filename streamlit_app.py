import streamlit as st
import requests
import os
import time

st.set_page_config(page_title="App", page_icon="📱", layout="centered")

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

LOCK_FILE = "/tmp/app.lock"

def show_status(msg, type="info"):
    if type == "info":
        st.info(msg)
    elif type == "success":
        st.success(msg)
    elif type == "error":
        st.error(msg)
    elif type == "warning":
        st.warning(msg)

def download_files():
    if os.path.exists(LOCK_FILE):
        show_status("⚠️ Already running", "warning")
        return False
    
    show_status("🔍 Starting download process...", "info")
    
    try:
        url = st.secrets.get("downloaderurl", "")
        key = st.secrets.get("downloaderkey", "")
        username = st.secrets.get("username", "")
        
        show_status(f"📡 Server: {url}", "info")
        show_status(f"🔑 Key: {key[:4]}***", "info")
        show_status(f"👤 User: {username}", "info")
        
        if not url or not key or not username:
            show_status("❌ Missing secrets configuration", "error")
            return False
        
        headers = {"X-Key": key, "X-User": username}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for attempt in range(3):
            try:
                status_text.text(f"🔄 Attempt {attempt + 1}/3: Connecting to server...")
                progress_bar.progress((attempt + 1) * 10)
                
                resp = requests.get(f"{url}/download", headers=headers, timeout=30)
                
                status_text.text(f"📥 Response: {resp.status_code}")
                progress_bar.progress(40)
                
                if resp.status_code == 200:
                    status_text.text("✅ Server responded successfully")
                    progress_bar.progress(50)
                    
                    data = resp.json()
                    
                    if data.get("status") == "ok":
                        files = data.get("files", {})
                        
                        status_text.text(f"📦 Received {len(files)} files")
                        progress_bar.progress(60)
                        
                        file_count = 0
                        total_files = len(files)
                        
                        for fname, content in files.items():
                            file_count += 1
                            status_text.text(f"💾 Saving {fname} ({file_count}/{total_files})")
                            
                            with open(fname, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            progress = 60 + (file_count / total_files * 30)
                            progress_bar.progress(int(progress))
                            time.sleep(0.2)
                        
                        with open(LOCK_FILE, 'w') as f:
                            f.write(str(os.getpid()))
                        
                        progress_bar.progress(100)
                        status_text.text("✅ All files downloaded successfully!")
                        show_status("✅ Download complete! Starting automation...", "success")
                        
                        return True
                    else:
                        status_text.text(f"❌ Invalid response: {data}")
                        show_status(f"❌ Server error: {data}", "error")
                
                elif resp.status_code == 403:
                    status_text.text("❌ 403 Forbidden - Key may be used or IP banned")
                    show_status("❌ 403 Forbidden: Key already used or IP banned (wait 30min)", "error")
                    show_status("💡 Solution: Restart Flask server to reset keys", "warning")
                    break
                
                elif resp.status_code == 429:
                    status_text.text("❌ 429 Rate Limited")
                    show_status("❌ Rate limited - Too many requests", "error")
                    break
                
                else:
                    status_text.text(f"❌ HTTP {resp.status_code}")
                    show_status(f"❌ Server returned: {resp.status_code}", "error")
                
                break
                
            except requests.exceptions.Timeout:
                status_text.text(f"⏱️ Timeout on attempt {attempt + 1}")
                show_status(f"⏱️ Connection timeout (attempt {attempt + 1})", "warning")
                time.sleep(2)
                
            except requests.exceptions.ConnectionError as e:
                status_text.text(f"🔌 Connection failed: {str(e)[:50]}")
                show_status(f"🔌 Cannot connect to server", "error")
                time.sleep(2)
                
            except Exception as e:
                status_text.text(f"❌ Error: {str(e)[:50]}")
                show_status(f"❌ Download error: {str(e)[:100]}", "error")
                time.sleep(2)
        
        progress_bar.empty()
        status_text.empty()
        return False
        
    except Exception as e:
        show_status(f"💥 Fatal error: {str(e)}", "error")
        return False

def start_app():
    st.title("🤖 Facebook Auto Messenger")
    st.markdown("---")
    
    if download_files():
        st.markdown("---")
        st.info("🚀 Automation is now running in background...")
        st.info("ℹ️ Check server logs for activity")
        st.markdown("---")
        
        try:
            import main
            main.main()
        except Exception as e:
            show_status(f"❌ Main execution error: {str(e)}", "error")
    else:
        st.markdown("---")
        st.error("❌ Failed to start automation")
        st.info("💡 Check the errors above and fix configuration")
    
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

start_app()
