import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from openai import OpenAI
# Path to the saved model and its components
MODEL_PATH = 'artifacts/model_data.joblib'

# Load the model and its components
model_data = joblib.load(MODEL_PATH)
model = model_data['model']
scaler = model_data['scaler']
features = model_data['features']
cols_to_scale = model_data['cols_to_scale']

# Initialize Anthropic client (you'll need to set ANTHROPIC_API_KEY environment variable)
# You can get your API key from: https://console.anthropic.com/
# Initialize OpenAI client
openai_client = None
try:
    api_key = ""
    if api_key:
        openai_client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")


def prepare_input(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                    delinquency_ratio, credit_utilization_ratio, num_open_accounts, residence_type,
                    loan_purpose, loan_type):
    # Create a dictionary with input values and dummy values for missing features
    input_data = {
        'age': age,
        'loan_tenure_months': loan_tenure_months,
        'number_of_open_accounts': num_open_accounts,
        'credit_utilization_ratio': credit_utilization_ratio,
        'loan_to_income': loan_amount / income if income > 0 else 0,
        'delinquency_ratio': delinquency_ratio,
        'avg_dpd_per_delinquency': avg_dpd_per_delinquency,
        'residence_type_Owned': 1 if residence_type == 'Owned' else 0,
        'residence_type_Rented': 1 if residence_type == 'Rented' else 0,
        'loan_purpose_Education': 1 if loan_purpose == 'Education' else 0,
        'loan_purpose_Home': 1 if loan_purpose == 'Home' else 0,
        'loan_purpose_Personal': 1 if loan_purpose == 'Personal' else 0,
        'loan_type_Unsecured': 1 if loan_type == 'Unsecured' else 0,
        # additional dummy fields just for scaling purpose
        'number_of_dependants': 1,
        'years_at_current_address': 1,
        'zipcode': 1,
        'sanction_amount': 1,
        'processing_fee': 1,
        'gst': 1,
        'net_disbursement': 1,
        'principal_outstanding': 1,
        'bank_balance_at_application': 1,
        'number_of_closed_accounts': 1,
        'enquiry_count': 1
    }

    df = pd.DataFrame([input_data])
    df[cols_to_scale] = scaler.transform(df[cols_to_scale])
    df = df[features]

    return df


def predict(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
            delinquency_ratio, credit_utilization_ratio, num_open_accounts,
            residence_type, loan_purpose, loan_type):
    # Prepare input data
    input_df = prepare_input(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                             delinquency_ratio, credit_utilization_ratio, num_open_accounts, residence_type,
                             loan_purpose, loan_type)

    probability, credit_score, rating = calculate_credit_score(input_df)

    return probability, credit_score, rating


def calculate_credit_score(input_df, base_score=300, scale_length=600):
    x = np.dot(input_df.values, model.coef_.T) + model.intercept_
    default_probability = 1 / (1 + np.exp(-x))
    non_default_probability = 1 - default_probability
    credit_score = base_score + non_default_probability.flatten() * scale_length

    def get_rating(score):
        if 300 <= score < 500:
            return 'Poor'
        elif 500 <= score < 650:
            return 'Average'
        elif 650 <= score < 750:
            return 'Good'
        elif 750 <= score <= 900:
            return 'Excellent'
        else:
            return 'Undefined'

    rating = get_rating(credit_score[0])

    return default_probability.flatten()[0], int(credit_score[0]), rating


def get_llm_insights_openai(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                             delinquency_ratio, credit_utilization_ratio, num_open_accounts,
                             residence_type, loan_purpose, loan_type, probability, credit_score, 
                             rating, loan_to_income_ratio):
    """
    Use OpenAI GPT-4 to generate detailed insights about the credit risk assessment
    """
    
    if openai_client is None:
        return """
        **⚠️ OpenAI Integration Not Configured**
        
        To enable AI-powered insights with OpenAI:
        
        1. Get your API key from https://platform.openai.com/api-keys
        2. Set the environment variable: `export OPENAI_API_KEY='your-api-key'`
        3. Restart the application
        
        Meanwhile, here's the basic assessment:
        - **Credit Score**: {score} ({rating})
        - **Default Probability**: {prob:.2%}
        """.format(score=credit_score, rating=rating, prob=probability)
    
    # Create a detailed prompt for GPT
    prompt = f"""You are a credit risk analyst providing insights on a loan application. Based on the following information, provide a comprehensive risk assessment:

**Applicant Profile:**
- Age: {age} years
- Income: ₹{income:,}
- Loan Amount Requested: ₹{loan_amount:,}
- Loan Purpose: {loan_purpose}
- Loan Type: {loan_type}
- Residence Type: {residence_type}

**Financial Metrics:**
- Loan to Income Ratio: {loan_to_income_ratio:.2f}
- Loan Tenure: {loan_tenure_months} months
- Credit Utilization Ratio: {credit_utilization_ratio}%
- Number of Open Accounts: {num_open_accounts}
- Delinquency Ratio: {delinquency_ratio}%
- Average Days Past Due per Delinquency: {avg_dpd_per_delinquency}

**Model Assessment:**
- Credit Score: {credit_score}
- Rating: {rating}
- Default Probability: {probability:.2%}

Please provide:
1. **Risk Summary**: A brief overview of the overall credit risk level
2. **Key Risk Factors**: Identify the top 2-3 factors contributing to the risk (positive or negative)
3. **Recommendations**: 
   - For the lender: Should they approve/reject and under what conditions?
   - For the borrower: How can they improve their creditworthiness?
4. **Alternative Actions**: Any suggestions for loan restructuring or mitigation strategies

Format your response in markdown with clear sections. Be professional, concise, and actionable."""

    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4o" for faster responses
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert credit risk analyst providing detailed, actionable insights on loan applications."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        # Extract the response
        insights = response.choices[0].message.content
        return insights
        
    except Exception as e:
        return f"""
        **Error generating AI insights**: {str(e)}
        
        **Basic Assessment:**
        - Credit Score: {credit_score} ({rating})
        - Default Probability: {probability:.2%}
        - Loan to Income Ratio: {loan_to_income_ratio:.2f}
        
        The model indicates a **{rating}** credit rating with a {probability:.2%} probability of default.
        """

