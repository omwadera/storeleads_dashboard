import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load the dataset
df = pd.read_csv("has_stores_data_all_divided.csv")
# Convert 'estimated_yearly_sales' to numeric, setting non-numeric values to NaN
df['estimated_yearly_sales'] = pd.to_numeric(df['estimated_yearly_sales'], errors='coerce')

# Ensure 'assigned_to' column exists
if 'assigned_to' not in df.columns:
    df['assigned_to'] = None  # Initialize with None or empty string

# Streamlit Page Configuration
st.set_page_config(page_title="E-commerce Platform Dashboard", page_icon="📊", layout="wide")
st.title("Brands Dashboard from Store Leads")

# Sidebar Filters
st.sidebar.header("Filters")
region_filter = st.sidebar.multiselect("Select Regions", df["region"].unique(), default=df["region"].unique())
category_filter = st.sidebar.multiselect("Select Categories", df["Head_category"].unique(), default=df["Head_category"].unique())
status_filter = st.sidebar.selectbox("Select Status", df["status"].unique())

# Filter Data based on selections
filtered_df = df[
    (df["region"].isin(region_filter)) & 
    (df["Head_category"].isin(category_filter)) & 
    (df["status"] == status_filter)
]

# Display Filtered Data
if filtered_df.empty:
    st.write(f"No data available for the filters: Regions - {region_filter}, Categories - {category_filter}, Status - {status_filter}")
else:
    st.write(f"Displaying data for **{', '.join(region_filter)}** regions, **{', '.join(category_filter)}** categories, and **{status_filter}** status:")

    # Select and display specific columns in the table with 'domain' first
    columns_to_display = [
        "domain", "region", "estimated_yearly_sales", "linkedin_url", "instagram_url", "Head_category", "description", 
        "platform", "city", "state", "store_locator_url", "phones", "shipping_carriers", "assigned_to"
    ]
    
    # Display the filtered DataFrame with editable options for updating lead information
    edited_df = st.data_editor(filtered_df[columns_to_display], key="editable_table")

    # Bulk Assignment Functionality
    st.subheader("Bulk Assign Leads to Sales Team")
    
    # Group leads by region
    grouped_by_region = filtered_df.groupby('region')['domain'].apply(list).reset_index()
    
    # Select Region for Bulk Assignment
    selected_region = st.selectbox("Select Region for Bulk Assignment:", grouped_by_region['region'].tolist())
    
    if selected_region:
        leads_in_region = grouped_by_region[grouped_by_region['region'] == selected_region]['domain'].values[0]
        # st.write(f"Leads in {selected_region}:")
        # st.write(leads_in_region)

        # Adding new sales team member functionality
        if 'sales_team_members' not in st.session_state:
            st.session_state.sales_team_members = ["Yadvendra"]  # Default members

        new_member = st.text_input("Add New Sales Team Member:")
        if st.button("Add Member"):
            if new_member and new_member not in st.session_state.sales_team_members:
                st.session_state.sales_team_members.append(new_member)
                st.success(f"Added new sales team member: {new_member}")
            elif new_member in st.session_state.sales_team_members:
                st.warning("This member already exists.")

        assigned_member = st.selectbox("Assign to Sales Team Member:", st.session_state.sales_team_members) 
        
        if st.button("Assign All Leads in Selected Region"):
            # Here we update the 'assigned_to' column for all leads in the selected region.
            for lead in leads_in_region:
                edited_df.loc[edited_df['domain'] == lead, 'assigned_to'] = assigned_member  # Update the DataFrame
            st.success(f"Assigned {len(leads_in_region)} leads in {selected_region} to {assigned_member}.")

    # Update Functionality - Save changes back to the main DataFrame
    if edited_df is not None:
        df.update(edited_df)  # Update the original DataFrame with changes made in the editable table

    # Export Button for Filtered Data
    export_format = st.sidebar.selectbox("Select Export Format", ["CSV", "Excel"])
    
    if export_format == "CSV":
        st.download_button(
            label="Download Filtered Data as CSV",
            data=filtered_df[columns_to_display].to_csv(index=False),
            file_name="filtered_ecommerce_data.csv",
            mime="text/csv"
        )
    elif export_format == "Excel":
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df[columns_to_display].to_excel(writer, index=False, sheet_name='Filtered Data')
        st.download_button(
            label="Download Filtered Data as Excel",
            data=output.getvalue(),
            file_name="filtered_ecommerce_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Summary Statistics
    st.subheader("Summary Statistics")
    st.write(filtered_df.describe())

    # Data Visualizations
    st.subheader(f"Distribution of {', '.join(category_filter)} in {', '.join(region_filter)}")

    # Plot the distribution of categories within the filtered data using Plotly for interactivity
    fig1 = px.bar(filtered_df, x='Head_category', title=f"{status_filter} Distribution by Category")
    st.plotly_chart(fig1)

    # Region Distribution Chart using Seaborn
    region_counts = filtered_df['region'].value_counts()
    plt.figure(figsize=(8, 6))
    sns.barplot(x=region_counts.index, y=region_counts.values, palette="coolwarm")
    plt.title(f"Region-wise Distribution of {', '.join(category_filter)}")
    plt.xlabel("Region")
    plt.ylabel("Count")
    st.pyplot(plt)

# Footer Section
st.markdown("""
<hr>
<p style="text-align:center;">Created with Streamlit</p>
""", unsafe_allow_html=True)
