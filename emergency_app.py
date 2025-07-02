import streamlit as st
from twilio.rest import Client
from streamlit_js_eval import streamlit_js_eval
import geocoder

st.set_page_config(page_title="Emergency Assistant", page_icon="🚨")
st.title("🚨 Emergency AI Assistant")

# ✅ Browser-based voice output using JavaScript
def speak_browser(text: str):
    st.components.v1.html(f"""
        <script>
        const utterance = new SpeechSynthesisUtterance("{text}");
        utterance.lang = "en-US";
        window.speechSynthesis.speak(utterance);
        </script>
    """, height=0)

# Emergency Classifier
def classify_emergency(text):
    text = text.lower()
    if "fire" in text:
        return "fire", "101"
    elif "accident" in text or "ambulance" in text:
        return "medical", "102"
    elif "crime" in text or "thief" in text:
        return "police", "100"
    return "general", "112"

# GPS via browser
def get_precise_location():
    coords = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="getpos")
    if coords and 'coords' in coords:
        return coords['coords']['latitude'], coords['coords']['longitude']
    else:
        g = geocoder.ip('me')
        return g.latlng if g.ok else (0, 0)

# Send SMS via Twilio
def send_sms(message, contacts):
    account_sid = st.secrets["TWILIO_SID"]
    auth_token = st.secrets["TWILIO_AUTH"]
    twilio_number = st.secrets["TWILIO_PHONE"]
    client = Client(account_sid, auth_token)

    for number in contacts:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=number
        )

# Main flow
if "step" not in st.session_state:
    st.session_state.step = 0

if st.button("🆘 Activate Emergency Agent"):
    speak_browser("What is the emergency?")
    st.session_state.step = 1

if st.session_state.step == 1:
    speech_text = st.text_input("Speak or type the emergency:")
    if speech_text:
        category, number = classify_emergency(speech_text)
        st.info("📍 Fetching your precise location...")
        lat, lon = get_precise_location()
        maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        message = f"🚨 EMERGENCY ALERT:\nType: {category.upper()}\nLocation: {maps_url}\nPlease send help immediately."
        st.success(f"Emergency classified as **{category.upper()}**. Sending alerts...")

        emergency_contacts = ["+919987301895"]  # Replace with verified numbers
        send_sms(message, emergency_contacts)
        st.session_state.step = 2

if st.session_state.step == 2:
    st.balloons()
    st.success("✅ Alerts sent. Help is on the way!")
