import streamlit as st
from PIL import Image
import os

# ==========================================
# קבועים (לפי האקסל)
# ==========================================
PRICE_PER_KG_POLUAL = 96.59
PRICE_PER_KG_PRIMER = 96.74
PREP_COST = 50.0
COVERAGE_POLUAL = 0.05
COVERAGE_PRIMER = 2.5
LABOR_COST_PER_HOUR = 200.0
LABOR_OUTPUT_m2_PER_HOUR = 1.5
OVERHEAD_PERCENT = 0.10
PROFIT_MARGIN = 0.55
FIELD_WORK_EXTRA = 2900.0
FINS_PER_METER_FACTOR = 39.3700787

# ==========================================
# לוגיקת החישוב
# ==========================================
def calculate_exact_price(length_m, height_m, depth_m, fpi, include_primer, is_field_work):
    fins_per_meter = fpi * FINS_PER_METER_FACTOR
    coated_area = length_m * height_m * depth_m * fins_per_meter * 2
    faced_area = length_m * height_m
    
    cost_polual = coated_area * COVERAGE_POLUAL * PRICE_PER_KG_POLUAL
    
    cost_primer = 0.0
    if include_primer:
        primer_area = height_m * depth_m
        cost_primer = primer_area * COVERAGE_PRIMER * PRICE_PER_KG_PRIMER
        
    labor_hours = faced_area / LABOR_OUTPUT_m2_PER_HOUR
    cost_labor = labor_hours * LABOR_COST_PER_HOUR
    
    total_material = cost_polual + cost_primer + PREP_COST
    total_direct_base = total_material + cost_labor
    overheads = total_direct_base * OVERHEAD_PERCENT
    total_cost_per_coil = total_direct_base + overheads
    profit = total_cost_per_coil * PROFIT_MARGIN
    price_excl_field = total_cost_per_coil + profit
    
    final_price = price_excl_field
    if is_field_work:
        final_price += FIELD_WORK_EXTRA
        
    return {
        "final_price": int(final_price),
        "coated_area": coated_area,
        "cost_polual": cost_polual,
        "cost_primer": cost_primer,
        "cost_labor": cost_labor,
        "total_cost_per_coil": total_cost_per_coil
    }

# ==========================================
# הגדרות עמוד ועיצוב (CSS)
# ==========================================
st.set_page_config(page_title="Blygold Calculator", page_icon="🔧", layout="centered")

# הזרקת CSS לעיצוב מתקדם (יישור לימין + עיצוב כותרות)
st.markdown("""
    <style>
    /* יישור לימין כללי */
    body { direction: rtl; text-align: right; }
    .stTextInput, .stNumberInput, .stSelectbox, .stCheckbox, .stRadio { direction: rtl; text-align: right; }
    div.row-widget.stRadio > div { flex-direction: row-reverse; justify-content: right; }
    p, h1, h2, h3, div { text-align: right; }
    
    /* עיצוב הכפתור הראשי לצבעי המותג */
    div.stButton > button {
        width: 100%;
        font-weight: bold;
        font-size: 20px;
        padding: 10px;
    }
    
    /* רקע עדין לתוצאה */
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #FFC72C; /* פס זהב בצד */
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# כותרת ולוגו
# ==========================================
# נסיון לטעון לוגו, אם לא קיים מציג טקסט
with col_logo:
    # כתובת הלוגו מהאתר הרשמי (או כל קישור אחר לתמונה)
    logo_url = "https://www.blygold.com/wp-content/uploads/2020/05/Blygold-Logo.png"
    
    try:
        st.image(logo_url, width=150)
    except:
        st.write("🔧") # אייקון גיבוי אם התמונה לא נטענת

with col_title:
    st.title("מחשבון ציפוי סוללות")
    st.markdown("**Blygold HVAC Protection**")

st.divider()

# ==========================================
# טופס קלט
# ==========================================
col1, col2 = st.columns(2)

with col1:
    height = st.number_input("גובה (מטרים)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    depth = st.number_input("עומק (מטרים)", min_value=0.0, value=0.13, step=0.01, format="%.3f")

with col2:
    length = st.number_input("אורך (מטרים)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    fpi = st.number_input("צפיפות (FPI)", min_value=1, value=10, step=1)

st.write("") # מרווח
st.markdown("### אפשרויות מתקדמות")
include_primer = st.checkbox("כולל ציפוי קשתות (פריימר)?")
location = st.radio("מיקום ביצוע העבודה:", ["בית מלאכה ", "ציפוי באתר הלקוח)"])
is_field_work = location == "שטח (באתר הלקוח)"

st.write("")
# ==========================================
# כפתור ותוצאה
# ==========================================
if st.button("חשב הצעת מחיר", type="primary"):
    res = calculate_exact_price(length, height, depth, fpi, include_primer, is_field_work)
    
    st.markdown("---")
    
    # הצגת התוצאה בתוך "קופסה" מעוצבת
    st.markdown(f"""
    <div class="result-box">
        <h2 style="margin:0; color:#333;">סה"כ להצעת מחיר</h2>
        <h1 style="margin:0; color:#0055A5; font-size: 50px;">{res['final_price']:,} ₪</h1>
        <p style="margin-top:10px; color:#666;">המחיר אינו כולל מע"מ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # פירוט טכני מוסתר
    with st.expander("📝 פירוט נתונים טכניים (לשימוש פנימי)"):
        st.write(f"🔹 **שטח לציפוי (Coated Area):** {res['coated_area']:.2f} מ\"ר")
        st.write(f"🔹 **עלות חומר גלם:** {res['cost_polual']:.2f} ₪")
        if include_primer:
             st.write(f"🔹 **עלות פריימר:** {res['cost_primer']:.2f} ₪")
        st.write(f"🔹 **עלות עבודה:** {res['cost_labor']:.2f} ₪")
        st.write(f"🔹 **סה\"כ עלות ישירה (לפני רווח):** {res['total_cost_per_coil']:.2f} ₪")






