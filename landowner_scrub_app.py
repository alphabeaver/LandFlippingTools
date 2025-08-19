import streamlit as st
import pandas as pd
import re
import io

# Page configuration
st.set_page_config(
    page_title="Land Owner Data Scrubber",
    page_icon="🏠",
    layout="wide"
)

# Title and description
st.title("🏠 Land Owner Data Scrubber")
st.markdown("""
Clean your land owner lists by automatically removing unwanted entities such as:
- Churches and religious organizations
- Government entities (counties, cities, townships)
- Utilities (gas, electric, water companies)
- Schools and educational institutions
- Cemeteries and hospitals
- Fire departments and emergency services
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Option to customize scrub patterns
    customize_patterns = st.checkbox("Customize Scrub Patterns", value=False)
    
    if customize_patterns:
        st.subheader("Additional Keywords to Remove")
        custom_keywords = st.text_area(
            "Enter additional keywords (one per line):",
            placeholder="association\ntrust\nfoundation"
        )

# Define default scrub patterns
def get_scrub_patterns(custom_keywords=None):
    default_patterns = [
        # Gas / Utility / Energy
        r'\bgas\b',
        r'\bgas company\b',
        r'\bgas co\b',
        r'\bgas utility\b',
        r'\butility\b',
        r'\butilities co\b',
        r'\bmunicipal utility\b',
        r'\bmunicipal electric\b',
        r'\belectric co\b',
        r'\belectric company\b',
        r'\belectric utility\b',
        r'\belectric authority\b',
        r'\belectric corp\b',
        r'\bpower co\b',
        r'\bpower company\b',
        r'\bpower authority\b',
        r'\bpower & light\b',
        r'\bpower corp\b',
        r'\benergy co\b',
        r'\benergy company\b',
        r'\brural electric\b',
        r'\brural co-op\b',
        r'\belectric co-op\b',
        r'\bwater authority\b',
        r'\bwater dept\b',
        r'\bpwr\b',
        r'\bpwr co\b',
        r'\belec\b',
        r'\btel co\b',
        r'\btelco\b',
        r'\btelephone co\b',

        # Government / Municipality
        r'\bborough of\b',
        r'\btwp\b',
        r'\btownship\b',
        r'\btown of\b',
        r'\bcity of\b',
        r'\bcounty of\b',
        r'\bcounty\b',
        r'\bcommonwealth of\b',
        r'\bstate dep\b',
        r'\bstate highway\b',
        r'\bdepartment of\b',
        r'\bdept of\b',
        r'\bdept\b',
        r'\bmunicipal\b',
        r'\bboard of\b',
        r'\bcommission\b',
        r'\bdevelopment district\b',
        r'\broad commission\b',

        # School / Education
        r'\bschool district\b',
        r'\bschool dist\b',
        r'\bsch dis\b',
        r'\bcity schools\b',
        r'\bschool system\b',

        # Fire / Emergency Services
        r'\bfire co\b',
        r'\bfire company\b',
        r'\bvolunteer fire\b',

        # Rail / Transport
        r'\b Rr Co\b',
        r'\brail car co\b',
        r'\brailway\b',
        r'\brr\b',

        # Hospitals / Health
        r'\bhospital\b',

        # Cemetery / Conservancy
        r'\bcemetery\b',
        r'\bconservation authority\b',
        r'\bconservancy\b',

        # Waste Management
        r'\bwaste management\b',

        # Churches / Religious Orgs
        r'\bchurch\b',
        r'\bcommunity church\b',
        r'\bfamily church\b',
        r'\bchurch of\b',
        r'\bbaptist\b',
        r'\bmethodist\b',

        # Development / Public Works
        r'\bpublic works\b',
        r'\bpub works\b',
        r'\bdevl\b',
        r'\bdevl co\b',
        r'\bindustrial\b',
    ]
    
    # Add custom patterns if provided
    if custom_keywords:
        custom_lines = [line.strip() for line in custom_keywords.split('\n') if line.strip()]
        for keyword in custom_lines:
            default_patterns.append(rf'\b{re.escape(keyword.lower())}\b')
    
    return default_patterns

# Function to check if a name needs scrubbing
def needs_scrub(owner_name, patterns):
    if pd.isna(owner_name):
        return False
    name_lower = str(owner_name).lower()
    return any(re.search(pattern, name_lower) for pattern in patterns)

# Main app interface
st.header("📁 Upload Your Excel File")

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=['xlsx', 'xls'],
    help="Upload your land owner Excel file to be cleaned"
)

if uploaded_file is not None:
    try:
        # Load the file
        with st.spinner("Loading your file..."):
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File loaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
        
        # Show preview of the data
        st.subheader("📊 Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        
        # Column selection
        st.subheader("🎯 Select Owner Name Column")
        
        # Try to auto-detect owner column
        potential_cols = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['owner', 'name', 'mail'])]
        
        if potential_cols:
            default_col = potential_cols[0]
        else:
            default_col = df.columns[0]
        
        selected_column = st.selectbox(
            "Choose the column containing owner names:",
            options=df.columns,
            index=list(df.columns).index(default_col),
            help="This should be the column with the landowner names you want to filter"
        )
        
        # Show sample data from selected column
        st.write("**Sample data from selected column:**")
        sample_data = df[selected_column].dropna().head(10).tolist()
        for i, sample in enumerate(sample_data, 1):
            st.write(f"{i}. {sample}")
        
        # Process the data
        if st.button("🧹 Clean Data", type="primary", use_container_width=True):
            with st.spinner("Processing your data..."):
                # Get scrub patterns
                custom_keywords_input = custom_keywords if customize_patterns else None
                patterns = get_scrub_patterns(custom_keywords_input)
                
                # Apply scrubbing
                df['needs_scrub'] = df[selected_column].apply(lambda x: needs_scrub(x, patterns))
                
                # Get results
                scrubbed_rows = df[df['needs_scrub']]
                cleaned_df = df[~df['needs_scrub']].copy()
                cleaned_df = cleaned_df.drop(columns=['needs_scrub'])
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Original Rows", len(df))
                
                with col2:
                    st.metric("Rows Removed", len(scrubbed_rows))
                
                with col3:
                    st.metric("Remaining Rows", len(cleaned_df))
                
                # Show removed entries
                if len(scrubbed_rows) > 0:
                    st.subheader("🗑️ Entries Being Removed")
                    st.write(f"The following {len(scrubbed_rows)} entries will be removed:")
                    
                    removed_names = scrubbed_rows[selected_column].dropna().tolist()
                    
                    # Show in expandable section
                    with st.expander(f"View all {len(removed_names)} removed entries"):
                        for i, name in enumerate(removed_names, 1):
                            st.write(f"{i}. {name}")
                
                # Download cleaned file
                st.subheader("💾 Download Cleaned Data")
                
                # Convert to Excel bytes
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    cleaned_df.to_excel(writer, index=False, sheet_name='Cleaned_Data')
                
                excel_data = output.getvalue()
                
                # Create download button
                original_filename = uploaded_file.name
                base_name = original_filename.rsplit('.', 1)[0]
                cleaned_filename = f"{base_name}_cleaned.xlsx"
                
                st.download_button(
                    label="📥 Download Cleaned Excel File",
                    data=excel_data,
                    file_name=cleaned_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Show preview of cleaned data
                st.subheader("📋 Cleaned Data Preview")
                st.dataframe(cleaned_df.head(), use_container_width=True)
                
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.write("Please make sure your file is a valid Excel file (.xlsx or .xls)")

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload an Excel file to get started")
    
    st.subheader("🔍 What This App Does")
    st.markdown("""
    This tool automatically identifies and removes entries that match common patterns for:
    
    **🏛️ Government Entities**
    - Counties, cities, townships
    - Municipal departments
    - State agencies
    
    **⚡ Utilities & Infrastructure**
    - Gas and electric companies
    - Water authorities
    - Telephone companies
    
    **⛪ Religious Organizations**
    - Churches of all denominations
    - Religious communities
    
    **🏫 Educational Institutions**
    - School districts
    - Educational boards
    
    **🚑 Public Services**
    - Fire departments
    - Hospitals
    - Emergency services
    
    **🪦 Other Entities**
    - Cemeteries
    - Conservation authorities
    - Waste management companies
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Land Owner Data Scrubber | Built with Streamlit"
    "</div>", 
    unsafe_allow_html=True
)