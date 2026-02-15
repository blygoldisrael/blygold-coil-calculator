import streamlit as st

# ==========================================
# קבועים (נלקחו ישירות מתוך קובץ האקסל שלך)
# ==========================================

# מחירי חומרים
PRICE_PER_KG_POLUAL = 96.59  # מחיר פוליאול (לפי הטקסט שלך, באקסל היה 95.69)
PRICE_PER_KG_PRIMER = 96.74  # מחיר פריימר
PREP_COST = 50.0             # עלות הכנה קבועה (Pretreatment)

# מקדמי כיסוי
COVERAGE_POLUAL = 0.05       # ק"ג למ"ר (עובי ציפוי רגיל)
COVERAGE_PRIMER = 2.5        # ק"ג למ"ר (עובי ציפוי פריימר)

# עבודה
LABOR_COST_PER_HOUR = 200.0
LABOR_OUTPUT_m2_PER_HOUR = 1.5  # הספק עבודה (מ"ר לשעה)

# תוספות ומרווחים
# באקסל יש שתי תוספות של 5% (Sundry + Transport), סה"כ כ-10.25% או 10% במצטבר
# חישוב אקסל: (עלות + עבודה) * 0.05 ועוד פעם * 0.05.
OVERHEAD_PERCENT = 0.10      # איחוד של Sundry + Transport (כדי להתאים לתוצאה באקסל)

PROFIT_MARGIN = 0.55         # 55% רווח (Markup)
FIELD_WORK_EXTRA = 2900.0    # תוספת יציאה לשטח

# המרה מ-FPI לפינים למטר (אינץ' למטר)
FINS_PER_METER_FACTOR = 39.3700787

def calculate_exact_price(length_m, height_m, depth_m, fpi, include_primer, is_field_work):
    # 1. חישוב שטח לציפוי (Coated Area) - שורה 10 באקסל
    # הנוסחה באקסל: Volume * FinsPerMeter * 2
    # כאשר FinsPerMeter = FPI * 39.37
    fins_per_meter = fpi * FINS_PER_METER_FACTOR
    coated_area = length_m * height_m * depth_m * fins_per_meter * 2
    
    # 2. שטח פנים (Faced Area) - שורה 11 באקסל
    # משמש לחישוב שעות העבודה
    faced_area = length_m * height_m
    
    # 3. עלות חומר Polual - שורה 19 באקסל
    cost_polual = coated_area * COVERAGE_POLUAL * PRICE_PER_KG_POLUAL
    
    # 4. עלות פריימר (אם נבחר) - שורה 9 (בחלק השני של האקסל)
    cost_primer = 0.0
    if include_primer:
        # הנוסחה לפריימר: גובה * עומק * כיסוי * מחיר
        primer_area = height_m * depth_m
        cost_primer = primer_area * COVERAGE_PRIMER * PRICE_PER_KG_PRIMER
        
    # 5. עלות עבודה - שורה 18 באקסל
    # קריטי: האקסל מחשב לפי Faced Area (ולא Coated Area)
    labor_hours = faced_area / LABOR_OUTPUT_m2_PER_HOUR
    cost_labor = labor_hours * LABOR_COST_PER_HOUR
    
    # 6. סיכום עלויות ישירות (לפני תוספות)
    total_material = cost_polual + cost_primer + PREP_COST
    total_direct_base = total_material + cost_labor
    
    # 7. תוספות (Sundry + Transport) - שורות 23-24 באקסל
    # האקסל מוסיף 5% ועוד 5%.
    overheads = total_direct_base * OVERHEAD_PERCENT
    
    # 8. סה"כ עלות ישירה לקויל (לפני רווח) - שורה 26 באקסל
    total_cost_per_coil = total_direct_base + overheads
    
    # 9. רווח (Profit) - שורה 32 באקסל
    profit = total_cost_per_coil * PROFIT_MARGIN
    
    # 10. מחיר סופי (לפני שטח) - שורה 34 באקסל
    price_excl_field = total_cost_per_coil + profit
    
    # 11. תוספת שטח (אם נבחר)
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
# הגדרות תצוגה
# ==========================================
st.set_page_config(page_title="מחשבון בלייגולד", layout="centered")

# CSS ליישור לימין
st.markdown("""
    <style>
    body { direction: rtl; text-align: right; }
    .stTextInput, .stNumberInput, .stSelectbox, .stCheckbox, .stRadio { direction: rtl; text-align: right; }
    div.row-widget.stRadio > div { flex-direction: row-reverse; }
    p, h1, h2, h3, div { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("מחשבון הצעת מחיר - בלייגולד")
st.caption("חישוב מדויק לפי נוסחאות האקסל המקורי")
st.divider()

# טופס קלט
col1, col2 = st.columns(2)

with col1:
    height = st.number_input("גובה (מטרים)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    depth = st.number_input("עומק (מטרים)", min_value=0.0, value=0.13, step=0.01, format="%.3f", help="לדוגמה: 13 ס\"מ יש להזין 0.13")

with col2:
    length = st.number_input("אורך (מטרים)", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    fpi = st.number_input("צפיפות (FPI)", min_value=1, value=10, step=1)

st.markdown("### אפשרויות")
include_primer = st.checkbox("כולל ציפוי קשתות (פריימר)?")
location = st.radio("מיקום:", ["בית מלאכה", "שטח (באתר הלקוח)"])
is_field_work = location == "שטח (באתר הלקוח)"

if st.button("חשב מחיר", type="primary", use_container_width=True):
    res = calculate_exact_price(length, height, depth, fpi, include_primer, is_field_work)
    
    st.divider()
    st.success(f"הצעת מחיר: {res['final_price']:,} ₪")
    
    with st.expander("פירוט החישוב (להשוואה לאקסל)"):
        st.write(f"שטח לציפוי: {res['coated_area']:.2f} מ\"ר")
        st.write(f"עלות חומר (Polual): {res['cost_polual']:.2f} ₪")
        st.write(f"עלות עבודה: {res['cost_labor']:.2f} ₪")
        if include_primer:
             st.write(f"עלות פריימר: {res['cost_primer']:.2f} ₪")
        st.write(f"סה\"כ עלות ישירה (לפני רווח): {res['total_cost_per_coil']:.2f} ₪")
        st.caption("* המחיר אינו כולל מע\"מ")
