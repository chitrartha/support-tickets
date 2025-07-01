import streamlit as st
import pandas as pd
import json
import time
from PIL import Image

# --- Page Configuration ---
st.set_page_config(page_title="Utopiaequity", page_icon="📈", layout="wide")

# --- MOCK DATABASE AND API FETCHER ---
MOCK_DATABASE = {
  "Natco Pharma Ltd": [
    {"output": {"company_name": "Natco Pharma Ltd", "report_details": {"Part 1: Corporate Governance and Management Credibility Assessment": {"1. Future Forecast vs. Actuals (Past 5 Years)": "Based on available information...", "2. Management Guidance Analysis": {"Current Guidance": "Natco Pharma's current guidance...", "Historical Comparison": {"Revenue": "In previous years...", "Bottom Line": "Similar to revenue...", "CapEx/Strategic Initiatives": "Natco Pharma has consistently announced..."}, "Overall Credibility Assessment": "Overall, Natco Pharma's management..."}}, "Part 2: Operational Risk and Business Quality Analysis": {"summary_table": [{"Factor": "High Capex", "Assessment": "NO", "Data": "Most recent annual Capex...", "Justification": "Capex is relatively low..."}, {"Factor": "High R&D", "Assessment": "YES", "Data": "Most recent annual R&D expense...", "Justification": "R&D expense is significant..."}], "Overall Risk Assessment": "Natco Pharma presents a moderate risk..."}, "Part 3: Holistic Investment Investigation Report": {"1. Overall Investigation (Li Lu Style)": "Natco Pharma is a vertically integrated...", "2. Business Model and Moat (Nick Sleep Style)": "Natco Pharma's business model...", "3. Risks and Quality of Business (Charlie Munger Style)": "Key risks associated with Natco...", "4. Owner's Earnings and Margin of Safety (Warren Buffett Style)": {"Owner's Earnings and Margin of Safety Analysis": "Estimating Natco Pharma's...", "IRR Projections": {"Li Lu": "Bear: 5%, Base: 10%, Bull: 15%", "Nick Sleep": "Bear: 7%, Base: 12%, Bull: 18%", "Charlie Munger": "Bear: 3%, Base: 8%, Bull: 13%", "Warren Buffett": "Bear: 4%, Base: 9%, Bull: 14%"}, "Fat Pitch Analysis": "A \"fat pitch\" investment..."}, "5. 3-10 Year Hold Scenarios": "Bear Case (20% probability): Regulatory setbacks..."}}, "Part 4: investment score": 69}}
  ],
  "IZMO Ltd": [
    {"output": {"company_name": "IZMO Ltd", "report_details": {"Part 1: Corporate Governance and Management Credibility Assessment": {"1. Future Forecast vs. Actuals (Past 5 Years)": "Analysis of past forecasts...", "2. Management Guidance Analysis": {"Current Guidance": "Detailed management's...", "Historical Comparison": {"Revenue": "Comparison of past revenue...", "Bottom Line": "Comparison of past bottom-line...", "CapEx/Strategic Initiatives": "Comparison of past CapEx..."}, "Overall Credibility Assessment": "Assessment of management's..."}}, "Part 2: Operational Risk and Business Quality Analysis": {"summary_table": [{"Factor": "High Capex", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine..."}, {"Factor": "High R&D", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine..."}], "Overall Risk Assessment": "Based on the lack of..."}, "Part 3: Holistic Investment Investigation Report": {"1. Overall Investigation (Li Lu Style)": "A comprehensive investigation...", "2. Business Model and Moat (Nick Sleep Style)": "Analyzing IZMO Ltd's...", "3. Risks and Quality of Business (Charlie Munger Style)": "Assessing the risks...", "4. Owner's Earnings and Margin of Safety (Warren Buffett Style)": {"Owner's Earnings and Margin of Safety Analysis": "Calculating IZMO Ltd's...", "IRR Projections": {"Li Lu": "Unable to project IRR...", "Nick Sleep": "Unable to project IRR...", "Charlie Munger": "Unable to project IRR...", "Warren Buffett": "Unable to project IRR..."}, "Fat Pitch Analysis": "Identifying conditions..."}, "5. 3-10 Year Hold Scenarios": "Developing bear, base, and bull..."}}, "Part 4: investment score": 25}}
  ]
}

def fetch_data(stock_name: str):
    """Placeholder function to simulate fetching data for a single stock."""
    time.sleep(0.5) # Simulate network delay
    return MOCK_DATABASE.get(stock_name)

# --- REPORT DISPLAY FUNCTION ---
def display_report(report_dictionary):
    """Renders the detailed investment report from the JSON data."""
    output_data = report_dictionary.get("output", {})
    
    st.header(f"Analysis for: {output_data.get('company_name', 'N/A')}")
    st.metric(label="Overall Investment Score", value=output_data.get('Part 4: investment score', 'N/A'))
    
    report_details = output_data.get("report_details", {})

    # Part 1: Corporate Governance
    part1_data = report_details.get("Part 1: Corporate Governance and Management Credibility Assessment", {})
    if part1_data:
        with st.expander("**Part 1: Corporate Governance and Management Credibility Assessment**", expanded=False):
            for key, value in part1_data.items():
                st.subheader(key)
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        st.markdown(f"**{sub_key}**")
                        if isinstance(sub_value, dict):
                            for item_key, item_value in sub_value.items():
                                st.markdown(f"***{item_key}***: {item_value}")
                        else:
                            st.markdown(sub_value)
                else:
                    st.markdown(value)

    # Part 2: Operational Risk
    part2_data = report_details.get("Part 2: Operational Risk and Business Quality Analysis", {})
    if part2_data:
        with st.expander("**Part 2: Operational Risk and Business Quality Analysis**", expanded=False):
            st.subheader("Summary Table")
            summary_table = part2_data.get("summary_table")
            if summary_table:
                st.dataframe(pd.DataFrame(summary_table), use_container_width=True, hide_index=True)
            
            st.subheader("Overall Risk Assessment")
            st.markdown(part2_data.get("Overall Risk Assessment", "N/A"))

    # Part 3: Holistic Investment Investigation
    part3_data = report_details.get("Part 3: Holistic Investment Investigation Report", {})
    if part3_data:
        with st.expander("**Part 3: Holistic Investment Investigation Report**", expanded=False):
            for key, value in part3_data.items():
                st.subheader(key)
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        st.markdown(f"**{sub_key}**")
                        if isinstance(sub_value, dict):
                            df_irr = pd.DataFrame.from_dict(sub_value, orient='index')
                            df_irr.index.name = "Investment Style"
                            df_irr.columns = ["Scenario"]
                            st.table(df_irr)
                        else:
                            st.markdown(sub_value)
                else:
                    st.markdown(value)

# --- UI STYLES ---
st.markdown("""
    <style>
        /* Main App Style */
        .stApp {
            background-color: #f0f5f9; /* Lightish Blue */
        }
        /* Title Style */
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem 0;
        }
        .title {
            font-size: 3rem;
            font-weight: 600;
            color: #1e2a38; /* Dark Blue/Charcoal */
            padding: 0 1rem;
        }
        /* Button Style */
        div[data-testid="stButton"] > button {
            background-color: #00a896; /* Vibrant Green/Teal */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #00897b;
        }
        /* Tabs Style */
        div[data-testid="stTabs"] button {
            color: #1e2a38; /* Dark text for inactive tabs */
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background-color: #00a896;
            color: white;
            border-radius: 5px 5px 0 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
try:
    logo_img = Image.open("assets/logo.png")
    arrow_img = Image.open("assets/arrow.png")

    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.image(logo_img, width=100)
    with col2:
        st.markdown('<div class="title-container"><p class="title">Utopiaequity</p></div>', unsafe_allow_html=True)
    with col3:
        st.image(arrow_img, width=150)
except FileNotFoundError:
    st.error("Error: Image files not found. Please make sure `logo.png` and `arrow.png` are in an 'assets' folder.")

st.divider()

# --- TABS FOR NAVIGATION ---
tab1, tab2 = st.tabs(["Analyze Specific Stocks", "Browse All Reports"])

# --- TAB 1: ANALYZE MULTIPLE STOCKS ---
with tab1:
    st.header("Analyze Stocks by Name")
    st.write("Enter one or more stock names separated by commas or newlines.")
    
    stock_names_input = st.text_area(
        "Stock Names:",
        placeholder="e.g.\nNatco Pharma Ltd,\nIZMO Ltd",
        height=100,
        key="text_area_input"
    )
    
    if st.button("Generate Reports"):
        if stock_names_input:
            standardized_input = stock_names_input.replace(',', '\n')
            stock_list = [name.strip() for name in standardized_input.split('\n') if name.strip()]
            
            if stock_list:
                st.info(f"Found {len(stock_list)} stock(s) to process.")
                for stock_name in stock_list:
                    with st.spinner(f"Fetching data for {stock_name}..."):
                        # BUG FIX: The fetch function returns a list
                        report_data_list = fetch_data(stock_name)
                    
                    if report_data_list:
                        # Unpack the dictionary from the list before passing it
                        report_dictionary = report_data_list[0]
                        display_report(report_dictionary)
                    else:
                        st.error(f"No data found for '{stock_name}'.")
                    st.divider()
            else:
                st.warning("Please enter at least one valid stock name.")
        else:
            st.warning("The input box is empty. Please enter one or more stock names.")

# --- TAB 2: BROWSE ALL AVAILABLE REPORTS ---
with tab2:
    st.header("Browse All Available Reports")
    
    all_company_names = list(MOCK_DATABASE.keys())
    
    selected_company = st.selectbox(
        "Select a company to view its report:",
        options=all_company_names,
        index=0
    )
    
    if selected_company:
        with st.spinner(f"Loading report for {selected_company}..."):
            # BUG FIX: The fetch function returns a list
            report_data_list = fetch_data(selected_company)
        
        if report_data_list:
            # Unpack the dictionary from the list before passing it
            report_dictionary = report_data_list[0]
            display_report(report_dictionary)