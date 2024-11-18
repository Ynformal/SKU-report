import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

# Sample DataFrame for illustration
# Replace this with your actual data loaded from CSV
data = pd.DataFrame({
    'date': pd.date_range(start="2024-01-01", periods=30, freq='D'),
    'cost': [i * 10 for i in range(30)],
    'NB2Bs': [i * 5 for i in range(30)],
    'nB2B CPA': [i * 2 for i in range(30)]
})

# Ensure 'date' is the index if needed for the line chart
data.set_index('date', inplace=True)

# Use Streamlit's line_chart method to plot the data
st.title("SKU Performance Line Chart")

# Customize line chart
st.line_chart(
    data,  # Automatically uses the 'date' index as the x-axis
    y=["cost", "NB2Bs", "nB2B CPA"],  # Define columns for y-axis
    color=["#1f77b4", "#ff7f0e", "#2ca02c"],  # Set specific colors for each line
    use_container_width=True  # Make sure it fits the container width
)

# Load external CSS file from the main folder
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    try:
        # Read CSV from file-like object with semicolon delimiter
        data = pd.read_csv(io.StringIO(file.getvalue().decode('utf-8')), delimiter=';')
        
        # Strip any leading/trailing whitespace from column names
        data.columns = data.columns.str.strip()

        # Debugging: Print the column names to check for discrepancies
        st.write("Columns in the uploaded file:", data.columns)

        # Ensure 'date' column is present
        if 'date' not in data.columns:
            raise ValueError("The 'date' column is missing from the CSV file.")
        
        # Ensure 'cost' column is present
        if 'cost' not in data.columns:
            raise ValueError("The 'cost' column is missing from the CSV file.")
        
        # Convert 'date' column to datetime, with updated format for DD.MM.YYYY
        data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y', dayfirst=True)
        
        return data
    except UnicodeDecodeError:
        # Fallback if the file isn't UTF-8 encoded
        data = pd.read_csv(io.StringIO(file.getvalue().decode('latin1')), delimiter=';')
        data.columns = data.columns.str.strip()
        data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y', dayfirst=True)
        return data
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return None  # Return None to prevent further processing if there was an error
        
# Main Streamlit app
def main():
    st.title("Google Ads SKU Performance Dashboard")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        # Load the data
        data = load_data(uploaded_file)

        # Ensure data was loaded correctly
        if data is None:
            return
        
        # Ensure required columns exist
        required_columns = {'date', 'SKU', 'cost', 'NB2Bs', 'nB2B CPA'}
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            st.error(f"The uploaded file must contain the following columns: {', '.join(missing_columns)}")
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
        filtered_data = data[(
            data['SKU'] == selected_sku) &
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
