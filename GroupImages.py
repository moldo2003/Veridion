import os
import shutil
import numpy as np
import scipy.cluster.hierarchy as sch

def group_similar_images(similarity_matrix, filenames, input_dir, output_dir, threshold=0.5):
    """
    Groups similar images into directories based on the similarity matrix using hierarchical clustering.
    
    Parameters:
    - similarity_matrix (np.ndarray): The similarity scores between images.
    - filenames (list): List of filenames corresponding to the images.
    - input_dir (str): Directory containing the input images.
    - output_dir (str): The base directory to store grouped images.
    - threshold (float): Threshold for forming clusters (0 to 1, higher means stricter grouping).
    """
    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    
    # Perform hierarchical clustering
    linkage_matrix = sch.linkage(distance_matrix, method='ward')
    
    # Determine clusters based on the threshold
    cluster_labels = sch.fcluster(linkage_matrix, t=threshold, criterion='distance')
    
    # Organize filenames into clusters
    clusters = {}
    for idx, label in enumerate(cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(filenames[idx])
    
    # Create directories and copy files into them
    os.makedirs(output_dir, exist_ok=True)
    
    for cluster_id, images in clusters.items():
        cluster_path = os.path.join(output_dir, f"cluster_{cluster_id}")
        os.makedirs(cluster_path, exist_ok=True)
        
        for image in images:
            src_path = os.path.join(input_dir, image)  # Use input_dir parameter
            dst_path = os.path.join(cluster_path, image)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)  # Copy file instead of moving it
    
    print(f"Images grouped into {len(clusters)} directories inside '{output_dir}'")
    return clusters

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="clones/tier1", help="Input directory")
    parser.add_argument("--output", default="grouped_images", help="Output directory for grouped images")
    args = parser.parse_args()
    
    # Load the saved similarity matrix and filenames
    similarity_matrix = np.load("results/similarity_matrix.npy")
    
    with open("results/website_names.txt", "r") as f:
        filenames = [line.strip() for line in f]
    
    # Group images and organize into directories
    group_similar_images(similarity_matrix, filenames, args.input, args.output, threshold=0.5)
