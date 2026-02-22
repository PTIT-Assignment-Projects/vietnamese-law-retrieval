import streamlit as st
import pandas as pd
from src.search_engine import SearchEngine
from src.indexing.elasticsearch_indexing import ElasticSearchIndexing
from src.util import constant

class LawRetrievalApp:
    def __init__(self):
        self._setup_page()
        self._setup_styles()
        self.search_engine, self.es_engine = self._init_engines()

    def _setup_page(self):
        st.set_page_config(
            page_title="Vietnamese Law Retrieval System",
            page_icon="⚖️",
            layout="wide"
        )

    def _setup_styles(self):
        st.markdown("""
        <style>
            .main {
                background-color: #f5f7f9;
            }
            .stButton>button {
                width: 100%;
                border-radius: 5px;
                height: 3em;
                background-color: #007bff;
                color: white;
            }
            .result-card {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 20px;
                border-left: 5px solid #007bff;
            }
            .score-badge {
                background-color: #e7f3ff;
                color: #007bff;
                padding: 4px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 0.9em;
            }
            .doc-id {
                color: #6c757d;
                font-size: 0.8em;
            }
        </style>
        """, unsafe_allow_html=True)

    @st.cache_resource(_self=True)
    def _init_engines(_self):
        search_engine = SearchEngine()
        try:
            search_engine.load_prebuilt_index()
        except Exception as e:
            st.warning(f"Note: Some local models might not be built yet. Error: {e}")
        
        try:
            es_engine = ElasticSearchIndexing()
        except Exception as e:
            st.error(f"Failed to connect to Elasticsearch: {e}")
            es_engine = None
            
        return search_engine, es_engine

    def _render_sidebar(self):
        with st.sidebar:
            st.header("Configuration")
            method = st.selectbox(
                "Retrieval Method",
                options=[
                    "Boolean",
                    "Vector Space Model (VSM)",
                    "BM25",
                    "Elasticsearch (Normal)",
                    "Elasticsearch (Processed)"
                ],
                index=2
            )
            top_n = st.number_input("Top N Results", min_value=1, max_value=100, value=10)
            st.divider()
            st.info("This demo retrieves documents from the Vietnamese law corpus.")
            return method, top_n

    def _perform_search(self, query, method, top_n):
        results = []
        with st.spinner(f"Searching using {method}..."):
            if method == "Boolean":
                results = self.search_engine.search(query, method=constant.BOOLEAN_RETRIEVAL_NAME, top_n=top_n)
            elif method == "Vector Space Model (VSM)":
                results = self.search_engine.search(query, method=constant.VSM_MODEL_NAME, top_n=top_n)
            elif method == "BM25":
                results = self.search_engine.search(query, method=constant.BM25_MODEL_NAME, top_n=top_n)
            elif "Elasticsearch" in method:
                if self.es_engine:
                    is_normal = "Normal" in method
                    es_results = self.es_engine.search(query, top_n=top_n, is_normal_index=is_normal)
                    results = [(hit["_id"], hit["_score"]) for hit in es_results]
                else:
                    st.error("Elasticsearch engine is not available.")
        return results

    def _display_results(self, results, method):
        if results:
            st.subheader(f"Found {len(results)} results")
            for i, (doc_id, score) in enumerate(results):
                raw_text = self.search_engine.raw_documents.get(doc_id)
                if raw_text is None:
                    try:
                        raw_text = self.search_engine.raw_documents.get(int(doc_id))
                    except (ValueError, TypeError):
                        raw_text = self.search_engine.raw_documents.get(str(doc_id))
                
                if raw_text is None:
                    raw_text = "Document text not found."
                
                score_display = f"{score:.4f}" if method != "Boolean" else "N/A (Match)"
                st.markdown(f"""
                <div class="result-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span class="doc-id">Rank #{i+1} | ID: {doc_id}</span>
                        <span class="score-badge">Score: {score_display}</span>
                    </div>
                    <div style="white-space: pre-wrap;">{raw_text}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No results found for your query.")

    def run(self):
        st.title("⚖️ Vietnamese Law Retrieval")
        st.markdown("Search for legal documents using various retrieval methods.")

        method, top_n = self._render_sidebar()
        query = st.text_input("Enter your search query", placeholder="e.g., quy định về thuế thu nhập cá nhân")
        search_button = st.button("Search")

        if search_button:
            if query:
                results = self._perform_search(query, method, top_n)
                self._display_results(results, method)
            else:
                st.warning("Please enter a query first.")

        st.divider()
        st.caption("Developed for PTIT Vietnamese Law Retrieval Assignment")

if __name__ == "__main__":
    app = LawRetrievalApp()
    app.run()
