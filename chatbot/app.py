# File: app.py
# Dynamic Semantic Patent Chatbot (Live Search via DuckDuckGo + Google Patents)

import streamlit as st
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup

# ---------------------- Search DuckDuckGo for Google Patent URLs ----------------------
def search_patents_duckduckgo(query, num_results=5):
    links = []
    with DDGS() as ddgs:
        results = ddgs.text(f"{query} site:patents.google.com", max_results=num_results)
        for r in results:
            if "patents.google.com" in r['href']:
                links.append(r['href'])
    return links

# ---------------------- Scrape Abstract from Google Patents ----------------------
def extract_abstract_google_patents(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        abstract = soup.find('meta', {'name': 'DC.description'})
        return abstract['content'] if abstract else "Abstract not found."
    except Exception as e:
        return f"Error fetching abstract: {str(e)}"

# ---------------------- Streamlit Chat UI ----------------------
st.set_page_config(page_title="Live Patent Chatbot", layout="wide")
st.title("🔍 Dynamic Patent Search Chatbot")
st.markdown("Enter a natural language question to find related patents live from Google Patents.")

# Maintain chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("Your Query:", placeholder="e.g., rice-based edible straws without wheat")

if st.button("Search") and query:
    st.session_state.chat_history.append({"user": query})
    st.markdown("🔎 Searching...")
    urls = search_patents_duckduckgo(query)
    results = []
    for url in urls:
        abstract = extract_abstract_google_patents(url)
        results.append((url, abstract))
    st.session_state.chat_history.append({"bot": results})

# Display chat history
for turn in st.session_state.chat_history:
    if 'user' in turn:
        st.markdown(f"**🧑 You:** {turn['user']}")
    elif 'bot' in turn:
        st.markdown("**🤖 Bot:**")
        for url, abstract in turn['bot']:
            st.markdown(f"- 🔗 [Patent Link]({url})\n\n📝 {abstract}")