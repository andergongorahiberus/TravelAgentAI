import streamlit as st
from datetime import date, timedelta
import time

# Basic Page Setup
st.set_page_config(page_title="Travel Planner", page_icon="✈️")

st.title("Travel Plan Generator")
st.write("Enter your trip details below to generate a custom itinerary.")

# Use a form to group inputs and prevent unnecessary reruns
with st.form("travel_input_form"):
    
    # Destination Input
    origin = st.text_input("Origin", placeholder="e.g. Paris, France")
    
    travel_style = st.multiselect(
        "Travel Style (Select all that apply)",
        ["Adventure", "Relaxation", "Foodie", "History", "Nightlife", "Family Friendly"],
        default=["History"]
    )

    budget = st.number_input("Budget", min_value=0, step=100, help="Enter your total budget for the trip in USD.") 
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Arrival Date", value=date.today() + timedelta(days=30))
    with col2:
        end_date = st.date_input("Departure Date", value=date.today() + timedelta(days=35))
    
    special_requests = st.text_area("Special Requests or Constraints", help="e.g. Accessibility needs, dietary restrictions, or 'no museums'.")
    
    submit = st.form_submit_button("Generate Itinerary")

# Logic to display results
if submit:
    if not origin:
        st.warning("Please provide an origin.")
    elif end_date <= start_date:
        st.error("Error: Departure date must be after the arrival date.")
    else:
        # Visual feedback for the user
        with st.spinner(f"Creating your dream trip from {origin}..."):
            # This is a placeholder for your AI API call
            time.sleep(1.5) 
            
            st.success("Itinerary Ready!")
            st.divider()
            
            # Placeholder Output
            st.header(f"Trip to {origin}")
            st.subheader(f"{start_date} to {end_date}")
            
            st.markdown(f"""
            **Summary:**
            - **Budget:** {budget}
            - **Focus:** {', '.join(travel_style)}
            
            **Day 1: Arrival**
            - Check into hotel.
            - Light walking tour of the neighborhood.
            - Dinner at a local spot matching your '{travel_style[0]}' preference.
            
            **Day 2: Exploration**
            - Morning activity based on: {special_requests if special_requests else "General sightseeing"}.
            - Evening relaxation.
            """)
            
            # Simple text download
            st.download_button("Download as Text", "Your Travel Plan Data...", file_name="itinerary.txt")