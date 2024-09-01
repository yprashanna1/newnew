import streamlit as st
import json
import os
from model import load_rules, get_ai_response, check_response_against_rules, request_modified_response, add_rule

# Load rules from the JSON file
def load_rules_from_file():
    with open('rules.json', 'r') as f:
        return json.load(f)

def save_rules_to_file(rules):
    with open('rules.json', 'w') as f:
        json.dump(rules, f, indent=4)

rules_data = load_rules_from_file()

# Set up the page configuration
st.set_page_config(
    page_title="AI Governance and Monitoring System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .title {
        font-size: 50px;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        font-family: 'Montserrat', sans-serif;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 25px;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 50px;
    }
    .query-box {
        border-radius: 15px;
        padding: 15px;
        background-color: #ECF0F1;
        font-size: 18px;
        margin: 0 10px;
        width: 22%;
        text-align: center;
        display: inline-block;
        font-family: 'Montserrat', sans-serif;
        cursor: pointer;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .query-box:hover {
        background-color: #D5DBDB;
    }
    .query-container {
        text-align: center;
        margin-top: 50px;
    }
    .query-input {
        width: 100%;
        padding: 20px;
        font-size: 18px;
        border-radius: 15px;
        border: 1px solid #BDC3C7;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .get-response-button {
        background-color: #2980B9;
        color: white;
        padding: 10px 20px;
        font-size: 18px;
        border-radius: 15px;
        margin-left: 10px;
        cursor: pointer;
        border: none;
        font-family: 'Montserrat', sans-serif;
    }
    .get-response-button:hover {
        background-color: #1B4F72;
    }
    .spinner {
        text-align: center;
        font-size: 18px;
        margin-top: 20px;
        color: #2980B9;
        font-family: 'Montserrat', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Interface
st.markdown('<div class="title">AI Governance and Monitoring System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ensuring Ethical AI Responses</div>', unsafe_allow_html=True)

# Example queries in square boxes
example_queries = [
    "💼 How can I invest in the stock market?",
    "⚖️ What happens in a divorce regarding property?",
    "🩺 What are the symptoms of diabetes?",
    "🏦 Should I refinance my mortgage?"
]

clicked_query = None
st.markdown('<div class="query-container">', unsafe_allow_html=True)
cols = st.columns(len(example_queries))
for i, query in enumerate(example_queries):
    if cols[i].button(query):
        st.session_state.user_query = query  # Update session state with clicked query
st.markdown('</div>', unsafe_allow_html=True)

# Initialize the user query state if not already set
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""

# Display text area with session state value
user_input = st.text_area("Enter your query here:", value=st.session_state.user_query, key="user_query", height=60, max_chars=None)

# Button to trigger AI response generation
if st.button("Get AI Response", key="get_response_button", help="Click to get AI's response"):
    if st.session_state.user_query.strip() == "":
        st.warning("Please enter a query before getting a response.")
    else:
        with st.spinner('Generating response...'):
            try:
                response = get_ai_response(st.session_state.user_query)
                st.write("AI Response:")
                st.write(response)
                
                # Check the response against the rules
                rule_check, missing_rule = check_response_against_rules(response, rules_data)
                if not rule_check:
                    st.warning(f"The response may not fully comply with the rule: {missing_rule}")
                    st.write("Requesting a modified response...")
                    modified_response = request_modified_response(st.session_state.user_query, missing_rule)
                    st.write("Modified AI Response:")
                    st.write(modified_response)
            except Exception as e:
                st.error(f"An error occurred while generating the response: {str(e)}")

# Move the Trainer Interface to Sidebar
with st.sidebar:
    st.header("Trainer Interface")
    st.subheader("Select the domain you want to train:")
    domain = st.selectbox("", ["Finance", "Law", "Medical"])

    # Initialize session states for trainer inputs
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'query_keywords' not in st.session_state:
        st.session_state.query_keywords = ""
    if 'rules_list' not in st.session_state:
        st.session_state.rules_list = ""

    # User authentication
    if not st.session_state.logged_in:
        st.session_state.user_id = st.text_input("User ID", type="default")
        st.session_state.password = st.text_input("Password", type="password")

        if st.button("Login"):
            if (domain == "Finance" and st.session_state.user_id == "finance" and st.session_state.password == "financepass") or \
               (domain == "Law" and st.session_state.user_id == "lawyer" and st.session_state.password == "lawyerpass") or \
               (domain == "Medical" and st.session_state.user_id == "doctor" and st.session_state.password == "doctorpass"):
                st.success(f"Welcome, {st.session_state.user_id}!")
                st.session_state.logged_in = True
            else:
                st.error("Invalid User ID or Password")
    else:
        st.subheader(f"Add new rules to the {domain} domain")

        # Maintain input values using session state
        st.session_state.query_keywords = st.text_input(
            "Query Keywords (comma-separated)", 
            value=st.session_state.query_keywords
        )
        
        st.session_state.rules_list = st.text_area(
            "Rules (separated by semicolon ';')", 
            value=st.session_state.rules_list
        )

        if st.button("Add Rule"):
            if st.session_state.query_keywords.strip() == "" or st.session_state.rules_list.strip() == "":
                st.warning("Please provide both query keywords and rules before adding.")
            else:
                query_keywords_list = [kw.strip() for kw in st.session_state.query_keywords.split(',')]
                new_rules = [rule.strip() for rule in st.session_state.rules_list.split(';')]

                # Add rule to rules_data and save it to the JSON file
                add_rule(domain.lower(), query_keywords_list, new_rules, rules_data)
                save_rules_to_file(rules_data)
                st.success(f"New rules added under the {domain} domain.")

                # Clear input fields after successful addition
                st.session_state.query_keywords = ""
                st.session_state.rules_list = ""
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.session_state.password = ""
