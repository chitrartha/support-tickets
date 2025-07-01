import streamlit as st
import pandas as pd
import json
import time
from PIL import Image
import base64
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(page_title="Utopiaequity", page_icon="assets/logo.png", layout="wide")

# --- Function to encode image to base64 for embedding in CSS ---
def get_image_as_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- MOCK DATABASE (now with your provided JSON data) ---
MOCK_DATABASE = {
  "Natco Pharma Ltd": [
    {
      "output": {
        "company_name": "Natco Pharma Ltd",
        "report_details": {
          "Part 1: Corporate Governance and Management Credibility Assessment": {
            "1. Future Forecast vs. Actuals (Past 5 Years)": "Based on available information, assessing Natco Pharma's forecasts against actual performance over the past five years reveals a mixed track record. While specific conference call transcripts and detailed financial data would be needed for a precise analysis, general trends suggest that the company has faced challenges in consistently meeting its ambitious growth targets. Factors such as regulatory hurdles in key markets (like the US), pricing pressures in the generic drug market, and delays in product approvals have impacted their performance. The management's communication has generally been transparent regarding these challenges, but the predictability of their forecasts could be improved.",
            "2. Management Guidance Analysis": {
              "Current Guidance": "Natco Pharma's current guidance typically includes projections for revenue growth, EBITDA margins, and specific CapEx plans related to new facilities or product development. While exact figures vary year to year, recent guidance has emphasized expansion in key markets (US, India, and emerging markets), investment in complex generics and specialty products, and maintaining a healthy balance sheet. More granular figures require up-to-date earnings calls and investor presentations.",
              "Historical Comparison": {
                "Revenue": "In previous years (e.g., 3-5 years ago), Natco Pharma's revenue guidance often targeted double-digit percentage growth, driven by new product launches and market penetration. In some years, they met or exceeded these targets, particularly when they successfully launched key products. However, there were instances where revenue growth fell short due to unexpected regulatory delays, increased competition, or market-specific challenges. Specific figures will require a review of past annual reports and investor presentations.",
                "Bottom Line": "Similar to revenue, Natco Pharma aimed for significant bottom-line growth (EBITDA/PAT) in past guidance. Success in achieving these targets depended heavily on their ability to control costs, manage pricing pressures, and efficiently scale up production. There were instances where they exceeded expectations due to favorable product mixes or cost optimization initiatives, but also instances where they fell short due to increased operating expenses or pricing pressures. Specific figures will require a review of past annual reports and investor presentations.",
                "CapEx/Strategic Initiatives": "Natco Pharma has consistently announced CapEx plans focused on expanding manufacturing capacity, upgrading R&D facilities, and investing in new technologies. The execution of these plans has generally been consistent with their stated intentions, although there have been occasional delays due to unforeseen circumstances or regulatory approvals. For instance, announcements regarding capacity expansion for specific product lines or investments in biosimilar development have largely materialized as planned."
              },
              "Overall Credibility Assessment": "Overall, Natco Pharma's management has demonstrated reasonable credibility in forecasting, although their projections can be susceptible to external factors such as regulatory changes and market dynamics. They tend to provide relatively transparent guidance, acknowledging both potential opportunities and challenges. However, investors should exercise caution and consider the inherent uncertainties in the pharmaceutical industry when evaluating their forecasts."
            }
          },
          "Part 2: Operational Risk and Business Quality Analysis": {
            "summary_table": [
              {"Factor": "High Capex", "Assessment": "NO", "Data": "Most recent annual Capex is around 150-200 Cr INR", "Justification": "Capex is relatively low as a percentage of revenue compared to other Pharma companies, indicating a lower capital intensity."},
              {"Factor": "High R&D", "Assessment": "YES", "Data": "Most recent annual R&D expense is around 10-12% of revenues.", "Justification": "R&D expense is significant, reflecting the need for continuous innovation in the pharmaceutical industry. Relatively higher than industry average indicates higher risk and reward."},
              {"Factor": "Risky Capex", "Assessment": "NO", "Data": "N/A", "Justification": "Capex is primarily directed towards expanding existing facilities and upgrading equipment, with a focus on known product lines. Although there is risk, the company isn't known for taking extreme capital expenditure risk."},
              {"Factor": "Risky R&D", "Assessment": "YES", "Data": "N/A", "Justification": "R&D efforts are focused on complex generics and specialty products, which carry higher risks of failure but also offer potentially higher rewards if successful."},
              {"Factor": "Dual Class Shares", "Assessment": "NO", "Data": "N/A", "Justification": "Natco Pharma does not have a dual-class share structure."},
              {"Factor": "Wasteful FCF", "Assessment": "NO", "Data": "FCF positive", "Justification": "FCF is typically reinvested into R&D, capacity expansion, and debt reduction, indicating efficient capital allocation. Dividends are also paid."},
              {"Factor": "Bad Industry", "Assessment": "NO", "Data": "N/A", "Justification": "The pharmaceutical industry offers growth opportunities, particularly in generics and specialty products, but faces regulatory and pricing pressures. Overall good prospects."},
              {"Factor": "Acquisition Growth", "Assessment": "NO", "Data": "N/A", "Justification": "Natco Pharma's growth strategy primarily relies on organic growth through product development and market expansion, rather than aggressive acquisitions. This lowers risk."},
              {"Factor": "High Debt", "Assessment": "NO", "Data": "Debt to equity ratio below 0.5", "Justification": "Debt levels are manageable, with a healthy debt-to-equity ratio compared to industry peers."},
              {"Factor": "Intense Competition", "Assessment": "YES", "Data": "Generic drug market is competitive", "Justification": "The generic pharmaceutical market is highly competitive, with numerous players vying for market share. Pricing pressures are always present."},
              {"Factor": "High SBC (Stock-Based Compensation)", "Assessment": "NO", "Data": "SBC is less than 3% of revenue.", "Justification": "Stock-based compensation is relatively low compared to revenue and industry standards."}
            ],
            "Overall Risk Assessment": "Natco Pharma presents a moderate risk profile. Key risks include R&D success and competition, while financial health is maintained with moderate debt and good FCF management. Company’s moderate capital expenditure is used efficiently. Although R&D is risky, is necessary to grow business. The industry presents opportunities, but also competitive pressure."
          },
          "Part 3: Holistic Investment Investigation Report": {
            "1. Overall Investigation (Li Lu Style)": "Natco Pharma is a vertically integrated pharmaceutical company focusing on niche therapeutic areas and complex generics. They have demonstrated a strong track record of innovation and successful product launches, particularly in oncology and specialty products. The company's key strengths include its R&D capabilities, manufacturing efficiency, and strong relationships with key stakeholders. Challenges include regulatory hurdles, pricing pressures, and competition in the generic drug market. Recent FDA inspections have increased concern about quality control.",
            "2. Business Model and Moat (Nick Sleep Style)": "Natco Pharma's business model centers around developing, manufacturing, and marketing niche pharmaceutical products, including generics and specialty drugs. Its competitive advantages (moats) include its strong R&D capabilities, which enable it to develop complex generics and differentiated products. Furthermore, its manufacturing efficiency and vertically integrated operations allow it to maintain cost competitiveness. These moats are reasonably sustainable, providing a buffer against competition, particularly in niche therapeutic areas. However, pricing pressures in the generic drug market can erode profitability.",
            "3. Risks and Quality of Business (Charlie Munger Style)": "Key risks associated with Natco Pharma's business include regulatory risks (e.g., FDA approvals, inspections), pricing pressures, competition, and product liability risks. The overall quality of the business is considered good, given its strong R&D capabilities, efficient operations, and experienced management team. However, investors should be aware of the inherent uncertainties in the pharmaceutical industry and potential for adverse events. Management integrity is good with a long track record.",
            "4. Owner's Earnings and Margin of Safety (Warren Buffett Style)": {
              "Owner's Earnings and Margin of Safety Analysis": "Estimating Natco Pharma's \"owner's earnings\" requires adjusting net income for non-cash expenses (e.g., depreciation, amortization) and CapEx. Intrinsic value can then be determined using a discounted cash flow (DCF) analysis, considering future growth rates and discount rates. The margin of safety depends on the difference between the intrinsic value and the current market price. Due to the uncertainties inherent to forecasting the company's earnings accurately, a conservative estimate is needed.",
              "IRR Projections": {"Li Lu": "Bear: 5%, Base: 10%, Bull: 15%", "Nick Sleep": "Bear: 7%, Base: 12%, Bull: 18%", "Charlie Munger": "Bear: 3%, Base: 8%, Bull: 13%", "Warren Buffett": "Bear: 4%, Base: 9%, Bull: 14%"},
              "Fat Pitch Analysis": "A \"fat pitch\" investment opportunity for Natco Pharma would occur if the company's stock price significantly declined due to temporary setbacks (e.g., regulatory delays, market corrections) while its long-term fundamentals remained strong. This would create an opportunity to buy a high-quality business at a discounted valuation, providing a substantial margin of safety."
            },
            "5. 3-10 Year Hold Scenarios": "Bear Case (20% probability): Regulatory setbacks, increased competition, and pricing pressures lead to declining revenue and profit margins. Average revenue declines 5% annually. Base Case (60% probability): Natco Pharma maintains its market position, introduces new products, and achieves moderate growth. Average revenue grows 8% annually. Bull Case (20% probability): Successful product launches, expansion into new markets, and favorable regulatory environment drive significant growth. Average revenue grows 15% annually. All scenarios assume continued investment in R&D."
          }
        },
        "Part 4: investment score": 69
      }
    }
  ],
  "IZMO Ltd": [
    {
      "output": {
        "company_name": "IZMO Ltd",
        "report_details": {
          "Part 1: Corporate Governance and Management Credibility Assessment": {
            "1. Future Forecast vs. Actuals (Past 5 Years)": "Analysis of past forecasts vs. actuals for IZMO Ltd requires detailed financial data, including revenue projections and actual results. Without this data, a thorough assessment cannot be provided.",
            "2. Management Guidance Analysis": {
              "Current Guidance": "Detailed management's current guidance for IZMO Ltd is needed, including revenue growth, CapEx plans, and strategic initiatives. Specific figures and timelines are required for an accurate analysis.",
              "Historical Comparison": {"Revenue": "Comparison of past revenue guidance with actuals for IZMO Ltd requires historical data on management's projections and reported revenue. This information is necessary to assess accuracy.", "Bottom Line": "Comparison of past bottom-line guidance with actuals for IZMO Ltd requires historical data on management's profit projections and reported earnings. Without this data, an evaluation is impossible.", "CapEx/Strategic Initiatives": "Comparison of past CapEx/strategic initiative announcements with actual execution for IZMO Ltd requires tracking management's plans and comparing them to actual investments and results. This data is currently unavailable."},
              "Overall Credibility Assessment": "Assessment of management's credibility in forecasting for IZMO Ltd requires a track record of guidance versus actual results. Without sufficient historical data, an objective assessment is not feasible."
            }
          },
          "Part 2: Operational Risk and Business Quality Analysis": {
            "summary_table": [
              {"Factor": "High Capex", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd's capital expenditure is high relative to its peers or historical performance without financial data."},
              {"Factor": "High R&D", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd's research and development spending is high relative to its peers or historical performance without financial data."},
              {"Factor": "Risky Capex", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Cannot determine whether IZMO Ltd has undertaken risky capital expenditure projects without detailed financial information."},
              {"Factor": "Risky R&D", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Cannot determine whether IZMO Ltd has undertaken risky R&D projects without detailed financial information."},
              {"Factor": "Dual Class Shares", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to assess the share structure of IZMO Ltd without detailed information on its corporate governance."},
              {"Factor": "Wasteful FCF", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd is wasting free cash flow without detailed financial analysis."},
              {"Factor": "Bad Industry", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine the long-term prospects of IZMO Ltd's industry without detailed industry analysis."},
              {"Factor": "Acquisition Growth", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to assess whether IZMO Ltd relies on acquisitions for growth without analyzing its acquisition history."},
              {"Factor": "High Debt", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd has a high debt level without a review of its financial statements."},
              {"Factor": "Intense Competition", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to assess the competitive landscape for IZMO Ltd without market analysis."},
              {"Factor": "High SBC (Stock-Based Compensation)", "Assessment": "N/A", "Data": "Insufficient data", "Justification": "Unable to determine if IZMO Ltd's SBC is high without analyzing its financial statements."}
            ],
            "Overall Risk Assessment": "Based on the lack of available data, a comprehensive risk assessment for IZMO Ltd cannot be performed."
          },
          "Part 3: Holistic Investment Investigation Report": {
            "1. Overall Investigation (Li Lu Style)": "A comprehensive investigation into IZMO Ltd's strengths, weaknesses, and key business drivers requires detailed financial and operational data. Without sufficient information, an accurate analysis is not possible.",
            "2. Business Model and Moat (Nick Sleep Style)": "Analyzing IZMO Ltd's business model, competitive advantages, and their sustainability requires in-depth knowledge of the company's operations and industry dynamics. More data is needed for this assessment.",
            "3. Risks and Quality of Business (Charlie Munger Style)": "Assessing the risks and quality of IZMO Ltd's business requires evaluating its financial stability, competitive positioning, and management's capital allocation decisions. This analysis requires access to additional data.",
            "4. Owner's Earnings and Margin of Safety (Warren Buffett Style)": {
              "Owner's Earnings and Margin of Safety Analysis": "Calculating IZMO Ltd's owner's earnings and determining a margin of safety requires detailed financial projections and a valuation analysis, which cannot be completed without sufficient data.",
              "IRR Projections": {"Li Lu": "Unable to project IRR for IZMO Ltd without sufficient data.", "Nick Sleep": "Unable to project IRR for IZMO Ltd without sufficient data.", "Charlie Munger": "Unable to project IRR for IZMO Ltd without sufficient data.", "Warren Buffett": "Unable to project IRR for IZMO Ltd without sufficient data."},
              "Fat Pitch Analysis": "Identifying conditions for a 'fat pitch' investment in IZMO Ltd requires a thorough understanding of its intrinsic value and potential future growth. Further data is needed for this analysis."
            },
            "5. 3-10 Year Hold Scenarios": "Developing bear, base, and bull case scenarios for holding IZMO Ltd for 3-10 years requires financial modeling and projections based on assumptions about its future performance. These projections cannot be made without additional information."
          }
        },
        "Part 4: investment score": 25
      }
    }
  ]
}

def fetch_data(stock_name: str):
    time.sleep(0.5)
    return MOCK_DATABASE.get(stock_name)

# --- REPORT DISPLAY FUNCTION ---
def display_report(report_dictionary):
    output_data = report_dictionary.get("output", {})
    st.header(f"Analysis for: {output_data.get('company_name', 'N/A')}")
    st.metric(label="Overall Investment Score", value=output_data.get('Part 4: investment score', 'N/A'))
    report_details = output_data.get("report_details", {})

    part1 = report_details.get("Part 1: Corporate Governance and Management Credibility Assessment", {})
    if part1:
        with st.expander("**Part 1: Corporate Governance and Management Credibility Assessment**", expanded=False):
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

    part2 = report_details.get("Part 2: Operational Risk and Business Quality Analysis", {})
    if part2:
        with st.expander("**Part 2: Operational Risk & Business Quality**", expanded=False):
            st.subheader("Summary Table")
            summary_table = part2.get("summary_table")
            if summary_table:
                st.dataframe(pd.DataFrame(summary_table), use_container_width=True, hide_index=True)
            st.subheader("Overall Risk Assessment")
            st.write(part2.get("Overall Risk Assessment", "N/A"))

    part3 = report_details.get("Part 3: Holistic Investment Investigation Report", {})
    if part3:
        with st.expander("**Part 3: Holistic Investment Investigation**", expanded=False):
            for k, v in part3.items():
                st.subheader(k)
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        st.markdown(f"**{sub_k}**")
                        if isinstance(sub_v, dict):
                            st.table(pd.DataFrame.from_dict(sub_v, orient='index', columns=["Scenario"]).rename_axis("Investment Style"))
                        else:
                            st.markdown(sub_v)
                else:
                    st.write(v)


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
            font-size: 6rem; /* 3x larger than h2 */
            font-weight: 700;
            color: #e6f1ff;
            margin: 0;
        }}
        /* General button styling - making them rectangular */
        div[data-testid="stButton"] > button {{
            background-color: #c8a2c8; /* Light Purple */
            color: #0a192f; /* Dark text */
            font-weight: bold;
            border: none;
            border-radius: 8px; /* Rectangular with slight rounding */
            padding: 10px 20px;
        }}
        div[data-testid="stButton"] > button:hover {{
            background-color: #b19cd9;
            color: #0a192f;
        }}
        
        /* Streamlit tabs styling - making them rectangular */
        div[data-testid="stTabs"] {{
            background-color: transparent;
        }}
        div[data-testid="stTabs"] button {{
            background-color: #c8a2c8; /* Light Purple for inactive */
            color: #0a192f;
            font-weight: bold;
            border-radius: 8px; /* Rectangular with slight rounding */
            padding: 10px 20px;
            margin: 0 5px; /* Space between tabs */
            border: none; /* Remove default button border */
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            background-color: #00a896; /* Vibrant Green for active */
            color: white;
            border-radius: 8px; /* Rectangular for active tab button */
        }}

        /* Style for the expander chevron icon to ensure it's not squared */
        /* This targets the chevron SVG within the expander header */
        .stExpander > div > div > div > button > div > svg {{
            border-radius: 0 !important; /* Ensure the SVG background is not rounded */
            background-color: transparent !important; /* Ensure background is transparent */
        }}
        /* Also ensure the button housing the chevron is not rounded unexpectedly */
        .stExpander > div > div > div > button {{
            border-radius: 0 !important;
            background-color: transparent !important;
        }}


        h1, h2, h3 {{ color: #e6f1ff; }}
    </style>
    <div class="header-container">
        <img src="data:image/png;base64,{logo_base64}">
        <p class="title">Utopiaequity</p>
    </div>
""", unsafe_allow_html=True)

# --- TABS FOR NAVIGATION ---
tab1, tab2 = st.tabs(["Analyze Specific Stocks", "Browse All Reports"])

with tab1:
    st.header("Analyze Stocks by Name")
    stock_names_input = st.text_area(
        "Enter one or more stock names separated by commas or newlines:",
        placeholder="e.g.\nNatco Pharma Ltd,\nIZMO Ltd",
        height=100,
        key="text_area_input",
        label_visibility="collapsed"
    )
    if st.button("Generate Reports"):
        if stock_names_input:
            stock_list = [name.strip() for name in stock_names_input.replace(',', '\n').split('\n') if name.strip()]
            if stock_list:
                st.info(f"Found {len(stock_list)} stock(s) to process.")
                for stock_name in stock_list:
                    with st.spinner(f"Fetching data for {stock_name}..."):
                        report_data_list = fetch_data(stock_name)
                    if report_data_list:
                        display_report(report_data_list[0])
                    else:
                        st.error(f"No data found for '{stock_name}'.")
                    st.divider()
            else:
                st.warning("Please enter at least one valid stock name.")
        else:
            st.warning("The input box is empty.")

with tab2:
    st.header("Browse All Available Reports")
    all_company_names = list(MOCK_DATABASE.keys())
    selected_company = st.selectbox(
        "Select a company to view its report:",
        options=all_company_names,
        index=0,
        label_visibility="collapsed"
    )
    if selected_company:
        with st.spinner(f"Loading report for {selected_company}..."):
            report_data_list = fetch_data(selected_company)
        if report_data_list:
            display_report(report_data_list[0])