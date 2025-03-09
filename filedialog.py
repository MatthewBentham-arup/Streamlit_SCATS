import streamlit as st
import easygui

def upload_folder_button():
    # Define the upload icon (Unicode for the "Upload" symbol)
    upload_icon = "📂"  # You can use other symbols or Font Awesome icons if needed
    st.warning(
    "⚠️ Please import the folder containing the .db files you wish to use (e.g. 'Scats2024' needs to be in the folder if you want 2024 data). "
    "It is recommended to use a local directory and not one over the network."
)

    if st.button(f'{upload_icon} Select Database Folder'):
        # Use easygui to open a folder dialog
        folder_path = easygui.diropenbox(title='Select Folder')

        # Display the selected folder path
        if folder_path:
            st.write(f"Selected folder: {folder_path}")
        else:
            st.write("No folder selected.")
        return folder_path


