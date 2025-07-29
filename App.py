import streamlit as st
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import spacy
nltk.download('stopwords')
import spacy

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
        # fit_transform is a method in scikit-learn that does it learns all the words and turn text int numbers:
        # Makes a list of unique words.
        # Counts how many times each word appears in each text.
        print("cv",cv)
        similarity = cosine_similarity(cv[0:1], cv[1:2])
        # formula similarity= A⋅B / ∥A∥∥B∥ 
        # A.B is dot product
        # Multiply each pair of numbers:
        # Add them all up:
        # || A|| ||B|| =  lenght of a vector
        # Add them up:
        # Take the square root: 
        # Similarity [[0.33337762]]
        print("similarity",similarity)
        return round(float(similarity[0][0]) * 100, 2)
        return None

st.set_page_config(page_title="Smart Resume Analyzer", page_icon='./Logo/images.png')

def run():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User") #streamlit
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
      # Debugging file existence here:
    
    #st.write("Current working directory:", os.getcwd())
    #st.write("Files in current dir:", os.listdir('.'))
    #st.write("Files in 'Logo' folder:", os.listdir('./Logo') if os.path.exists('./Logo') else "Logo folder NOT found")

        
    img = Image.open('./Logo/images.png')
    img = img.resize((250, 250))
    st.image(img)

    if choice == 'Normal User':
       # pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf", "docx", "doc"])

        if pdf_file is not None:
           
            file_extension = os.path.splitext(pdf_file.name)[1].lower()
            
            
            save_path = './Uploaded_Resumes/' + pdf_file.name
# Save the uploaded file to disk exactly as it was uploaded

            with open(save_path, "wb") as f:
               f.write(pdf_file.getbuffer())

            # Read resume text depending on file type
            if file_extension == ".pdf":
                show_pdf(save_path)
                resume_text = pdf_reader(save_path)
            elif file_extension in [".docx", ".doc"]:
                doc = Document(save_path)
                resume_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                st.error("Unsupported file format.")
                return

            # Try extracting structured data
            try:
                resume_data = ResumeParser(save_path).get_extracted_data()
            except Exception as e:
                st.warning("ResumeParser could not extract structured info.")
                resume_data = {}
            
            if resume_data:
                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                
                
            st.subheader("**Skills Recommendation **")
               ## Skill shows
            keywords = st_tags(label='### Skills that you have',
                                 
                                   value=resume_data['skills'], key='2')

                ##  recommendation
            ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit']
            web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
            android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
            ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
            uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']

            recommended_skills = []
                ## Courses recommendation
            for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                     
                                                       value=recommended_skills, key='3')
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',

                                                       value=recommended_skills, key='4')
                        
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',

                                                       value=recommended_skills, key='5')
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                      
                                                       value=recommended_skills, key='6')
                        break

            
             
            # JD Input
            st.subheader("Paste the Job Description")
            job_description = st.text_area("Enter or paste the Job Description here...", height=200)

            # Define and handle match score ONLY if JD is provided
            #  if job_description:
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

                # Declare everything inside this block
                    folder_path = "./Uploaded_Resumes/"
                    resume_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

                    data = []
                for idx, file in enumerate(resume_files, start=1):
                    name = resume_data['name']
                    email = resume_data['email']
                    timestamp = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                    data.append({
                        "ID": idx,
                        "Name": name,
                        "Email": email,
                        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    })

                df = pd.DataFrame(data)
                st.markdown("### User's  Resume Data")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=" Download Report",
                    data=csv,
                    file_name="resume_analysis_report.csv",
                    mime="text/csv"
                )
        else:
                st.error("Wrong ID & Password Provided")

run()
