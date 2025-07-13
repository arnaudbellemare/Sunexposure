import streamlit as st
import datetime
import pytz
import math  # For BMI calculation

# App title
st.title("Vitamin D Synthesis Calculator")

# Sidebar for adjustable inputs
st.sidebar.header("Adjustable Parameters")
uv_index = st.sidebar.number_input("UV Index", min_value=0.0, max_value=20.0, value=9.0, step=0.1)
adaptation_factor = st.sidebar.slider("Adaptation Factor (0.8 for no prior sun, up to 1.2 for regular exposure)", min_value=0.8, max_value=1.2, value=0.8, step=0.05)

# Clothing options
clothing_options = {
    "Nude (100%)": 1.0,
    "Minimal/Swimwear (80%)": 0.8,
    "Light/Shorts & T-shirt (40%)": 0.4,
    "Moderate/Long sleeves (15%)": 0.15,
    "Heavy/Fully covered (5%)": 0.05
}
selected_clothing = st.sidebar.selectbox("Clothing Factor", list(clothing_options.keys()), index=0)  # Default to Nude (1.0)
clothing_factor = clothing_options[selected_clothing]

# Fixed parameters based on user info
base_rate = 21000
skin_type_factor = 1.0  # Light skin, Type III
age_factor = 0.95  # For age 25
height_inches = 74  # 6'2" = 74 inches
weight_lbs = 180
height_m = height_inches * 0.0254  # Convert to meters
weight_kg = weight_lbs * 0.453592  # Convert to kg
bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0
med_uv1 = 425  # MED at UV 1 for Skin Type III (minutes)

# Get current time and date in New York
ny_tz = pytz.timezone('America/New_York')
current_time = datetime.datetime.now(ny_tz)
current_hour = current_time.hour
current_month = current_time.month

# Quality Factor: 1 if between 10 AM and 3 PM, else reduced
if 10 <= current_hour < 15:
    quality_factor = 1.0
    quality_note = "Peak time (10 AM - 3 PM): Quality Factor = 1.0"
else:
    quality_factor = 0.5  # Reduced for off-peak
    quality_note = f"Off-peak time ({current_time.strftime('%I:%M %p')}): Quality Factor = 0.5 (reduced for lower UV-B efficacy)"

# UV Factor calculation
uv_factor = (uv_index * 3.0) / (4.0 + uv_index)

# Full calculation
vitamin_d_rate = base_rate * uv_factor * clothing_factor * skin_type_factor * age_factor * quality_factor * adaptation_factor

# Time to get 15,000 IU
if vitamin_d_rate > 0:
    time_to_15000_hours = 15000 / vitamin_d_rate
    time_to_15000_minutes = time_to_15000_hours * 60
else:
    time_to_15000_minutes = float('inf')  # Avoid division by zero

# Burn time calculation
if uv_index > 0:
    burn_time_minutes = med_uv1 / uv_index
    safety_warning_minutes = burn_time_minutes * 0.8
else:
    burn_time_minutes = float('inf')
    safety_warning_minutes = float('inf')

# Display results
st.write(f"Current New York Time: {current_time.strftime('%Y-%m-%d %I:%M %p')}")
st.write(quality_note)
st.write("### Calculated Vitamin D Rate")
st.write(f"{vitamin_d_rate:.2f} IU/hour")

st.write("### Time Needed for 15,000 IU")
st.write(f"Approximately {time_to_15000_minutes:.1f} minutes of exposure.")

st.write("### Time Before Burning")
st.write(f"Technical burn time (1 MED): {burn_time_minutes:.1f} minutes.")
st.write(f"Safety warning threshold (80% of burn time): {safety_warning_minutes:.1f} minutes.")

# Winter supplement notice
if current_month in [11, 12, 1, 2]:
    supplement_rec = 2000  # Base for normal BMI
    if bmi >= 30:
        supplement_rec = 4000  # 2x for obese
    elif bmi >= 25:
        supplement_rec = 3000  # 1.5x for overweight
    
    st.warning(f"""
    **Winter Vitamin D Notice**: You're in the north (New York, ~40.7°N latitude), where UV-B is insufficient for vitamin D synthesis from November to February. 
    Based on your height (6'2") and weight (180 lbs), your BMI is approximately {bmi:.1f} (normal range). 
    Recommend supplementing {supplement_rec} IU/day of vitamin D during these months to maintain adequate levels. 
    This is a general guideline; consult a healthcare provider for personalized advice, especially if you have risk factors for deficiency.
    """)
else:
    st.info("It's not winter (Nov-Feb), so sun exposure can contribute to vitamin D needs, but monitor UV levels.")

# Formula breakdown
with st.expander("Formula Breakdown"):
    st.write(f"Base Rate: {base_rate}")
    st.write(f"UV Factor: {uv_factor:.2f} = ({uv_index} × 3) / (4 + {uv_index})")
    st.write(f"Clothing Factor: {clothing_factor}")
    st.write(f"Skin Type Factor: {skin_type_factor}")
    st.write(f"Age Factor: {age_factor}")
    st.write(f"Quality Factor: {quality_factor}")
    st.write(f"Adaptation Factor: {adaptation_factor}")

# Guidance on factors
st.header("How to Determine Quality and Adaptation Factors")
st.write("""
**Quality Factor**: 
- Automatically calculated based on current time in New York.
- Set to 1.0 if between 10 AM and 3 PM (optimal solar zenith angle for UV-B).
- Otherwise, set to 0.5 as a conservative estimate (morning/evening UV has less effective UV-B; in a real app, this could use zenith angle calculations for precision, e.g., via libraries like astral or pvlib).
- To know it: Check the time—if peak hours, use 1.0; else, estimate 0.3-0.9 based on how far from noon (earlier/later means lower).
""")
st.write("""
**Adaptation Factor**: 
- Use the slider in the sidebar.
- Range 0.8-1.2 based on 7-14 day sun exposure history.
- 0.8: No prior sun exposure (conservative for 'shock' on pale skin).
- 1.0: Moderate recent exposure.
- 1.2: Regular daily exposure (upregulates synthesis pathways).
- To know it: Track your sun habits—if no sun in past week+, use 0.8; adjust up with more exposure.
""")
