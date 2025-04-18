import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import requests
import plotly.express as px  # This import is correct
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

# Page configuration
st.set_page_config(
    page_title="Personal Library Manager System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main_header {
            font-size: 3rem !important;
            color: #1E3A8A;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }      
        .sub_header {
            font-size: 1.5rem !important;
            color: #3B82F6;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }     
        .footer {
            text-align: center;
            padding: 2rem;
            font-size: 1rem;
            color: #555555;
            background-color: #F3F4F6;
            border-top: 2px solid #3B82F6;
        }
        .form-label {
            font-size: 1.2rem;
            color: #1E40AF;
        }
        .streamlit-button {
            background-color: #3B82F6 !important;
            color: white !important;
            font-weight: bold;
        }
        .book-card {
            padding: 1rem;
            background-color: #F3F4F6;
            border-left: 5px solid #3B82F6;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }
        .read-badge {
            padding: 0.5rem 1rem;
            background-color: #10B981;
            color: white;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .unread-badge {
            padding: 0.5rem 1rem;
            background-color: #EF4444;
            color: white;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Load Lottie
def load_lottieur(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return None

# Init state
for key in ['library', 'search_results', 'book_added', 'book_removed', 'current_view']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'library' or key == 'search_results' else False if 'book' in key else 'library'

# Load/save library from JSON
def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as f:
            try:
                st.session_state.library = json.load(f)
            except json.JSONDecodeError:
                st.session_state.library = []

def save_library():
    try:
        with open('library.json', 'w') as f:
            json.dump(st.session_state.library, f, indent=4)
    except Exception as e:
        st.error(f"Error saving library: {str(e)}")

# Add/remove books
def add_book(title, author, publication_year, genre, read_status):
    st.session_state.library.append({
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

# Search
def search_books(term, search_by):
    term = term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Stats
def get_library_stats():
    total = len(st.session_state.library)
    read = sum(1 for b in st.session_state.library if b['read_status'])
    percent = (read / total) * 100 if total else 0
    genres = {}
    authors = {}
    decades = {}
    for b in st.session_state.library:
        genres[b['genre']] = genres.get(b['genre'], 0) + 1
        authors[b['author']] = authors.get(b['author'], 0) + 1
        decade = (b['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1
    return {
        'total_books': total,
        'read_books': read,
        'percent_read': percent,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items()))
    }

# Charts
def create_visualizations(stats):
    if stats['total_books'] == 0:
        return

    pie_fig = go.Figure(data=[go.Pie(
        labels=['Read', 'Unread'],
        values=[stats['read_books'], stats['total_books'] - stats['read_books']],
        hole=0.4,
        marker=dict(colors=['#10B981', '#EF4444']),
        textinfo='percent+label'
    )])
    pie_fig.update_layout(title='Read vs Unread Books')
    st.plotly_chart(pie_fig, use_container_width=True)

    if stats['genres']:
        df_genres = pd.DataFrame({'Genre': list(stats['genres'].keys()), 'Count': list(stats['genres'].values())})
        fig = px.bar(df_genres, x='Genre', y='Count', color='Count', color_continuous_scale='Blues')
        fig.update_layout(title='Books by Genre')
        st.plotly_chart(fig, use_container_width=True)

    if stats['decades']:
        df_decades = pd.DataFrame({'Decade': list(stats['decades'].keys()), 'Count': list(stats['decades'].values())})
        fig = px.line(df_decades, x='Decade', y='Count', markers=True)
        fig.update_layout(title='Books by Decade')
        st.plotly_chart(fig, use_container_width=True)

# Load data
load_library()
st.title("📚 Personal Library Manager")

# Sidebar
st.sidebar.header("📖 Navigation")
lottie_url = "https://assets.lottielibrary.com/l/books.json"
animation = load_lottieur(lottie_url)
if animation:
    st.sidebar.lottie(animation, height=150)

choice = st.sidebar.radio("Select view", ["View Library", "Add Book", "Search Books", "Library Statistics"])

if choice == "View Library":
    st.subheader("📚 Your Library")
    if not st.session_state.library:
        st.info("Library is empty. Add some books.")
    else:
        for i, book in enumerate(st.session_state.library):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                    <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book['read_status'] else "unread-badge"}'>
                    {"Read" if book["read_status"] else "Unread"}</span></p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("❌", key=f"remove_{i}"):
                    remove_book(i)
                    st.experimental_rerun()

elif choice == "Add Book":
    st.subheader("➕ Add a New Book")
    with st.form("book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title")
            author = st.text_input("Author")
            year = st.number_input("Year", 1800, datetime.datetime.now().year, 2024)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Biography", "Science Fiction", "Mystery", "Romance", "Horror", "Fantasy"])
            status = st.radio("Read?", ["Read", "Unread"], horizontal=True)
        submitted = st.form_submit_button("Add Book")
        if submitted and title and author:
            add_book(title, author, year, genre, status == "Read")
            st.success("Book added!")

elif choice == "Search Books":
    st.subheader("🔍 Search Your Library")
    col1, col2 = st.columns(2)
    with col1:
        search_by = st.selectbox("Search by", ["Title", "Author", "Genre"])
    with col2:
        term = st.text_input("Search term")
    if st.button("Search"):
        search_books(term, search_by)
        st.success(f"Found {len(st.session_state.search_results)} result(s)")
    for book in st.session_state.search_results:
        st.markdown(f"""
            <div class='book-card'>
            <h3>{book['title']}</h3>
            <p><strong>Author:</strong> {book['author']}</p>
            <p><strong>Year:</strong> {book['publication_year']}</p>
            <p><strong>Genre:</strong> {book['genre']}</p>
            <p><span class='{"read-badge" if book['read_status'] else "unread-badge"}'>
            {"Read" if book["read_status"] else "Unread"}</span></p>
            </div>
        """, unsafe_allow_html=True)

elif choice == "Library Statistics":
    st.subheader("📊 Statistics")
    if not st.session_state.library:
        st.warning("Library is empty. Add some books to see stats.")
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", stats['total_books'])
        col2.metric("Read", stats['read_books'])
        col3.metric("Read %", f"{stats['percent_read']:.1f}%")
        create_visualizations(stats)

st.markdown("---")
st.markdown("<div class='footer'>© 2025 Arsala Rana — Personal Library Manager</div>", unsafe_allow_html=True)
