import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import io

# Function to update the current date dynamically
@st.cache(suppress_st_warning=True, ttl=60)  # Cache the function for 60 seconds
def update_current_date():
    return datetime.today().strftime("%d/%B/%Y")

# Function to save DataFrame to Excel file
def save_to_excel(df, file_name):
    df.to_excel(file_name, index=True)  # Include index in the Excel file

# Function to load DataFrame from Excel file
def load_from_excel(file_name):
    try:
        df = pd.read_excel(file_name)
        if not df.empty:
            df.set_index("Entry No", inplace=True)  # Set "Entry No" as the index
        return df
    except FileNotFoundError:
        return pd.DataFrame()  # Return an empty DataFrame if the file doesn't exist


# Function to get a download link for an Excel file
def get_table_download_link(df):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="customer_records.xlsx">Download Customer Records</a>'

# Page configuration
st.set_page_config(
    page_title="Moin Dairy Farm",
    page_icon="🐄",
    layout="wide",
)

# Logo and header
st.title("Moin Dairy Farm Customer Details")
st.header("Enter Customer Information")

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
        # Load existing customer records
        existing_records = load_from_excel("customer_records.xlsx")

        # Save customer details to a DataFrame
        data = {
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

        # Check if there are existing records
        if not existing_records.empty:
            # Increment the entry number and set it for the new entry
            new_entry["Entry No"] = existing_records.index.max() + 1

            # Concatenate the new entry with existing records
            updated_records = pd.concat([existing_records, new_entry], ignore_index=True)
        else:
            # If no existing records, set the entry number to 1 for the new entry
            new_entry["Entry No"] = 1
            updated_records = new_entry

        # Save the DataFrame to an Excel file
        save_to_excel(updated_records, "customer_records.xlsx")

        # Show success message
        st.success("Customer details saved successfully!")

else:
    # Submit button for "Close" customers
    if st.button("Close Customer"):
        # Load existing customer records
        existing_records = load_from_excel("customer_records.xlsx")

        # Save customer details to a DataFrame for "Closed" customer
        data = {
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

        # Check if there are existing records
        if not existing_records.empty:
            # Increment the entry number and set it for the new entry
            new_entry["Entry No"] = existing_records.index.max() + 1

            # Concatenate the new entry with existing records
            updated_records = pd.concat([existing_records, new_entry], ignore_index=True)
        else:
            # If no existing records, set the entry number to 1 for the new entry
            new_entry["Entry No"] = 1
            updated_records = new_entry

        # Save the DataFrame to an Excel file
        save_to_excel(updated_records, "customer_records.xlsx")

        # Show success message
        st.success("Customer status updated to 'Close'!")

# Clear button for specific row
if st.button("Clear"):
    try:
        # Load existing customer records
        existing_records = load_from_excel("customer_records.xlsx")

        # Show the list of available entry numbers for the user to choose which row to clear
        selected_entry_no = st.selectbox("Select Entry No to Clear", existing_records.index.tolist())

        # Filter out the row to clear
        updated_records = existing_records.drop(index=selected_entry_no)

        # Re-index the DataFrame to rearrange the "Entry No"
        updated_records.reset_index(drop=True, inplace=True)
        updated_records.index += 1  # Start the "Entry No" from 1

        # Save the DataFrame to an Excel file
        save_to_excel(updated_records, "customer_records.xlsx")

        # Show success message
        st.success(f"Entry No {selected_entry_no} cleared successfully!")

    except FileNotFoundError:
        st.warning("No customer records found. Start by entering new customer details.")

# Display existing customer records for the current date
st.subheader("Customer Records for " + datetime.today().strftime("%d/%B/%Y"))
try:
    existing_records = load_from_excel("customer_records.xlsx")

    # Show the updated customer records
    if not existing_records.empty:
        if "Date" in existing_records.columns:
            st.dataframe(existing_records.drop(columns=["Date"]))  # Drop the "Date" column from display
        else:
            st.dataframe(existing_records)

        # Show the download link if records are available
        st.markdown(get_table_download_link(existing_records), unsafe_allow_html=True)
    else:
        st.warning("No customer records found. Start by entering new customer details.")

except FileNotFoundError:
    st.warning("No customer records found. Start by entering new customer details.")
