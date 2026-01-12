import os
import sys
import zipfile
import shutil

def extract_zips_to_folder(zip_folder, extract_dir):
    """
    Extract all zip files to a folder structure.
    Each zip is extracted to a subfolder named after the zip file (without .zip extension).
    """
    zip_folder = os.path.abspath(zip_folder)
    extract_dir = os.path.abspath(extract_dir)
    
    print(f"Extracting zip files from: {zip_folder}")
    print(f"To directory: {extract_dir}")
    
    # Create extraction directory
    os.makedirs(extract_dir, exist_ok=True)
    
    # Get all zip files
    zip_files = [f for f in os.listdir(zip_folder) if f.lower().endswith('.zip')]
    
    if not zip_files:
        print("No zip files found!")
        return extract_dir
    
    print(f"Found {len(zip_files)} zip file(s)")
    
    for zip_file in sorted(zip_files):
        zip_path = os.path.join(zip_folder, zip_file)
        # Extract to subfolder named after zip file (without extension)
        zip_extract_dir = os.path.join(extract_dir, zip_file.replace('.zip', ''))
        
        try:
            print(f"Extracting: {zip_file}")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(zip_extract_dir)
            print(f"  Extracted to: {zip_extract_dir}")
        except Exception as e:
            print(f"  Error extracting {zip_file}: {e}")
    
    print(f"\nExtraction complete! Files extracted to: {extract_dir}")
    return extract_dir

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_zips_to_folder.py <zip_folder> <extract_dir>")
        print("Example: python extract_zips_to_folder.py C:\\zips C:\\extracted")
    else:
        extract_zips_to_folder(sys.argv[1], sys.argv[2])

