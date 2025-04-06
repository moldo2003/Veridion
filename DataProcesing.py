import os
import json
import math
import numpy as np
from scipy.optimize import linear_sum_assignment
from difflib import SequenceMatcher

class GridSimilarityCalculator:
    def __init__(self):
        # Configurable parameters
        self.position_threshold_factor = 0.05  # 5% of element size
        self.min_position_threshold = 5       # 5px minimum
        self.size_threshold_factor = 0.1      # 10% of element size
        self.min_size_threshold = 10          # 10px minimum
        self.text_similarity_weight = 0.2     # Weight for text content comparison
        self.hierarchy_weight = 0.15          # Weight for hierarchical structure
        self.similarity_threshold = 0.45      # Threshold for comparing children
        
    def calculate_element_similarity(self, e1, e2):
        """Calculate similarity between two grid elements based on position and size"""
        # Extract position and size data from the grid format
        x1, y1, width1, height1 = e1.get('x', 0), e1.get('y', 0), e1.get('width', 0), e1.get('height', 0)
        x2, y2, width2, height2 = e2.get('x', 0), e2.get('y', 0), e2.get('width', 0), e2.get('height', 0)
        
        # Calculate adaptive thresholds
        ref_size = max(width1, height1, width2, height2, 1)  # prevent division by zero
        pos_threshold = max(self.min_position_threshold, ref_size * self.position_threshold_factor)
        size_threshold = max(self.min_size_threshold, ref_size * self.size_threshold_factor)
        
        # Calculate position similarity
        # Normalize by viewport/body size for better comparisons across different screen sizes
        viewport_width = 1280  # Assumed viewport width, adjust as needed
        viewport_height = 800  # Assumed viewport height, adjust as needed
        
        # Calculate both absolute and relative position similarity
        abs_x_sim = 1 - min(1, abs(x1 - x2) / pos_threshold)
        abs_y_sim = 1 - min(1, abs(y1 - y2) / pos_threshold)
        
        # Relative position (normalized by viewport)
        rel_x1, rel_x2 = x1 / viewport_width, x2 / viewport_width
        rel_y1, rel_y2 = y1 / viewport_height, y2 / viewport_height
        rel_x_sim = 1 - abs(rel_x1 - rel_x2)
        rel_y_sim = 1 - abs(rel_y1 - rel_y2)
        
        # Combine absolute and relative similarities
        x_sim = (abs_x_sim + rel_x_sim) / 2
        y_sim = (abs_y_sim + rel_y_sim) / 2
        
        # Size similarity
        width_sim = 1 - min(1, abs(width1 - width2) / size_threshold)
        height_sim = 1 - min(1, abs(height1 - height2) / size_threshold)
        
        # Aspect ratio similarity (for distinguishing between similarly sized but differently shaped elements)
        aspect1 = width1 / height1 if height1 > 0 else 0
        aspect2 = width2 / height2 if height2 > 0 else 0
        aspect_sim = 1 - min(1, abs(aspect1 - aspect2) / 2)  # Difference normalized to [0,1]
        
        # Calculate position and size similarity
        # Position gets higher weight as it's more important for identifying corresponding elements
        position_sim = 0.6 * x_sim + 0.4 * y_sim
        size_sim = 0.4 * width_sim + 0.4 * height_sim + 0.2 * aspect_sim
        
        # Final similarity score for grid elements
        return 0.6 * position_sim + 0.4 * size_sim
    
    def find_corresponding_element(self, element, elements_list):
        """Find the most similar element in a list based on position and size"""
        best_match = None
        best_score = -1
        
        for candidate in elements_list:
            score = self.calculate_element_similarity(element, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match, best_score
    
    def calculate_grid_similarity(self, grid1, grid2):
        """Calculate similarity between two grids of elements"""
        if not grid1 or not grid2:
            return 0.0
        
        # Build similarity matrix for grid elements
        sim_matrix = np.zeros((len(grid1), len(grid2)))
        for i, e1 in enumerate(grid1):
            for j, e2 in enumerate(grid2):
                sim_matrix[i, j] = self.calculate_element_similarity(e1, e2)
        
        # Optimal assignment using Hungarian algorithm
        row_ind, col_ind = linear_sum_assignment(-sim_matrix)
        
        # Calculate overall grid similarity
        total_sim = 0
        matched_elements = 0
        
        for r, c in zip(row_ind, col_ind):
            element_sim = sim_matrix[r, c]
            total_sim += element_sim
            matched_elements += 1
        
        # Normalize by maximum possible matches
        grid_sim = total_sim / max(len(grid1), len(grid2))
        
        return grid_sim
    
    def calculate_detailed_similarity(self, website1, website2):
        """Calculate detailed similarity between two websites with grid and elements structure"""
        # First compare the grids (positioning of main elements)
        grid_sim = self.calculate_grid_similarity(website1['grid'], website2['grid'])
        
        # If grid similarity is sufficient to continue
        if grid_sim >= self.similarity_threshold:
            # Match corresponding elements for detailed comparison
            total_element_sim = 0
            matched_elements = 0
            
            for elem1 in website1['elements']:
                # Find corresponding element in website2
                elem2, match_score = self.find_corresponding_element(
                    {'x': elem1['position']['x'], 'y': elem1['position']['y'], 
                     'width': elem1['position']['width'], 'height': elem1['position']['height']},
                    [{'x': e['position']['x'], 'y': e['position']['y'], 
                      'width': e['position']['width'], 'height': e['position']['height']} 
                     for e in website2['elements']]
                )
                
                # If a good match was found, compare the detailed structure
                if match_score >= self.similarity_threshold:
                    # Find the full element data
                    full_elem2 = next((e for e in website2['elements'] 
                                      if e['position']['x'] == elem2['x'] and 
                                         e['position']['y'] == elem2['y']), None)
                    
                    if full_elem2:
                        # Compare detailed properties (tag, classes, text, children)
                        detailed_sim = self.compare_detailed_elements(elem1, full_elem2)
                        total_element_sim += detailed_sim
                        matched_elements += 1
            
            # Calculate average element similarity
            element_sim = total_element_sim / matched_elements if matched_elements > 0 else 0
            
            # Combine grid similarity and element similarity
            final_sim = 0.4 * grid_sim + 0.6 * element_sim
        else:
            # If grid similarity is too low, don't bother with detailed comparison
            final_sim = grid_sim
        
        return final_sim
    
    def compare_detailed_elements(self, elem1, elem2):
        """Compare detailed properties of two elements including their children"""
        # Calculate tag similarity
        tag_sim = 1.0 if elem1['tag'].lower() == elem2['tag'].lower() else 0.0
        
        # Calculate class similarity
        class_sim = self.calculate_class_similarity(
            ' '.join(elem1.get('classes', [])), 
            ' '.join(elem2.get('classes', []))
        )
        
        # Calculate text similarity
        text_sim = self.calculate_text_similarity(elem1.get('text', ''), elem2.get('text', ''))
        
        # Calculate children similarity if both elements have children
        children_sim = 0
        if elem1.get('children') and elem2.get('children'):
            children_sim = self.calculate_children_similarity(elem1['children'], elem2['children'])
        
        # Weight different aspects of similarity
        return 0.2 * tag_sim + 0.2 * class_sim + 0.3 * text_sim + 0.3 * children_sim
    
    def calculate_class_similarity(self, classes1, classes2):
        """Calculate similarity between class attributes"""
        if not classes1 and not classes2:
            return 1.0
        if not classes1 or not classes2:
            return 0.0
            
        classes1_set = set(classes1.split())
        classes2_set = set(classes2.split())
        
        if not classes1_set and not classes2_set:
            return 1.0
        
        intersection = classes1_set.intersection(classes2_set)
        union = classes1_set.union(classes2_set)
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_text_similarity(self, text1, text2):
        """Calculate text similarity using sequence matching"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
            
        # Normalize text for comparison
        text1 = str(text1).strip().lower()
        text2 = str(text2).strip().lower()
        
        if text1 == text2:
            return 1.0
            
        # Use sequence matcher for partial matches
        return SequenceMatcher(None, text1, text2).ratio()
    
    def calculate_children_similarity(self, children1, children2):
        """Calculate similarity between children elements using recursive grid comparison"""
        if not children1 and not children2:
            return 1.0
        if not children1 or not children2:
            return 0.0
        
        # Convert children to grid format
        grid1 = []
        grid2 = []
        
        for child in children1:
            grid1.append({
                'x': child['position']['x'], 
                'y': child['position']['y'], 
                'width': child['position']['width'], 
                'height': child['position']['height']
            })
        
        for child in children2:
            grid2.append({
                'x': child['position']['x'], 
                'y': child['position']['y'], 
                'width': child['position']['width'], 
                'height': child['position']['height']
            })
        
        # Use grid similarity algorithm recursively
        return self.calculate_grid_similarity(grid1, grid2)

def process_files(input_dir, output_dir):
    """Process all website files and calculate similarity matrix"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Load all website data
    json_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.json')])
    website_names = [f.replace('.json', '') for f in json_files]
    
    all_websites = []
    for filename in json_files:
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_websites.append(data)
    
    # Compute similarity matrix
    calculator = GridSimilarityCalculator()
    n = len(all_websites)
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            similarity_matrix[i, j] = calculator.calculate_detailed_similarity(all_websites[i], all_websites[j])
            similarity_matrix[j, i] = similarity_matrix[i, j]  # Symmetric matrix
    
    # Save results
    np.save(os.path.join(output_dir, 'similarity_matrix.npy'), similarity_matrix)
    save_enhanced_matrix(
        similarity_matrix,
        os.path.join(output_dir, "similarity_matrix.txt"),
        website_names,
        title="Enhanced Similarity Matrix"
    )
    
    # Save website names with .html extension
    with open(os.path.join(output_dir, 'website_names.txt'), 'w') as f:
        f.write('\n'.join([name + '.html' for name in website_names]))

def save_enhanced_matrix(matrix, filepath, labels=None, title="", num_width=10):
    """Save matrix with formatting"""
    n = matrix.shape[0]
    
    with open(filepath, 'w') as f:
        if title:
            f.write(f"{title} ({n}x{n})\n")
            f.write("=" * (len(title) + 6 + len(str(n))*2) + "\n\n")
        
        f.write(" " * 5)
        for j in range(n):
            f.write(f"{j:^{num_width}d}")
        f.write("\n")
        
        divider_length = 5 + n * num_width
        f.write("-" * divider_length + "\n")
        
        for i in range(n):
            f.write(f"{i:4d} ")
            for val in matrix[i,:]:
                f.write(f"{val:^{num_width}.4f}")
            f.write("\n")
            
            if n > 10 and (i+1) % 5 == 0 and i != n-1:
                f.write("-" * divider_length + "\n")
    
    if labels is not None:
        with open(filepath.replace('.txt', '_labels.txt'), 'w') as f:
            f.write("Index\tLabel\n")
            f.write("-----\t-----\n")
            for idx, label in enumerate(labels):
                f.write(f"{idx}\t{label}\n")

if __name__ == '__main__':
    process_files('./output', './results')