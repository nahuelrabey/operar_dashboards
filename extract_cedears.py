import pdfplumber
import pandas as pd

def extract_cedears_data(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # increasing snap_tolerance might help with alignment issues
            # 'vertical_strategy': 'text' relies on the text positions to guess column dividers
            tables = page.extract_tables(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})
            for table in tables:
                # Assuming the first row is the header
                if not table:
                    continue
                
                # Iterate through all rows to find the header
                header_found = False
                byma_idx = -1
                ratio_idx = -1
                
                for row_idx, row in enumerate(table):
                    if not row: continue
                    # Clean row for checking
                    clean_row = [str(col).replace('\n', ' ').strip() if col else '' for col in row]
                    
                    # Check if this row is the header
                    # Check for "Ratio" and "BYMA" (case insensitive)
                    # We use a flag to track if we found the header in this table
                    if not header_found:
                        # Convert to lower for searching
                        row_lower = [c.lower() for c in clean_row]
                        
                        # Check existance
                        # We need to find which index corresponds to what
                        b_idx = -1
                        r_idx = -1
                        
                        for i, cell in enumerate(row_lower):
                            if "byma" in cell and "código" in cell: # "Código BYMA"
                                b_idx = i
                            elif "byma" in cell and b_idx == -1: # Fallback if just BYMA
                                b_idx = i
                            
                            if "ratio" in cell:
                                r_idx = i
                        
                        if b_idx != -1 and r_idx != -1:
                            # Found header
                            byma_idx = b_idx
                            ratio_idx = r_idx
                            header_found = True
                    
                    else:
                        # Header already found, this is a data row
                        if len(row) > max(byma_idx, ratio_idx):
                            byma_code = row[byma_idx]
                            ratio = row[ratio_idx]
                            
                            # Basic cleanup
                            if byma_code:
                                byma_code = str(byma_code).strip()
                                # specific cleanup: remove " N" suffix if present
                                if byma_code.endswith(" N"):
                                    byma_code = byma_code[:-2]
                            if ratio:
                                ratio = str(ratio).strip()
                                
                            if byma_code and ratio:
                                # Validation: Ratio should look like a number or ratio (e.g., "10:1" or "0,5")
                                # BYMA code should be short, usually all caps.
                                
                                # Calculate ratio float
                                ratio_calc = 0.0
                                try:
                                    # Normalize separators just in case (e.g. 5:01 -> 5:1, or mishandled chars)
                                    # Some might be "700:" which implies 700:1 usually, or just parse error.
                                    # Assuming format "A:B"
                                    parts = ratio.split(':')
                                    if len(parts) >= 1:
                                        num_str = parts[0].strip()
                                        den_str = parts[1].strip() if len(parts) > 1 else '1'
                                        
                                        # Handle empty denominator as 1
                                        if not den_str: 
                                            den_str = '1'
                                            
                                        num = float(num_str.replace(',', '.'))
                                        den = float(den_str.replace(',', '.'))
                                        
                                        if den != 0:
                                            ratio_calc = num / den
                                except Exception:
                                    # invalid format, keep 0.0 or handle otherwise
                                    pass

                                data.append({
                                    "byma_code": byma_code,
                                    "ratio": ratio,
                                    "ratio_calculated": ratio_calc
                                })

    return data

if __name__ == "__main__":
    pdf_file = "data/cedears.pdf"
    print(f"Extracting data from {pdf_file}...")
    try:
        results = extract_cedears_data(pdf_file)
        
        if results:
            print(f"Found {len(results)} records.")
            print("\nPreview first 10:")
            df = pd.DataFrame(results)
            print(df.head(10).to_string(index=False))
            
            # Option to save
            csv_file = "data/cedears.csv"
            df.to_csv(csv_file, index=False)
            print(f"\nData saved to {csv_file}")
        else:
            print("No matching data found. Please check PDF headers.")
            
    except Exception as e:
        print(f"Error: {e}")
