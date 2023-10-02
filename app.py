""" 
This file will run the website app.
"""

import streamlit as st
import timeline_generator as tg


# Page config
st.set_page_config(page_title="Visual History Storyteller", page_icon=":framed_picture:")

# Ask for input year and event 
with st.sidebar:
    with st.form(key="input_form"):
        year = st.sidebar.text_area(
            label="Enter the year of the historical event",
            max_chars=15,
            key="year"
        )
        hist_event = st.sidebar.text_area(
            label="Enter a short description of the historical event",
            max_chars=50,
            key="hist_event"
        )

        submit_btn = st.form_submit_button(label="Submit")

# Title and notes
with st.container():
    st.title("Visual History Storyteller")
    st.write(
        """
        DISCLAIMER: This web app uses GPT-3.5 AI model to generate the timeline of a historical event. It is still important
        to verify the accuracy of information posted here.
        """
    )

# Collect data for the visual timeline
title, caption_list, illustration_urls, error_message = tg.get_timeline_infos(year, hist_event)

# If input is valid, show visual timeline 
if len(caption_list) != 0:
    with st.container():
        st.write("---")
        st.header(f"Visual Timeline: {title}")
        st.write("##")

    for caption, illustration_url in zip(caption_list, illustration_urls):
        image_col, text_col = st.columns((1,2))
        with image_col:
            st.image(illustration_url)
        with text_col:
            st.subheader(caption)
# Else, return the explanation for invalid input
else:
    with st.container():
        st.write("---")
        st.write(error_message)






    
    
