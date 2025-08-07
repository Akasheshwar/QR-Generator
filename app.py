import streamlit as st
import qrcode
import io
from urllib.parse import urlparse, quote

st.set_page_config(page_title="Multi-Type QR Code Generator", page_icon="🔗")
st.title("🔳 Multi-Type QR Code Generator")

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

if option == "URL":
    url = st.text_input("Enter the URL:")
    
    def is_valid_url(url):
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])

    if url:
        if not urlparse(url).scheme:
            url = "https://" + url  # Auto-fix missing scheme
        if is_valid_url(url):
            content = url
        else:
            st.error("Please enter a valid URL (e.g., https://example.com)")


elif option == "Plain Text":
    content = st.text_area("Enter the plain text to encode:")


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


if content:
    # Generate QR code
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
    st.info("Enter the information above to generate a QR code.")