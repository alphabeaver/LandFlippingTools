# 📞 Excel Phone Data Processor

A Streamlit web application that automatically processes real estate contact data exported from **LandPortal** software, separating mobile/VoIP phone numbers from landlines and reformatting the data for use with **LaunchControl** software.

## 🎯 Purpose

This tool bridges the gap between LandPortal and LaunchControl software by:
- **Processing LandPortal exports** to extract and clean contact data
- **Separating mobile/VoIP numbers** from landlines for targeted marketing campaigns
- **Reformatting data structure** to match LaunchControl's required format
- **Generating clean datasets** ready for import into LaunchControl calling campaigns
- **Providing comprehensive QA reports** to ensure data integrity during conversion
- **Identifying data leakage** when contacts have more than 3 mobile numbers

## ✨ Features

### 📱 Smart Phone Classification & Reformatting
- **LandPortal Data Processing**: Reads and processes Excel exports from LandPortal software
- **Mobile & VoIP Detection**: Automatically identifies and extracts mobile and VoIP numbers
- **Landline Separation**: Moves landlines, pagers, and special service numbers to discard file
- **LaunchControl Formatting**: Restructures data to match LaunchControl's required column format
- **Type Preservation**: Maintains original phone type classifications in discard file

### 📊 Comprehensive Output Files
1. **Cleaned File** (`[State][County][Date]LCT.xlsx`)
   - **LaunchControl-ready format** with mobile/VoIP contacts only
   - Up to 3 phone numbers per contact (LaunchControl limitation)
   - Standardized column mapping from LandPortal to LaunchControl structure

2. **Discard File** (`[State][County][Date]LandlinesNoNumber.xlsx`)
   - Contains contacts without mobile/VoIP phones in LandPortal format
   - Includes landlines with their original type classifications
   - Up to 5 phone numbers per contact for reference

3. **QA Report** (`[State][County][Date]QAReport.xlsx`)
   - Summary statistics and verification metrics for LandPortal → LaunchControl conversion
   - Missing phone analysis (leakage detection during reformatting)
   - Contact count verification between source and target formats
   - Phone type distribution analysis from original LandPortal data

### 🔍 Quality Assurance
- **Leakage Detection**: Identifies when mobile/VoIP numbers are lost during processing
- **Contact Count Verification**: Ensures all original contacts are accounted for
- **Duplicate Tracking**: Handles contacts that appear in both output files
- **Missing Phone Analysis**: Detailed breakdown of any lost phone numbers

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation
1. **Clone or download this repository**
2. **Install required packages:**
   ```bash
   pip3 install streamlit pandas openpyxl
   ```

### Running the Application
1. **Navigate to project folder:**
   ```bash
   cd path/to/excel-processor
   ```

2. **Launch the app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to `http://localhost:8501`

## 📋 How to Use

### Step 1: Export Data from LandPortal
- Export your contact data from LandPortal software as an Excel file (.xlsx or .xls)
- Ensure the export includes all phone columns and contact information
- The exported file should contain the standard LandPortal column structure

### Step 2: Upload to Processor
- Click "Choose an Excel file" 
- Select your LandPortal export file
- Review the data preview to ensure proper loading

### Step 3: Process the Data
- Click "🚀 Process File" to start the LandPortal → LaunchControl conversion
- Watch the progress bar and status updates
- Review the processing results and QA metrics

### Step 4: Download Results
- **📱 Cleaned File**: LaunchControl-ready mobile/VoIP contacts for calling campaigns
- **📞 Discard File**: Landline/pager contacts in original LandPortal format for reference
- **📊 QA Report**: Comprehensive analysis and verification of the conversion process

### Step 5: Import to LaunchControl
- Use the cleaned file directly in LaunchControl software
- The format is optimized for LaunchControl's contact import requirements

## 📄 LandPortal Export File Format

Your Excel file exported from LandPortal should contain these columns:

### Phone Columns (LandPortal Standard):
- `Phone` + `Phone (Line Type)`
- `Alt Phone 1` + `Alt Phone 1 (Line Type)`
- `Alt Phone 2` + `Alt Phone 2 (Line Type)`
- `Alt Phone 3` + `Alt Phone 3 (Line Type)`
- `Alt Phone 4` + `Alt Phone 4 (Line Type)`
- `Alt Phone 5` + `Alt Phone 5 (Line Type)`

### Contact Information (LandPortal Fields):
- `Owner 1 First Name`, `Owner 1 Last Name`, `Owner 1 Full Name`
- `Mail Full Address`, `Mail City`, `Mail State`, `Mail Zip`
- `Parcel Full Address`, `Parcel City`, `Parcel State`, `Parcel Zip`
- `APN`, `Parcel County`, `Lot Acres`

### Phone Types (LandPortal Classifications):
- **Processed for LaunchControl**: `Mobile`, `Voip`
- **Kept in Discard File**: `Landline`, `Pager`, `SpecialService`

## 📊 Output File Structure

### LaunchControl-Ready Cleaned File Columns:
```
First Name | Last Name | Mailing Address | Mailing City | Mailing State | Mailing Zip |
Property Address | Property City | Property State | Property Zip |
Phone1 | Phone2 | Phone3 | APN | Property County | Acreage
```
*This format is optimized for direct import into LaunchControl software*

### LandPortal-Format Discard File Columns:
```
First Name | Last Name | Mailing Address | ... |
Phone1 | Phone1_Type | Phone2 | Phone2_Type | Phone3 | Phone3_Type |
Phone4 | Phone4_Type | Phone5 | Phone5_Type | APN | Property County | Acreage
```
*Maintains original LandPortal structure for reference*

### QA Report Sheets:
- **Summary**: Overall statistics and LandPortal → LaunchControl conversion verification
- **Missing Phones**: Detailed breakdown of any mobile/VoIP numbers lost during reformatting

## 🔧 LandPortal → LaunchControl Mapping

### Column Transformation:
The application automatically maps LandPortal fields to LaunchControl requirements:

| LandPortal Field | LaunchControl Field |
|------------------|-------------------|
| `Owner 1 First Name` | `First Name` |
| `Owner 1 Last Name` | `Last Name` |
| `Mail Full Address` | `Mailing Address` |
| `Mail City` | `Mailing City` |
| `Mail State` | `Mailing State` |
| `Mail Zip` | `Mailing Zip` |
| `Parcel Full Address` | `Property Address` |
| `Parcel City` | `Property City` |
| `Parcel State` | `Property State` |
| `Parcel Zip` | `Property Zip` |
| `Lot Acres` | `Acreage` |
| `Parcel County` | `Property County` |

### Phone Number Processing:
- **LandPortal Format**: Up to 5 phone numbers with individual type classifications
- **LaunchControl Format**: Maximum 3 mobile/VoIP numbers only (business requirement)
- **Automatic Filtering**: Only `Mobile` and `Voip` types are included in LaunchControl file

### Phone Number Processing
- Automatically handles scientific notation (e.g., `9.317879e+09`)
- Normalizes to 10-digit format
- Removes formatting characters
- Handles 11-digit numbers starting with "1"

## 📈 Understanding the QA Report

### Key Metrics for LandPortal → LaunchControl Conversion:
- **Contact Count Verification**: Ensures all LandPortal contacts are processed
- **Phone Type Distribution**: Breakdown of all phone types in original LandPortal data
- **Leakage Detection**: Identifies mobile/VoIP numbers lost during LaunchControl formatting
- **Duplicate Analysis**: Contacts appearing in both LaunchControl and discard files
- **LaunchControl Compatibility**: Verification that output meets LaunchControl requirements

### Status Indicators:
- **✅ PASS**: No data leakage detected during conversion
- **❌ LEAKAGE DETECTED**: Some mobile/VoIP numbers were lost (often due to 3-phone limit)
- **✅ MATCH**: All LandPortal contacts properly accounted for
- **❌ MISMATCH**: Contact count discrepancy between source and output files

## 🚀 Deployment Options

### Local Use
- Run locally using the instructions above
- Create desktop shortcuts for easy access

### Online Deployment (Streamlit Cloud)
1. Upload code to GitHub repository
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click
4. Share public URL with team members

## 🔍 Troubleshooting

### Common Issues:

**"No rows with valid mobile/voip phones found"**
- Check that your LandPortal export contains phone type columns with "Mobile" or "Voip" values
- Verify the export includes the standard LandPortal column structure
- Ensure phone numbers are properly formatted in the LandPortal data

**"Certificate errors during installation"**
```bash
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org streamlit pandas openpyxl
```

**"Streamlit command not found"**
```bash
python3 -m streamlit run app.py
```

**Large LandPortal files processing slowly**
- This is normal for LandPortal exports with thousands of property records
- Progress bars show current conversion status
- Consider processing in smaller geographic batches if needed

**LaunchControl import issues**
- Verify the cleaned file format matches LaunchControl's import requirements
- Check that phone numbers are properly formatted (10 digits)
- Ensure all required columns are present in the output

## 📁 Project Structure
```
excel-processor/
├── app.py              # Main Streamlit application
├── README.md           # This file
└── requirements.txt    # Python dependencies (optional)
```

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Excel file format matches requirements
3. Ensure all required columns are present
4. Check that phone types are spelled correctly

## 📝 Version History

### v1.0.0
- Initial release with LandPortal → LaunchControl conversion
- Automatic phone type separation and reformatting
- QA reporting and leakage detection for data conversion
- Streamlit web interface for easy file processing
- Support for up to 5 phone numbers per contact in LandPortal format
- LaunchControl-optimized output with 3-phone limitation

---

**Built with ❤️ using Streamlit, Pandas, and Python**  
*Bridging LandPortal and LaunchControl for seamless real estate marketing workflows*
