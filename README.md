An end-to-end Generative AI application that generates style-aware LinkedIn posts using LLaMA 3.3 (70B) via Groq Cloud, LangChain, and Streamlit.

The system leverages structured metadata extraction and few-shot prompting to generate posts conditioned on topic, length, and language (English, Hinglish, Tanglish).


- Style-aware LinkedIn post generation
- Few-shot prompting using curated example posts
- LLM-based metadata extraction (line count, language, tags)
- Intelligent tag normalization pipeline
- Multi-language support (English, Hinglish, Tanglish)
- Interactive Streamlit UI
- Groq-hosted LLaMA 3.3 (70B) inference


Architecture
Raw Posts (JSON)
        ↓
LLM Metadata Extraction (LangChain + LLaMA)
        ↓
Tag Unification & Structuring
        ↓
Few-Shot Retrieval (Pandas filtering)
        ↓
Prompt Template Construction
        ↓
LLaMA 3.3 via Groq API
        ↓
Generated LinkedIn Post
        ↓
Streamlit UI


Tech Stack:
LLMs & GenAI: LLaMA 3.3 (70B), Groq Cloud API, LangChain, Prompt Engineering, Few-Shot Learning
Backend & Data: Python, Pandas, JSON processing, Structured Output Parsing
Frontend: Streamlit
