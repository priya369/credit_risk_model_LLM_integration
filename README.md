# Credit Risk Modelling with LLM Integration

This enhanced version of your credit risk model integrates Large Language Models (LLMs) to provide intelligent, interpretable insights alongside your machine learning predictions.

## 🚀 Features

### Original Features
- Credit risk prediction using logistic regression
- Credit score calculation (300-900 range)
- Risk rating (Poor, Average, Good, Excellent)
- Interactive Streamlit interface

### New LLM-Enhanced Features
- **AI-Powered Risk Analysis**: Detailed explanations of risk factors
- **Personalized Recommendations**: Actionable advice for both lenders and borrowers
- **Risk Factor Identification**: Highlights key factors affecting creditworthiness
- **Alternative Solutions**: Suggests loan restructuring or mitigation strategies
- **Natural Language Insights**: Human-readable explanations of model outputs

## 📋 Setup Instructions

### 1. Install Required Packages

```bash
pip install streamlit anthropic joblib numpy pandas scikit-learn
```

Or create a `requirements.txt`:
```txt
streamlit==1.31.0
joblib==1.3.2
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
openai
```

Then install:
```bash
pip install -r requirements.txt
```

### 2. Get Your openai API Key

1. Visit https://platform.openai.com/settings/organization/api-keys
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-proj-`)

### 3. Set Up Environment Variable

**Linux/Mac:**
```bash
export openai_api_key='your-api-key-here'
```

**Windows (Command Prompt):**
```cmd
set  openai_api_key=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env: openai_api_key='your-api-key-here'
```

**Or create a `.env` file:**
```
 openai_api_key=your-api-key-here
```

Then load it in your code:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. File Structure

```
credit_risk_model/app
│
├── main.py                    # Enhanced Streamlit app
├── prediction_llm_helper.py       # ML + LLM integration                          # Original Streamlit app
├── artifacts/
│   └── model_data.joblib              # Your trained model
```

### 5. Run the Application

```bash
streamlit run main_with_llm.py
```

## 🎯 How It Works

### 1. Traditional ML Pipeline (Unchanged)
- Takes user inputs (age, income, loan details, etc.)
- Preprocesses data with scaling
- Uses logistic regression for prediction
- Calculates credit score and rating

### 2. LLM Enhancement Layer (New)
- Receives ML model outputs + input features
- Constructs a detailed prompt with financial context
- Calls Claude API for intelligent analysis
- Returns structured insights with:
  - Risk summary
  - Key risk factors
  - Lender recommendations
  - Borrower improvement tips
  - Alternative strategies

## 📊 Example Output

**Traditional Output:**
- Default Probability: 15.32%
- Credit Score: 678
- Rating: Good

**Enhanced LLM Output:**
```markdown
### Risk Summary
This applicant presents a MODERATE risk profile with a Good credit rating...

### Key Risk Factors
1. **Positive**: Low loan-to-income ratio (2.13) indicates strong repayment capacity
2. **Concern**: Delinquency ratio of 30% suggests past payment issues
3. **Concern**: Average DPD of 20 days shows pattern of late payments

### Recommendations

**For the Lender:**
- Approve with conditions: higher interest rate (prime + 2-3%)
- Require additional collateral or guarantor
- Set up automated payment reminders

**For the Borrower:**
- Focus on consistent on-time payments for next 6-12 months
- Reduce credit utilization below 20%
- Consider debt consolidation to simplify payments

### Alternative Actions
- Offer a smaller loan amount initially (₹18L instead of ₹25.6L)
- Implement graduated payment structure
- Provide financial literacy counseling
```

## 🔧 Customization Options

### 1. Use Different LLM Providers

**OpenAI (GPT-4):**
```python
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": prompt}]
)
insights = response.choices[0].message.content
```

**Google (Gemini):**
```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(prompt)
insights = response.text
```

### 2. Customize the Prompt

Modify the prompt in `get_llm_insights()` to:
- Focus on specific risk factors
- Change the tone (more technical/casual)
- Add regulatory compliance checks
- Include industry-specific guidelines

### 3. Add Caching

For repeated requests with similar parameters:

```python
import functools
from functools import lru_cache

@lru_cache(maxsize=100)
def get_llm_insights_cached(credit_score, rating, probability):
    # Cached version for similar scores
    pass
```

### 4. Streaming Responses

For real-time output in Streamlit:

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1500,
    messages=[{"role": "user", "content": prompt}]
) as stream:
    for text in stream.text_stream:
        st.write(text, end="")
```



