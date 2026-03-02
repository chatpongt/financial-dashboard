# 📊 Executive Financial Dashboard

Streamlit app สำหรับวิเคราะห์งบการเงินหุ้นไทยแบบ interactive

## Features
- อัปโหลด CSV งบกำไรขาดทุน, งบดุล, งบกระแสเงินสด
- แสดงผล KPI หลัก (Revenue, Net Profit, GPM, CFO)
- กราฟ Revenue vs Net Income, Margin Trends, Capital Structure, D/E Ratio, Free Cash Flow

## วิธีใช้งาน

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Format
รองรับไฟล์ CSV ที่มี header row ประกอบด้วย `Period End Date`
