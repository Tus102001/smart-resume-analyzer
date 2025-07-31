import streamlit as st
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import spacy
nltk.download('stopwords')

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
from sklearn.feature_extraction.text import CountVectorizer
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
from sklearn.metrics.pairwise import cosine_similarity
import os
import datetime
import random
from docx import Document
import re

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        PDFbyte = f.read()
    st.download_button(label="Download Resume PDF", data=PDFbyte, file_name=os.path.basename(file_path))

def get_similarity(resume_text, job_description):
    if resume_text and job_description:
        cv = CountVectorizer().fit_transform([resume_text, job_description])
        similarity = cosine_similarity(cv[0:1], cv[1:2])
        return round(float(similarity[0][0]) * 100, 2)

def extract_name_spacy(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return "N/A"

def extract_skills_from_text(text):
    skill_keywords = [
        'python', 'java', 'c++', 'sql', 'excel', 'html', 'css', 'javascript',
        'machine learning', 'deep learning', 'tensorflow', 'react', 'django',
        'flask', 'pytorch', 'angular', 'node', 'android', 'kotlin', 'swift',
        'aws', 'azure', 'git', 'docker', 'linux'
    ]
    found = [skill for skill in skill_keywords if skill.lower() in text.lower()]
    return list(set(found))

def fallback_resume_data(text):
    name = extract_name_spacy(text)
    email_match = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.findall(r"\+?\d[\d -]{8,}\d", text)

    return {
        "name": name,
        "email": email_match[0] if email_match else "N/A",
        "mobile_number": phone_match[0] if phone_match else "N/A",
        "skills": extract_skills_from_text(text),
        "no_of_pages": text.count("\n\n")  # crude page estimator
    }

def process_resume(save_path, resume_text):
    try:
        resume_data = ResumeParser(save_path).get_extracted_data()
        # Do NOT show warning messages if parsing fails
        if not resume_data or not resume_data.get('skills'):
            resume_data = fallback_resume_data(resume_text)
    except Exception:
        resume_data = fallback_resume_data(resume_text)

    if resume_data:
        st.header("**Resume Analysis**")
        st.success("Hello " + resume_data.get('name', 'User'))
        st.subheader("**Your Basic info**")
        st.text('Name: ' + resume_data.get('name', 'N/A'))
        st.text('Email: ' + resume_data.get('email', 'N/A'))
        st.text('Contact: ' + resume_data.get('mobile_number', 'N/A'))
        st.text('Resume pages: ' + 1)
    else:
        st.warning("Could not extract any info from the resume.")

    return resume_data

st.set_page_config(page_title="Smart Resume Analyzer", page_icon='./Logo/images.png')

def run():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # Removed image preview as requested
    # img = Image.open('./Logo/images.png')
    # img = img.resize((250, 250))
    # st.image(img)

    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "docx", "doc"])

        if pdf_file is not None:
            file_extension = os.path.splitext(pdf_file.name)[1].lower()
            save_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            if file_extension == ".pdf":
                show_pdf(save_path)  # Only show download button, no preview
                resume_text = pdf_reader(save_path)
            elif file_extension in [".docx", ".doc"]:
                doc = Document(save_path)
                resume_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                st.error("Unsupported file format.")
                return

            resume_data = process_resume(save_path, resume_text)

            st.subheader("**Skills Recommendation**")
            skills = resume_data.get('skills', [])

            keywords = st_tags(label='### Skills that you have',
                   value=skills, key='2')

            ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
            web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                           'javascript', 'angular js', 'c#', 'flask']
            android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
            ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
            uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                            'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                            'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                            'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                            'user research', 'user experience']

            recommended_skills = []

            for i in skills:
                if i.lower() in ds_keyword:
                    reco_field = 'Data Science'
                    recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                          'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                          'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                          'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                          'Streamlit']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                  value=recommended_skills, key='3')
                    break
                elif i.lower() in web_keyword:
                    reco_field = 'Web Development'
                    recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                          'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                  value=recommended_skills, key='4')
                    break
                elif i.lower() in android_keyword:
                    reco_field = 'Android Development'
                    recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                          'Kivy', 'GIT', 'SDK', 'SQLite']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                  value=recommended_skills, key='5')
                    break
                elif i.lower() in ios_keyword:
                    reco_field = 'IOS Development'
                    recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                          'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                          'Auto-Layout']
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                  value=recommended_skills, key='6')
                    break

            st.subheader("Paste the Job Description")
            job_description = st.text_area("Enter or paste the Job Description here...", height=200)

            if st.button("Check ATS Score", key="match_button"):
                match_score = get_similarity(resume_text, job_description)
                st.success(f" Resume–Job Description Match Score: **{match_score}%**")

    else:
        st.subheader("Admin Login")
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button("Login"):
            if ad_user == 'nikhil' and ad_password == 'Nik@123':
                st.success("Welcome Group 6")

                folder_path = "./Uploaded_Resumes/"
                resume_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

                data = []
                for idx, file in enumerate(resume_files, start=1):
                    # Extract resume data for each file (you might want to parse each file here)
                    # For simplicity, this example uses placeholders
                    name = "Name Placeholder"
                    email = "Email Placeholder"
                    timestamp = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                    data.append({
                        "ID": idx,
                        "Name": name,
                        "Email": email,
                        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    })

                df = pd.DataFrame(data)
                st.markdown("### User's Resume Data")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Report",
                    data=csv,
                    file_name="resume_analysis_report.csv",
                    mime="text/csv"
                )
            else:
                st.error("Wrong ID & Password Provided")

run()
