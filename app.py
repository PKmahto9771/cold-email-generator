import streamlit as st
import os
import pandas as pd
import chromadb
import uuid
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Cold Email Generator",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-bottom: 1rem;
    }
    .email-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Set user agent
user_agent = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
os.environ["USER_AGENT"] = user_agent

# Initialize session state
api_key = os.getenv("GROQ_API_KEY")
if 'generated_email' not in st.session_state:
    st.session_state.generated_email = None
if 'job_data' not in st.session_state:
    st.session_state.job_data = None

@st.cache_resource
def initialize_llm():
    """Initialize the language model"""
    
    if not api_key:
        st.error("GROQ_API_KEY environment variable is not set. Please set it in your environment or .env file.")
        st.stop()
    
    return ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0.0,
        max_retries=2
    )

@st.cache_resource
def initialize_chroma():
    """Initialize ChromaDB and load portfolios"""
    try:
        df = pd.read_csv("resources/portfolios.csv")
        chroma_client = chromadb.PersistentClient()
        collection = chroma_client.create_collection(name="portfolio", get_or_create=True)
        
        if not collection.count():
            for _, row in df.iterrows():
                collection.add(
                    documents=row["Tech stacks"],
                    metadatas={"links": row["Portfolio link"]},
                    ids=[str(uuid.uuid4())]
                )
        
        return collection
    except Exception as e:
        st.error(f"Error initializing ChromaDB: {str(e)}")
        return None

def extract_job_info(job_url):
    """Extract job information from URL"""
    try:
        loader = WebBaseLoader(web_path=job_url)
        docs = []
        for doc in loader.lazy_load():
            docs.append(doc)
        
        if not docs:
            return None
        
        prompt_extract = PromptTemplate.from_template(
            """You are an intelligent assistant.

Given the following job post:

{docs}

Extract the following as JSON:
- role
- description
- skills (as a list)

Only return valid JSON. No explanations, no markdown, no preamble."""
        )
        
        llm = initialize_llm()
        chain_extract = prompt_extract | llm
        result = chain_extract.invoke(input={'docs': docs[0].page_content})
        
        json_parser = JsonOutputParser()
        job_data = json_parser.parse(str(result.content))
        
        return job_data
    except Exception as e:
        st.error(f"Error extracting job information: {str(e)}")
        return None

def generate_email(job_data, portfolio_links):
    """Generate cold email based on job data and portfolio links"""
    try:
        prompt_email = PromptTemplate.from_template(
            """ 
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Mohan, a Business Development Executive at AtliQ Technologies. 
            AtliQ is a fast-growing AI and Software Solutions company focused on 
            enabling digital transformation for businesses across industries. We specialize 
            in building intelligent, scalable, and secure software solutions that streamline 
            operations, enhance productivity, and deliver measurable business outcomes.

            Your task is to write a professional, concise, and personalized cold email 
            to the client regarding the job mentioned above. Clearly convey how AtliQ is 
            well-positioned to fulfill their technical and business needs based on the job 
            requirements.

            Use confident but non-pushy language. Highlight relevant experience, technical 
            capabilities, and past work. Incorporate the most relevant items from the 
            following portfolio links to demonstrate AtliQ's credibility and alignment with 
            the client's goals: {link_list}

            Sign off as Mohan, BDE at AtliQ.

            ### EMAIL (NO PREAMBLE, NO MARKDOWN)
            """
        )
        
        llm = initialize_llm()
        chain_email = prompt_email | llm
        result = chain_email.invoke({"job_description": job_data, 'link_list': portfolio_links})
        
        return result.content
    except Exception as e:
        st.error(f"Error generating email: {str(e)}")
        return None

# Main app
def main():
    st.markdown('<h1 class="main-header">📧 Cold Email Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">Generate personalized cold emails for job opportunities using AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sub-header">🔧 Configuration</h2>', unsafe_allow_html=True)
        st.info("Enter a job posting URL to generate a personalized cold email.")
        
        # Portfolio preview
        st.markdown('<h3 class="sub-header">📁 Portfolio Skills</h3>', unsafe_allow_html=True)
        try:
            df = pd.read_csv("resources/portfolios.csv")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load portfolios: {str(e)}")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">🔗 Job URL Input</h2>', unsafe_allow_html=True)
        job_url = st.text_input(
            "Enter Job Posting URL:",
            placeholder="https://careers.nike.com/principal-software-engineering/job/R-63381",
            help="Paste the URL of the job posting you want to apply for"
        )
        
        if st.button("🔍 Extract Job Info", type="primary"):
            if job_url:
                with st.spinner("Extracting job information..."):
                    job_data = extract_job_info(job_url)
                    if job_data:
                        st.session_state.job_data = job_data
                        st.success("Job information extracted successfully!")
                    else:
                        st.error("Failed to extract job information. Please check the URL.")
            else:
                st.error("Please enter a job URL.")
    
    with col2:
        st.markdown('<h2 class="sub-header">📋 Job Information</h2>', unsafe_allow_html=True)
        if st.session_state.job_data:
            job_data = st.session_state.job_data
            
            st.write("**Role:**", job_data.get('role', 'N/A'))
            st.write("**Description:**", job_data.get('description', 'N/A')[:200] + "..." if len(job_data.get('description', '')) > 200 else job_data.get('description', 'N/A'))
            st.write("**Required Skills:**")
            skills = job_data.get('skills', [])
            if skills:
                for skill in skills:
                    st.write(f"• {skill}")
            else:
                st.write("No skills extracted")
        else:
            st.info("Job information will appear here after extraction.")
    
    # Email generation section
    st.markdown('<h2 class="sub-header">📧 Email Generation</h2>', unsafe_allow_html=True)
    
    if st.session_state.job_data:
        col3, col4 = st.columns([1, 2])
        
        with col3:
            if st.button("🚀 Generate Cold Email", type="primary"):
                with st.spinner("Generating personalized email..."):
                    # Get relevant portfolio links
                    collection = initialize_chroma()
                    if collection:
                        job_data = st.session_state.job_data
                        links = collection.query(
                            query_texts=job_data.get("skills", []),
                            n_results=2
                        ).get('metadatas', [])
                        
                        # Generate email
                        email_content = generate_email(job_data, links)
                        if email_content:
                            st.session_state.generated_email = email_content
                            st.success("Email generated successfully!")
                        else:
                            st.error("Failed to generate email.")
                    else:
                        st.error("Failed to initialize portfolio database.")
        
        with col4:
            if st.session_state.generated_email:
                st.markdown('<div class="email-container">', unsafe_allow_html=True)
                st.markdown("**Generated Email:**")
                st.text_area(
                    "",
                    value=st.session_state.generated_email,
                    height=300,
                    key="email_content"
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Copy to clipboard button
                if st.button("📋 Copy Email"):
                    st.success("Email copied to clipboard! (Note: Copy functionality requires additional setup)")
    else:
        st.info("Please extract job information first to generate an email.")

if __name__ == "__main__":
    main()
