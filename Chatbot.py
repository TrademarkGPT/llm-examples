import openai
import streamlit as st
from streamlit_chat import message
import PyPDF2

# Function to process PDF files
def process_pdf(file):
    pdf_file_obj = open(file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    num_pages = pdf_reader.numPages
    text = ""
    for page in range(num_pages):
        page_obj = pdf_reader.getPage(page)
        text += page_obj.extractText()
    pdf_file_obj.close()
    return text

# PDF Processing Module
def upload_pdf(label):
    pdf_file = st.sidebar.file_uploader(label, type=['pdf'])
    if pdf_file is not None:
        pdf_text = process_pdf(pdf_file)
        return pdf_text
    return None

# Data Entry and Presets Module
def get_user_input():
    user_input = {
        'persona': st.sidebar.selectbox('Which persona(s) are conducting the interviews?', ['CEO', 'CTO', 'Head of Sales', 'HR', 'Associate', 'Custom Role']),
        'difficulty': st.sidebar.selectbox('Overall Interview Difficulty', ['Easy', 'Medium', 'Hard', 'Impossible']),
        'disagreeableness': st.sidebar.selectbox('Disagreeableness', ['Low', 'Medium', 'High', 'Extremely High']),
        'qty_of_questions': st.sidebar.number_input('Qty of questions per interview', min_value=1, value=10, step=1),
        'interview_scope': st.sidebar.text_input('Specific areas of questioning')
    }
    return user_input

# Interview Simulation Module
def generate_prompt(user_input, pdf_texts):
    prompt = f"""
    Context: You are an AI designed to simulate a customized interviewer from a specific company and job description.  
    The company information of the firm interviewing is {pdf_texts['company_info']} and the Job description is {pdf_texts['job_description']}. 
    The user’s resume consists of {pdf_texts['resume']} and their personal story is {pdf_texts['personal_story']}. 
    Using the persona(s) of {user_input['persona']} conduct an interview with {user_input['qty_of_questions']} qty of questions from the interviewer with an overall interview difficulty of {user_input['difficulty']} and a disagreeableness level (disagreeing with the user/. Challenging them) {user_input['disagreeableness']}. 
    The interviewer should focus some of the questions / follow up questions on {user_input['interview_scope']}.
    """
    return prompt


def main():
    st.title("💬 Streamlit GPT")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    with st.form("chat_input", clear_on_submit=True):
        a, b = st.columns([4, 1])
        user_input = a.text_input(
            label="Your message:",
            placeholder="What would you like to say?",
            label_visibility="collapsed",
        )
        b.form_submit_button("Send", use_container_width=True)

    for msg in st.session_state.messages:
        message(msg["content"], is_user=msg["role"] == "user")

    openai_api_key = st.sidebar.text_input('OpenAI API Key',key='chatbot_api_key')

    if user_input and not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    
    if user_input and openai_api_key:
        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": user_input})
        message(user_input, is_user=True)

        pdf_texts = {
            'job_description': upload_pdf('Job Description (PDF)'),
            'company_info': upload_pdf('Company Information (PDF)'),
            'resume': upload_pdf('CV/Resume (PDF)'),
            'personal_story': upload_pdf('Personal Story / Background (PDF)')
        }

        user_input = get_user_input()

        prompt = generate_prompt(user_input, pdf_texts)

        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages, prompt=prompt)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        message(msg.content)

if __name__ == "__main__":
    main()
