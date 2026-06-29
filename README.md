# 📊 Executive Financial Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=chatpongt/financial-dashboard&branch=main&mainModule=app.py)

อัปโหลดงบการเงิน CSV/XLSX → KPI + กราฟ interactive  
ส่วนหนึ่งของ **Jon's RSI Cluster System** (🟡 DECIDE — fundamental overlay)

**Live:** https://chatpongt-financial-dashboard.streamlit.app/

---

## Features

- อัปโหลด **Income Statement / Balance Sheet / Cash Flow** (CSV หรือ XLSX)
- KPI: Revenue, Net Profit, GPM, CFO (พร้อม YoY delta)
- กราฟ: Revenue vs Net Income, Margins, Capital Structure, D/E, FCF

## Deploy (Streamlit Cloud)

1. [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Repo `chatpongt/financial-dashboard` → branch `main` → `app.py`
3. ไม่ต้องใส่ secrets
4. **Deploy**

## Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Format

ไฟล์ต้องมีแถว header ที่มีคำว่า `Period End Date` และรายการมาตรฐาน เช่น:

| Statement | Required rows |
|-----------|---------------|
| Income | `Revenue`, `Net Income to Company`, `Gross Profit Margin` |
| Balance | `Total Assets`, `Total Liabilities`, `Total Equity`, `Cash And Equivalents` |
| Cash Flow | `Cash from Operations`, `Capital Expenditures` |

รองรับ export จาก LSEG/Excel ที่มี format เดียวกับ Neo Corporate template

## RSI Cluster

| Repo | Role |
|------|------|
| [dashboard-set50](https://github.com/chatpongt/dashboard-set50) | Valuation sheet 100+ หุ้น (consensus) |
| **financial-dashboard** | Deep-dive งบ 3 statement ต่อตัว (upload) |
| [thai-set-ir](https://github.com/chatpongt/thai-set-ir) | IR links + OppDay |