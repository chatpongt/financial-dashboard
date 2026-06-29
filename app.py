import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ตั้งค่าหน้า Dashboard
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- CSS เพื่อความสวยงาม ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def _read_raw(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(uploaded_file, header=None)
    return pd.read_csv(uploaded_file, header=None)


# --- ฟังก์ชันทำความสะอาดและโหลดข้อมูล ---
def clean_and_load(uploaded_file):
    if uploaded_file is not None:
        try:
            df_raw = _read_raw(uploaded_file)
            
            header_row_index = -1
            for i, row in df_raw.iterrows():
                # ค้นหา row ที่เป็น header ของตาราง (มีวันที่)
                if row.astype(str).str.contains("Period End Date").any():
                    header_row_index = i
                    break
            
            if header_row_index != -1:
                name = uploaded_file.name.lower()
                if name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file, header=header_row_index + 1)
                else:
                    df = pd.read_csv(uploaded_file, header=header_row_index + 1)
                
                # เปลี่ยนชื่อคอลัมน์แรกเป็น 'Item'
                df.columns.values[0] = 'Item'
                df = df.dropna(subset=['Item']) # ลบแถวที่ไม่มีชื่อรายการ
                
                # Set Index เป็นชื่อรายการเพื่อการค้นหาง่ายๆ
                df.set_index('Item', inplace=True)
                
                # ทำความสะอาดข้อมูลตัวเลข (ลบ , และเปลี่ยนเป็น float)
                # เลือกเฉพาะคอลัมน์ที่เป็นวันที่ (สมมติว่าเป็นคอลัมน์ที่ 1 ถึงสุดท้าย)
                cols = df.columns
                for col in cols:
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('%', '').str.replace('NM', '0').str.replace('-', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                return df
            else:
                st.error(f"ไม่พบโครงสร้างตารางที่ถูกต้องในไฟล์ {uploaded_file.name}")
                return None
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
            return None
    return None

# --- ส่วน Header ของ Dashboard ---
company_name = st.sidebar.text_input("ชื่อบริษัท / Ticker", value="Neo Corporate PCL")
st.title("📊 Financial Performance Dashboard")
st.markdown(f"ระบบติดตามผลประกอบการ: **{company_name}**")

# --- ส่วน Upload ไฟล์ (Sidebar) ---
with st.sidebar:
    st.header("📂 Data Input Zone")
    st.info("อัปโหลด CSV หรือ XLSX (format LSEG/Excel export)")
    
    file_income = st.file_uploader("1. Income Statement (งบกำไรขาดทุน)", type=['csv', 'xlsx', 'xls'])
    file_balance = st.file_uploader("2. Balance Sheet (งบดุล)", type=['csv', 'xlsx', 'xls'])
    file_cashflow = st.file_uploader("3. Cash Flow (งบกระแสเงินสด)", type=['csv', 'xlsx', 'xls'])

# --- Main Logic ---
if file_income and file_balance and file_cashflow:
    
    # โหลดข้อมูล
    df_is = clean_and_load(file_income)
    df_bs = clean_and_load(file_balance)
    df_cf = clean_and_load(file_cashflow)

    if df_is is not None and df_bs is not None and df_cf is not None:
        
        # เตรียมข้อมูลสำหรับ Plot (Transpose ให้ปีเป็นแกน X)
        # เราจะใช้ข้อมูล 6 ปีล่าสุดตามไฟล์
        years = df_is.columns.tolist() # รายชื่อปี
        
        # ดึงข้อมูลสำคัญ (Key Metrics Extraction)
        try:
            # Income Statement Items
            revenue = df_is.loc['Revenue']
            net_income = df_is.loc['Net Income to Company']
            gross_margin = df_is.loc['Gross Profit Margin']
            
            # Balance Sheet Items
            total_assets = df_bs.loc['Total Assets']
            total_liab = df_bs.loc['Total Liabilities']
            equity = df_bs.loc['Total Equity']
            cash = df_bs.loc['Cash And Equivalents']
            
            # Cash Flow Items
            cfo = df_cf.loc['Cash from Operations']
            capex = df_cf.loc['Capital Expenditures']
            
            # คำนวณ Ratio เพิ่มเติม
            fcf = cfo + capex # Free Cash Flow (Capex is usually negative)
            roe = (net_income / equity) * 100
            de_ratio = total_liab / equity

            # ข้อมูลปีล่าสุด
            latest_year = years[-1]
            prev_year = years[-2]

            # --- ส่วนแสดงผล KPI (Top Cards) ---
            st.subheader(f"📌 Key Highlights ({latest_year})")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("รายได้รวม (Revenue)", 
                          f"{revenue[latest_year]:,.0f} MB", 
                          f"{(revenue[latest_year] - revenue[prev_year]):,.0f} MB")
            with col2:
                st.metric("กำไรสุทธิ (Net Profit)", 
                          f"{net_income[latest_year]:,.0f} MB", 
                          f"{((net_income[latest_year] - net_income[prev_year])/net_income[prev_year]*100):.1f} %")
            with col3:
                st.metric("อัตรากำไรขั้นต้น (GPM)", 
                          f"{gross_margin[latest_year]:.1f}%", 
                          f"{(gross_margin[latest_year] - gross_margin[prev_year]):.1f}%")
            with col4:
                st.metric("กระแสเงินสดดำเนินงาน (CFO)", 
                          f"{cfo[latest_year]:,.0f} MB", 
                          f"{(cfo[latest_year] - cfo[prev_year]):,.0f} MB")

            # --- Tabs สำหรับการวิเคราะห์เชิงลึก ---
            tab1, tab2, tab3 = st.tabs(["📈 Profitability & Growth", "💰 Financial Health", "🔄 Cash Flow Analysis"])

            with tab1:
                st.subheader("แนวโน้มการเติบโตและความสามารถในการทำกำไร")
                
                # กราฟ 1: Revenue vs Net Income
                fig_rev = go.Figure()
                fig_rev.add_trace(go.Bar(x=years, y=revenue, name='Revenue', marker_color='#1f77b4'))
                fig_rev.add_trace(go.Scatter(x=years, y=net_income, name='Net Income', mode='lines+markers', yaxis='y2', line=dict(color='#ff7f0e', width=3)))
                
                fig_rev.update_layout(
                    title='Revenue vs Net Income Trend',
                    yaxis=dict(title='Amount (MB)'),
                    yaxis2=dict(title='Net Income (MB)', overlaying='y', side='right'),
                    legend=dict(x=0, y=1.1, orientation='h'),
                    hovermode="x unified"
                )
                st.plotly_chart(fig_rev, use_container_width=True)

                # กราฟ 2: Margins Analysis
                df_margins = pd.DataFrame({
                    'Year': years,
                    'Gross Margin': gross_margin.values,
                    'Net Profit Margin': (net_income.values / revenue.values) * 100
                })
                
                fig_margin = px.line(df_margins, x='Year', y=['Gross Margin', 'Net Profit Margin'], 
                                     title='Margin Trends (%)', markers=True)
                st.plotly_chart(fig_margin, use_container_width=True)

            with tab2:
                st.subheader("ความแข็งแกร่งทางการเงิน (Balance Sheet)")
                
                col_b1, col_b2 = st.columns(2)
                
                with col_b1:
                    # กราฟโครงสร้างสินทรัพย์
                    fig_asset = go.Figure(data=[
                        go.Bar(name='Liabilities', x=years, y=total_liab, marker_color='#d62728'),
                        go.Bar(name='Equity', x=years, y=equity, marker_color='#2ca02c')
                    ])
                    fig_asset.update_layout(barmode='stack', title='Capital Structure (Liabilities vs Equity)')
                    st.plotly_chart(fig_asset, use_container_width=True)
                
                with col_b2:
                    # กราฟ D/E Ratio
                    fig_de = px.line(x=years, y=de_ratio, title='D/E Ratio (ความเสี่ยงทางการเงิน)', markers=True)
                    fig_de.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
                    st.plotly_chart(fig_de, use_container_width=True)

                st.info("💡 **Analyst Note:** หาก D/E Ratio สูงเกิน 2.0 อาจแสดงถึงภาระหนี้ที่สูง แต่ต้องดูประเภทหนี้ประกอบด้วย (หนี้ที่มีดอกเบี้ย vs เจ้าหนี้การค้า)")

            with tab3:
                st.subheader("การบริหารจัดการกระแสเงินสด")
                
                # กราฟ Free Cash Flow
                fig_fcf = go.Figure()
                fig_fcf.add_trace(go.Bar(x=years, y=cfo, name='Cash from Operations', marker_color='teal'))
                fig_fcf.add_trace(go.Bar(x=years, y=capex, name='Capital Expenditure', marker_color='crimson'))
                fig_fcf.add_trace(go.Scatter(x=years, y=fcf, name='Free Cash Flow', line=dict(color='black', dash='dot')))
                
                fig_fcf.update_layout(title='Operating Cash Flow vs CAPEX', barmode='group')
                st.plotly_chart(fig_fcf, use_container_width=True)
                
                st.write("**Free Cash Flow (FCF)** คือเงินสดที่เหลือจริงๆ หลังหักงบลงทุน หากเป็นบวกต่อเนื่อง แสดงถึงศักยภาพในการปันผลหรือลงทุนต่อ")

        except KeyError as e:
            st.error(f"ไม่พบข้อมูล Key หลักในไฟล์: {e} กรุณาตรวจสอบว่าชื่อรายการในไฟล์ Excel ตรงกับ Standard (Revenue, Net Income to Company ฯลฯ)")

else:
    # --- หน้าจอเริ่มต้นเมื่อยังไม่ Upload ---
    st.info("👋 ยินดีต้อนรับสู่ระบบวิเคราะห์หุ้น")
    st.markdown("""
    **วิธีใช้งาน:**
    1. ดาวน์โหลดงบการเงินล่าสุด (Excel/CSV) 
    2. อัปโหลดไฟล์ที่แถบเมนูด้านซ้าย:
       - **Income Statement**
       - **Balance Sheet**
       - **Cash Flow**
    3. Dashboard จะวิเคราะห์ข้อมูลให้อัตโนมัติ
    
    *ระบบรองรับไฟล์ที่มี Format เดียวกับ Neo Corporate PCL ที่แนบมา*
    """)
    
    # แสดงตัวอย่าง (Dummy Data เพื่อความสวยงามตอนเปิดครั้งแรก)
    st.markdown("---")
    st.markdown("### 🔒 ตัวอย่างการแสดงผล (Demo Mode)")
    st.warning("กรุณา Upload ไฟล์จริงเพื่อดูข้อมูลที่ถูกต้อง")