import pandas as pd
import streamlit as st
import io
import plotly.graph_objects as go

@st.cache_data
def load_data(file):
    try:
        # Read CSV from file-like object with semicolon delimiter
        data = pd.read_csv(io.StringIO(file.getvalue().decode('utf-8')), delimiter=';')
        data.columns = data.columns.str.strip()

        # Ensure required columns
        if 'date' not in data.columns or 'cost' not in data.columns:
            raise ValueError("The CSV file must include 'date' and 'cost' columns.")

        # Convert date to datetime
        data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y', dayfirst=True)
        return data
    except UnicodeDecodeError:
        data = pd.read_csv(io.StringIO(file.getvalue().decode('latin1')), delimiter=';')
        data.columns = data.columns.str.strip()
        data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y', dayfirst=True)
        return data
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    st.title("Google Ads SKU Performance Dashboard")
    
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        if data is None:
            return

        required_columns = {'date', 'SKU', 'cost', 'NB2Bs', 'nB2B CPA'}
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            st.error(f"The file is missing these columns: {', '.join(missing_columns)}")
            return

        st.sidebar.header("Filters")
        skus = data['SKU'].unique()
        selected_sku = st.sidebar.selectbox("Select SKU", options=skus)
        
        min_date, max_date = data['date'].min(), data['date'].max()
        start_date, end_date = st.sidebar.date_input(
            "Select date range", [min_date, max_date], min_value=min_date, max_value=max_date
        )
        
        filtered_data = data[
            (data['SKU'] == selected_sku) &
            (data['date'] >= pd.Timestamp(start_date)) &
            (data['date'] <= pd.Timestamp(end_date))
        ]

        if filtered_data.empty:
            st.warning("No data available for the selected SKU and date range.")
        else:
            st.subheader(f"Performance for SKU: {selected_sku}")
            
            # Dynamic Y-Axis Selection
            metrics = st.sidebar.multiselect(
                "Select metrics to display",
                options=['cost', 'NB2Bs', 'nB2B CPA'],
                default=['cost', 'NB2Bs']
            )
            right_y_axis_metric = st.sidebar.selectbox(
                "Select metric for the right y-axis (optional)",
                options=[None] + metrics,
                index=0
            )

            if not metrics:
                st.warning("Please select at least one metric to display.")
                return
            
            # Ensure all days in range are shown
            date_range = pd.date_range(start_date, end_date)
            filtered_data = filtered_data.set_index('date').reindex(date_range).reset_index()
            filtered_data.rename(columns={'index': 'date'}, inplace=True)

            # Create the plot
            fig = go.Figure()

            # Add primary y-axis metrics
            for metric in metrics:
                if metric != right_y_axis_metric:
                    fig.add_trace(go.Scatter(
                        x=filtered_data['date'], 
                        y=filtered_data[metric],
                        mode='lines+markers',
                        name=metric,
                        yaxis="y1"
                    ))

            # Add right y-axis metric
            if right_y_axis_metric:
                fig.add_trace(go.Scatter(
                    x=filtered_data['date'], 
                    y=filtered_data[right_y_axis_metric],
                    mode='lines+markers',
                    name=f"{right_y_axis_metric} (Right Axis)",
                    yaxis="y2"
                ))

            # Update layout for dual y-axes
            fig.update_layout(
                title="Daily Performance Metrics",
                xaxis=dict(title="Date", tickformat="%d-%b"),
                yaxis=dict(title="Primary Metrics", titlefont=dict(color="blue")),
                yaxis2=dict(
                    title="Secondary Metric",
                    titlefont=dict(color="red"),
                    overlaying="y",
                    side="right"
                ),
                legend=dict(title="Metrics"),
                template="plotly_white",
                width=1500,
                height=700
            )
            
            # Display plot
            st.plotly_chart(fig, use_container_width=False)

            # Filtered data table with hidden columns
            st.subheader("Filtered Data")
            columns_to_hide = ['SKU']  # Example: Hide SKU column
            visible_columns = [col for col in filtered_data.columns if col not in columns_to_hide]
            st.dataframe(filtered_data[visible_columns])
    else:
        st.info("Please upload a CSV file to get started.")

if __name__ == "__main__":
    main()
