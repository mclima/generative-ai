import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with error handling
try:
    import business_insight as bi
    df = bi.df.copy()
    # Fix date column for Arrow serialization
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.floor('s')  # Remove nanoseconds
    generate_rag_insight = bi.generate_rag_insight
    memory = bi.memory
    advanced_summary = bi.advanced_summary
    create_sales_trend_plot = bi.create_sales_trend_plot
    create_product_performance_plot = bi.create_product_performance_plot
    create_regional_analysis_plot = bi.create_regional_analysis_plot
    create_customer_demographics_plot = bi.create_customer_demographics_plot
    create_satisfaction_by_product_plot = bi.create_satisfaction_by_product_plot
    create_monthly_sales_plot = bi.create_monthly_sales_plot
    evaluate_model_responses = bi.evaluate_model_responses
except Exception as e:
    st.error(f"Error loading business_insight module: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Catalyst AI - Business Intelligence",
    page_icon="⚫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-HDH90MLFDM"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-HDH90MLFDM');
    </script>
    """,
    unsafe_allow_html=True
)

# Load external CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Catalyst AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Business Intelligence Assistant</div>', unsafe_allow_html=True)
st.markdown('<p class="attribution">Data resources provided by Purdue University/Simplilearn</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:

    st.title("Navigation")
    page = st.radio("Select Page", [
        "Dashboard",
        "AI Assistant",
        "Visualizations",
        "Data Explorer",
        "Model Evaluation"
    ])
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Catalyst AI uses advanced AI technologies including:
    - Large Language Models (LLMs)
    - Retrieval-Augmented Generation (RAG)
    - Conversation Memory
    """)

# Dashboard Page
if page == "Dashboard":
    st.header("Business Overview Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sales", f"${df['sales'].sum():,.2f}", 
                 delta=f"{df['sales'].pct_change().mean()*100:.1f}%")
    
    with col2:
        st.metric("Average Sale", f"${df['sales'].mean():,.2f}",
                 delta=f"{(df['sales'].mean() - df['sales'].median()):.2f}")
    
    with col3:
        st.metric("Total Transactions", f"{len(df):,}",
                 delta="Active")
    
    with col4:
        st.metric("Avg Satisfaction", f"{df['customer_satisfaction'].mean():.2f}",
                 delta=f"{df['customer_satisfaction'].std():.2f}")
    
    st.markdown("---")
    
    # Quick Insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales Trend")
        st.plotly_chart(create_sales_trend_plot(df), width='stretch')
    
    with col2:
        st.subheader("Regional Distribution")
        st.plotly_chart(create_regional_analysis_plot(df), width='stretch')
    
    # Advanced Summary
    with st.expander("View Detailed Data Summary"):
        st.text(advanced_summary)

# AI Assistant Page
elif page == "AI Assistant":
    st.header("AI Business Intelligence Assistant")
    st.markdown("Ask questions about the business data and get AI-powered insights!")
    
    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat['question'])
        with st.chat_message("assistant"):
            st.write(chat['answer'])
    
    # User input
    user_question = st.chat_input("Ask a question about the business data...")
    
    if user_question:
        # Display user message
        with st.chat_message("user"):
            st.write(user_question)
        
        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data and generating insights..."):
                answer = generate_rag_insight(user_question)
                st.write(answer)
        
        # Save to chat history
        st.session_state.chat_history.append({
            'question': user_question,
            'answer': answer
        })
    
    # Suggested questions
    st.markdown("---")
    st.subheader("💡 Suggested Questions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    suggested_questions = [
        "What are our top-selling products?",
        "How can we improve customer satisfaction?",
        "Which regions need more attention?"
    ]
    
    with col1:
        if st.button(suggested_questions[0], key="sq1"):
            with st.chat_message("user"):
                st.write(suggested_questions[0])
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data and generating insights..."):
                    answer = generate_rag_insight(suggested_questions[0])
                    st.write(answer)
            st.session_state.chat_history.append({
                'question': suggested_questions[0],
                'answer': answer
            })
            st.rerun()
    
    with col2:
        if st.button(suggested_questions[1], key="sq2"):
            with st.chat_message("user"):
                st.write(suggested_questions[1])
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data and generating insights..."):
                    answer = generate_rag_insight(suggested_questions[1])
                    st.write(answer)
            st.session_state.chat_history.append({
                'question': suggested_questions[1],
                'answer': answer
            })
            st.rerun()
    
    with col3:
        if st.button(suggested_questions[2], key="sq3"):
            with st.chat_message("user"):
                st.write(suggested_questions[2])
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data and generating insights..."):
                    answer = generate_rag_insight(suggested_questions[2])
                    st.write(answer)
            st.session_state.chat_history.append({
                'question': suggested_questions[2],
                'answer': answer
            })
            st.rerun()
    
    with col4:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# Visualizations Page
elif page == "Visualizations":
    st.header("Data Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Sales Analysis", 
        "Product Performance", 
        "Customer Insights",
        "Time-Based Analysis"
    ])
    
    with tab1:
        st.subheader("Sales Trends Over Time")
        with st.spinner("Loading chart..."):
            st.plotly_chart(create_sales_trend_plot(df), width='stretch')
        
        st.subheader("Regional Sales Distribution")
        with st.spinner("Loading chart..."):
            st.plotly_chart(create_regional_analysis_plot(df), width='stretch')
    
    with tab2:
        st.subheader("Product Performance Comparison")
        with st.spinner("Loading chart..."):
            st.plotly_chart(create_product_performance_plot(df), width='stretch')
        
        st.subheader("Customer Satisfaction by Product")
        with st.spinner("Loading chart..."):
            st.plotly_chart(create_satisfaction_by_product_plot(df), width='stretch')
    
    with tab3:
        st.subheader("Customer Demographics and Sales")
        with st.spinner("Loading chart..."):
            st.plotly_chart(create_customer_demographics_plot(df), width='stretch')
        
        # Additional demographic insights
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Sales by Gender")
            with st.spinner("Loading chart..."):
                gender_sales = df.groupby('customer_gender')['sales'].sum()
                fig_gender = px.bar(x=gender_sales.index, y=gender_sales.values,
                                   labels={'x': 'Gender', 'y': 'Total Sales ($)'},
                                   color_discrete_sequence=['gray'])
                st.plotly_chart(fig_gender, width='stretch')
        
        with col2:
            st.markdown("#### Average Age by Region")
            with st.spinner("Loading chart..."):
                age_region = df.groupby('region')['customer_age'].mean()
                fig_age = px.bar(x=age_region.index, y=age_region.values,
                                labels={'x': 'Region', 'y': 'Average Age'},
                                color_discrete_sequence=['gray'])
                st.plotly_chart(fig_age, width='stretch')
    
    with tab4:
        st.subheader("Monthly Sales Performance")
        with st.spinner("Loading chart..."):
            st.plotly_chart(create_monthly_sales_plot(df), width='stretch')
        
        # Sales statistics by month
        st.markdown("#### Monthly Statistics")
        monthly_stats = df.groupby(df['date'].dt.to_period('M'))['sales'].agg([
            ('Total', 'sum'),
            ('Average', 'mean'),
            ('Count', 'count')
        ])
        st.dataframe(monthly_stats, width='stretch')

# Data Explorer Page
elif page == "Data Explorer":
    st.header("Data Explorer")
    
    # Filters
    st.subheader("Filter Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_products = st.multiselect(
            "Select Products",
            options=df['product'].unique(),
            default=df['product'].unique()
        )
    
    with col2:
        selected_regions = st.multiselect(
            "Select Regions",
            options=df['region'].unique(),
            default=df['region'].unique()
        )
    
    with col3:
        selected_gender = st.multiselect(
            "Select Gender",
            options=df['customer_gender'].unique(),
            default=df['customer_gender'].unique()
        )
    
    # Filter dataframe
    filtered_df = df[
        (df['product'].isin(selected_products)) &
        (df['region'].isin(selected_regions)) &
        (df['customer_gender'].isin(selected_gender))
    ].copy()
    
    # Fix date column for display
    if 'date' in filtered_df.columns:
        filtered_df['date'] = filtered_df['date'].astype(str)
    
    # Display filtered data
    st.subheader(f"Filtered Data ({len(filtered_df)} records)")
    st.dataframe(filtered_df, width='stretch')
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_business_data.csv",
        mime="text/csv"
    )
    
    # Summary statistics
    st.subheader("Summary Statistics")
    st.dataframe(filtered_df.describe(), width='stretch')

# Model Evaluation Page
elif page == "Model Evaluation":
    st.header("Model Performance Evaluation with LangSmith")
    
    st.markdown("""
    Evaluate the AI model's performance using LangSmith criteria-based evaluation.
    Questions are automatically traced and evaluated on multiple criteria.
    """)
    
    # LangSmith status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("🔗 **LangSmith Integration Active** - All interactions are traced for monitoring")
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Test questions input
    st.subheader("Enter Test Questions")
    st.markdown("*Expected contexts are optional - evaluation works without them*")
    
    num_questions = st.number_input("Number of test questions", min_value=1, max_value=10, value=3)
    
    test_questions = []
    
    for i in range(num_questions):
        question = st.text_input(f"Question {i+1}", key=f"q_{i}", 
                                placeholder="e.g., What are our top-selling products?")
        test_questions.append(question)
    
    if st.button("Run Evaluation with LangSmith"):
        # Filter out empty questions
        valid_questions = [q for q in test_questions if q.strip()]
        
        if valid_questions:
            with st.spinner("Evaluating model responses with LangSmith criteria..."):
                eval_results = evaluate_model_responses(valid_questions, None)
                
                st.success("✅ Evaluation Complete!")
                
                # Display results
                for i, result in enumerate(eval_results):
                    with st.expander(f"📊 Question {i+1}: {result['question']}", expanded=True):
                        st.markdown("**Generated Answer:**")
                        st.info(result['answer'])
                        
                        st.markdown("**LangSmith Evaluation Criteria:**")
                        st.markdown(result['evaluation'])
                        
                        # Show individual criteria scores if available
                        if 'criteria_scores' in result:
                            st.markdown("---")
                            cols = st.columns(4)
                            for idx, (criterion, score) in enumerate(result['criteria_scores'].items()):
                                with cols[idx % 4]:
                                    st.metric(criterion.title(), "Evaluated ✓")
        else:
            st.warning("⚠️ Please enter at least one question.")
    
    # Conversation Memory Display
    st.markdown("---")
    st.subheader("Conversation Memory")
    
    if memory.messages:
        st.write(f"Total messages in memory: {len(memory.messages)}")
        
        with st.expander("View Conversation History"):
            for msg in memory.messages:
                if hasattr(msg, 'type'):
                    if msg.type == 'human':
                        st.markdown(f"**User:** {msg.content}")
                    else:
                        st.markdown(f"**AI:** {msg.content}")
                st.markdown("---")
    else:
        st.info("No conversation history yet. Start chatting in the AI Assistant page!")

# Footer
st.markdown("---")
st.markdown("""
    <div class='footer'>
        <p>Catalyst AI - AI-Powered Business Intelligence Assistant</p>
        <p>Built with LangChain, LangSmith, OpenAI, and Streamlit</p>
    </div>
""", unsafe_allow_html=True)
