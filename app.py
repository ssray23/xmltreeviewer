import os
import xml.etree.ElementTree as ET # For XML handling
from flask import Flask, request, render_template_string
from markupsafe import escape
import base64 # <-- Font Change Start --> Import for encoding
import os.path # <-- Font Change Start --> Import for path handling

app = Flask(__name__)

# <-- Font Change Start -->
# --- Font Configuration ---
# Matches the WOFF files provided previously.
FONT_CONFIG = {
    'Helvetica Local': { # The name you'll use in CSS
        'normal': { # Font Style: Normal
            '400': 'Helvetica-Regular.woff', # Regular weight
            '700': 'Helvetica-Bold.woff',    # Bold weight
        },
        'italic': { # Font Style: Italic
            '400': 'Helvetica-Italic.woff',     # Italic weight
            '700': 'Helvetica-BoldItalic.woff', # Bold Italic weight
        }
    }
}

# --- Helper to Encode Font ---
def encode_font_to_base64(font_path):
    """Reads a font file and returns its Base64 encoded string."""
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, font_path)

    if not os.path.exists(full_path):
        print(f"Warning: Font file not found at {full_path}. Skipping.")
        return None
    try:
        with open(full_path, "rb") as font_file:
            encoded_string = base64.b64encode(font_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding font {font_path}: {e}")
        return None

# --- Generate @font-face CSS ---
def generate_font_face_css(config):
    """Generates @font-face CSS rules from the FONT_CONFIG."""
    css = ""
    for family_name, styles in config.items():
        for style, weights in styles.items():
            for weight, path in weights.items():
                encoded_font = encode_font_to_base64(path)
                if encoded_font:
                    if path.lower().endswith('.woff'): mime_type, format_type = 'font/woff', 'woff'
                    # Add elif for woff2 if needed
                    else: print(f"Warning: Unsupported font format {path}. Skipping."); continue
                    css += f"""
@font-face {{
    font-family: '{family_name}';
    src: url(data:{mime_type};base64,{encoded_font}) format('{format_type}');
    font-weight: {weight};
    font-style: {style};
    font-display: swap;
}}"""
    return css

# --- Generate and Assign the FONT_FACE_CSS variable ---
FONT_FACE_CSS = generate_font_face_css(FONT_CONFIG)
# <-- Font Change End -->


# --- Color Palette (Keep as before) ---
NODE_COLOR_PALETTE = ["#005f73", "#7a1a4f", "#a4710a", "#9b2226", "#343a40"]

# --- Helper Function to get color (Keep as before) ---
def get_color(depth):
    palette_index = depth % len(NODE_COLOR_PALETTE)
    return NODE_COLOR_PALETTE[palette_index]


# --- Helper Function to Recursively Build HTML Tree for XML (Keep as before, ensure uses get_color) ---
def generate_html_tree(element, depth=0):
    """Recursively generates HTML list representation of an XML element."""
    html = '<li>'
    has_children = len(element) > 0
    has_text = element.text and element.text.strip()
    full_tag = element.tag
    local_tag = full_tag.split('}')[-1] if '}' in full_tag else full_tag

    # --- Determine Pill Color based on Depth ---
    bg_color = get_color(depth)
    text_color = "#ffffff" # Assuming dark pills always

    # --- Build Node Content ---
    html += '<div class="node-content">'
    toggle_class = "toggle"
    # Add .empty class ONLY if there are NO children elements.
    if not has_children:
        toggle_class += " empty"
    html += f'<span class="{toggle_class}"></span>'
    # Tag Name Pill (with inline style for color)
    html += f'<span class="tag-name" style="background-color: {bg_color}; color: {text_color};">{escape(local_tag)}</span>'

    # Attributes (styled differently)
    if element.attrib:
        html += '<span class="attributes">'
        attr_html = []
        for name, value in element.items():
            local_attr_name = name.split('}')[-1] if '}' in name else name
            attr_html.append(
                f'<span class="attribute">'
                f'<span class="attr-name">{escape(local_attr_name)}</span>'
                f'<span class="attr-equals">=</span>'
                f'<span class="attr-value">"{escape(value)}"</span>'
                f'</span>'
            )
        html += " ".join(attr_html)
        html += '</span>'

    # Element Text (styled differently)
    if has_text:
        html += f'<span class="text-content">{escape(element.text.strip())}</span>'

    html += '</div>' # End Node Content

    # --- Child Elements (Recursive Call with Increased Depth) ---
    if has_children:
        html += '<ul class="collapsed">'
        for child in element:
            html += generate_html_tree(child, depth + 1)
            # Display tail text
            if child.tail and child.tail.strip():
                 html += f'<li><div class="node-content"><span class="toggle empty"></span><span class="text-content" style="margin-left: 0;">{escape(child.tail.strip())}</span></div></li>'
        html += '</ul>'

    html += '</li>'
    return html


# --- **** MOVED HTML_TEMPLATE DEFINITION HERE **** ---
# --- HTML Template with Updated CSS and Escaping ---
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XML Tree Viewer</title>
    <style>
        /* --- Inject Font Face Rules --- */
        {FONT_FACE_CSS}

        /* --- Base Styles --- */
        body {{
            font-family: 'Helvetica Local', Helvetica, Arial, sans-serif; /* <-- Use custom font */
            font-size: 14px;
            line-height: 1.6;
            background-color: #f8f9fa;
            color: #495057;
            margin: 0;
            padding: 20px;
        }}
        /* --- Other CSS (Keep consistent with JSON version, adjust class names) --- */
        .container {{ max-width: 1000px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); }}
        h1 {{ color: #343a40; text-align: center; margin-bottom: 30px; font-weight: 700; /* <-- Use bold */ }}
        textarea {{ width: 100%; min-height: 150px; border: 1px solid #ced4da; border-radius: 4px; padding: 10px; font-family: monospace; font-size: 13px; margin-bottom: 15px; box-sizing: border-box; }}
        button {{ display: block; width: 100%; padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: background-color 0.2s ease; font-family: 'Helvetica Local', Helvetica, Arial, sans-serif; /* <-- Use custom font */ font-weight: 700; /* <-- Use bold */ }}
        button:hover {{ background-color: #0056b3; }}
        .error-message {{ color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; }}
        hr {{ border: none; border-top: 1px solid #dee2e6; margin: 30px 0; }}
        /* --- XML Tree Styles --- */
        .xml-tree {{ margin-top: 20px; padding-left: 0; overflow-x: auto; }}
        .xml-tree ul {{ list-style-type: none; padding-left: 28px; margin-top: 5px; border-left: 1px dashed #adb5bd; }}
        .xml-tree li {{ position: relative; margin-bottom: 5px; }}
        .xml-tree li::before {{ content: ""; position: absolute; top: 11px; left: -16px; width: 16px; height: 1px; background-color: #adb5bd; }}
        .xml-tree li:last-child > ul {{ border-left: none; }}
        .xml-tree li:last-child::after {{ content: ""; position: absolute; top: 11px; left: -16px; width: 1px; height: calc(50% - 11px); background-color: #ffffff; }}
        .node-content {{ display: flex; align-items: center; flex-wrap: nowrap; cursor: default; min-height: 26px; padding-bottom: 2px; }}
        .toggle {{ display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; width: 18px; height: 18px; cursor: pointer; margin-right: 8px; font-weight: bold; color: #8B0000; user-select: none; font-size: 12px; text-align: center; line-height: 1; transition: opacity 0.2s ease; }}
        .toggle.empty {{ opacity: 0.4; cursor: default; }}
        .toggle::before {{ content: '►'; display: inline-block; }}
        .toggle.expanded::before {{ content: '▼'; }}
        .tag-name {{ color: #ffffff; padding: 3px 10px; border-radius: 12px; font-weight: 700; /* <-- Use bold */ font-size: 0.9em; margin-right: 8px; display: inline-block; line-height: 1.3; white-space: nowrap; flex-shrink: 0; }}
        /* --- XML Specific Styles --- */
        .attributes {{ margin-left: 5px; display: inline-flex; flex-wrap: nowrap; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-shrink: 1; }}
        .attribute {{ margin-right: 12px; font-size: 0.85em; display: inline-block; white-space: nowrap; }}
        .attr-name {{ color: #6f42c1; /* Maybe use italic? font-style: italic; */ }}
        .attr-equals {{ color: #adb5bd; margin: 0 2px; }}
        .attr-value {{ color: #198754; font-style: normal; }}
        .text-content {{ color: #5a6268; margin-left: 8px; font-style: italic; /* <-- Use italic */ word-break: break-word; background-color: #e9ecef; padding: 2px 6px; border-radius: 4px; display: inline-block; border: 1px solid #dee2e6; line-height: 1.4; white-space: normal; flex-shrink: 1; overflow-wrap: break-word; }}
        .xml-tree ul.collapsed {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>XML Tree Viewer</h1>
        <form method="post">
            <!-- Double braces for Jinja2 within f-string -->
            <textarea name="xml_data" placeholder="Paste your XML here...">{{{{ xml_input | safe }}}}</textarea>
            <button type="submit">Display Tree</button>
        </form>

        <!-- Double braces for Jinja2 within f-string -->
        {{% if error %}}
            <div class="error-message">
                <strong>Error parsing XML:</strong><br>
                {{{{ error }}}}
            </div>
        {{% elif xml_tree_html %}}
            <hr>
            <h2>XML Tree Structure</h2>
            <div id="xml-viewer" class="xml-tree">
                 <!-- Double braces for Jinja2 within f-string -->
                {{{{ xml_tree_html | safe }}}}
            </div>
        {{% endif %}}
    </div>

    <script>
        // Double braces {{ }} for JS within f-string
        document.addEventListener('DOMContentLoaded', function() {{
            const treeContainer = document.getElementById('xml-viewer'); // Target XML viewer ID
            if (treeContainer) {{
                treeContainer.addEventListener('click', function(event) {{
                    const toggle = event.target.closest('.toggle');
                    if (toggle && !toggle.classList.contains('empty')) {{
                        const parentLi = toggle.closest('li');
                        const childUl = parentLi.querySelector(':scope > ul');
                        if (childUl) {{
                            childUl.classList.toggle('collapsed');
                            toggle.classList.toggle('expanded');
                            const isExpanded = !childUl.classList.contains('collapsed');
                            parentLi.setAttribute('aria-expanded', isExpanded.toString());
                        }}
                    }}
                }}); // End click listener
                const allToggles = treeContainer.querySelectorAll('.toggle');
                allToggles.forEach(toggle => {{
                    if (!toggle.classList.contains('empty')) {{
                         const parentLi = toggle.closest('li');
                         const childUl = parentLi.querySelector(':scope > ul');
                         if (childUl) {{
                             childUl.classList.add('collapsed');
                             parentLi.setAttribute('aria-expanded', 'false');
                             toggle.classList.remove('expanded');
                         }}
                    }} else {{
                         toggle.setAttribute('aria-hidden', 'true');
                    }}
                }}); // End forEach
            }} // End if treeContainer
        }}); // End DOMContentLoaded
    </script>
</body>
</html>
"""

# --- Flask Routes (Keep as before for XML) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    xml_input = ""
    xml_tree_html = ""
    error_message = ""

    if request.method == 'POST':
        xml_input = request.form.get('xml_data', '')
        if xml_input:
            try:
                clean_xml_input = xml_input.strip()
                if not clean_xml_input:
                    raise ValueError("Input is empty or only whitespace.")
                root = ET.fromstring(clean_xml_input) # Use ET for XML
                # Initial call to generate tree starts at depth 0
                xml_tree_html = f'<ul class="xml-tree">{generate_html_tree(root, depth=0)}</ul>' # Call correct function
            except ET.ParseError as e: # Catch XML error
                error_message = f"Invalid XML: {escape(str(e))}"
            except ValueError as e:
                 error_message = f"Input Error: {escape(str(e))}"
            except Exception as e:
                error_message = f"An unexpected error occurred: {escape(str(e))}"
        else:
            pass # No input provided

    # Pass correct variables to template
    return render_template_string(
        HTML_TEMPLATE,
        xml_input=xml_input,        # Pass xml_input
        xml_tree_html=xml_tree_html,# Pass xml_tree_html
        error=error_message
    )


# --- Main Execution (Keep as before) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG') == '1')