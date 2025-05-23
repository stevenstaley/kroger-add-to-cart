import streamlit as st
import keyboard
import time

time.sleep(2)
st.text_input("Waiting for UPC")
left, right = st.columns(2)
def initialize():
    keyboard.press_and_release('F11')
    
    st.session_state['initialized'] = True


if "initialized" not in st.session_state:
    initialize()


if left.button("Price Check", use_container_width=True):
    left.markdown("You clicked the plain button.")
if right.button("Add to Cart", use_container_width=True):
    right.markdown("You clicked the Material button.")
