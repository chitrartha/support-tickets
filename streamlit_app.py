import streamlit as st
import pandas as pd
import json
import time
from PIL import Image
from pathlib import Path
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os # Import os for environment variables (though we're reverting its use for creds)
import warnings # Import warnings to suppress the rsa UserWarning

# Suppress the specific rsa UserWarning globally if you're sure it's not a critical issue for your use case
warnings.filterwarnings("ignore", category=UserWarning, module="rsa.key")

# --- Page Configuration ---
st.set_page_config(page_title="Utopiaequity", page_icon="assets/logo.png", layout="wide")

# --- Function to encode image to base64 for embedding in CSS ---
def get_image_as_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.error(f"Logo file not found at: {path}. Please ensure 'assets/logo.png' exists.")
        return ""

# --- Google Sheet Configuration ---
GOOGLE_SHEET_SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
GOOGLE_SHEET_NAME = "ai_agents"
GOOGLE_SHEET_TAB_NAME_RESULTS = "result_stocks" # Original tab for results
GOOGLE_SHEET_TAB_NAME_STOCKS = "stocks"       # New tab for stock names from where autocomplete suggestions are fetched
GCP_CREDS_FILE = Path("assets/creds.json") # Path to your service account JSON file (fallback)


# --- Initialize MOCK_DATABASE with fixed companies, and use session state for dynamic data ---
if "MOCK_DATABASE" not in st.session_state:
    st.session_state.MOCK_DATABASE = {
        "Natco Pharma Ltd": [
            {"output": {"company_name": "Natco Pharma Ltd", "report_details": {"Part 1: Corporate Governance and Management Credibility Assessment": {"1. Future Forecast vs. Actuals (Past 5 Years)": "Based on available information, assessing Natco Pharma's forecasts against actual performance over the past five years reveals a mixed track record. While specific conference call transcripts and detailed financial data would be needed for a precise analysis, general trends suggest that the company has faced challenges in consistently meeting its ambitious growth targets. Factors such as regulatory hurdles in key markets (like the US), pricing pressures in the generic drug market, and delays in product approvals have impacted their performance. The management's communication has generally been transparent regarding these challenges, but the predictability of their forecasts could be improved.", "2. Management Guidance Analysis": {"Current Guidance": "Natco Pharma's current guidance typically includes projections for revenue growth, EBITDA margins, and specific CapEx plans related to new facilities or product development. While exact figures vary year to year, recent guidance has emphasized expansion in key markets (US, India, and emerging markets), investment in complex generics and specialty products, and maintaining a healthy balance sheet. More granular figures require up-to-date earnings calls and investor presentations.", "Historical Comparison": {"Revenue": "In previous years (e.g., 3-5 years ago), Natco Pharma's revenue guidance often targeted double-digit percentage growth, driven by new product launches and market penetration. In some years, they met or exceeded these targets, particularly when they successfully launched key products. However, there.were instances where revenue growth fell short due to unexpected regulatory delays, increased competition, or market-specific challenges. Specific figures will require a review of past annual reports and investor presentations.", "Bottom Line": "Similar to revenue, Natco Pharma aimed for significant bottom-line growth (EBITDA/PAT) in past guidance. Success in achieving these targets depended heavily on their ability to control costs, manage pricing pressures, and efficiently scale up production. There were instances where they exceeded expectations due to favorable product mixes or cost optimization initiatives, but also instances where they fell short due to increased operating expenses or pricing pressures. Specific figures will will require a review of past annual reports and investor presentations.", "CapEx/Strategic Initiatives": "Natco Pharma has consistently announced CapEx plans focused on expanding manufacturing capacity, upgrading R&D facilities, and investing in new technologies. The execution of these plans has generally been consistent with their stated intentions, although there have been occasional delays due to unforeseen circumstances or regulatory approvals. For instance, announcements regarding capacity expansion for specific product lines or investments in biosimilar development have largely materialized as planned."}, "Overall Credibility Assessment": "Overall, Natco Pharma's management has demonstrated reasonable credibility in forecasting, although their projections can be susceptible to external factors such as regulatory changes and market dynamics. They tend to provide relatively transparent guidance, acknowledging both potential opportunities and challenges. However, investors should exercise caution and consider the inherent uncertainties in the pharmaceutical industry when evaluating their forecasts."}}, "Part 2: Operational Risk and Business Quality Analysis": {"summary_table": [{"Factor": "High Capex", "Assessment": "NO", "Data": "Most recent annual Capex is around 150-200 Cr INR", "Justification": "Capex is relatively low as a percentage of revenue compared to other Pharma companies, indicating a lower capital intensity."}, {"Factor": "High R&D", "Assessment": "YES", "Data": "Most recent annual R&D expense is around 10-12% of revenues.", "Justification": "R&D expense is significant, reflecting the need for continuous innovation in the pharmaceutical industry. Relatively higher than industry average indicates higher risk and reward."}, {"Factor": "Risky Capex", "Assessment": "NO", "Data": "N/A", "Justification": "Capex is primarily directed towards expanding existing facilities and upgrading equipment, with a focus on known product lines. Although there is risk, the company isn't known for taking extreme capital expenditure risk."}, {"Factor": "Risky R&D", "Assessment": "YES", "Data": "N/A", "Justification": "R&D efforts are focused on complex generics and specialty products, which carry higher risks of failure but also offer potentially higher rewards if successful."}, {"Factor": "Dual Class Shares", "Assessment": "NO", "Data": "N/A", "Justification": "Natco Pharma does not have a dual-class share structure."}, {"Factor": "Wasteful FCF", "Assessment": "NO", "Data": "FCF positive", "Justification": "FCF is typically reinvested into R&D, capacity expansion, and debt reduction, indicating efficient capital allocation. Dividends are also paid."}, {"Factor": "Bad Industry", "Assessment": "NO", "Data": "N/A", "Justification": "The pharmaceutical industry offers growth opportunities, particularly in generics and specialty products, but faces regulatory and pricing pressures. Overall good prospects."}, {"Factor": "Acquisition Growth", "Assessment": "NO", "Data": "N/A", "Justification": "Natco Pharma's growth strategy primarily relies on organic growth through product development and market expansion, rather than aggressive acquisitions. This lowers risk."}, {"Factor": "High Debt", "Assessment": "NO", "Data": "Debt to equity ratio below 0.5", "Justification": "Debt levels are manageable, with a healthy debt-to-equity ratio compared to industry peers."}, {"Factor": "Intense Competition", "Assessment": "YES", "Data": "Generic drug market is competitive", "Justification": "The generic pharmaceutical market is highly competitive, with numerous players vying for market share. Pricing pressures are always present."}, {"Factor": "High SBC (Stock-Based Compensation)", "Assessment": "NO", "Data": "SBC is less than 3% of revenue.", "Justification": "Stock-based compensation is relatively low compared to revenue and industry standards."}], "Overall Risk Assessment": "Natco Pharma presents a moderate risk profile. Key risks include R&D success and competition, while financial health is maintained with moderate debt and good FCF management. Company’s moderate capital expenditure is used efficiently. Although R&D is risky, is necessary to grow business. The industry presents opportunities, but also competitive pressure."}, "Part 3: Holistic Investment Investigation Report": {"1. Overall Investigation (Li Lu Style)": "Natco Pharma is a vertically integrated pharmaceutical company focusing on niche therapeutic areas and complex generics. They have demonstrated a strong track record of innovation and successful product launches, particularly in oncology and specialty products. The company's key strengths include its R&D capabilities, manufacturing efficiency, and strong relationships with key stakeholders. Challenges include regulatory hurdles, pricing pressures, and competition in the generic drug market. Recent FDA inspections have increased concern about quality control.", "2. Business Model and Moat (Nick Sleep Style)": "Natco Pharma's business model centers around developing, manufacturing, and marketing niche pharmaceutical products, including generics and specialty drugs. Its competitive advantages (moats) include its strong R&D capabilities, which enable it to develop complex generics and differentiated products. Furthermore, its manufacturing efficiency and vertically integrated operations allow it to maintain cost competitiveness. These moats are reasonably sustainable, providing a buffer against competition, particularly in niche therapeutic areas. However, pricing pressures in the generic drug market can erode profitability.", "3. Risks and Quality of Business (Charlie Munger Style)": "Key risks associated with Natco Pharma's business include regulatory risks (e.g., FDA approvals, inspections), pricing pressures, competition, and product liability risks. The overall quality of the business is considered good, given its strong R&D capabilities, efficient operations, and experienced management team. However, investors should be aware of the inherent uncertainties in the pharmaceutical industry and potential for adverse events. Management integrity is good with a long track record.", "4. Owner's Earnings and Margin of Safety (Warren Buffett Style)": {"Owner's Earnings and Margin of Safety Analysis": "Estimating Natco Pharma's \"owner's earnings\" requires adjusting net income for non-cash expenses (e.g., depreciation, amortization) and CapEx. Intrinsic value can then be determined using a discounted cash flow (DCF) analysis, considering future growth rates and discount rates. The margin of safety depends on the difference between the intrinsic value and the current market price. Due to the uncertainties inherent to forecasting the company's earnings accurately, a conservative estimate is needed.", "IRR Projections": {"Li Lu": "Bear: 5%, Base: 10%, Bull: 15%", "Nick Sleep": "Bear: 7%, Base: 12%, Bull: 18%", "Charlie Munger": "Bear: 3%, Base: 8%, Bull: 13%", "Warren Buffett": "Bear: 4%, Base: 9%, Bull: 14%"}, "Fat Pitch Analysis": "A \"fat pitch\" investment opportunity for Natco Pharma would occur if the company's stock price significantly declined due to temporary setbacks (e.g., regulatory delays, market corrections) while its long-term fundamentals remained strong. This would create an opportunity to buy a high-quality business at a discounted valuation, providing a substantial margin of safety."}, "5. 3-10 Year Hold Scenarios": "Bear Case (20% probability): Regulatory setbacks, increased competition, and pricing pressures lead to declining revenue and profit margins. Average revenue declines 5% annually. Base Case (60% probability): Natco Pharma maintains its market position, introduces new products, and achieves moderate growth. Average revenue grows 8% annually. Bull Case (20% probability): Successful product launches, expansion into new markets, and favorable regulatory environment drive significant growth. Average revenue grows 15% annually. All scenarios assume continued investment in R&D."}}, "Part 4: investment score": 69}}
        ],
        "IZMO Ltd": [
            {"output": {"company_name": "IZMO Ltd", "report_details": {"Part 1: Corporate Governance and Management Credibility Assessment": {"1. Future Forecast vs. Actuals (Past 5 Years)": "Analysis of past forecasts vs. actuals for IZMO Ltd requires detailed financial data, including revenue projections and actual results. Without this data, a thorough assessment cannot be provided.", "2. Management Guidance Analysis": {"Current Guidance": "Detailed management's current guidance for IZMO Ltd is needed, including revenue growth, CapEx plans, and strategic initiatives. Specific figures and timelines are required for an accurate analysis.", "Historical Comparison": {"Revenue": "Comparison of past revenue guidance with actuals for IZMO Ltd requires historical data on management's projections and reported revenue. This information is necessary to assess accuracy.", "Bottom Line": "Comparison of past bottom-line guidance with actuals for IZMO Ltd requires historical data on management's profit projections and reported earnings. Without this data, an evaluation is impossible.", "CapEx/Strategic Initiatives": "Comparison of past CapEx/strategic initiative announcements with actual execution for IZMO Ltd requires tracking management's plans and comparing them to actual investments and results. This data is currently unavailable."}, "Overall Credibility Assessment": "Assessment of management's credibility in forecasting for IZMO Ltd requires a track record of guidance versus actual results. Without sufficient historical data, an objective assessment is not feasible."}}, "Part 2: Operational Risk and Business Quality Analysis": {"summary_table": [{"Factor": "High Capex", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd's capital expenditure is high relative to its peers or historical performance without financial data."}, {"Factor": "High R&D", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd's research and development spending is high relative to its peers or historical performance without financial data."}, {"Factor": "Risky Capex", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Cannot determine whether IZMO Ltd has undertaken risky capital expenditure projects without detailed financial information."}, {"Factor": "Risky R&D", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Cannot determine whether IZMO Ltd has undertaken risky R&D projects without detailed financial information."}, {"Factor": "Dual Class Shares", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to assess the share structure of IZMO Ltd without detailed information on its corporate governance."}, {"Factor": "Wasteful FCF", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd is wasting free cash flow without detailed financial analysis."}, {"Factor": "Bad Industry", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine the long-term prospects of IZMO Ltd's industry without detailed industry analysis."}, {"Factor": "Acquisition Growth", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to assess whether IZMO Ltd relies on acquisitions for growth without analyzing its acquisition history."}, {"Factor": "High Debt", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd has a high debt level without a review of its financial statements."}, {"Factor": "Intense Competition", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to assess the competitive landscape for IZMO Ltd without market analysis."}, {"Factor": "High SBC (Stock-Based Compensation)", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd's SBC is high without analyzing its financial statements."}], "Overall Risk Assessment": "Based on the lack of available data, a comprehensive risk assessment for IZMO Ltd cannot be performed."}, "Part 3: Holistic Investment Investigation Report": {"1. Overall Investigation (Li Lu Style)": "A comprehensive investigation into IZMO Ltd's strengths, weaknesses, and key business drivers requires detailed financial and operational data. Without sufficient information, an accurate analysis is not possible.", "2. Business Model and Moat (Nick Sleep Style)": "Analyzing IZMO Ltd's business model, competitive advantages and their sustainability requires in-depth knowledge of the company's operations and industry dynamics. More data is needed for this assessment.", "3. Risks and Quality of Business (Charlie Munger Style)": "Assessing the risks and quality of IZMO Ltd's business requires evaluating its financial stability, competitive positioning, and management's capital allocation decisions. This analysis requires access to additional data.", "4. Owner's Earnings and Margin of Safety (Warren Buffett Style)": {"Owner's Earnings and Margin of Safety Analysis": "Calculating IZMO Ltd's owner's earnings and determining a margin of safety requires detailed financial projections and a valuation analysis, which cannot be completed without sufficient data.", "IRR Projections": {"Li Lu": "Unable to project IRR for IZMO Ltd without sufficient data.", "Nick Sleep": "Unable to project IRR for IZMO Ltd without sufficient data.", "Charlie Munger": "Unable to project IRR for IZMO Ltd without sufficient data.", "Warren Buffett": "Unable to project IRR for IZMO Ltd without sufficient data."}, "Fat Pitch Analysis": "Identifying conditions for a 'fat pitch' investment in IZMO Ltd requires a thorough understanding of its intrinsic value and potential future growth. Further data is needed for this analysis."}, "5. 3-10 Year Hold Scenarios": "Developing bear, base, and bull case scenarios for holding IZMO Ltd for 3-10 years requires financial modeling and projections based on assumptions about its future performance. These projections cannot be made without additional information."}}, "Part 4: investment score": 25}}
        ]
    }

# --- Helper function to get GCP credentials from the JSON file ---
@st.cache_resource(ttl=3600) # Cache the loaded credentials for efficiency
def _get_gcp_creds():
    # --- RESTORED TO YOUR ORIGINAL WORKING LOGIC ---
    if not GCP_CREDS_FILE.exists():
        st.error(f"Credentials file not found at: {GCP_CREDS_FILE}. Please ensure it exists in your 'assets/' folder.")
        st.stop()
    try:
        with open(GCP_CREDS_FILE, "r") as f:
            creds_data = json.load(f)
        return creds_data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON from credentials file {GCP_CREDS_FILE}: {e}. Please check its content for valid JSON.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while reading credentials file {GCP_CREDS_FILE}: {e}.")
        st.stop()
    # --- END RESTORED LOGIC ---


# Function to fetch data from Google Sheet
@st.cache_resource(ttl=3600) # Cache the connection and data for an hour (3600 seconds)
def get_google_sheet_data():
    try:
        creds_info = _get_gcp_creds() # Get credentials from the file

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_info, GOOGLE_SHEET_SCOPE
        )
        client = gspread.authorize(creds)

        # Open the sheet and select the worksheet tab
        sheet = client.open(GOOGLE_SHEET_NAME)
        worksheet = sheet.worksheet(GOOGLE_SHEET_TAB_NAME_RESULTS) # Use correct results tab name

        # Get all records as a list of dictionaries
        list_of_dicts = worksheet.get_all_records()

        # Transform data into the desired JSON structure
        sheet_data = {}
        for row in list_of_dicts:
            company_name = row.get("company_name")
            if company_name:
                report_details = {}
                for part_key in ["Part 1: Corporate Governance and Management Credibility Assessment",
                                 "Part 2: Operational Risk and Business Quality Analysis",
                                 "Part 3: Holistic Investment Investigation Report"]:
                    part_content = row.get(part_key, "") 
                    try:
                        if isinstance(part_content, str) and part_content.strip().startswith(("{", "[")):
                            report_details[part_key] = json.loads(part_content)
                        else:
                            report_details[part_key] = part_content if part_content else {}
                    except json.JSONDecodeError as e:
                        report_details[part_key] = part_content
                        #st.warning(f"Warning: Could not parse JSON for '{part_key}' of '{company_name}'. Data might be malformed. Error: {e}. Raw content: {part_content[:100]}...")


                investment_score = row.get("Part 4: investment score", "N/A")
                try:
                    investment_score = int(investment_score)
                except ValueError:
                    pass 

                company_report = {
                    "output": {
                        "company_name": company_name,
                        "report_details": report_details,
                        "Part 4: investment score": investment_score
                    }
                }
                sheet_data[company_name] = [company_report]
        return sheet_data

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Error: Google Sheet '{GOOGLE_SHEET_NAME}' not found. Please check the sheet name and sharing permissions.")
        return {}
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Error: Worksheet tab '{GOOGLE_SHEET_TAB_NAME_RESULTS}' not found in '{GOOGLE_SHEET_NAME}'. Please check the tab name.")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred while accessing Google Sheet for results: {e}. Please ensure:\n"
                 f"- The file '{GCP_CREDS_FILE}' contains valid JSON.\n"
                 f"- The service account has editor access to the Google Sheet '{GOOGLE_SHEET_NAME}'.\n"
                 f"- The sheet name and tab name are exact.")
        return {}

# Function to fetch all stock names from the "stocks" sheet
@st.cache_resource(ttl=3600)
def get_all_stock_names():
    try:
        creds_info = _get_gcp_creds()

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_info, GOOGLE_SHEET_SCOPE
        )
        client = gspread.authorize(creds)

        sheet = client.open(GOOGLE_SHEET_NAME)
        worksheet = sheet.worksheet(GOOGLE_SHEET_TAB_NAME_STOCKS) # Use correct stocks tab name

        # Get all values from the "Stocks_name" column
        # Assuming "Stocks_name" is in the first row (header)
        header = worksheet.row_values(1)
        if "Stocks_name" not in header:
            st.error(f"Error: 'Stocks_name' column not found in '{GOOGLE_SHEET_TAB_NAME_STOCKS}' tab.")
            return []
        
        col_index = header.index("Stocks_name") + 1 # gspread is 1-indexed

        # Get all values from that column, skipping the header
        stock_names = worksheet.col_values(col_index)[1:] 
        return [name.strip() for name in stock_names if name.strip()]

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Error: Google Sheet '{GOOGLE_SHEET_NAME}' not found. Please check the sheet name and sharing permissions.")
        return []
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Error: Worksheet tab '{GOOGLE_SHEET_TAB_NAME_STOCKS}' not found in '{GOOGLE_SHEET_NAME}'. Please check the tab name.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while accessing Google Sheet for stock names: {e}. Please ensure:\n"
                 f"- The file '{GCP_CREDS_FILE}' contains valid JSON.\n"
                 f"- The service account has editor access to the Google Sheet '{GOOGLE_SHEET_NAME}'.\n"
                 f"- The sheet name and tab name are exact.")
        return []


# Function to fetch data from MOCK_DATABASE or Google Sheet
def fetch_data(stock_name: str):
    time.sleep(0.5)

    if stock_name in st.session_state.MOCK_DATABASE:
        return st.session_state.MOCK_DATABASE.get(stock_name)

    google_sheet_data = get_google_sheet_data()

    if stock_name in google_sheet_data:
        st.session_state.MOCK_DATABASE[stock_name] = google_sheet_data[stock_name]
        st.success(f"Successfully fetched '{stock_name}' from Google Sheet.")
        return st.session_state.MOCK_DATABASE.get(stock_name)
    else:
        return None

# --- REPORT DISPLAY FUNCTION ---
def display_report(report_dictionary):
    output_data = report_dictionary.get("output", {})
    st.header(f"Analysis for: {output_data.get('company_name', 'N/A')}")
    st.metric(label="Overall Investment Score", value=output_data.get('Part 4: investment score', 'N/A'))
    report_details = output_data.get("report_details", {})

    part1 = report_details.get("Part 1: Corporate Governance and Management Credibility Assessment", {})
    if part1:
        with st.expander("**Part 1: Corporate Governance and Management Credibility Assessment**", expanded=False):
            if isinstance(part1, dict):
                for k, v in part1.items():
                    st.subheader(k)
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            st.markdown(f"**{sub_k}**")
                            if isinstance(sub_v, dict):
                                for deep_k, deep_v in sub_v.items():
                                    st.write(f"- **{deep_k}:** {deep_v}")
                            else:
                                st.write(sub_v)
                    else:
                        st.write(v)
            else:
                st.write(part1)


    part2 = report_details.get("Part 2: Operational Risk and Business Quality Analysis", {})
    if part2:
        with st.expander("**Part 2: Operational Risk & Business Quality**", expanded=False):
            st.subheader("Summary Table")
            summary_table = part2.get("summary_table")
            if isinstance(summary_table, list) and all(isinstance(i, dict) for i in summary_table):
                st.dataframe(pd.DataFrame(summary_table), use_container_width=True, hide_index=True)
            elif summary_table:
                st.write("Summary table data is not in the expected tabular format:")
                st.write(summary_table)
            else:
                st.write("No summary table data available or it is empty.")


            st.subheader("Overall Risk Assessment")
            st.write(part2.get("Overall Risk Assessment", "N/A"))

    part3 = report_details.get("Part 3: Holistic Investment Investigation Report", {})
    if part3:
        with st.expander("**Part 3: Holistic Investment Investigation**", expanded=False):
            if isinstance(part3, dict):
                for k, v in part3.items():
                    st.subheader(k)
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            st.markdown(f"**{sub_k}**")
                            if isinstance(sub_v, dict):
                                if sub_k == "IRR Projections" and all(isinstance(val, str) for val in sub_v.values()):
                                    st.table(pd.DataFrame.from_dict(sub_v, orient='index', columns=["Scenario"]).rename_axis("Investment Style"))
                                else:
                                    st.write(sub_v)
                            else:
                                st.markdown(sub_v)
                    else:
                        st.write(v)
            else:
                st.write(part3)


# --- UI STYLES AND HEADER ---
logo_base64 = get_image_as_base64(Path("assets/logo.png"))

st.markdown(f"""
    <style>
        .stApp {{
            background-color: #0a192f;
            color: #e6f1ff;
        }}
        .header-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 0;
            gap: 20px;
        }}
        .header-container img {{
            width: 150px;
            height: auto;
        }}
        .header-container .title {{
            font-size: 6rem;
            font-weight: 700;
            color: #e6f1ff;
            margin: 0;
        }}

        div[data-testid="stTextInput"] > div > input,
        div[data-testid="stSelectbox"] > div > button,
        textarea[data-testid="stTextArea"] {{
            border-radius: 8px !important;
            border: 1px solid #c8a2c8;
            background-color: #1a2a42;
            color: #e6f1ff;
        }}

        div[data-testid="stButton"] > button {{
            background-color: #c8a2c8;
            color: #0a192f;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        }}
        div[data-testid="stButton"] > button:hover {{
            background-color: #b19cd9;
            color: #0a192f;
        }}

        div[data-testid="stTabs"] {{
            background-color: transparent;
        }}
        div[data-testid="stTabs"] button {{
            background-color: #c8a2c8;
            color: #0a192f;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 20px;
            margin: 0 5px;
            border: none;
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            background-color: #00a896;
            color: white;
            border-radius: 8px;
        }}

        .stExpander > div > div > div > button > div > svg {{
            border-radius: 0 !important;
            background-color: transparent !important;
        }}
        .stExpander > div > div > div > button {{
            border-radius: 0 !important;
            background-color: transparent !important;
        }}

        h1, h2, h3 {{ color: #e6f1ff; }}
        div[data-testid="stExpander"] div[role="button"] {{
            border-radius: 8px;
            background-color: #1a2a42;
            border: 1px solid #2a415a;
        }}
        /* Style for the "pill" like selected stock display */
        .st-emotion-cache-p5mrg7.eczjsme4 {{ /* This class might change with Streamlit updates, inspect element for exact class */
            background-color: #1a2a42;
            padding: 8px 12px;
            border-radius: 8px;
            color: #e6f1ff;
            margin-right: 5px;
            display: inline-block;
            border: 1px solid #2a415a; /* Added border for better pill appearance */
        }}
        /* Style for the 'X' button inside the pill */
        .st-emotion-cache-19p080p.e1f1d6gn0 > button {{ /* Adjust based on inspection if needed */
            background-color: transparent !important;
            color: #e6f1ff !important;
            border: none !important;
            padding: 0 5px !important;
            margin-left: 10px !important;
            font-weight: bold !important;
        }}
        .st-emotion-cache-19p080p.e1f1d6gn0 > button:hover {{
            color: #ff4b4b !important; /* Red color on hover for delete */
            background-color: transparent !important;
        }}

    </style>
    <div class="header-container">
        <img src="data:image/png;base64,{logo_base64}">
        <p class="title">Utopiaequity</p>
    </div>
""", unsafe_allow_html=True)


# --- Initialize session state for selected stocks if not already present ---
if "selected_stocks_for_analysis" not in st.session_state:
    st.session_state.selected_stocks_for_analysis = []
if "current_input_stock" not in st.session_state:
    st.session_state.current_input_stock = ""
if "last_selected_suggestion" not in st.session_state:
    st.session_state.last_selected_suggestion = ""
if "reports_to_display_in_tab1" not in st.session_state: # New state to hold reports for tab1
    st.session_state.reports_to_display_in_tab1 = []


# --- TABS FOR NAVIGATION ---
tab1, tab2 = st.tabs(["Analyze Specific Stocks", "Browse All Reports"])

# This helper function will be used by the selectbox's on_change
def _add_selected_stock_from_dropdown(selected_value):
    if selected_value and selected_value not in st.session_state.selected_stocks_for_analysis:
        st.session_state.selected_stocks_for_analysis.append(selected_value)
        st.session_state.current_input_stock = "" # Clear text input
        st.session_state.last_selected_suggestion = selected_value # Store for persistence
        # No clearing of reports_to_display_in_tab1 here
        # st.rerun() # This rerun is now handled by the main flow of the selectbox below

# This helper function clears all related states for tab1
def _clear_all_tab1_selections():
    st.session_state.selected_stocks_for_analysis = []
    st.session_state.current_input_stock = ""
    st.session_state.last_selected_suggestion = ""
    st.session_state.reports_to_display_in_tab1 = [] # Clear reports here
    st.rerun() # Force a rerun to clear the UI


with tab1:
    st.header("Analyze Stocks by Name")

    # Fetch all available stock names for autocomplete
    all_available_stock_names = get_all_stock_names()

    # Input for typing stock names. on_change is key for dynamic updates.
    user_input = st.text_input(
        "Type a stock name to add:",
        value=st.session_state.current_input_stock,
        key="autocomplete_input",
        placeholder="e.g., Natco Pharma Ltd",
        on_change=lambda: st.session_state.update(current_input_stock=st.session_state.autocomplete_input, last_selected_suggestion="") # Update input, clear last suggestion on text change
    )

    # Filter suggestions based on current user input
    suggestions = []
    if user_input:
        suggestions = [
            name for name in all_available_stock_names
            if user_input.lower() in name.lower() and name not in st.session_state.selected_stocks_for_analysis
        ]
        suggestions.sort() # Keep suggestions sorted

    # Display suggestions in a selectbox. It will appear/disappear dynamically.
    if suggestions:
        # Determine the initial index for the selectbox to prevent unwanted auto-selection
        initial_index = 0
        if st.session_state.last_selected_suggestion in suggestions:
            initial_index = suggestions.index(st.session_state.last_selected_suggestion) + 1 # +1 for the "" empty option

        selected_suggestion_from_box = st.selectbox(
            "Did you mean?",
            options=[""] + suggestions, # Add an empty option at the top
            index=initial_index,
            key="suggestion_selectbox",
            help="Select a suggestion from the list.",
            on_change=lambda: _add_selected_stock_from_dropdown(st.session_state.suggestion_selectbox)
        )
        # This explicit rerun is necessary because on_change in selectbox doesn't always trigger it consistently
        # if the value itself (the actual object) remains the same after a programmatic update.
        if selected_suggestion_from_box and selected_suggestion_from_box != st.session_state.last_selected_suggestion:
             st.rerun()


    # Display currently selected stocks as "pills" or tags
    if st.session_state.selected_stocks_for_analysis:
        st.write("Stocks to analyze:")
        # Use columns for a neat layout of pills and remove buttons
        selected_stocks_copy = list(st.session_state.selected_stocks_for_analysis) # Iterate over a copy
        for stock_item in selected_stocks_copy:
            col1, col2 = st.columns([0.8, 0.2]) # Adjust column width ratio as needed
            with col1:
                st.markdown(f'<span style="background-color:#1a2a42; padding: 8px 12px; border-radius: 8px; color: #e6f1ff; border: 1px solid #2a415a; display: inline-block;">{stock_item}</span>', unsafe_allow_html=True)
            with col2:
                # Use a unique key for each remove button
                if st.button("Remove", key=f"remove_{stock_item}"):
                    st.session_state.selected_stocks_for_analysis.remove(stock_item)
                    st.session_state.last_selected_suggestion = "" # Reset suggestion state
                    st.session_state.reports_to_display_in_tab1 = [] # Clear reports only when removing a stock
                    st.rerun() # Rerun to update the list and clear reports

    # Manually add stock from text input if it's not empty and not already added
    if user_input and user_input not in st.session_state.selected_stocks_for_analysis:
        if st.button(f"Add '{user_input}' to list"):
            st.session_state.selected_stocks_for_analysis.append(user_input)
            st.session_state.current_input_stock = "" # Clear input after adding
            st.session_state.last_selected_suggestion = "" # Reset suggestion state
            # No clearing of reports_to_display_in_tab1 here
            st.rerun()

    st.markdown("---") # Separator

    # Row for action buttons: Generate and Clear
    col_generate, col_clear = st.columns([0.5, 0.5])

    with col_generate:
        if st.button("Generate Reports for Selected Stocks"):
            if st.session_state.selected_stocks_for_analysis:
                # Only set the reports_to_display_in_tab1 and let them render
                # This will ensure the reports stay until cleared or regenerated
                st.session_state.reports_to_display_in_tab1 = list(st.session_state.selected_stocks_for_analysis)
                # No st.rerun() here! This is crucial for the reports to show immediately.
            else:
                st.warning("Please add at least one stock to analyze before generating reports.")

    with col_clear:
        # Show clear button only if there's something to clear
        if st.session_state.selected_stocks_for_analysis or st.session_state.current_input_stock or st.session_state.reports_to_display_in_tab1:
            st.button("Clear All Selections & Reports", on_click=_clear_all_tab1_selections)


    # Display reports only if reports_to_display_in_tab1 is populated
    if st.session_state.reports_to_display_in_tab1:
        st.subheader("Generated Reports:")
        for stock_name in st.session_state.reports_to_display_in_tab1:
            with st.spinner(f"Fetching data for {stock_name}..."):
                report_data_list = fetch_data(stock_name)
            if report_data_list:
                display_report(report_data_list[0])
            else:
                st.error(f"No data found for '{stock_name}'. Please ensure the name is correct and it exists in the Google Sheet.")
            st.divider()


with tab2:
    st.header("Browse All Available Reports")

    # Ensure mock database is populated with Google Sheet data for Browse
    # This ensures that Tab 2 always pulls the latest data
    google_sheet_data_all = get_google_sheet_data()
    st.session_state.MOCK_DATABASE.update(google_sheet_data_all)

    all_company_names_available = list(st.session_state.MOCK_DATABASE.keys())

    if not all_company_names_available:
        st.warning("No reports available to browse. Please analyze a stock first or check Google Sheet connection.")
    else:
        all_company_names_available.sort()

        selected_company = st.selectbox(
            "Select a company to view its report:",
            options=all_company_names_available,
            index=0 if all_company_names_available else None,
            label_visibility="collapsed"
        )
        if selected_company:
            with st.spinner(f"Loading report for {selected_company}..."):
                report_data_list = fetch_data(selected_company)
            if report_data_list:
                display_report(report_data_list[0])
            else:
                st.warning(f"Could not load report for {selected_company}.")
