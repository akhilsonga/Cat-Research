import pandas as pd
import streamlit as st

# -----------------------------
# 0. Set Page Configuration
# -----------------------------
st.set_page_config(page_title="Beautiful Card Viewer - Categories", layout="wide")

# -----------------------------
# 1. Load Data from CSV
# -----------------------------

@st.cache_data
def load_data(file_path):
    """
    Load data from a CSV file.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Specify the path to your CSV file
csv_path = r'D:\Research_chat\arxiv_papers_category.csv'
df = load_data(csv_path)

# -----------------------------
# 2. Data Preprocessing
# -----------------------------

# Ensure necessary columns are present
required_columns = ['Title', 'Authors', 'Link', 'Description', 'PDF Link', 'HTML Link', 'Category', 'Date']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"The following required columns are missing in the CSV: {', '.join(missing_columns)}")
    st.stop()

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Handle any parsing errors
if df['Date'].isnull().any():
    st.warning("Some dates could not be parsed and will be set as NaT.")

# -----------------------------
# 3. Helper Function to Truncate Description
# -----------------------------

def truncate_description(text, max_words=200):
    """
    Truncate the input text to a maximum number of words.
    
    Args:
        text (str): The text to truncate.
        max_words (int): Maximum number of words.
        
    Returns:
        str: Truncated text.
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    else:
        return ' '.join(words[:max_words]) + '...'

# -----------------------------
# 4. Streamlit App Configuration
# -----------------------------

st.title('📚 Beautiful Card Viewer - Category Filter')

# -----------------------------
# 5. Custom CSS for Styling
# -----------------------------

custom_css = """
<style>
/* Style for the card container */
.card-container {
    background-color: #f9f9f9;
    padding: 20px;
    margin-bottom: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.card-container:hover {
    transform: scale(1.02);
}
.card-title {
    font-size: 1.5em;
    font-weight: bold;
}
.card-authors {
    font-size: 1em;
    color: #333;
    margin-top: 5px;
}
.card-date {
    font-size: 0.9em;
    color: #555;
    margin-top: 5px;
}
.card-description {
    margin-top: 10px;
    flex-grow: 1;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card-links a {
    text-decoration: none;
    color: #1e90ff;
    margin-right: 10px;
}
.card-links a:hover {
    text-decoration: underline;
}

/* Ensure all buttons in the sidebar have the same width */
[data-testid="stSidebar"] button {
    width: 100%;
    margin-bottom: 5px;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------
# 6. Sidebar with Buttons for Category Selection
# -----------------------------

# Get the unique categories from the dataframe and sort them alphabetically
categories = sorted(df['Category'].unique())

# Initialize session state to store the selected category
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = categories[0]  # Default to the first category

# Initialize session state for pagination reset when category changes
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# Display all categories as buttons in the sidebar
st.sidebar.title("📂 Categories")
for category in categories:
    # Use a unique key for each button to prevent conflicts
    if st.sidebar.button(category, key=category):
        st.session_state.selected_category = category
        st.session_state.current_page = 0  # Reset to first page when category changes

# Retrieve the selected category
selected_category = st.session_state.selected_category

# Filter the dataframe based on the selected category
filtered_df = df[df['Category'] == selected_category]

# Check if any data exists after filtering
if filtered_df.empty:
    st.warning(f"No records found for category: {selected_category}")
    st.stop()

# Sort the filtered data by 'Date' descending
filtered_df = filtered_df.sort_values(by='Date', ascending=False).reset_index(drop=True)

# -----------------------------
# 7. Pagination Setup
# -----------------------------

# Define the number of cards per page
cards_per_page = 20

# Calculate total number of pages
total_cards = len(filtered_df)
total_pages = (total_cards - 1) // cards_per_page + 1

# Function to get the current page's data
def get_page_data(df, page, cards_per_page):
    start_idx = page * cards_per_page
    end_idx = start_idx + cards_per_page
    return df.iloc[start_idx:end_idx]

# Get data for the current page
current_page_data = get_page_data(filtered_df, st.session_state.current_page, cards_per_page)

# -----------------------------
# 8. Display Cards on the Right
# -----------------------------

st.markdown(f"### 📂 Showing results for: **{selected_category}** (Page {st.session_state.current_page + 1} of {total_pages})")

# Define number of columns per row (Reduced from 3 to 2 for wider cards)
num_columns = 2
rows = (len(current_page_data) + num_columns - 1) // num_columns  # Ceiling division

for row in range(rows):
    cols = st.columns(num_columns)
    for col in range(num_columns):
        idx = row * num_columns + col
        if idx < len(current_page_data):
            item = current_page_data.iloc[idx]
            with cols[col]:
                # Handle missing links gracefully
                link = item.get('Link', '#')
                pdf_link = item.get('PDF Link', '#')
                html_link = item.get('HTML Link', '#')
                
                # Format the date
                date_str = item['Date'].strftime('%Y-%m-%d') if pd.notnull(item['Date']) else 'N/A'
                
                # Truncate the description to 200 words
                truncated_description = truncate_description(item['Description'], max_words=200)
                
                # Create the card HTML
                card_html = f"""
                <div class="card-container">
                    <div>
                        <div class="card-title">{item['Title']}</div>
                        <div class="card-authors"><strong>Authors:</strong> {item['Authors']}</div>
                        <div class="card-date"><strong>Date:</strong> {date_str}</div>
                        <div class="card-description">{truncated_description}</div>
                    </div>
                    <div class="card-links">
                        <a href="{link}" target="_blank">🔗 Visit Link</a>
                        <a href="{pdf_link}" target="_blank">📄 PDF</a>
                        <a href="{html_link}" target="_blank">🖥️ HTML</a>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

# -----------------------------
# 9. Pagination Controls
# -----------------------------

st.markdown("### Navigation")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.session_state.current_page > 0:
        if st.button("⬅️ Previous"):
            st.session_state.current_page -= 1

with col2:
    # You can add additional navigation info or leave it empty
    pass

with col3:
    if st.session_state.current_page < total_pages - 1:
        if st.button("Next ➡️"):
            st.session_state.current_page += 1

# Optional: Display progress or page info
# with st.expander("ℹ️ Show Page Information"):
st.write(f"You are on page {st.session_state.current_page + 1} of {total_pages}.")
