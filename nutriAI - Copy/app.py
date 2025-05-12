import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from groq import Groq
import streamlit as st
from pages import login, register

# Set up the Streamlit app
st.set_page_config(page_title="NutriMumbai AI", page_icon="🍏", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: white;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #4CAF50;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
        padding: 10px;
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #4CAF50;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45A049;
    }
    .stSidebar {
        background-color: #1E1E1E;
        color: white;
    }
    .stSelectbox>div>div>select {
        background-color: #1E1E1E;
        color: white;
        border-radius: 8px;
    }
    .stMarkdown {
        color: white;
    }
    .main-content {
        display: none;
    }
    .main-content.show {
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

if 'user' not in st.session_state:
    st.session_state['user'] = None

def main_app():
    # Show welcome message if just logged in
    if 'show_welcome' not in st.session_state:
        st.session_state['show_welcome'] = True

    if st.session_state.get('show_welcome', False):
        st.balloons()
        st.success("🎉 Welcome to NutriMumbai AI! We're excited to help you on your health journey.")
        st.session_state['show_welcome'] = False

    st.title("🍏 NutriMumbai AI")
    st.markdown(f"Welcome, {st.session_state['user']['name']}! 👋")
    st.markdown("Your AI-powered dietary companion for managing diseases and staying healthy in Mumbai.")
    
    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['current_page'] = 'login'
        st.rerun()
    
    st.markdown("---")

    # Step 1: Load preprocessed data and FAISS index
    @st.cache_resource
    def load_data_and_model():
        df = pd.read_csv("preprocessed_data.csv")  # Preprocessed dataset
        index = faiss.read_index("food_disease_index.faiss")  # FAISS index
        model = SentenceTransformer("all-MiniLM-L6-v2")  # Embedding model
        return df, index, model

    df, index, model = load_data_and_model()

    # Step 2: Define the recommendation function
    def recommend_foods(disease: str, k: int = 5):
        """
        Recommend foods to eat or avoid based on a disease.

        Args:
            disease (str): The disease input by the user.
            k (int): Number of top recommendations to return.

        Returns:
            dict: A dictionary containing recommended and avoid foods.
        """
        # Generate embedding for the query (disease)
        query_embedding = model.encode([disease])

        # Perform similarity search using FAISS
        distances, indices = index.search(query_embedding, k)

        # Get top recommendations
        top_recommendations = df.iloc[indices[0]]

        # Filter by label
        recommend_foods = top_recommendations[top_recommendations["label"] == 1]["food_entity"].tolist()
        avoid_foods = top_recommendations[top_recommendations["label"] == -1]["food_entity"].tolist()

        return {"recommend": recommend_foods, "avoid": avoid_foods}

    # Step 3: Initialize the Groq client
    client = Groq(api_key='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')

    # Step 4: Define the reasoning function
    def generate_reasoning(disease: str, recommendations: dict):
        """
        Generate reasoning and summary using Groq's API.

        Args:
            disease (str): The disease input by the user.
            recommendations (dict): A dictionary containing recommended and avoid foods.

        Returns:
            dict: A dictionary containing the reasoning and summary.
        """
        # Prepare the prompt
        prompt = (
            f"For a patient with {disease}, the system recommends eating {recommendations['recommend']} and avoiding {recommendations['avoid']}. "
            f"Can you explain why these recommendations are made and provide additional medical advice? "
            f"Please provide your reasoning inside <think> tags and the final summary/recommendations after the </think> tag."
        )

        # Generate the response using Groq's API
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",  # Use the desired model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful, respectful and honest medical assistant. "
                        "Always answer as helpfully as possible, while being safe. "
                        "Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. "
                        "Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. "
                        "If you don't know the answer to a question, please don't share false information."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,  # Control the randomness of the output
            max_tokens=4096,  # Maximum number of tokens to generate
            top_p=0.95,  # Nucleus sampling parameter
            stream=False,  # Set to False for a single response
            stop=None,  # No specific stop tokens
        )

        # Extract the response
        response = completion.choices[0].message.content

        # Split the response into reasoning and summary
        if "<think>" in response and "</think>" in response:
            reasoning = response.split("<think>")[1].split("</think>")[0].strip()
            summary = response.split("</think>")[1].strip()
        else:
            reasoning = "No reasoning provided."
            summary = response.strip()

        return {"reasoning": reasoning, "summary": summary}

    # Step 5: Streamlit UI
    st.sidebar.title("Settings")
    disease = st.sidebar.text_input("Enter the disease (e.g., diabetes):", "diabetes")
    k = st.sidebar.slider("Number of recommendations:", min_value=1, max_value=10, value=5)

    # Step 6: Get recommendations and reasoning
    if st.sidebar.button("Get Recommendations"):
        with st.spinner("Generating recommendations..."):
            recommendations = recommend_foods(disease, k)
            result = generate_reasoning(disease, recommendations)

        # Display results
        st.subheader(f"Recommendations for {disease}:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🍎 Foods to Eat")
            for food in recommendations["recommend"]:
                st.markdown(f"- {food}")
        with col2:
            st.markdown("### 🚫 Foods to Avoid")
            for food in recommendations["avoid"]:
                st.markdown(f"- {food}")

        st.markdown("---")
        st.subheader("Reasoning")
        st.markdown(result["reasoning"])

        st.markdown("---")
        st.subheader("Summary and Recommendations")
        st.markdown(result["summary"])

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ by NutriMumbai AI")

# Authentication routing
if not st.session_state['logged_in']:
    if st.session_state['current_page'] == 'login':
        login.app()
    elif st.session_state['current_page'] == 'register':
        register.app()
else:
    main_app()