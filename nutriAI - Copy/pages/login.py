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

        st.title("🔐 Login")
        
        # Show registration success message if coming from registration
        if 'registration_success' in st.session_state and st.session_state['registration_success']:
            st.markdown(
                '<div class="success-message">✅ Registration successful! Please login with your credentials.</div>',
                unsafe_allow_html=True
            )
            # Clear the registration success flag
            st.session_state['registration_success'] = False
        
        with st.container():
            st.markdown('<div class="auth-form">', unsafe_allow_html=True)
            
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Login", use_container_width=True):
                    if email and password:
                        success, result = db.verify_user(email, password)
                        if success:
                            st.session_state['logged_in'] = True
                            st.session_state['user'] = result
                            st.success("🎉 Login successful! Redirecting to dashboard...")
                            time.sleep(1)  # Short delay to show the success message
                            st.rerun()
                        else:
                            st.error(result)
                    else:
                        st.error("Please fill in all fields")
            
            with col2:
                if st.button("Register", use_container_width=True):
                    st.session_state['current_page'] = 'register'
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app() 