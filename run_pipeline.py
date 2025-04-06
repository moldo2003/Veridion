import os
import subprocess
import argparse
import shutil

def run_pipeline_for_directory(input_dir, output_dir):
    """
    Runs the pipeline for a single directory.
    """
    print(f"\nProcessing directory: {input_dir}")
    # Delete the ./output and ./results directories if they exist
    for dir_to_delete in ["./output", "./results"]:
     if os.path.exists(dir_to_delete):
        print(f"Deleting directory: {dir_to_delete}")
        shutil.rmtree(dir_to_delete)

    # Step 1: Data extraction
    print(f"Step 1: Running data extraction from {input_dir}...")
    extraction_cmd = [
        "python", "DataExtraction.py", 
        "--input", input_dir,
        "--threads", "20"
    ]
    subprocess.run(extraction_cmd)
    
    # Step 2: Data processing
    print("\nStep 2: Running data processing...")
    subprocess.run(["python", "DataProcesing.py"])
    
    # Step 3: Group images
    print("\nStep 3: Running image grouping...")
    grouping_cmd = [
        "python", "GroupImages.py",
        "--input", input_dir,
        "--output", os.path.join(output_dir)
    ]
    subprocess.run(grouping_cmd)
    
    print(f"\nPipeline completed for directory: {input_dir}")

def main():
    parser = argparse.ArgumentParser(description="Run the data processing pipeline for all subdirectories in the clones directory")
    parser.add_argument("clones_dir", help="Directory containing subdirectories of HTML files to process")
    args = parser.parse_args()
    
    clones_dir = args.clones_dir
    
    if not os.path.isdir(clones_dir):
        print(f"Error: '{clones_dir}' is not a valid directory")
        return
    
    # Iterate through each subdirectory in the clones directory
    for subdir in os.listdir(clones_dir):
        subdir_path = os.path.join(clones_dir, subdir)
        if os.path.isdir(subdir_path):
            output_dir = os.path.join("./grouped_html", subdir)  # Create a separate output folder for each subdirectory
            os.makedirs(output_dir, exist_ok=True)
            run_pipeline_for_directory(subdir_path, output_dir)

if __name__ == "__main__":
    main()