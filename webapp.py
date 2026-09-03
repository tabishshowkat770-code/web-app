import streamlit as st


st.title("My Simple web app")
st.write("hi this is my simple app are you agree with it man ? ")
st.text_input("Enter your name", key="name")


def main():
    if st.button("Submit"):
        name = st.session_state.name
        st.write(f"Hello, {name}! Welcome to my simple web app.")
st.button("Submit", on_click=main)  