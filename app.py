import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime
import io

# Set page config
st.set_page_config(
    page_title="Excel Phone Data Processor", 
    page_icon="📞", 
    layout="wide"
)

# ---------- CONFIGURATION ----------
phone_columns = [
    ('Phone', 'Phone (Line Type)'),
    ('Alt Phone 1', 'Alt Phone 1 (Line Type)'),
    ('Alt Phone 2', 'Alt Phone 2 (Line Type)'),
    ('Alt Phone 3', 'Alt Phone 3 (Line Type)'),
    ('Alt Phone 4', 'Alt Phone 4 (Line Type)'),
    ('Alt Phone 5', 'Alt Phone 5 (Line Type)')
]

allowed_types = ['mobile', 'voip']
landline_types = ['landline', 'pager', 'specialservice']

# ---------- HELPER FUNCTIONS ----------
def normalize_phone(phone):
    if pd.isnull(phone) or phone == '':
        return None
    
    if isinstance(phone, float):
        try:
            phone = int(phone)
        except (ValueError, OverflowError):
            return None
    
    digits = re.sub(r'\D', '', str(phone))
    
    if len(digits) == 10:
        return digits
    elif len(digits) == 11 and digits.startswith('1'):
        return digits[1:]
    else:
        return None

def extract_valid_phones(row):
    valid_phones = []
    for phone_col, type_col in phone_columns:
        if phone_col not in row.index or type_col not in row.index:
            continue
            
        phone = normalize_phone(row[phone_col])
        phone_type = str(row[type_col]).strip().lower() if pd.notnull(row[type_col]) else ''
        
        if phone and phone_type in allowed_types:
            valid_phones.append(phone)
        if len(valid_phones) == 3:
            break
    
    result = valid_phones + [None] * (3 - len(valid_phones))
    return pd.Series(result, index=['Phone1', 'Phone2', 'Phone3'])

def extract_landlines_with_types(row):
    landlines = []
    phone_types = []
    
    for phone_col, type_col in phone_columns:
        if phone_col not in row.index or type_col not in row.index:
            continue
            
        phone = normalize_phone(row[phone_col])
        phone_type = str(row[type_col]).strip() if pd.notnull(row[type_col]) else ''
        
        if phone and phone_type.lower() in landline_types:
            landlines.append(phone)
            phone_types.append(phone_type)
        if len(landlines) == 5:
            break
    
    result_phones = landlines + [None] * (5 - len(landlines))
    result_types = phone_types + [None] * (5 - len(phone_types))
    
    return pd.Series(
        result_phones + result_types, 
        index=['Phone1', 'Phone2', 'Phone3', 'Phone4', 'Phone5', 
               'Phone1_Type', 'Phone2_Type', 'Phone3_Type', 'Phone4_Type', 'Phone5_Type']
    )

def has_valid_phones(row):
    for phone_col, type_col in phone_columns:
        if phone_col not in row.index or type_col not in row.index:
            continue
            
        phone = normalize_phone(row[phone_col])
        phone_type = str(row[type_col]).strip().lower() if pd.notnull(row[type_col]) else ''
        
        if phone and phone_type in allowed_types:
            return True
    return False

def get_match_key(row):
    apn = str(row.get('APN', '')).strip() if pd.notnull(row.get('APN')) else ''
    if apn and apn != 'nan':
        return apn
    else:
        full = str(row.get('Owner 1 Full Name', '')).strip()
        first = str(row.get('Owner 1 First Name', '')).strip()
        last = str(row.get('Owner 1 Last Name', '')).strip()
        
        if full and full != 'nan':
            return full
        else:
            name = f"{first} {last}".strip()
            return name if name != ' ' else 'NO_NAME'

def process_excel_file(df):
    """Main processing function with progress tracking"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Identify rows with valid phones
    status_text.text("🔍 Identifying rows with mobile/voip phones...")
    progress_bar.progress(10)
    
    has_phones_results = []
    for idx, row in df.iterrows():
        has_phones_results.append(has_valid_phones(row))
        if (idx + 1) % 1000 == 0:
            status_text.text(f"🔍 Processed {idx + 1:,} rows...")
    
    has_phones_mask = pd.Series(has_phones_results, index=df.index)
    rows_with_phones = df[has_phones_mask].copy()
    rows_without_phones = df[~has_phones_mask].copy()
    
    st.info(f"📱 Found {len(rows_with_phones):,} rows with mobile/voip phones")
    st.info(f"📞 Found {len(rows_without_phones):,} rows without mobile/voip phones")
    
    progress_bar.progress(30)
    
    # Step 2: Process cleaned file
    status_text.text("📱 Processing cleaned file...")
    
    df_final = pd.DataFrame()
    if not rows_with_phones.empty:
        phones_results = []
        for idx, row in rows_with_phones.iterrows():
            phones_results.append(extract_valid_phones(row))
            if len(phones_results) % 500 == 0:
                status_text.text(f"📱 Extracted phones from {len(phones_results):,} rows...")
        
        phones_df = pd.DataFrame(phones_results, index=rows_with_phones.index)
        df_with_phones = pd.concat([rows_with_phones, phones_df], axis=1)
        df_with_phones = df_with_phones.dropna(subset=['Phone1'])
        
        # FIXED: Column mapping without spaces to match Launch Control template
        column_mapping = {
            'Owner 1 First Name': 'FirstName',
            'Owner 1 Last Name': 'LastName',
            'Mail Full Address': 'MailingAddress',
            'Mail City': 'MailingCity',
            'Mail State': 'MailingState',
            'Mail Zip': 'MailingZip',
            'Parcel Full Address': 'PropertyAddress',
            'Parcel City': 'PropertyCity',
            'Parcel State': 'PropertyState',
            'Parcel Zip': 'PropertyZip',
            'APN': 'APN',
            'Parcel County': 'PropertyCounty',
            'Lot Acres': 'Acreage'
        }
        
        available_cols = [col for col in column_mapping.keys() if col in df_with_phones.columns]
        phone_cols = ['Phone1', 'Phone2', 'Phone3']
        selected_cols = available_cols + phone_cols
        
        df_cleaned = df_with_phones[selected_cols].copy()
        df_cleaned = df_cleaned.rename(columns=column_mapping)
        
        # Handle names - FIXED: Using column names without spaces
        df_cleaned['FirstName'] = df_cleaned.get('FirstName', pd.Series(dtype=object)).fillna('')
        df_cleaned['LastName'] = df_cleaned.get('LastName', pd.Series(dtype=object)).fillna('')
        
        if 'Owner 1 Full Name' in df_with_phones.columns:
            mask = (df_cleaned['FirstName'] == '') & (df_cleaned['LastName'] == '')
            if mask.any():
                df_cleaned.loc[mask, 'FirstName'] = df_with_phones.loc[mask, 'Owner 1 Full Name'].fillna('')
        
        # FIXED: Add required Email column for Launch Control
        df_cleaned['Email'] = ''
        
        # FIXED: Final columns to match Launch Control template exactly
        final_columns = [
            'FirstName', 'LastName', 'Email', 'MailingAddress', 'MailingCity', 'MailingState', 'MailingZip',
            'PropertyAddress', 'PropertyCity', 'PropertyState', 'PropertyZip',
            'Phone1', 'Phone2', 'Phone3', 'APN', 'PropertyCounty', 'Acreage'
        ]
        
        for col in final_columns:
            if col not in df_cleaned.columns:
                df_cleaned[col] = ''
        
        df_final = df_cleaned[final_columns]
    
    progress_bar.progress(60)
    
    # Step 3: Process discard file
    status_text.text("📞 Processing discard file...")
    
    df_discards_final = pd.DataFrame()
    if not rows_without_phones.empty:
        landlines_results = []
        for idx, row in rows_without_phones.iterrows():
            landlines_results.append(extract_landlines_with_types(row))
            if len(landlines_results) % 500 == 0:
                status_text.text(f"📞 Extracted landlines from {len(landlines_results):,} rows...")
        
        landlines_df = pd.DataFrame(landlines_results, index=rows_without_phones.index)
        df_discards_combined = pd.concat([rows_without_phones, landlines_df], axis=1)
        
        # Apply same column mapping - FIXED: No spaces in column names
        available_cols = [col for col in column_mapping.keys() if col in df_discards_combined.columns]
        phone_cols_discard = ['Phone1', 'Phone2', 'Phone3', 'Phone4', 'Phone5']
        phone_type_cols = ['Phone1_Type', 'Phone2_Type', 'Phone3_Type', 'Phone4_Type', 'Phone5_Type']
        df_discards_formatted = df_discards_combined[available_cols + phone_cols_discard + phone_type_cols].copy()
        df_discards_formatted = df_discards_formatted.rename(columns=column_mapping)
        
        # Handle names - FIXED: Using column names without spaces
        df_discards_formatted['FirstName'] = df_discards_formatted.get('FirstName', pd.Series(dtype=object)).fillna('')
        df_discards_formatted['LastName'] = df_discards_formatted.get('LastName', pd.Series(dtype=object)).fillna('')
        
        if 'Owner 1 Full Name' in rows_without_phones.columns:
            mask_np = (df_discards_formatted['FirstName'] == '') & (df_discards_formatted['LastName'] == '')
            if mask_np.any():
                df_discards_formatted.loc[mask_np, 'FirstName'] = rows_without_phones.loc[mask_np, 'Owner 1 Full Name'].fillna('')
        
        # FIXED: Add Email column to discard file too
        df_discards_formatted['Email'] = ''
        
        # FIXED: Column names without spaces and including Email
        ordered_discard_columns = [
            'FirstName', 'LastName', 'Email', 'MailingAddress', 'MailingCity', 'MailingState', 'MailingZip',
            'PropertyAddress', 'PropertyCity', 'PropertyState', 'PropertyZip',
            'Phone1', 'Phone1_Type', 'Phone2', 'Phone2_Type', 'Phone3', 'Phone3_Type', 
            'Phone4', 'Phone4_Type', 'Phone5', 'Phone5_Type', 'APN', 'PropertyCounty', 'Acreage'
        ]
        
        for col in ordered_discard_columns:
            if col not in df_discards_formatted.columns:
                df_discards_formatted[col] = ''
        
        df_discards_final = df_discards_formatted[ordered_discard_columns]
    
    progress_bar.progress(90)
    
    # Step 4: Generate QA report
    status_text.text("📊 Generating QA report...")
    qa_summary, qa_details = generate_qa_data(df, df_final, df_discards_final)
    
    progress_bar.progress(100)
    status_text.text("✅ Processing complete!")
    
    return df_final, df_discards_final, qa_summary, qa_details

def generate_qa_data(original_df, cleaned_df, discard_df):
    """Generate QA report data"""
    
    # Count phone types in original data
    phone_type_counts = {}
    total_phones_original = 0
    
    for phone_col, type_col in phone_columns:
        if phone_col in original_df.columns and type_col in original_df.columns:
            for idx, row in original_df.iterrows():
                phone = normalize_phone(row[phone_col])
                phone_type = str(row[type_col]).strip() if pd.notnull(row[type_col]) else ''
                if phone and phone_type:
                    total_phones_original += 1
                    if phone_type not in phone_type_counts:
                        phone_type_counts[phone_type] = 0
                    phone_type_counts[phone_type] += 1
    
    # Count mobile phones in discard file
    discard_mobile_contacts = 0
    discard_mobile_phones = 0
    
    if not discard_df.empty:
        for idx, row in discard_df.iterrows():
            contact_has_mobile = False
            for i in range(1, 6):  # Phone1 through Phone5
                phone_col = f'Phone{i}'
                type_col = f'Phone{i}_Type'
                
                if phone_col in discard_df.columns and type_col in discard_df.columns:
                    phone = row.get(phone_col)
                    phone_type = str(row.get(type_col, '')).strip()
                    
                    if pd.notnull(phone) and phone != '' and phone_type.lower() == 'mobile':
                        discard_mobile_phones += 1
                        contact_has_mobile = True
            
            if contact_has_mobile:
                discard_mobile_contacts += 1
    
    # Calculate unique contacts processed
    cleaned_contacts = len(cleaned_df) if not cleaned_df.empty else 0
    discard_contacts = len(discard_df) if not discard_df.empty else 0
    total_processed = cleaned_contacts + discard_contacts
    
    # Create summary data
    summary_data = [
        ['Total Contacts in Original File', f"{len(original_df):,}"],
        ['Contacts in Cleaned File', f"{cleaned_contacts:,}"],
        ['Contacts in Discard File', f"{discard_contacts:,}"],
        ['Total Contacts Processed', f"{total_processed:,}"],
        ['Contact Count Verification', '✅ MATCH' if len(original_df) == total_processed else '❌ MISMATCH'],
        ['', ''],
        ['Total Phone Numbers (All Types)', f"{total_phones_original:,}"],
    ]
    
    # Add phone type breakdown
    for phone_type, count in sorted(phone_type_counts.items()):
        summary_data.append([f'{phone_type} Phone Numbers', f"{count:,}"])
    
    summary_data.extend([
        ['', ''],
        ['Contacts with Mobile Phones in Discard File', f"{discard_mobile_contacts:,}"],
        ['Total Mobile Phone Numbers in Discard File', f"{discard_mobile_phones:,}"],
    ])
    
    summary = pd.DataFrame(summary_data, columns=['QA CHECK', 'RESULT'])
    
    # Placeholder for detailed missing phones (simplified for now)
    details = pd.DataFrame(columns=['FirstName', 'LastName', 'Phone 1', 'Phone 2', 'Phone 3', 'APN'])
    
    return summary, details

# ---------- STREAMLIT APP ----------
def main():
    st.title("📞 Excel Phone Data Processor")
    st.markdown("Upload your Excel file to automatically separate mobile/VoIP numbers from landlines")
    st.info("🎯 **Launch Control Compatible** - Output files match the required template format")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("**Allowed Phone Types:**")
        st.success("✅ Mobile")
        st.success("✅ VoIP")
        st.markdown("**Discard Phone Types:**")
        st.error("❌ Landline")
        st.error("❌ Pager") 
        st.error("❌ Special Service")
        
        st.markdown("---")
        st.markdown("**🎯 Launch Control Template:**")
        st.write("✅ Column names without spaces")
        st.write("✅ Email column included")
        st.write("✅ Correct column order")
        
        st.markdown("---")
        st.markdown("**Output Files:**")
        st.write("📱 Cleaned file (Mobile/VoIP)")
        st.write("📞 Discard file (Other types)")
        st.write("📊 QA Report")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an Excel file", 
        type=['xlsx', 'xls'],
        help="Upload your Excel file containing contact and phone data"
    )
    
    if uploaded_file is not None:
        try:
            # Load the file
            with st.spinner("📖 Loading Excel file..."):
                df = pd.read_excel(uploaded_file)
            
            # Display file info
            st.success(f"✅ File loaded successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", f"{len(df):,}")
            with col2:
                st.metric("Total Columns", f"{len(df.columns):,}")
            with col3:
                st.metric("File Size", f"{uploaded_file.size / 1024 / 1024:.1f} MB")
            
            # Show preview
            with st.expander("📋 Data Preview", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
                
                # Show phone columns found
                phone_cols_found = [col for col in df.columns if 'phone' in col.lower()]
                if phone_cols_found:
                    st.markdown("**Phone-related columns found:**")
                    for col in phone_cols_found[:10]:  # Show first 10
                        st.write(f"• {col}")
                    if len(phone_cols_found) > 10:
                        st.write(f"... and {len(phone_cols_found) - 10} more")
            
            # Process button
            if st.button("🚀 Process File", type="primary", use_container_width=True):
                
                # Process the file
                cleaned_df, discard_df, qa_summary, qa_details = process_excel_file(df)
                
                # Display results
                st.markdown("## 📊 Processing Results")
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📱 Cleaned Records", f"{len(cleaned_df):,}" if not cleaned_df.empty else "0")
                with col2:
                    st.metric("📞 Discard Records", f"{len(discard_df):,}" if not discard_df.empty else "0")
                with col3:
                    total_processed = (len(cleaned_df) if not cleaned_df.empty else 0) + (len(discard_df) if not discard_df.empty else 0)
                    st.metric("📋 Total Processed", f"{total_processed:,}")
                
                # QA Summary
                st.markdown("### 📋 QA Summary")
                st.dataframe(qa_summary, use_container_width=True, hide_index=True)
                
                # Download files
                st.markdown("### 📥 Download Files")
                
                # Generate filenames
                date_str = datetime.now().strftime("%b%d")
                
                # Extract state and county from data
                if not cleaned_df.empty:
                    state = cleaned_df['PropertyState'].dropna().iloc[0] if 'PropertyState' in cleaned_df.columns else 'Unknown'
                    county_raw = cleaned_df['PropertyCounty'].dropna().iloc[0] if 'PropertyCounty' in cleaned_df.columns else 'Unknown'
                    county = re.sub(r'\s+', '', str(county_raw))
                else:
                    state = "Unknown"
                    county = "Unknown"
                
                # Create download buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if not cleaned_df.empty:
                        cleaned_excel = io.BytesIO()
                        cleaned_df.to_excel(cleaned_excel, index=False, engine='openpyxl')
                        cleaned_excel.seek(0)
                        
                        st.download_button(
                            label="📱 Download Cleaned File",
                            data=cleaned_excel,
                            file_name=f"{state}{county}{date_str}LCT.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.info("No cleaned data to download")
                
                with col2:
                    if not discard_df.empty:
                        discard_excel = io.BytesIO()
                        discard_df.to_excel(discard_excel, index=False, engine='openpyxl')
                        discard_excel.seek(0)
                        
                        st.download_button(
                            label="📞 Download Discard File",
                            data=discard_excel,
                            file_name=f"{state}{county}{date_str}LandlinesNoNumber.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.info("No discard data to download")
                
                with col3:
                    # QA Report
                    qa_excel = io.BytesIO()
                    with pd.ExcelWriter(qa_excel, engine='openpyxl') as writer:
                        qa_summary.to_excel(writer, sheet_name="Summary", index=False)
                        if not qa_details.empty:
                            qa_details.to_excel(writer, sheet_name="Missing Phones", index=False)
                    qa_excel.seek(0)
                    
                    st.download_button(
                        label="📊 Download QA Report",
                        data=qa_excel,
                        file_name=f"{state}{county}{date_str}QAReport.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                # Show data previews with Launch Control compatibility check
                if not cleaned_df.empty:
                    with st.expander("📱 Cleaned Data Preview (Launch Control Compatible)", expanded=False):
                        st.success("✅ Column headers match Launch Control template")
                        st.dataframe(cleaned_df.head(20), use_container_width=True)
                        
                        # Show column mapping
                        st.markdown("**Column Headers:**")
                        col_display = st.columns(4)
                        for i, col in enumerate(cleaned_df.columns):
                            with col_display[i % 4]:
                                st.write(f"✅ {col}")
                
                if not discard_df.empty:
                    with st.expander("📞 Discard Data Preview", expanded=False):
                        st.dataframe(discard_df.head(20), use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            with st.expander("Error Details"):
                st.exception(e)
    
    else:
        st.info("👆 Please upload an Excel file to get started")
        
        # Show instructions
        with st.expander("📖 Instructions", expanded=True):
            st.markdown("""
            **How to use this app:**
            
            1. **Upload your Excel file** using the file uploader above
            2. **Review the data preview** to ensure the file loaded correctly
            3. **Click 'Process File'** to start the phone number separation
            4. **Download the results:**
               - **Cleaned File**: Contains contacts with mobile/VoIP phones (Launch Control compatible)
               - **Discard File**: Contains contacts with landlines/pagers only
               - **QA Report**: Summary and analysis of the processing
            
            **🎯 Launch Control Compatibility:**
            - Column headers without spaces (e.g., "FirstName" not "First Name")
            - Required Email column included (empty but present)
            - Columns in the exact order expected by Launch Control
            
            **Expected file format:**
            - Excel file (.xlsx or .xls)
            - Contains columns like: Phone, Phone (Line Type), Alt Phone 1, etc.
            - Phone types should be: Mobile, Voip, Landline, Pager, etc.
            """)

if __name__ == "__main__":
    main()
