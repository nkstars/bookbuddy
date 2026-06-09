import streamlit as st
import google.generativeai as genai
import requests
import os
import time
from PIL import Image
import io

# Configure Streamlit page
st.set_page_config(
    page_title="📚 Book Recommender",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Gemini AI
def initialize_gemini():
    """Initialize Gemini AI with API key"""
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyCp0GJPcS78BSF4DP87CF-GcVI3-o9q6WM")
    genai.configure(api_key=api_key)
    # Use Gemini 2.5 (old models like gemini-pro and gemini-1.5-flash were retired in 2025)
    return genai.GenerativeModel("gemini-2.5-flash")

# Initialize the model
if 'model' not in st.session_state:
    st.session_state.model = initialize_gemini()
model = st.session_state.model

def extract_genre_and_get_recommendations(user_input):
    """Extract genre from user input and get book recommendations using Gemini AI"""
    try:
        # Check if the input is anime-related
        anime_check_prompt = f"Is this request related to anime, manga, or Japanese animation? '{user_input}'. Answer only YES or NO."
        anime_response = model.generate_content(anime_check_prompt)
        is_anime_related = "YES" in anime_response.text.upper()

        # Create appropriate prompt for recommendations
        if is_anime_related:
            prompt = f"""
            Based on this request: '{user_input}', recommend exactly 5 books that include both anime-related content AND general books that match the theme.

            Mix of recommendations:
            - 3-4 anime-related books (light novels, manga adaptations, or books about anime culture)
            - 3-4 general books that share similar themes, genres, or storytelling elements

            For each book, provide:
            1. Title (series name only, no volume numbers)
            2. Author
            3. A brief 2-3 sentence summary
            4. Genre/Category

            Format your response as:
            TITLE: [Book Title]
            AUTHOR: [Author Name]
            SUMMARY: [Brief summary]
            GENRE: [Genre]
            ---
            
            Ensure all recommendations are in English and focus on series names without volume numbers.
            """
        else:
            prompt = f"""
            Based on this request: '{user_input}', recommend exactly 5 books.

            For each book, provide:
            1. Title (series name only, no volume numbers)
            2. Author
            3. A brief 2-3 sentence summary
            4. Genre/Category

            Format your response as:
            TITLE: [Book Title]
            AUTHOR: [Author Name]
            SUMMARY: [Brief summary]
            GENRE: [Genre]
            ---

            Ensure all recommendations are in English and focus on series names without volume numbers.
            """

        response = model.generate_content(prompt)
        return parse_recommendations(response.text), is_anime_related

    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return [], False
def parse_recommendations(response_text):
    """Parse the Gemini AI response into structured book data"""
    books = []
    book_blocks = response_text.split('---')
    
    for block in book_blocks:
        if block.strip():
            lines = block.strip().split('\n')
            book_data = {}
            
            for line in lines:
                if line.startswith('TITLE:'):
                    book_data['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('AUTHOR:'):
                    book_data['author'] = line.replace('AUTHOR:', '').strip()
                elif line.startswith('SUMMARY:'):
                    book_data['summary'] = line.replace('SUMMARY:', '').strip()
                elif line.startswith('GENRE:'):
                    book_data['genre'] = line.replace('GENRE:', '').strip()
            
            if 'title' in book_data and 'author' in book_data:
                books.append(book_data)
    
    return books[:5]  # Ensure exactly 5 recommendations

@st.cache_data
def get_book_cover(title, author):
    """Get book cover from OpenLibrary API"""
    try:
        # Search for the book
        search_url = f"https://openlibrary.org/search.json?title={title}&author={author}&limit=1"
        response = requests.get(search_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get('docs'):
                book = data['docs'][0]

                # Get cover ID
                cover_id = None
                if 'cover_i' in book:
                    cover_id = book['cover_i']
                elif 'isbn' in book and book['isbn']:
                    # Try to get cover by ISBN
                    isbn = book['isbn'][0]
                    cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
                    return cover_url

                if cover_id:
                    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                    return cover_url

        return None

    except Exception as e:
        return None   
        
        # Fallback: search by title only
        search_url = f"https://openlibrary.org/search.json?q={title}&limit=3"
        response = requests.get(search_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            for book in data.get('docs', []):
                if 'cover_i' in book:
                    cover_url = f"https://covers.openlibrary.org/b/id/{book['cover_i']}-M.jpg"
                    cover_response = requests.get(cover_url, timeout=5)
                    if cover_response.status_code == 200:
                        return cover_url
                        # Fallback image when no cover is available
                        return "https://via.placeholder.com/150x220?text=No+Cover"
        
        return "https://via.placeholder.com/120x160?text=No+Cover"
    except Exception as e:
        return "https://via.placeholder.com/120x160?text=No+Cover"

def display_book_card(book, index):
    """Display a book recommendation card"""
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Get and display book cover
            cover_url = get_book_cover(book['title'], book['author'])
            if cover_url:
                try:
                    st.image(cover_url, width=120)
                except:
                    st.write("📚")
            else:
                # Placeholder for books without covers
                st.markdown(
                    f"""
                    <div style="
                        width: 120px; 
                        height: 160px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 8px;
                        margin-bottom: 10px;
                    ">
                        <span style="font-size: 40px;">📚</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        
        with col2:
            st.markdown(f"### {index}. {book['title']}")
            st.markdown(f"**Author:** {book['author']}")
            if 'genre' in book:
                st.markdown(f"**Genre:** {book['genre']}")
            if 'summary' in book:
                st.markdown(f"**Summary:** {book['summary']}")
        
        st.markdown("---")

def main():
    """Main application function"""
    # Title and description
    st.markdown("# 📚 AI Book Recommender")
    st.markdown("*Get personalized book recommendations powered by AI*")
    
    # Initialize session state
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    if 'is_anime' not in st.session_state:
        st.session_state.is_anime = False
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    # Search interface
    st.markdown("### What kind of books are you looking for?")
    
    # Create columns for search bar and button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Search for books",
            placeholder="e.g., 'fantasy books with magic', 'anime like Attack on Titan', 'mystery novels'...",
            key="search_input",
            label_visibility="collapsed",
            help=None
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary")
    
    # Process search
    if search_button and user_input.strip():
        with st.spinner("🔍 Finding perfect book recommendations for you..."):
            recommendations, is_anime = extract_genre_and_get_recommendations(user_input)
            
            if recommendations:
                st.session_state.recommendations = recommendations
                st.session_state.is_anime = is_anime
                st.session_state.search_history.append(user_input)
                st.success(f"Found {len(recommendations)} great recommendations!")
            else:
                st.error("Sorry, I couldn't find any recommendations for that request. Please try a different search term.")
    
    # Display recommendations
    if st.session_state.recommendations:
        st.markdown("---")
        
        # Display each book
        for i, book in enumerate(st.session_state.recommendations, 1):
            display_book_card(book, i)
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Search again prompt
        st.info("💡 Want more recommendations? Just search for something else above!")
    else:
        # Welcome message
        st.markdown("---")
        st.markdown("## 🌟 Welcome to AI Book Recommender!")
        st.markdown("Enter your book preferences above to get personalized recommendations.")

if __name__ == "__main__":
    main()
