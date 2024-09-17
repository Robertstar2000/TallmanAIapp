import streamlit as st
import os
from dotenv import load_dotenv
import groq
import chromadb

# Set the page configuration at the very beginning
st.set_page_config(page_title="Tallman AI", layout="centered")

# Import custom modules
from auth import authenticate_user, create_new_account, get_user_role
from qa_module import get_ai_response, save_correction, reload_database
from user_management import manage_users, search_user, update_user, delete_user, get_new_users, approve_new_user

# Load environment variables
load_dotenv()

# Initialize Groq client
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Chroma client
chroma_client = chromadb.Client()

# Check if the collection exists
if "tallman_knowledge" in [coll.name for coll in chroma_client.list_collections()]:
    collection = chroma_client.get_collection("tallman_knowledge")
else:
    collection = chroma_client.create_collection("tallman_knowledge")

# Inject custom CSS
st.markdown("""
    <style>
    /* Set overall background color */
    body {
        background-color: #d3d3d3; /* Light gray */
    }
    /* Set input fields background to white */
    input, textarea, select, .stRadio, .stCheckbox {
        background-color: white !important;
    }
    /* Style all buttons to be red with white text, except specified ones */
    div.stButton > button {
        background-color: red;
        color: white;
    }
    /* Style for the light pink buttons */
    #forgot_pin_button button, #new_account_button button,
    #correct_button button, #manage_users_button button {
        background-color: #ffe6f2; /* Very light pink */
        color: black;
        border: none;
        padding: 5px 10px;
        margin: 0;
        font-size: 12px;
    }
    #forgot_pin_button button:hover, #new_account_button button:hover,
    #correct_button button:hover, #manage_users_button button:hover {
        background-color: #ffb3d9; /* Slightly darker pink on hover */
    }
    </style>
    """, unsafe_allow_html=True)

def main():

    # Session state initialization
    if "user" not in st.session_state:
        st.session_state.user = None
    if "screen" not in st.session_state:
        st.session_state.screen = "login"
    if "reload_confirm" not in st.session_state:
        st.session_state.reload_confirm = False
    if "new_account_confirm" not in st.session_state:
        st.session_state.new_account_confirm = False

    # Display appropriate screen based on session state
    if st.session_state.screen == "login":
        display_login_screen()
    elif st.session_state.screen == "new_account":
        display_new_account_screen()
    elif st.session_state.screen == "qa":
        display_qa_screen()
    elif st.session_state.screen == "correct":
        display_correct_screen()
    elif st.session_state.screen == "manage_users":
        display_manage_users_screen()

def display_login_screen():
    st.image("tallmanlC:\Users\rober\My Drive\Dunmore\Source for AI\Tallman\TallmanAIapp\TallmanAIapp\tallmanlogo.pngogo.png", width=200)
    st.title("Login Screen")

    # Only include login-related fields here (Username and PIN)
    username = st.text_input("Username", key="login_username")
    pin = st.text_input("PIN", type="password", key="login_pin")

    if st.button("LOG IN"):
        auth_result = authenticate_user(username, pin)  # Call the new function
        if auth_result['authenticated']:
            st.session_state.user = username
            st.session_state.user_role = auth_result['role']
            st.session_state.screen = "qa"  # Redirect to the QA screen after login
            st.experimental_rerun()
        else:
            st.error(auth_result['message'])  # Display the error message from authentication

    # "Forgot PIN" and "Request New Account" buttons with custom styling
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Forgot PIN", key="forgot_pin_button"):
            st.session_state.screen = "new_account"
            st.experimental_rerun()
    with col2:
        if st.button("Request New Account", key="new_account_button"):
            st.session_state.new_account_confirm = True
            st.experimental_rerun()

    # Handle the confirmation prompt for "Request New Account"
    if st.session_state.get('new_account_confirm', False):
        st.warning("Are you sure you want to request a new account?")
        confirm_col1, confirm_col2 = st.columns(2)
        with confirm_col1:
            if st.button("Yes", key="confirm_new_account"):
                st.session_state.screen = "new_account"
                st.session_state.new_account_confirm = False
                st.experimental_rerun()
        with confirm_col2:
            if st.button("Cancel", key="cancel_new_account"):
                st.session_state.new_account_confirm = False
                st.experimental_rerun()

def display_new_account_screen():
    st.image("C:\Users\rober\My Drive\Dunmore\Source for AI\Tallman\TallmanAIapp\TallmanAIapp\tallmanlogo.png.png", width=200)
    st.title("New Account Screen")
    
    username = st.text_input("Username")
    pin = st.text_input("PIN", type="password")
    email = st.text_input("Email")
    
    if st.button("SUBMIT"):
        if create_new_account(username, pin, email):
            st.success("Your request has been received and will be processed by the application administrator")
            st.session_state.screen = "login"
            st.experimental_rerun()
        else:
            st.error("Failed to create account. Please try again.")

def display_qa_screen():
    st.image("C:\Users\rober\My Drive\Dunmore\Source for AI\Tallman\TallmanAIapp\TallmanAIapp\tallmanlogo.png.png", width=200)
    st.title("Get Answer Screen")

    # Correct placement of st.radio() to select a subject
    query_type = st.radio("Subject", ["Tallman", "Sales", "Product", "Tutorial"])
    question = st.text_area("Your Question")

    if st.button("Answer"):
        response = get_ai_response(query_type, question, client, collection)
        st.text_area("Your Answer", value=response, height=200)
        
        # Save the response in the session state to be used later
        st.session_state.last_response = response

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("LOG OUT"):
            st.session_state.user = None
            st.session_state.screen = "login"
            st.experimental_rerun()

    # "Correct" and "Manage Users" buttons with custom styling
    if st.session_state.user_role == "admin":  # Only show admin options if the user is an admin
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Correct", key="correct_button"):
                st.session_state.screen = "correct"
                st.experimental_rerun()
        with col2:
            if st.button("Manage Users", key="manage_users_button"):
                st.session_state.screen = "manage_users"
                st.experimental_rerun()

def display_correct_screen():
    st.image("tallmanlogo.png", width=200)
    st.title("Correct Answer Screen")
    
    # Display the last response from session state as the answer to improve
    answer_to_improve = st.session_state.get("last_response", "No answer available to improve.")
    
    st.text_area("Answer to improve", value=answer_to_improve, height=200)
    improvement_instructions = st.text_area("Improvement Instructions")

    col1, col2 = st.columns(2)
    
    # Save button functionality
    with col1:
        if st.button("Save"):
            # Perform save action
            save_correction(answer_to_improve, improvement_instructions, collection)
            st.success("Correction saved successfully")
            
            # Redirect back to QA Screen
            st.session_state.screen = "qa"
            st.experimental_rerun()
    
    # Re-Load DB button functionality with immediate warning message
    with col2:
        if st.session_state.reload_confirm:
            st.warning("Warning: The vector database will be deleted and replaced. Do you want to proceed?")
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("Yes, proceed"):
                    qa_data_path = r"C:/Users/rober/My Drive/Dunmore/Source for AI/Tallman/TallmanAIapp/QA_data"  # Update with the correct path
                    
                    # Add error handling for reload_database
                    try:
                        reload_database(chroma_client, collection, qa_data_path)
                        st.success("Database reloaded successfully")
                    except Exception as e:
                        st.error(f"Failed to reload database: {e}")
                    
                    # Reset confirmation state
                    st.session_state.reload_confirm = False
                    
                    # Redirect back to QA Screen
                    st.session_state.screen = "qa"
                    st.experimental_rerun()
            with confirm_col2:
                if st.button("Cancel"):
                    st.session_state.reload_confirm = False
                    st.experimental_rerun()
        else:
            if st.button("Re-Load DB"):
                st.session_state.reload_confirm = True
                st.experimental_rerun()

def display_manage_users_screen():
    st.image("C:\Users\rober\My Drive\Dunmore\Source for AI\Tallman\TallmanAIapp\TallmanAIapp\tallmanlogo.png.png", width=200)
    st.title("Manage Users Screen")

    users = manage_users()  # Load all users from your user management function

    # Format users into a readable string with commas between fields and linefeed after each email
    formatted_users = "\n".join([f"{user.get('username', '')}, {user.get('pin', '')}, {user.get('email', '')}" for user in users])

    # Display the formatted string in a scrollable text area
    st.text_area("User List", value=formatted_users, height=300, max_chars=None)

    # Search for a user by term
    search_term = st.text_input("Search for User", key="search_user")

    # Add a search button
    if st.button("Search"):
        matching_user = search_user(search_term)  # Assuming search_user returns a matching user dictionary
        if matching_user:
            # Store the searched user in session state
            st.session_state.searched_user = matching_user
            st.success(f"User {matching_user.get('username', matching_user.get('name', ''))} found!")
        else:
            st.error("No user found")

    # Prepopulate the form fields with the searched user's info
    if 'searched_user' in st.session_state:
        # Prepopulate form with searched user's info
        name = st.text_input("Name (Username)", value=st.session_state.searched_user.get('username', st.session_state.searched_user.get('name', '')), key="manage_user_name")
        pin = st.text_input("PIN", type="password", value=str(st.session_state.searched_user.get('pin', '')), key="manage_user_pin")
        email = st.text_input("Email", value=st.session_state.searched_user.get('email', ''), key="manage_user_email")

        # Map role to index and display correct radio button
        role = st.session_state.searched_user.get('role', 'User').capitalize()
        role_options = ["New", "User", "Admin"]
        role_index = role_options.index(role) if role in role_options else 1  # Default to "User" if no match
        role = st.radio("Role", role_options, index=role_index, key="manage_user_role")
    else:
        # If no user is searched, show empty fields
        name = st.text_input("Name (Username - this cannot be changed)", key="empty_name")
        pin = st.text_input("PIN", type="password", key="empty_pin")
        email = st.text_input("Email", key="empty_email")
        role = st.radio("Role", ["New", "User", "Admin"], key="empty_role")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save"):
            # Prepare a dictionary to pass to update_user
            user_data = {
                "username": name,  # Ensure this is 'username' to match the database field
                "pin": pin,
                "email": email,
                "role": role
            }
            # Save changes using the dictionary
            if update_user(user_data):
                st.success(f"User {name} has been updated")
            else:
                st.error(f"Failed to update user {name}")

    with col2:
        if st.button("Delete"):
            # Implement delete user logic
            if delete_user(name):
                st.success(f"User {name} has been deleted")
            else:
                st.error(f"Failed to delete user {name}")
    
    with col3:
        if st.button("Done"):
            st.session_state.screen = "qa"
            st.experimental_rerun()

if __name__ == "__main__":
    main()
