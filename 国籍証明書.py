import streamlit as st
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="National Verification Generator", page_icon="🛂", layout="centered")

# 2. SECURITY LOCK & HIDE MENU
if st.query_params.get("access") != "namaste":
    st.error("🔒 Access Denied / アクセス拒否")
    st.warning("Please use the official link provided to access this tool. / このツールにアクセスするには、提供された公式リンクを使用してください。")
    st.stop()
    
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. APP HEADER
st.title("🛂 National Verification Generator")
st.markdown("Fill out the details below to generate the Nationality Paper. / 国籍証明書を作成するための詳細を入力してください。")

# Define the input fields 
INPUT_FIELDS = [
    "Registration No. (登録番号)", 
    "Registration Date (登録日)", 
    "Full Name (氏名)", 
    "Date of Birth (生年月日)", 
    "Permanent Address (永住住所)", 
    "Translator Name (翻訳者の氏名)", 
    "Address in Japan (日本での住所)"
]

def load_font():
    font_path = "msgothic.ttc" 
    try:
        pdfmetrics.registerFont(TTFont('JapaneseFont', font_path, subfontIndex=0))
        return 'JapaneseFont'
    except Exception as e:
        st.error(f"⚠️ Font Error: Could not load '{font_path}'. Please ensure the font file is uploaded.")
        return 'Helvetica'

def generate_pdf(data):
    buffer = io.BytesIO()
    font_name = load_font()

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=70, bottomMargin=50)
    elements = []
    
    # --- STYLES ---
    title_style = ParagraphStyle('Title', fontName=font_name, fontSize=18, alignment=1, spaceAfter=30)
    right_style = ParagraphStyle('Right', fontName=font_name, fontSize=11, alignment=2)
    left_style = ParagraphStyle('Left', fontName=font_name, fontSize=11, alignment=0)
    
    # Body style with line spacing (leading) for readability
    body_style = ParagraphStyle('Body', fontName=font_name, fontSize=12, leading=22, alignment=0)

    # --- HEADER: Reg No & Embassy Info ---
    header_data = [
        [Paragraph(f"{data['Registration No. (登録番号)']}", left_style), 
         Paragraph(f"ネパール大使館<br/>{data['Registration Date (登録日)']}", right_style)]
    ]
    t_header = Table(header_data, colWidths=[250, 240])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_header)
    elements.append(Spacer(1, 40))

    # --- TITLE & SALUTATION ---
    elements.append(Paragraph("国籍証明書（Nationality paper）", title_style))
    elements.append(Paragraph("ご担当者様,", left_style))
    elements.append(Spacer(1, 20))

    # --- BODY PARAGRAPH ---
    # We use <b> tags to make the client's specific data pop out in the letter
    body_text = f"""
    これは、<b>{data['Full Name (氏名)']}</b> によって大使館に提出された文書に従って、
    すべての関係者に通知するものです。<br/><br/>
    <b>{data['Full Name (氏名)']}</b> は、<b>{data['Date of Birth (生年月日)']}</b> 生まれ、
    ネパールの <b>{data['Permanent Address (永住住所)']}</b> の永住者であり、正真正銘のネパール国民です。<br/><br/>
    助けを必要としている彼/彼女に差し伸べられたあらゆる協力は、非常に高く評価されます。
    """
    elements.append(Paragraph(body_text, body_style))
    elements.append(Spacer(1, 60))

    # --- FOOTER: TRANSLATOR INFO ---
    footer_data = [
        [Paragraph("翻訳者:", left_style), Paragraph(f"<b>{data['Translator Name (翻訳者の氏名)']}</b>", left_style)],
        [Paragraph("住所:", left_style), Paragraph(f"{data['Address in Japan (日本での住所)']}", left_style)]
    ]
    t_footer = Table(footer_data, colWidths=[60, 430])
    t_footer.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8)
    ]))
    
    elements.append(t_footer)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

# --- DYNAMIC WEB UI ---
user_data = {}

for field in INPUT_FIELDS:
    if field == "Translator Name (翻訳者の氏名)":
        full_name_entered = user_data.get("Full Name (氏名)", "").strip()
        display_name = full_name_entered if full_name_entered else "Same as Full Name (氏名と同じ)"
        translator_choice = st.selectbox(field, [display_name, "Other (手動入力)"])
        
        if translator_choice == "Other (手動入力)":
            user_data[field] = st.text_input("Enter the Translator's Full Name / 翻訳者の氏名を入力してください")
        else:
            user_data[field] = full_name_entered
    else:
        user_data[field] = st.text_input(field)

st.write("---")

if st.button("Generate PDF / PDFを作成", type="primary"):
    client_name = user_data["Full Name (氏名)"]
    if not client_name:
        client_name = "Client"

    file_name = f"Nationality_Paper_{client_name}.pdf"
    
    with st.spinner("Generating document... / ドキュメントを作成中..."):
        pdf_buffer = generate_pdf(user_data)
        
        st.success("Success! Click the button below to download the certificate. / 成功しました！")
        
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )