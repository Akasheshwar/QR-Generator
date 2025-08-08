import streamlit as st
import qrcode
import io
from urllib.parse import urlparse, quote
import google.generativeai as genai
from io import BytesIO

# ---- Gemini API Setup ----
genai.configure(api_key="AIzaSyAgXwJkzbpEUr-KEoM-iLH5W5ZAWpLc878")
model = genai.GenerativeModel("gemini-2.5-pro")

# ---- Set up page config ----
st.set_page_config(page_title="Qobra", page_icon="🔮")

# ---- Custom CSS for Centering and Button Size ----
st.markdown("""
    <style>
        .centered-title {
            text-align: center;
            font-size: 3rem;
        }
        .centered-subtitle {
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 3rem;
        }
        div.stButton > button {
            width: 100%;
            padding: 1.2rem;
            font-size: 1.2rem;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Navigation via session state ----
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to_page(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()

# ========== HOME PAGE ==========
if st.session_state.page == "home":
    st.markdown("<h1 class='centered-title'>🔮 Qobra</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='centered-subtitle'>Our Services</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])

    with col2:
        if st.button("📦 QR Generator"):
            go_to_page("qr")

    with col3:
        if st.button("🤖 AI Assistant"):
            go_to_page("ai")

# ========== QR GENERATOR ==========
elif st.session_state.page == "qr":
    st.title("🔮 Qobra QR Code Generator")

    if st.button("⬅️ Back to Home", key="back_from_qr"):
        go_to_page("home")

    option = st.selectbox("Select what you'd like to encode in the QR code:", [
        "URL", "Plain Text", "Email Address"
    ])

    col1, col2 = st.columns(2)
    with col1:
        fill = st.color_picker("QR Code Color", "#000000")
    with col2:
        bg = st.color_picker("Background Color", "#FFFFFF")

    box_size = st.slider("QR Code Size", min_value=5, max_value=20, value=10)

    content = None
    valid = False

    # Wrap inputs and generate button inside a form
    with st.form("qr_form"):
        if option == "URL":
            url = st.text_input("Enter the URL:")

            def is_valid_url(url):
                parsed = urlparse(url)
                return all([parsed.scheme, parsed.netloc])

            if url:
                if not urlparse(url).scheme:
                    url = "https://" + url
                if is_valid_url(url):
                    content = url
                    valid = True
                else:
                    st.error("Please enter a valid URL (e.g., https://example.com)")

        elif option == "Plain Text":
            content = st.text_area("Enter the plain text to encode:")
            valid = bool(content)

        elif option == "Email Address":
            email = st.text_input("Enter the email address:")
            subject = st.text_input("Subject (optional):")
            body = st.text_area("Body (optional):")

            if email:
                mailto = f"mailto:{email}"
                query = []
                if subject:
                    query.append(f"subject={quote(subject)}")
                if body:
                    query.append(f"body={quote(body)}")
                if query:
                    mailto += "?" + "&".join(query)
                content = mailto
                valid = True
            elif email == "":
                valid = False

        send = st.form_submit_button("🚀 Generate QR")

    if send:
        if content and valid:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)

            img = qr.make_image(fill_color=fill, back_color=bg)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.image(byte_im, caption="Scan this QR code", use_container_width=True)

            st.download_button(
                label="⬇️ Download QR Code",
                data=byte_im,
                file_name="qr_code.png",
                mime="image/png",
            )
        else:
            st.warning("Please fill in all required fields to generate the QR code.")

# ========== AI ASSISTANT ==========
elif st.session_state.page == "ai":
    st.title("🔮 Qobra AI Assistant")

    if st.button("⬅️ Back to Home", key="back_from_ai"):
        go_to_page("home")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["summary"])
            if message.get("full"):
                with st.expander("🔽 View full response"):
                    st.markdown(message["full"])

    user_input = st.chat_input("Ask me anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "summary": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("🍳 Cooking up your response..."):
                try:
                    response_full = model.generate_content(user_input)

                    if not response_full.parts:
                        raise ValueError("No response generated by the model.")

                    full_reply = response_full.text.strip()

                    response_summary = model.generate_content(
                        f"Summarize this in 2 sentences:\n\n{full_reply}"
                    )

                    if not response_summary.parts:
                        raise ValueError("Failed to summarize the response.")

                    short_summary = response_summary.text.strip()

                except Exception as e:
                    short_summary = f"⚠️ Error: {str(e)}"
                    full_reply = ""

            st.markdown(short_summary)

            if full_reply:
                with st.expander("🔽 View full response"):
                    st.markdown(full_reply)

        st.session_state.messages.append({
            "role": "assistant",
            "summary": short_summary,
            "full": full_reply
        })

# ---- About Us and Created By at bottom ----
st.markdown("""
    <div style="text-align:center; margin-top:4rem; font-size:0.8rem; color:gray;">
        <h3 style="margin-bottom:0.2rem;">About Us</h3>
        <p style="margin:0 0 0.8rem 0; max-width:400px; margin-left:auto; margin-right:auto;">
            Welcome to Qobra! Easy tools for QR codes and AI assistance to boost your productivity and creativity.
        </p>
        <h4 style="margin-bottom:0.2rem;">Created By</h4>
        <p style="margin:0; line-height:1.3;">
            A.V.Gowtham Siddharth<br>Akash.E<br>Adarsh Kumar<br>Prathviraj
        </p>
    </div>
""", unsafe_allow_html=True)
