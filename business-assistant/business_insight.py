import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
import pickle
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from langsmith import Client
from langsmith.evaluation import evaluate

load_dotenv()

# Initialize LangSmith client
langsmith_client = Client()

df = pd.read_csv('sales_data.csv')

#print(df.head())
#print(df.info())

# Rename all columns to lowercase
df.columns = df.columns.str.lower()

# Verify the changes
#print(df.columns)
#print(df.head())

pdf_folder = 'pdf/'

documents = []

for file in os.listdir(pdf_folder):
    if file.endswith('.pdf'):
        loader = PyPDFLoader(os.path.join(pdf_folder, file))
        documents.extend(loader.load())

# Check if the pdf docus loaded successfully
#print(f"Number of documents loaded: {len(documents)}")
#print(f"First document preview: {documents[0] if documents else 'No documents loaded'}")

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# This actually splits the documents:
texts = text_splitter.split_documents(documents)

# Check if text splitting worked successfully
#print(f"Number of text chunks: {len(texts)}")
#print(f"First chunk preview: {texts[0] if texts else 'No chunks created'}")

# Save chunks to pickle file for reuse
with open('processed_text.pickle', 'wb') as f:
    pickle.dump(texts, f)

# Convert date column to datetime format
df['date'] = pd.to_datetime(df['date'])

def generate_advanced_data_summary(df):
    """
    Generate comprehensive analysis of business data
    """
    summary = {}

    # Calculate statistical measures
    summary['total_sales'] = df['sales'].sum()
    summary['average_sales'] = df['sales'].mean()
    summary['median_sales'] = df['sales'].median()
    summary['std_sales'] = df['sales'].std() 

    # Time-based analysis
    summary['sales_by_month'] = df.groupby(df['date'].dt.month)['sales'].sum()

    # Product analysis
    summary['sales_by_product'] = df.groupby('product')['sales'].sum()
    summary['satisfaction_by_product'] = df.groupby('product')['customer_satisfaction'].mean()

    # Region analysis
    summary['sales_by_region'] = df.groupby('region')['sales'].sum()

    # Customer segmentation
    summary['sales_by_age'] = df.groupby('customer_age')['sales'].mean()
    summary['sales_by_gender'] = df.groupby('customer_gender')['sales'].sum()

    # Format as text
    summary_text = f"""
    ADVANCED SALES SUMMARY

    Total Metrics:
    - Total Sales: ${summary['total_sales']:,.2f}
    - Average Sales: ${summary['average_sales']:,.2f}
    - Median Sales: ${summary['median_sales']:,.2f}
    - Standard Deviation: ${summary['std_sales']:,.2f}

    Time-Based Analysis:
    {summary['sales_by_month'].to_string()}

    Product Analysis:
    {summary['sales_by_product'].to_string()}

    Region Performance:
    {summary['sales_by_region'].to_string()}

    Customer Insights:
    Sales by Age: {summary['sales_by_age'].to_string()}
    Sales by Gender: {summary['sales_by_gender'].to_string()}
    """
    return summary_text

advanced_summary = generate_advanced_data_summary(df)
#print(advanced_summary)

#PROMPT ENGINEERING AND LLM INTEGRATION
# Initialize ChatOpenAI model

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
   temperature=0.7
)

# Define scenario template
scenario_template = """
You are an expert AI sales analyst. Use the following advanced sales data summary 
to provide in-depth insights and actionable recommendations.
Be specific and refer to the data points provided.

Advanced Summary:
{advanced_summary}

Question: {question}

Provide detailed analysis and recommendations:
"""

# Create prompt template
prompt = PromptTemplate(
    template=scenario_template,
    input_variables=["advanced_summary", "question"]
)

# Create LLM chain using LCEL
llm_chain = prompt | llm

def generate_insight(question):
    """Generate insights based on question"""
    response = llm_chain.invoke({
        "advanced_summary": advanced_summary,
        "question": question
    })
    return response.content


#SEQUENTIAL CHAIN FOR RECOMMENDATIONS

# Stage 1: Analysis prompt
analysis_template = """
Analyze the following advanced sales data summary and provide a concise analysis 
of the key points:

{advanced_summary}

Analysis:
"""
analysis_prompt = PromptTemplate(
    template=analysis_template,
    input_variables=["advanced_summary"]
)

analysis_chain = analysis_prompt | llm

# Stage 2: Recommendation prompt
recommendation_template = """
Based on the following analysis of sales data, provide specific recommendations:

Analysis:

{analysis}

Recommendations:
"""

recommendation_prompt = PromptTemplate(
    template=recommendation_template,
    input_variables=["analysis"]

)
recommendation_chain = recommendation_prompt | llm

#RAG SYSTEM IMPLEMENTATION

embeddings = OpenAIEmbeddings()
# Create FAISS vector store
vectordb = FAISS.from_documents(
    documents=texts,
    embedding=embeddings
)
# Create retriever (top 3 similar chunks)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# Create custom retrieval QA function
def ask_pdf_question(question):
    """Ask a question about the PDF documents"""
    # Retrieve relevant documents
    docs = retriever.invoke(question)
    
    # Combine document content
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Create prompt
    qa_prompt = PromptTemplate.from_template(
        """Answer the question based on the following context:
        
        {context}
        
        Question: {question}
        
        Answer:"""
    )
    
    # Create chain and invoke
    chain = qa_prompt | llm
    response = chain.invoke({"context": context, "question": question})
    return response.content


# INTEGRATE CONVERSATION MEMORY

# Initialize conversational buffer memory
memory = ChatMessageHistory()

# TEST RAG SYSTEM

def generate_rag_insight(question):
    """
    Generate insights using:
    1. RAG (PDF retrieval)
    2. Advanced summary from CSV
    3. Conversation memory
    """
    from langsmith import traceable
    
    @traceable(name="rag_insight_generation")
    def _generate_with_tracing(question):
        # Retrieve from vector DB
        retrieved_docs = retriever.invoke(question)
        pdf_answer = ask_pdf_question(question)   

        # Combine contexts
        retrieved_content = "\n".join([doc.page_content for doc in retrieved_docs])
        
        combined_context = f"""
        Advanced Summary:
        {advanced_summary}

        PDF Analysis:
        {pdf_answer}

        Question: {question}
        """

        # Generate final insight
        response = llm_chain.invoke({
            "advanced_summary": combined_context,
            "question": question
        })   

        # Update memory
        memory.add_user_message(question)
        memory.add_ai_message(response.content)

        return response.content
    
    return _generate_with_tracing(question)

# Test with various questions
questions = [
    "What are our top-selling products?",
    "How can we improve customer satisfaction based on sales trends?",
    "What regions need more attention?"
]

# Main execution block
if __name__ == "__main__":
    # Test sequential chains
    print("\n=== Running Sequential Analysis ===")
    analysis = analysis_chain.invoke({"advanced_summary": advanced_summary})
    recommendations = recommendation_chain.invoke({"analysis": analysis.content})
    print("Analysis:", analysis.content)
    print("\nRecommendations:", recommendations.content)
    
    # Test RAG system
    print("\n=== Testing RAG System ===")
    for question in questions:
        print(f"\nQuestion: {question}")
        answer = generate_rag_insight(question)
        print(f"Answer: {answer}")

# PART 2: DATA VISUALIZATION FUNCTIONS

def create_sales_trend_plot(df):
    """Create sales trends over time visualization"""
    df_plot = df.copy()
    df_plot['date'] = pd.to_datetime(df_plot['date']).dt.date
    df_plot = df_plot.sort_values('date')
    fig = px.line(df_plot, x='date', y='sales', 
                  title='Sales Trends Over Time',
                  labels={'date': 'Date', 'sales': 'Sales ($)'},
                  color_discrete_sequence=['gray'])
    fig.update_layout(hovermode='x unified')
    return fig

def create_product_performance_plot(df):
    """Create product performance comparison"""
    product_sales = df.groupby('product')['sales'].sum().sort_values(ascending=True)
    fig = px.bar(x=product_sales.values, y=product_sales.index, 
                 orientation='h',
                 title='Product Performance Comparison',
                 labels={'x': 'Total Sales ($)', 'y': 'Product'},
                 color_discrete_sequence=['gray'])
    return fig

def create_regional_analysis_plot(df):
    """Create regional analysis visualization"""
    region_sales = df.groupby('region')['sales'].sum()
    fig = px.pie(values=region_sales.values, names=region_sales.index,
                 title='Sales Distribution by Region',
                 color_discrete_sequence=px.colors.sequential.gray)
    return fig

def create_customer_demographics_plot(df):
    """Create customer demographics visualization"""
    fig = px.scatter(df, x='customer_age', y='sales', 
                     color='customer_gender',
                     title='Customer Demographics and Sales',
                     labels={'customer_age': 'Customer Age', 
                             'sales': 'Sales ($)',
                             'customer_gender': 'Gender'},
                     color_discrete_sequence=['#d3d3d3', '#a9a9a9'])
    return fig

def create_satisfaction_by_product_plot(df):
    """Create customer satisfaction by product"""
    satisfaction = df.groupby('product')['customer_satisfaction'].mean().sort_values()
    fig = px.bar(x=satisfaction.values, y=satisfaction.index,
                 orientation='h',
                 title='Average Customer Satisfaction by Product',
                 labels={'x': 'Average Satisfaction', 'y': 'Product'},
                 color=satisfaction.values,
                 color_continuous_scale='gray')
    return fig

def create_monthly_sales_plot(df):
    """Create monthly sales analysis"""
    df_plot = df.copy()
    df_plot['date'] = pd.to_datetime(df_plot['date'])
    df_plot['month'] = df_plot['date'].dt.to_period('M').astype(str)
    monthly_sales = df_plot.groupby('month')['sales'].sum()
    fig = px.bar(x=monthly_sales.index, y=monthly_sales.values,
                 title='Monthly Sales Performance',
                 labels={'x': 'Month', 'y': 'Total Sales ($)'},
                 color_discrete_sequence=['gray'])
    return fig

# MODEL EVALUATION FUNCTION
def evaluate_model_responses(test_questions, test_answers=None):
    """
    Evaluate model performance using LangSmith criteria evaluation
    """
    eval_results = []
    
    # Define evaluation criteria
    criteria = {
        "relevance": "Is the answer relevant to the question?",
        "helpfulness": "Is the answer helpful and actionable?",
        "accuracy": "Does the answer appear accurate based on the context?",
        "clarity": "Is the answer clear and well-structured?"
    }
    
    for i, question in enumerate(test_questions):
        # Generate answer with tracing
        generated_answer = generate_rag_insight(question)
        
        # Evaluate using LangSmith criteria
        evaluations = {}
        for criterion_name, criterion_desc in criteria.items():
            eval_prompt = f"""
            Evaluate the following answer based on this criterion: {criterion_desc}
            
            Question: {question}
            Answer: {generated_answer}
            {f"Expected Context: {test_answers[i]}" if test_answers and i < len(test_answers) and test_answers[i] else ""}
            
            Rate from 1-10 and explain briefly.
            """
            
            evaluation = llm.invoke(eval_prompt)
            evaluations[criterion_name] = evaluation.content
        
        # Combine all evaluations
        combined_eval = "\n\n".join([f"**{k.title()}**: {v}" for k, v in evaluations.items()])
        
        eval_results.append({
            'question': question,
            'answer': generated_answer,
            'evaluation': combined_eval,
            'criteria_scores': evaluations
        })
    
    return eval_results

def get_langsmith_traces(limit=10):
    """
    Retrieve recent LangSmith traces for monitoring
    """
    try:
        runs = langsmith_client.list_runs(
            project_name=os.getenv("LANGCHAIN_PROJECT", "business-assistant"),
            limit=limit
        )
        return list(runs)
    except Exception as e:
        return []

