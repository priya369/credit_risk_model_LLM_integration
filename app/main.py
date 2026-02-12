import streamlit as st
from prediction_llm_helper import predict, get_llm_insights_openai
from datetime import datetime

# Set the page configuration
st.set_page_config(
    page_title="Credit Risk Assessment", 
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Remove default padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Column styling */
    [data-testid="column"]:first-child {
        border-right: 1px solid #e5e7eb;
        padding-right: 2rem !important;
    }
    
    [data-testid="column"]:last-child {
        padding-left: 2rem !important;
    }
    
    /* Form title */
    .form-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .form-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* Chat header */
    .chat-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    /* Message bubbles */
    .ai-message {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.3s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .ai-avatar {
        width: 32px;
        height: 32px;
        min-width: 32px;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1rem;
    }
    
    .message-bubble {
        flex: 1;
        background: #ffffff;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .message-time {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.5rem;
        margin-left: 40px;
    }
    
    /* Form inputs */
    .stTextInput input,
    .stNumberInput input {
        background: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        font-size: 0.875rem !important;
        color: #111827 !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {
        color: #9ca3af !important;
    }
    
    .stSelectbox select {
        background: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        font-size: 0.875rem !important;
        color: #6b7280 !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stSlider label {
        font-size: 0.8125rem !important;
        font-weight: 500 !important;
        color: #111827 !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Reduce spacing between form elements */
    .stTextInput,
    .stNumberInput,
    .stSelectbox,
    .stSlider {
        margin-bottom: 0.75rem !important;
    }
    
    /* Compact form subtitle */
    .form-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 1.25rem;
    }
    
    /* Calculate button */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 0.9375rem;
        font-weight: 600;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }
    
    /* Results card */
    .results-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .result-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .result-row:last-child {
        border-bottom: none;
    }
    
    .result-label {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    .result-value {
        font-size: 0.9375rem;
        font-weight: 600;
    }
    
    .result-value-good {
        color: #10b981;
    }
    
    .result-value-warning {
        color: #f59e0b;
    }
    
    .result-value-danger {
        color: #ef4444;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Chat area styling */
    .chat-container {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 8px;
        min-height: 400px;
        max-height: calc(100vh - 200px);
        overflow-y: auto;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f3f4f6;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [{
        'role': 'assistant',
        'content': "Hello! I'm your AI assistant for credit risk analysis. I can help you understand credit scores, risk factors, and provide insights about loan applications. How can I assist you today?",
        'time': "16:45"
    }]

# Create two columns
col1, col2 = st.columns([1, 1.5])

# LEFT COLUMN - FORM
with col1:
    st.markdown('<h4 class="form-title">📊 Credit Risk Assessment</h4>', unsafe_allow_html=True)
    st.markdown('<p class="form-subtitle">Enter applicant details to evaluate credit risk</p>', unsafe_allow_html=True)
    
    # Row 1: Age and Income
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        age = st.number_input('Age', min_value=18, max_value=100, value=28, placeholder="Enter age")
    with r1c2:
        income = st.number_input('Income ($)', min_value=0, value=120000, step=5000, placeholder="Annual income")
    
    # Row 2: Loan Amount and Tenure
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        loan_amount = st.number_input('Loan Amount ($)', min_value=0, value=256000, step=5000, placeholder="Loan amount")
    with r2c2:
        loan_tenure_months = st.number_input('Tenure (months)', min_value=1, max_value=360, value=36, placeholder="Months")
    
    # Row 3: Loan Purpose and Type
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        loan_purpose = st.selectbox('Loan Purpose', ['Select', 'Education', 'Home', 'Auto', 'Personal'], index=0)
    with r3c2:
        loan_type = st.selectbox('Loan Type', ['Select', 'Secured', 'Unsecured'], index=0)
    
    r4c1, r4c2 =st.columns(2)
    with r4c1:
       residence_type = st.selectbox('Residence Type', ['Select', 'Owned', 'Rented', 'Mortgage'], index=0)
    with r4c2:
       avg_dpd_per_delinquency = st.number_input('Avg DPD', min_value=0, value=20, placeholder="Days past due")
    # Row 5: Credit metrics - compact sliders
    num_open_accounts = st.slider('Open Accounts', 0, 10, 2)
    credit_utilization_ratio = st.slider('Credit Util. (%)', 0, 100, 30)
    delinquency_ratio = st.slider('Delinquency (%)', 0, 100, 30)
    
    calculate_clicked = st.button('🔍 Analyze Credit Risk')

# RIGHT COLUMN - CHAT
with col2:
    st.markdown('<h4 class="chat-header">🤖 AI Assistant</h4>', unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        st.markdown(f"""
        <div class="ai-message">
            <div class="ai-avatar">🤖</div>
            <div class="message-bubble">
                {msg['content']}
            </div>
        </div>
        <div class="message-time">{msg['time']}</div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle calculate button
if calculate_clicked:
    if loan_purpose == 'Select' or residence_type == 'Select' or loan_type == 'Select':
        error_msg = {
            'role': 'assistant',
            'content': "⚠️ Please fill in all required fields before analyzing.",
            'time': datetime.now().strftime("%H:%M")
        }
        st.session_state.chat_messages.append(error_msg)
        st.rerun()
    else:
        # Get predictions
        probability, credit_score, rating = predict(
            age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
            delinquency_ratio, credit_utilization_ratio, num_open_accounts,
            residence_type, loan_purpose, loan_type
        )
        
        loan_to_income_ratio = loan_amount / income if income > 0 else 0
        
        # Determine colors
        prob_class = "good" if probability < 0.15 else ("warning" if probability < 0.30 else "danger")
        rating_class = {"Excellent": "good", "Good": "good", "Average": "warning", "Poor": "danger"}.get(rating, "warning")
        
        # Results card
        results_html = f"""
        <div class="results-card">
            <div style="font-weight: 600; margin-bottom: 1rem; color: #111827;">📊 Assessment Results</div>
            <div class="result-row">
                <span class="result-label">Credit Score</span>
                <span class="result-value result-value-{rating_class}">{credit_score}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Rating</span>
                <span class="result-value result-value-{rating_class}">{rating}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Default Probability</span>
                <span class="result-value result-value-{prob_class}">{probability:.2%}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Loan to Income Ratio</span>
                <span class="result-value">{loan_to_income_ratio:.2f}</span>
            </div>
        </div>
        """
        
        results_msg = {
            'role': 'assistant',
            'content': results_html,
            'time': datetime.now().strftime("%H:%M")
        }
        st.session_state.chat_messages.append(results_msg)
        
        # Get AI insights
        insights = get_llm_insights_openai(
            age=age, income=income, loan_amount=loan_amount,
            loan_tenure_months=loan_tenure_months,
            avg_dpd_per_delinquency=avg_dpd_per_delinquency,
            delinquency_ratio=delinquency_ratio,
            credit_utilization_ratio=credit_utilization_ratio,
            num_open_accounts=num_open_accounts,
            residence_type=residence_type,
            loan_purpose=loan_purpose,
            loan_type=loan_type,
            probability=probability,
            credit_score=credit_score,
            rating=rating,
            loan_to_income_ratio=loan_to_income_ratio
        )
        
        ai_msg = {
            'role': 'assistant',
            'content': insights,
            'time': datetime.now().strftime("%H:%M")
        }
        st.session_state.chat_messages.append(ai_msg)
        
        st.rerun()