# 🧠 Solution Presentation – HTML Page Similarity Clustering

## 👀 Problem Overview

The task was to design an algorithm that groups together **HTML documents** which appear **similar from the user’s perspective** in a web browser.

---

## 🧭 Initial Approach

My first idea was to render each HTML page visually and take **screenshots**, then compare them using **image similarity algorithms**.  
While this seemed intuitive, it turned out to be:

- Inefficient for large datasets
- Slow due to rendering and pixel comparison
- Unscalable for billions of pages

➡️ So I pivoted toward a structure-aware, content-based solution.

---

## 💡 Final Approach – Three Key Steps

I broke the problem into three main stages:

### 1. Data Extraction  
Transform HTML files into structured, machine-readable data.

### 2. Data Processing  
Calculate visual and semantic similarity between pairs of documents.

### 3. Clustering  
Group similar pages using hierarchical clustering.

---

## 🧱 Step 1: Data Extraction – HTML ➝ JSON Struct

Each HTML file is converted into a JSON object with two components:

- **`grid`**:  
  A flat list of elements within the `<body>` tag with:
  - `top`, `left`, `width`, `height` (relative layout)
  
- **`elements`**:  
  Rich description of each DOM element, including:
  - HTML tag (`div`, `p`, etc.)
  - `id`, `class`, `style` attributes
  - Inline text content
  - `children` (recursive structure)

> ✅ This separation allows for independent **visual layout** and **semantic structure** analysis.

---

## 🧮 Step 2: Data Processing – Similarity Calculation

### Phase 1: Grid-Level Similarity (Coarse Filter)
- A fast comparison based on layout:
  - Number of elements
  - Positions and sizes (relative to viewport)
- Used to **quickly eliminate dissimilar pages**

### Phase 2: Element-Level Similarity (Detailed Match)
- Elements matched based on:
  - Similar tag types
  - Spatial proximity
- For matched pairs, we compute similarity based on:
  - Tag structure
  - Text similarity 
  - Attribute matches (`id`, `class`, `style`)
  - Child structure depth

> 🧠 This two-step comparison balances **speed** and **accuracy**.

---

## 🧩 Step 3: Clustering – Grouping Similar Pages

Once the similarity scores were calculated, I applied **hierarchical clustering** to group the HTML pages.

This clustering method is particularly well-suited for this task because it:

- Doesn’t require predefining how many groups there will be
- Builds a tree of similarity, starting from the most similar pairs
- Allows flexible control over grouping using a similarity threshold

The output is a set of **clusters**, where each group contains HTML pages that are visually and structurally similar from a user’s perspective.

This way, even if two pages have different raw HTML, as long as they look and behave similarly in a browser, they will end up in the same group.

---

## 📌 Results & Observations

- Works well across different dataset complexity levels (tier1 to tier4)
- Can identify near-duplicates and layout clones effectively
- Avoids overfitting to HTML structure by integrating visual hierarchy


---

## ✅ Final Thoughts

This project was a refreshing change for me, as it pushed me out of my usual comfort zone. Over the past two years, I’ve mostly worked on full-stack mobile apps, so this was a new and exciting challenge that I didn’t expect to take on. It brought a fresh energy to my work, giving me a chance to explore something different and expand my skill set in ways I hadn't anticipated.

---

Thanks for reading!  

