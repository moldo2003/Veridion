import os
import json
import threading
import traceback
from queue import Queue
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from typing import Dict, List, Optional, Any

class HTMLExtractor:
    def __init__(self, input_dir: str = "./input", output_dir: str = "./output", thread_count: int = 4):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.thread_count = thread_count
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "screenshots"), exist_ok=True)
        self.task_queue = Queue()
        self.lock = threading.Lock()

    def process_directory(self):
        files = []
        for filename in os.listdir(self.input_dir):
            if filename.endswith(".html"):
                filepath = os.path.join(self.input_dir, filename)
                try:
                    filesize = os.path.getsize(filepath)
                    files.append((filesize, filename))
                except:
                    continue
        
        files.sort(reverse=True, key=lambda x: x[0])
        
        for _, filename in files:
            self.task_queue.put(filename)
        
        threads = []
        for _ in range(min(self.thread_count, len(files))):
            t = threading.Thread(target=self._worker)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

    def _worker(self):
        while not self.task_queue.empty():
            try:
                filename = self.task_queue.get_nowait()
                filepath = os.path.join(self.input_dir, filename)
                output_path = os.path.join(self.output_dir, f"{os.path.splitext(filename)[0]}.json")
                self.process_file(filepath, output_path)
            except:
                pass
            finally:
                self.task_queue.task_done()

    def process_file(self, html_path: str, output_path: str):
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except:
            raise

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-gpu',
                        '--disable-extensions',
                        '--disable-software-rasterizer',
                        '--disable-javascript',
                    ]   
                )
                page = browser.new_page()
                page.set_content(html_content)
                
                soup = BeautifulSoup(html_content, 'html.parser')
                body = soup.find('body') or soup
                
                elements_data = page.evaluate('''() => {
                    const results = [];
                    const body = document.body;
                    
                    for (const child of body.children) {
                        const rect = child.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            const elementData = {
                                tag: child.tagName.toLowerCase(),
                                id: child.id || null,
                                rect: rect,
                                zIndex: parseInt(window.getComputedStyle(child).zIndex) || 0,
                                styles: {
                                    display: window.getComputedStyle(child).display,
                                    position: window.getComputedStyle(child).position,
                                    width: window.getComputedStyle(child).width,
                                    height: window.getComputedStyle(child).height
                                }
                            };
                            results.push(elementData);
                        }
                    }
                    return results;
                }''')
                
                grid_info = []
                element_hierarchy = []
                
                for elem_data in elements_data:
                    soup_element = self._find_soup_element(body, elem_data['tag'], elem_data['id'])
                    if not soup_element:
                        continue
                    
                    grid_info.append({
                        "id": elem_data['id'],
                        "tag": elem_data['tag'],
                        "x": elem_data['rect']['left'],
                        "y": elem_data['rect']['top'],
                        "width": elem_data['rect']['width'],
                        "height": elem_data['rect']['height'],
                        "zIndex": elem_data['zIndex']
                    })
                    
                    element_hierarchy.append(self._extract_element(soup_element, page, elem_data))
                
                result = {
                    "grid": grid_info,
                    "elements": element_hierarchy
                }
                
                with self.lock:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                
                browser.close()
        
        except:
            raise

    def _find_soup_element(self, parent, tag_name: str, element_id: Optional[str]):
        try:
            for child in parent.children:
                if not child.name:
                    continue
                if child.name == tag_name and child.get('id') == element_id:
                    return child
            return None
        except:
            return None
        


    def _extract_element(self, element, page, precomputed_data=None) -> Dict[str, Any]:
        """
        Extract element information focusing on inline styles from style attribute
        """
        try:
            # Initialize basic element data
            element_data = {
                "id": element.get('id'),
                "tag": element.name,
                "classes": element.get('class', []),
                "attributes": self._get_attributes(element),
                "styles": {},
                "position": {
                    "x": precomputed_data['rect']['left'] if precomputed_data else 0,
                    "y": precomputed_data['rect']['top'] if precomputed_data else 0,
                    "width": precomputed_data['rect']['width'] if precomputed_data else 0,
                    "height": precomputed_data['rect']['height'] if precomputed_data else 0
                },
                "text": self._get_clean_text(element),
                "children": []
            }

            # Extract raw inline styles from style attribute
            if element.has_attr('style'):
                raw_styles = element['style']
                # Parse the style string into a dictionary
                styles_dict = {}
                for style_declaration in raw_styles.split(';'):
                    if ':' in style_declaration:
                        prop, value = style_declaration.split(':', 1)
                        styles_dict[prop.strip()] = value.strip()
                element_data['styles'] = styles_dict

            # Capture screenshot for media and interactive elements
            if element.name in ['img', 'iframe', 'video', 'canvas', 'svg']:
                try:
                    screenshot_path = self._capture_screenshot(element, page)
                    if screenshot_path:
                        element_data["screenshot"] = screenshot_path
                except Exception as e:
                    print(f"Screenshot capture error: {str(e)}")

            # Recursively process child elements
            for child in element.children:
                if child.name and child.name not in ['script', 'style', 'meta', 'link']:
                    try:
                        child_data = self._extract_element(child, page)
                        if child_data:
                            element_data["children"].append(child_data)
                    except Exception as e:
                        print(f"Child element extraction error: {str(e)}")

            return element_data

        except Exception as e:
            print(f"Critical error in element extraction: {str(e)}")
            return {
                "error": str(e),
                "tag": element.name if hasattr(element, 'name') else 'unknown'
            }
    
    def _get_attributes(self, element) -> Dict[str, str]:
        try:
            return {k: v for k, v in element.attrs.items() if k not in ['class', 'id']}
        except:
            return {}

    def _get_clean_text(self, element) -> Optional[str]:
        try:
            return element.string.strip() if element.string and element.string.strip() else None
        except:
            return None

    def _capture_screenshot(self, element, page) -> Optional[str]:
        try:
            selector = self._generate_selector(element)
            if not selector:
                return None
                
            screenshot_path = os.path.join(
                self.output_dir, 
                "screenshots", 
                f"{element.get('id', element.name)}_{hash(selector)}.png"
            )
            
            options = {
                'timeout': 1000,
                'animations': 'disabled',
            }
            
            try:
                if not page.locator(selector).is_visible(timeout=200):
                    return None
            except:
                return None
                
            try:
                page.locator(selector).screenshot(
                    path=screenshot_path,
                    **options
                )
                return screenshot_path
            except:
                return None
                
        except:
            return None

    def _generate_selector(self, element) -> Optional[str]:
        try:
            if element.get('id'):
                return f'#{element["id"]}'
            return None
        except:
            return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="./clones/tier1", help="Input directory")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--threads", type=int, default=20, help="Number of threads")
    args = parser.parse_args()
    
    extractor = HTMLExtractor(
        input_dir=args.input,
        output_dir=args.output,
        thread_count=args.threads
    )
    extractor.process_directory()