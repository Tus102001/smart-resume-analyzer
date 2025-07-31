import streamlit as st
import nltk
import spacy
import pandas as pd
import base64
import time
import datetime
import random
import io
import os
import re
from pyresparser import ResumeParser
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document

# Download nltk packages
nltk.download('punkt')
nltk.download('stopwords')

# Load spacy model or download if missing
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')


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
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_similarity(resume_text, job_description):
    if resume_text and job_description:
        cv = CountVectorizer().fit_transform([resume_text, job_description])
        similarity = cosine_similarity(cv[0:1], cv[1:2])
        return round(float(similarity[0][0]) * 100, 2)
    return 0.0


def extract_skills_from_text(text):
    skill_keywords = [
        'python', 'java', 'c++', 'sql', 'excel', 'html', 'css', 'javascript',
        'machine learning', 'deep learning', 'tensorflow', 'react', 'django',
        'flask', 'pytorch', 'angular', 'node', 'android', 'kotlin', 'swift',
        'aws', 'azure', 'git', 'docker', 'linux'
    ]
    return list({skill for skill in skill_keywords if skill.lower() in text.lower()})


def fallback_resume_data(text):
    name = next(iter(re.findall(r'(?i)\bName[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', text)), 'N/A')
    email = next(iter(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)), 'N/A')
    phone = next(iter(re.findall(r'\+?\d[\d -]{8,}\d', text)), 'N/A')
    return {
        "name": name,
        "email": email,
        "mobile_number": phone,
        "skills": extract_skills_from_text(text),
        "no_of_pages": text.count('\n\n')  # crude page estimate
    }


def process_resume(save_path, resume_text):
    try:
        resume_data = ResumeParser(save_path).get_extracted_data()
        st.write("📋 ResumeParser result:", resume_data)
    except Exception as e:
        st.warning("ResumeParser failed: Using fallback method.")
        resume_data = {}

    if not resume_data or not resume_data.get('skills'):
        st.warning("Using fallback parser (manual extraction).")
        resume_data = fallback_resume_data(resume_text)

    if resume_data:
        st.header("Resume Analysis")
        st.success("Hello " + resume_data.get('name', 'User'))
        st.subheader("Your Basic Info")
        st.text('Name: ' + resume_data.get('name', 'N/A'))
        st.text('Email: ' + resume_data.get('email', 'N/A'))
        st.text('Contact: ' + resume_data.get('mobile_number', 'N/A'))
        st.text('Pages: ' + str(resume_data.get('no_of_pages', 'N/A')))
    else:
        st.warning("Could not extract any info from the resume.")

    return resume_data


st.set_page_config(page_title="Smart Resume Analyzer", page_icon='./Logo/images.png')


def run():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # Display logo
    if os.path.exists('./Logo/images.png'):
        img = Image.open('./Logo/images.png')
        img = img.resize((250, 250))
        st.image(img)
    else:
        st.warning("Logo image not found at './Logo/images.png'")

    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "docx", "doc"])

        if pdf_file is not None:
            file_extension = os.path.splitext(pdf_file.name)[1].lower()
            save_path = './Uploaded_Resumes/' + pdf_file.name

            # Save the uploaded file
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            # Read resume text
            if file_extension == ".pdf":
                show_pdf(save_path)
                resume_text = pdf_reader(save_path)
            elif file_extension in [".docx", ".doc"]:
                doc = Document(save_path)
                resume_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                st.error("Unsupported file format.")
                return

            # Process resume and extract info
            resume_data = process_resume(save_path, resume_text)

            # Skills recommendations based on extracted skills
            if resume_data:
                st.subheader("Skills Recommendation")
                skills = resume_data.get('skills', [])

                keywords = st_tags(label='### Skills that you have', value=skills, key='2')

                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
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
                        break
                    elif i.lower() in web_keyword:
                        reco_field = 'Web Development'
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'PHP', 'Laravel', 'Magento',
                                              'Wordpress', 'Javascript', 'Angular JS', 'C#', 'Flask', 'SDK']
                        break
                    elif i.lower() in android_keyword:
                        reco_field = 'Android Development'
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        break
                    elif i.lower() in ios_keyword:
                        reco_field = 'IOS Development'
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        break

                if recommended_skills:
                    st_tags(label='### Recommended skills for you', value=recommended_skills, key='3')

            # Job Description input and ATS matching score
            st.subheader("Paste the Job Description")
            job_description = st.text_area("Enter or paste the Job Description here...", height=200)

            if st.button("Check ATS Score", key="match_button"):
                match_score = get_similarity(resume_text, job_description)
                st.success(f"Resume–Job Description Match Score: **{match_score}%**")

    else:  # Admin section
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
                    # Process each resume file to extract info
                    file_path = os.path.join(folder_path, file)
                    resume_text = pdf_reader(file_path)
                    resume_data = process_resume(file_path, resume_text)

                    data.append({
                        "ID": idx,
                        "Name": resume_data.get('name', 'N/A'),
                        "Email": resume_data.get('email', 'N/A'),
                        "Timestamp": (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
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


if __name__ == '__main__':
    run()
