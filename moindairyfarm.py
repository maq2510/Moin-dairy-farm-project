import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import io

# Page configuration
st.set_page_config(
    page_title="Moin Dairy Farm",
    page_icon="🐄",
    layout="wide",
)


# Logo and header
st.title("Moin Dairy Farm Customer Details")
st.header("Enter Customer Information")

# Function to update the current date dynamically
@st.cache(suppress_st_warning=True, ttl=60)  # Cache the function for 60 seconds
def update_current_date():
    return datetime.today().strftime("%d/%B/%Y")

# Input fields
customer_name = st.text_input("Customer Name", "")
open_close_status = st.radio("Open/Close Status", ["Open", "Close"])

# Check if the customer is open or closed
if open_close_status == "Open":
    frequency = st.radio("Frequency", ["Monthly", "Daily"])
    liters_purchased = st.selectbox("Liters of Milk Purchased", [i * 0.5 for i in range(1, 51)])
    rate_per_liter_options = [50, 60, 70]
    rate_per_liter = st.selectbox("Rate per Liter (INR)", rate_per_liter_options)

    # Calculate the bill amount based on liters purchased and rate per liter
    bill_amount_rupees = liters_purchased * rate_per_liter
    if frequency == "Monthly":
        bill_amount_rupees *= 30  # Assuming it's for a month

    st.write(f"Bill Amount (INR): {bill_amount_rupees:.2f}")

    # Payment status (Paid or Due)
    if frequency == "Monthly":
        payment_status = "Monthly"
    else:
        payment_status = st.radio("Payment Status", ["Paid", "Due"])

    # Remark
    if frequency == "Monthly":
        remark = ""
    else:
        remark = st.text_input("Remark", "")

    # Current date
    current_date = update_current_date()
    st.write(f"Current Date: {current_date}")

    # Submit button for "Open" customers
    if st.button("Submit"):
        # Save customer details to a DataFrame
        data = {
            "Entry No": [1],  # Start index from 1
            "Customer Name": [customer_name],
            "Open/Close": [open_close_status],
            "Frequency": [frequency],
            "Liters Purchased": [liters_purchased],
            "Rate per Liter (INR)": [rate_per_liter],
            "Bill Amount (INR)": [bill_amount_rupees],
            "Payment Status": [payment_status],
            "Remark": [remark],
            "Date": [current_date],  # Add the current date
        }
        new_entry = pd.DataFrame(data)

        # Check if the Excel file exists, if not, create it
        try:
            existing_records = pd.read_excel("customer_records.xlsx")
            entry_no = existing_records["Entry No"].max() + 1  # Increment the entry number
            new_entry["Entry No"] = entry_no

            # Check if the month has changed
            if not pd.isnull(existing_records["Date"]).any():
                last_date = pd.to_datetime(existing_records["Date"]).max()
                if last_date.month != pd.to_datetime(current_date).month:
                    # Create a new DataFrame for the next month
                    updated_records = new_entry
                else:
                    updated_records = pd.concat([existing_records, new_entry], ignore_index=True)
            else:
                updated_records = new_entry

        except FileNotFoundError:
            updated_records = new_entry

        # Save the DataFrame to an Excel file
        updated_records.to_excel("customer_records.xlsx", index=False)

        # Show success message
        st.success("Customer details saved successfully!")

else:
    # Submit button for "Close" customers
    if st.button("Close Customer"):
        # Save customer details to a DataFrame for "Closed" customer
        data = {
            "Entry No": [1],  # Start index from 1
            "Customer Name": [customer_name],
            "Open/Close": [open_close_status],
            "Frequency": ["na"],
            "Liters Purchased": ["na"],
            "Rate per Liter (INR)": ["na"],
            "Bill Amount (INR)": ["na"],
            "Payment Status": ["na"],
            "Remark": ["na"],
            "Date": [datetime.today().strftime("%d/%B/%Y")],  # Add the current date
        }
        new_entry = pd.DataFrame(data)

        # Check if the Excel file exists, if not, create it
        try:
            existing_records = pd.read_excel("customer_records.xlsx")
            entry_no = existing_records["Entry No"].max() + 1  # Increment the entry number
            new_entry["Entry No"] = entry_no
            updated_records = pd.concat([existing_records, new_entry], ignore_index=True)

        except FileNotFoundError:
            updated_records = new_entry

        # Save the DataFrame to an Excel file
        updated_records.to_excel("customer_records.xlsx", index=False)

        # Show success message
        st.success("Customer status updated to 'Close'!")

# Clear button for incorrect entry
if st.button("Clear"):
    try:
        existing_records = pd.read_excel("customer_records.xlsx")
        if not existing_records.empty:
            updated_records = existing_records.iloc[:-1]  # Remove the last row

            # Save the DataFrame to an Excel file
            updated_records.to_excel("customer_records.xlsx", index=False)

            # Show success message
            st.success("Last entry cleared successfully!")

    except FileNotFoundError:
        st.warning("No customer records found. Start by entering new customer details.")

# Download link for Excel file
def get_table_download_link(df):
    # Create a BytesIO buffer to hold the Excel file
    buffer = io.BytesIO()
    # Save the DataFrame to the buffer as an Excel file
    df.to_excel(buffer, index=False)
    # Rewind the buffer to the beginning
    buffer.seek(0)
    # Encode the buffer to Base64 for download
    b64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="customer_records.xlsx">Download Customer Records</a>'

# Display existing customer records for the current date
st.subheader("Customer Records for " + datetime.today().strftime("%d/%B/%Y"))
try:
    existing_records = pd.read_excel("customer_records.xlsx")
    existing_records.set_index("Entry No", inplace=True)  # Set "Entry No" as the index
    if "Date" in existing_records.columns:
        st.dataframe(existing_records.drop(columns=["Date"]))  # Drop the "Date" column from display
    else:
        st.dataframe(existing_records)

    # Show the download link if records are available
    st.markdown(get_table_download_link(existing_records), unsafe_allow_html=True)

except FileNotFoundError:
    st.warning("No customer records found. Start by entering new customer details.")
