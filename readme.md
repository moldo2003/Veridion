# README: HTML Page Similarity Clustering

## 📖 Overview

This project provides a pipeline to analyze and group HTML pages based on their **visual and structural similarity**. The pipeline consists of three main steps:

1. **Data Extraction**: Converts HTML files into structured JSON data.
2. **Data Processing**: Calculates similarity scores between HTML pages.
3. **Clustering**: Groups similar pages into clusters using hierarchical clustering.

The project is designed to process multiple directories of HTML files and outputs grouped results for each directory.

---



## 🚀 How to Use

### 1. Run the Pipeline
The pipeline processes all subdirectories in the clones directory. Each subdirectory is treated as a separate dataset.

To run the pipeline:
```bash
python run_pipeline.py <path_to_clones_directory>
```

#### Example:
```bash
python run_pipeline.py ./clones
```

### 2. Input and Output
- **Input**: The clones directory should contain subdirectories, each with HTML files to process.
- **Output**:
  - Extracted JSON data is saved in `./output/<subdirectory_name>`.
  - Similarity results are saved in `./results/<subdirectory_name>`.
  - Grouped images are saved in `./grouped_html/<subdirectory_name>`.

---

## 📂 Project Structure

```
Veridion/
├── DataExtraction.py       # Extracts structured data from HTML files
├── DataProcesing.py        # Calculates similarity scores between pages
├── GroupImages.py          # Groups similar pages into clusters
├── run_pipeline.py         # Main script to run the pipeline
├── presentation.md         # Detailed explanation of the project
├── readme.md               # Instructions for using the project
├── requirements.txt        # Python dependencies
└── clones/                 # Input directory containing subdirectories of HTML files
```

---

## 📝 Steps in Detail

### Step 1: Data Extraction
- **Script**: DataExtraction.py
- **Description**: Converts HTML files into JSON objects containing:
  - `grid`: Layout information (position, size, etc.)
  - `elements`: Detailed DOM structure (tags, attributes, text, etc.)
- **Command**:
  ```bash
  python DataExtraction.py --input <input_directory> --output <output_directory> --threads <num_threads>
  ```

### Step 2: Data Processing
- **Script**: DataProcesing.py
- **Description**: Calculates similarity scores between HTML pages using:
  - Grid-level similarity (layout comparison)
  - Element-level similarity (detailed DOM comparison)
- **Command**:
  ```bash
  python DataProcesing.py
  ```

### Step 3: Clustering
- **Script**: GroupImages.py
- **Description**: Groups similar pages into clusters using hierarchical clustering.
- **Command**:
  ```bash
  python GroupImages.py --input <input_directory> --output <output_directory>
  ```

---

## 🧪 Example Workflow

1. Place your HTML files in subdirectories under clones. For example:
   ```
   clones/
   ├── tier1/
   │   ├── page1.html
   │   ├── page2.html
   │   └── ...
   ├── tier2/
   │   ├── page1.html
   │   ├── page2.html
   │   └── ...
   ```

2. Run the pipeline:
   ```bash
   python run_pipeline.py ./clones
   ```

3. Check the output:
   - Extracted JSON files: `./output/<subdirectory_name>`
   - Similarity matrix and results: `./results/<subdirectory_name>`
   - Grouped clusters: `./grouped_html/<subdirectory_name>`

---

## ⚙️ Configuration

### Modify Parameters
You can adjust parameters like similarity thresholds, clustering methods, and thread counts directly in the scripts:
- **`DataExtraction.py`**: Adjust thread count and input/output paths.
- **`DataProcesing.py`**: Modify similarity thresholds and weights.
- **`GroupImages.py`**: Change clustering thresholds.

---

## 🛡️ Troubleshooting

1. **Playwright Errors**:
   - Ensure Playwright is installed and browsers are set up:
     ```bash
     playwright install
     ```

2. **Missing Dependencies**:
   - Install missing libraries:
     ```bash
     pip install -r requirements.txt
     ```

3. **Invalid Input Directory**:
   - Ensure the clones directory exists and contains subdirectories with HTML files.

---

## 📌 Notes

- The pipeline is designed to handle multiple datasets (subdirectories) in parallel.
- Outputs are organized by subdirectory for easy analysis.
- Clustering results are based on visual and structural similarity, not raw HTML.

---

## 📧 Contact

For questions or issues, feel free to reach out!