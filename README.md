# Cold Email Generator App 📧

A powerful AI-driven Streamlit application that generates personalized cold emails for job opportunities. This app analyzes job postings and creates tailored emails based on your portfolio and skills.

## Features ✨

- **🔗 Job URL Processing**: Extract job information from any job posting URL
- **🤖 AI-Powered Analysis**: Uses LangChain and Groq LLM to analyze job requirements
- **📊 Portfolio Matching**: Automatically matches relevant portfolio items using ChromaDB
- **📧 Email Generation**: Creates personalized cold emails with professional tone
- **🎨 Modern UI**: Clean, responsive Streamlit interface with custom styling
- **⚡ Real-time Processing**: Instant feedback and loading indicators

## Technology Stack 🛠️

- **Frontend**: Streamlit
- **AI/ML**: LangChain, Groq LLM (Llama-3.1-8b-instant)
- **Database**: ChromaDB (Vector Database)
- **Web Scraping**: WebBaseLoader

## Installation 🚀

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- Groq API key

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd cold-email-generator-tool
```

2. **Create and activate virtual environment**
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the app directory:
```bash
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
GROQ_API_KEY=your_groq_api_key_here
```

5. **Prepare portfolio data**
Ensure `resources/portfolios.csv` exists with the following structure:
```csv
Tech stacks,Portfolio link
"React, AWS, Lambda",https://portfolio1.example.com
"Angular, S3, DynamoDB",https://portfolio2.example.com
```

### Starting the Application
```bash
# Navigate to project directory
cd /path/to/cold-email-generator-tool

# Activate virtual environment
source myenv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

### Using the App

1. **Enter Job URL**: Paste a job posting URL in the input field
2. **Extract Job Info**: Click "Extract Job Info" to analyze the posting
3. **Review Job Details**: Check the extracted role, description, and skills
4. **Generate Email**: Click "Generate Cold Email" to create personalized content
5. **Copy & Use**: Copy the generated email for your outreach

### Example Workflow

```
Input: https://careers.nike.com/principal-software-engineering/job/R-63381
↓
AI extracts: Role, Description, Required Skills
↓
ChromaDB matches: Relevant portfolio items
↓
Output: Personalized cold email from AtliQ Technologies
```

## Configuration ⚙️

### API Configuration
Update the API key in `app.py`:
```python
llm = ChatGroq(
    api_key="your_groq_api_key_here",
    model="llama-3.1-8b-instant",
    temperature=0.0,
    max_retries=2
)
```

### Portfolio Management
Add your portfolio items to `resources/portfolios.csv`:
- **Tech stacks**: Comma-separated list of technologies
- **Portfolio link**: URL to your portfolio/project

### Email Template Customization
Modify the email template in the `generate_email()` function to match your:
- Company name
- Role/title
- Company description
- Contact information

## File Structure 📁

```
app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── resources/
│   └── portfolios.csv    # Portfolio data
├── chroma/               # ChromaDB storage (auto-generated)
├── myenv/                # Virtual environment
├── static/               # Static assets (if any)
└── templates/            # HTML templates (if any)
```

## Dependencies 📦

```
streamlit>=1.46.1
langchain-groq>=0.3.6
langchain-community>=0.3.27
langchain-core>=0.3.68
pandas>=2.3.1
chromadb>=1.0.15
selenium>=4.34.2
```

### Performance Tips

- **First Run**: Initial setup may take a few minutes to process portfolios
- **Caching**: ChromaDB and LLM are cached for better performance
- **URL Compatibility**: Works best with standard job board formats

---
