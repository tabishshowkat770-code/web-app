import streamlit as st


st.title("My Simple web app")
st.write("hi this is my simple app are you agree with it man ? ")
name = st.text_input("Enter your name", key="name")

def greet():
    st.write(f"Hello, {name}! Welcome to my simple web app.")

if name:
    greet() 
st.button("Submit", on_click=greet)

