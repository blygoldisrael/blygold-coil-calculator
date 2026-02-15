import streamlit as st

# --- הגדרת משתנים קבועים ועלויות ---
PRICE_PER_KG_POLUAL = 96.59
COVERAGE_POLUAL = 0.05
PRICE_PER_KG_PRIMER = 96.74
COVERAGE_PRIMER = 2.5
PREP_COST = 50
LABOR_COST_PER_HOUR = 200
LABOR_COVERAGE = 1.5
OVERHEAD_FACTOR = 1.15
PROFIT_MARGIN = 1.50
FIELD_WORK_EXTRA = 2900

def calculate_price(length, height, depth, fpi, include_primer, is_field_work):
    # 1. חישוב שטח מצופה כללי
    coated_area = length * height * depth * fpi * 2
    
    # 2. עלות חומר Polual XT
    cost_polual = coated_area * COVERAGE_POLUAL * PRICE_PER_KG_POLUAL
    
    # 3. חישוב עלות פריימר
    cost_primer = 0
    if include_primer:
        primer_area = height * depth
        cost_primer = primer_area * COVERAGE_PRIMER * PRICE_PER_KG_PRIMER
        
    # 4. חישוב עלות עבודה
    labor_hours = coated_area / LABOR_COVERAGE
    cost_labor = labor_hours * LABOR_COST_PER_HOUR
    
    # 5. סכום ביניים א'
    base_cost = cost_polual + cost_primer + cost_labor + PREP_COST
    
    # 6. תוספת ייבוש והובלה
    cost_with_overhead = base_cost * OVERHEAD_FACTOR
    
    # 7. הוספת רווח (55%)
    price_before_field = cost_with_overhead * PROFIT_MARGIN
    
    # 8. תוספת שטח
    final_price = price_before_field
    if is_field_work:
        final_price += FIELD_WORK_EXTRA
        
    return int(final_price), coated_area

# --- הגדרת הדף (התיקון בוצע כאן) ---
st.set_page_config(page_title="מחשבון בלייגולד", layout="centered")

# --- הזרקת CSS ליישור לימין (RTL) ---
st.markdown("""
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stCheckbox label {
        direction: rtl;
        text-align: right;
        width: 100%;
    }
    div[data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# כותרת
st.markdown("# מחשבון הצעת מחיר - ציפוי סוללות")
st.markdown("הזן את נתוני הסוללה לקבלת הערכה מיידית")
st.divider()

# טופס קלט
col1, col2 = st.columns(2)

with col1:
    height = st.number_input("גובה הסוללה (מטר)", min_value=0.0, step=0.1, format="%.2f")
    depth = st.number_input("עומק/מספר שורות (מטר)", min_value=0.0, step=0.01, format="%.2f")

with col2:
    length = st.number_input("אורך הסוללה (מטר)", min_value=0.0, step=0.1, format="%.2f")
    fpi = st.number_input("צפיפות עלעלים (FPI)", min_value=1, value=12, step=1)

st.divider()
st.markdown("### אפשרויות נוספות")

include_primer = st.checkbox("כולל ציפוי קשתות (פריימר REFAMAC 3509)?")

location_option = st.radio(
    "מיקום ביצוע העבודה:",
    ["בית מלאכה (אצלנו)", "עבודת שטח (באתר הלקוח)"],
    horizontal=True
)

is_field_work = "שטח" in location_option

st.write("")
if st.button("חשב הצעת מחיר ₪", type="primary", use_container_width=True):
    if length > 0 and height > 0 and depth > 0:
        final_price, area_calc = calculate_price(length, height, depth, fpi, include_primer, is_field_work)
        
        st.success(f"הצעת מחיר משוערת: {final_price:,} ₪")
        
        with st.expander("פרטים נוספים על החישוב"):
            st.info(f"שטח מחושב לציפוי: {area_calc:.2f} מ\"ר")
            if include_primer:
                st.write("✅ כולל תוספת ציפוי קשתות (פריימר)")
            if is_field_work:
                st.write("✅ כולל תוספת יציאה לשטח")
            st.caption("המחיר אינו כולל מע\"מ. ט.ל.ח.")
            
    else:
        st.error("נא להזין מידות תקינות (גדולות מ-0)")

