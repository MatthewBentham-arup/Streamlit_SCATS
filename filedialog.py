import streamlit as st


def upload_folder_button():
    # Add custom HTML to use webkitdirectory for folder selection
    upload_icon = "📂"  # You can use other symbols or Font Awesome icons if needed
    
    st.warning(
        "⚠️ Please import the folder containing the .db files you wish to use (e.g. 'Scats2024' needs to be in the folder if you want 2024 data). "
        "It is recommended to use a local directory and not one over the network."
    )
    folder = st.text_input(f'{upload_icon}Input Directory to Database folder')

    return folder



