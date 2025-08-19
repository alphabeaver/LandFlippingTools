# 🏠 Land Owner Data Scrubber

A Streamlit web application that automatically cleans landowner lists by removing unwanted entities such as government organizations, utilities, churches, and other non-individual property owners.

## 🎯 Purpose

When working with landowner data for real estate investment, marketing, or research, you often need to filter out institutional and organizational property owners to focus on individual landowners. This tool automates that process by identifying and removing entries that match common patterns for:

- Government entities (counties, cities, townships)
- Utility companies (gas, electric, water)
- Religious organizations (churches, denominations)
- Educational institutions (school districts)
- Public services (fire departments, hospitals)
- Cemeteries and conservation authorities

## ✨ Features

- **🚀 Easy Upload**: Drag-and-drop Excel file upload
- **🎯 Smart Detection**: Automatically identifies likely owner name columns
- **🧹 Comprehensive Filtering**: Removes 80+ types of unwanted entities
- **⚙️ Customizable**: Add your own keywords to filter
- **📊 Visual Results**: See exactly what's being removed and what remains
- **💾 One-Click Download**: Get your cleaned Excel file instantly
- **📱 Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone or download this repository
2. Install required packages:

```bash
pip install streamlit pandas openpyxl
```

### Running the App

```bash
streamlit run landowner_scrub_app.py
```

The app will open in your default web browser at `http://localhost:8501`

## 📖 How to Use

1. **Upload Your File**: Click "Choose an Excel file" and select your landowner data
2. **Preview Data**: Review the loaded data and column structure
3. **Select Owner Column**: Choose which column contains the owner names
4. **Optional Customization**: Use the sidebar to add custom keywords to filter
5. **Clean Data**: Click the "Clean Data" button to process your file
6. **Review Results**: See how many entries were removed and preview the cleaned data
7. **Download**: Click "Download Cleaned Excel File" to save your results

## 📁 Input File Requirements

- **Format**: Excel files (.xlsx or .xls)
- **Structure**: Should contain a column with landowner names
- **Size**: No specific limit, but larger files may take longer to process

### Example Input Data Structure:
```
| Property ID | APN           | Owner Name                    | Address           |
|-------------|---------------|-------------------------------|-------------------|
| 123456      | 065D-B-019.00 | John Smith                    | 123 Main St      |
| 123457      | 090N-J-021.00 | Cumberland County             | County Courthouse |
| 123458      | 089-048.33    | First Baptist Church          | 456 Church Ave    |
| 123459      | 065C-C-069.00 | Mary Johnson                  | 789 Oak Dr        |
```

## 🗑️ What Gets Removed

The app automatically identifies and removes entries containing these patterns:

### Government & Municipal
- Counties, cities, townships
- State departments and agencies
- Municipal utilities and services
- Development districts

### Utilities & Infrastructure
- Gas and electric companies
- Water authorities
- Telephone companies
- Power cooperatives

### Religious Organizations
- Churches of all denominations
- Religious communities and organizations

### Educational Institutions
- School districts and systems
- Educational boards

### Public Services
- Fire departments
- Hospitals and medical facilities
- Emergency services

### Other Entities
- Cemeteries
- Conservation authorities
- Waste management companies
- Railway companies

## ⚙️ Customization

### Adding Custom Keywords

1. Check "Customize Scrub Patterns" in the sidebar
2. Enter additional keywords (one per line) in the text area
3. Keywords are automatically converted to case-insensitive patterns

Example custom keywords:
```
association
foundation
trust
llc
```

### Modifying Default Patterns

To permanently modify the filtering patterns, edit the `get_scrub_patterns()` function in the code. Each pattern is a regular expression that matches against the owner names.

## 📊 Output

- **Cleaned Excel File**: Contains only the rows that didn't match any filter patterns
- **Removal Statistics**: Shows how many entries were removed vs. retained
- **Detailed List**: View all removed entries before downloading

## 🔧 Technical Details

- **Built with**: Streamlit, Pandas, OpenPyXL
- **Pattern Matching**: Uses regular expressions for flexible text matching
- **Processing**: All data processing happens locally in your browser
- **Privacy**: No data is sent to external servers

## 🐛 Troubleshooting

### Common Issues

**File won't upload:**
- Ensure file is in Excel format (.xlsx or .xls)
- Check file isn't corrupted or password protected
- Try with a smaller file to test

**App runs slowly:**
- Large files (>10MB) may take longer to process
- Close other browser tabs to free up memory

**Unexpected removals:**
- Review the removed entries list to see what was filtered
- Use custom keywords to add specific patterns
- Check if owner names contain filtered keywords unexpectedly

### Getting Help

If you encounter issues:
1. Check the error message displayed in the app
2. Verify your input file format and structure
3. Try with a smaller sample file first

## 📝 License

This project is provided as-is for educational and commercial use. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Suggestions and improvements are welcome! Consider contributing:
- Additional filter patterns for other entity types
- Performance improvements for large files
- UI/UX enhancements
- Bug fixes and error handling

## 📈 Version History

- **v1.0**: Initial release with core filtering functionality
- Comprehensive pattern matching for major entity types
- Streamlit web interface with file upload/download
- Customizable keyword filtering

---

*Built for real estate professionals, researchers, and anyone working with landowner data who needs to focus on individual property owners.*
