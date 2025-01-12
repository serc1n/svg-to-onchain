import json
import urllib.parse
import sys
import re

def clean_svg(svg_content):
    # Remove XML declaration
    svg_content = re.sub(r'<\?xml[^>]+\?>', '', svg_content)
    
    # Remove comments
    svg_content = re.sub(r'<!--.*?-->', '', svg_content, flags=re.DOTALL)
    
    # Remove newlines and minimize whitespace
    svg_content = re.sub(r'\s+', ' ', svg_content)
    svg_content = svg_content.strip()
    
    return svg_content

def convert_svg_to_json(svg_content, name):
    try:
        # Clean and prepare SVG
        cleaned_svg = clean_svg(svg_content)
        
        # URL encode the SVG content
        encoded_svg = urllib.parse.quote(cleaned_svg)
        
        # Create JSON structure
        json_data = {
            "name": name,
            "image": f"data:image/svg+xml,{encoded_svg}"
        }
        
        # Convert to JSON string with minimal whitespace
        json_str = json.dumps(json_data, separators=(',', ':'))
        
        # URL encode the entire JSON string
        return f"data:application/json;utf8,{urllib.parse.quote(json_str)}"
        
    except Exception as e:
        raise Exception(f"Error converting SVG to JSON: {str(e)}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 svg_to_json.py <input_svg_file> <name>")
        sys.exit(1)
    
    svg_file = sys.argv[1]
    name = sys.argv[2]
    
    try:
        with open(svg_file, 'r') as f:
            svg_content = f.read()
            
        result = convert_svg_to_json(svg_content, name)
        
        # Save to output file
        output_file = svg_file.rsplit('.', 1)[0] + '.txt'
        with open(output_file, 'w') as f:
            f.write(result)
            
        print(f"Result saved to {output_file}")
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{svg_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
