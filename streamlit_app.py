import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load CSV data
@st.cache_data  # Updated caching method
def load_data(file_path):
    try:
        # Try reading the file with UTF-8 encoding
        data = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to Latin-1 encoding if UTF-8 fails
        data = pd.read_csv(file_path, encoding='latin1')
    # Ensure the 'date' column is in datetime format
    data['date'] = pd.to_datetime(data['date'])
    return data

# Main Streamlit app
def main():
    st.title("Google Ads SKU Performance Dashboard")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        # Load the data
        data = load_data(uploaded_file)

        # Ensure required columns exist
        required_columns = {'date', 'SKU', 'cost', 'NB2Bs', 'nB2B CPA'}
        if not required_columns.issubset(data.columns):
            st.error(f"The uploaded file must contain the following columns: {required_columns}")
            return
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # SKU selector
        skus = data['SKU'].unique()
        selected_sku = st.sidebar.selectbox("Select SKU", options=skus)
        
        # Date range selector
        min_date = data['date'].min()
        max_date = data['date'].max()
        start_date, end_date = st.sidebar.date_input(
            "Select date range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date,
        )
        
        # Filter data based on SKU and date range
        filtered_data = data[
            (data['SKU'] == selected_sku) &
            (data['date'] >= pd.Timestamp(start_date)) &
            (data['date'] <= pd.Timestamp(end_date))
        ]

        # Ensure there's data to show
        if filtered_data.empty:
            st.warning("No data available for the selected SKU and date range.")
        else:
            # Plotting section
            st.subheader(f"Performance for SKU: {selected_sku}")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(filtered_data['date'], filtered_data['cost'], label='Cost', marker='o')
            ax.plot(filtered_data['date'], filtered_data['NB2Bs'], label='NB2Bs', marker='s')
            ax.plot(filtered_data['date'], filtered_data['nB2B CPA'], label='nB2B CPA', marker='^')
            ax.set_title("Daily Performance Metrics")
            ax.set_xlabel("Date")
            ax.set_ylabel("Values")
            ax.legend()
            ax.grid(True)
            
            # Display plot
            st.pyplot(fig)

            # Display filtered data
            st.subheader("Filtered Data")
            st.dataframe(filtered_data)
    else:
        st.info("Please upload a CSV file to get started.")

if __name__ == "__main__":
    main()
