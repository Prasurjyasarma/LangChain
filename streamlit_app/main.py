import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Page config
st.set_page_config(
    page_title="🎮 Game Recommender",
    page_icon="🎮",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .game-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize LLM
@st.cache_resource
def init_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in .env file!")
        st.stop()
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.3
    )

llm = init_llm()

# Templates
template_1 = """You are a video game expert. Recommend 5 {genre} games similar to {type}.

Requirements:
- Only list game titles (one per line)
- No descriptions, ratings, or extra text
- Focus on critically acclaimed games
- Include both classic and modern titles

Format:
1. Game Title
2. Game Title
..."""

template_2 = """You are a gaming expert. Here are the recommended games:

{games}

For each game listed above, provide a concise description (1-2 sentences).

Format:
**Game Title**: [Description]

Note: Only describe the games from this list."""

# Prompts
prompt_temp_genre_1 = PromptTemplate(
    input_variables=["genre"],
    template=template_1,
    partial_variables={"type": ""}
)

prompt_temp_genre_2 = PromptTemplate(
    input_variables=["games"],
    template=template_2
)

# Chains
game_chain = prompt_temp_genre_1 | llm | StrOutputParser()
des_chain = prompt_temp_genre_2 | llm | StrOutputParser()

combined_chain = (
    game_chain
    | (lambda games: {
        "games": games,
        "descriptions": des_chain.invoke({"games": games})
    })
)

# UI Layout
st.markdown('<h1 class="main-header">🎮 Game Recommendation Engine</h1>', unsafe_allow_html=True)

st.markdown("### Find your next favorite game!")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Search Preferences")
    
    # Genre input
    genre = st.text_input(
        "Game Genre",
        value="RPG",
        placeholder="e.g., RPG, Action, Strategy",
        help="What type of games do you like?"
    )
    
    # Type/Reference game input
    game_type = st.text_input(
        "Similar to (Optional)",
        value="",
        placeholder="e.g., Dark Souls, Zelda",
        help="Name a game you like for better recommendations"
    )
    
    st.markdown("---")
    
    # Examples
    with st.expander("📝 Examples"):
        st.markdown("""
        **Popular Combinations:**
        - Genre: `RPG`, Similar to: `Dark Souls`
        - Genre: `Action`, Similar to: `God of War`
        - Genre: `Strategy`, Similar to: `Civilization`
        - Genre: `Platformer`, Similar to: `Hollow Knight`
        """)
    
    # Search button
    search_button = st.button("🔍 Get Recommendations", type="primary")

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Recommended Games")
    games_placeholder = st.empty()

with col2:
    st.subheader("📖 Game Details")
    descriptions_placeholder = st.empty()

# Handle search
if search_button:
    if not genre:
        st.error("⚠️ Please enter a game genre!")
    else:
        with st.spinner("🎲 Finding the best games for you..."):
            try:
                # Get recommendations
                result = combined_chain.invoke({
                    "genre": genre,
                    "type": game_type
                })
                
                # Display games list
                with games_placeholder.container():
                    st.markdown('<div class="game-card">', unsafe_allow_html=True)
                    st.markdown(result["games"])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Display descriptions
                with descriptions_placeholder.container():
                    st.markdown('<div class="game-card">', unsafe_allow_html=True)
                    st.markdown(result["descriptions"])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.success("✅ Recommendations generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try adjusting your search or check your API key.")
