import streamlit as st
import requests
import pandas as pd
import time

# --- Helper Function to Fetch DR ---
def get_domain_rating(domain):
    url = "https://api.ahrefs.com/v3/public/domain-rating-free"
    params = {
        "target": domain,
        "output": "json"
    }
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            dr = data.get("domain_rating", {}).get("domain_rating", "N/A")
            
            # Convert float to integer if a valid number is returned
            if isinstance(dr, (float, int)):
                return int(dr)
            return dr
            
        elif response.status_code == 429:
            return "Rate Limited (429)"
        else:
            return f"Error HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return "Connection Error"

# --- Main Streamlit App UI ---
st.set_page_config(page_title="Ahrefs Free DR Checker", page_icon="🔗", layout="centered")
st.title("🔗 Ahrefs Free Domain Rating Checker")
st.markdown("Check the Domain Rating (DR) of any website.")

# Create tabs for Single and Batch processing
tab1, tab2 = st.tabs(["Single URL", "Batch Check"])

# --- Tab 1: Single URL Checker ---
with tab1:
    st.subheader("Check a Single Domain")
    single_url = st.text_input("Enter a domain or URL (e.g., ahrefs.com):", placeholder="https://www.example.com")
    
    if st.button("Check DR", key="btn_single", type="primary"):
        if single_url:
            with st.spinner(f"Fetching Domain Rating for {single_url}..."):
                dr = get_domain_rating(single_url.strip())
                
                # Check if the result is a valid number (now guaranteed to be an integer)
                if isinstance(dr, int):
                    # Display the success message
                    # st.success(f"**{single_url}** has a Domain Rating of: **{dr}**")
                    
                    # Display the exact same table interface as the bulk check
                    df_single = pd.DataFrame([{"Target URL": single_url.strip(), "Domain Rating": dr}])
                    st.dataframe(df_single, use_container_width=True)
                else:
                    st.error(f"Could not retrieve DR. Status: {dr}")
        else:
            st.warning("Please enter a valid URL.")

# --- Tab 2: Batch URL Checker ---
with tab2:
    st.subheader("Check Multiple Domains")
    st.markdown("Enter multiple domains below (one per line). You can add upto 50 urls at a time.")
    
    batch_urls = st.text_area("Enter domains here:", height=200, placeholder="ahrefs.com\ngoogle.com\nstripe.com")
    
    if st.button("Check Batch DR", key="btn_batch", type="primary"):
        # Clean the input list and remove empty lines
        urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
        
        if not urls:
            st.warning("Please enter at least one URL.")
        else:
            results = []
            
            # Setup progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, url in enumerate(urls):
                status_text.text(f"Fetching DR for {url}... ({i+1}/{len(urls)})")
                dr = get_domain_rating(url)
                
                results.append({
                    "Target URL": url, 
                    "Domain Rating": dr
                })
                
                # Update progress
                progress_bar.progress((i + 1) / len(urls))
                
                # Sleep to respect rate limits (1.5 seconds for safer bulk processing)
                if i < len(urls) - 1:
                    time.sleep(1.5)
                
            status_text.text("Batch processing complete!")
            
            # Display results in a Pandas DataFrame
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Allow users to download the results as a CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name="domain_ratings.csv",
                mime="text/csv",
            )
            
st.markdown("---")
st.caption("Data powered by Ahrefs. According to the [Ahrefs License Terms](http://ahrefs.com/legal/domain-rating-license), if you display this data publicly, attribution is required: *Domain Rating by Ahrefs*.")
