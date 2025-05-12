import streamlit as st
from database import db
import streamlit.components.v1 as components
import time

def app():
    if not st.session_state.get('logged_in', False):
        st.markdown(
            """
            <style>
            .auth-form {
                max-width: 400px;
                margin: 0 auto;
                padding: 20px;
                background-color: #1E1E1E;
                border-radius: 10px;
                border: 1px solid #4CAF50;
            }
            .success-message {
                padding: 20px;
                border-radius: 10px;
                background-color: rgba(76, 175, 80, 0.1);
                border: 1px solid #4CAF50;
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.title("📝 Register")
        
        with st.container():
            st.markdown('<div class="auth-form">', unsafe_allow_html=True)
            
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Register", use_container_width=True):
                    if name and email and password and confirm_password:
                        if password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            success, message = db.register_user(email, password, name)
                            if success:
                                st.success("✨ Registration successful! Redirecting to login...")
                                # Set flag for login page to show success message
                                st.session_state['registration_success'] = True
                                time.sleep(1)  # Short delay to show the success message
                                st.session_state['current_page'] = 'login'
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.error("Please fill in all fields")
            
            with col2:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state['current_page'] = 'login'
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app() 