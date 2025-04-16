import os
import json
from flask import Flask, request, render_template_string
from markupsafe import escape
import base64
import os.path

app = Flask(__name__)

# <-- Font Change Start -->
# --- Font Configuration ---
FONT_CONFIG = {
    'Helvetica Local': {
        'normal': { '400': 'Helvetica-Regular.woff', '700': 'Helvetica-Bold.woff' },
        'italic': { '400': 'Helvetica-Italic.woff', '700': 'Helvetica-BoldItalic.woff' }
    }
}

# --- Helper to Encode Font ---
def encode_font_to_base64(font_path):
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, font_path)
    if not os.path.exists(full_path): print(f"Warning: Font file not found {full_path}. Skipping."); return None
    try:
        with open(full_path, "rb") as font_file: return base64.b64encode(font_file.read()).decode('utf-8')
    except Exception as e: print(f"Error encoding font {font_path}: {e}"); return None

# --- Generate @font-face CSS ---
def generate_font_face_css(config):
    css = ""
    for family_name, styles in config.items():
        for style, weights in styles.items():
            for weight, path in weights.items():
                encoded_font = encode_font_to_base64(path)
                if encoded_font:
                    if path.lower().endswith('.woff'): mime_type, format_type = 'font/woff', 'woff'
                    else: print(f"Warning: Unsupported format {path}. Skipping."); continue
                    css += f"""
@font-face {{ font-family: '{family_name}'; src: url(data:{mime_type};base64,{encoded_font}) format('{format_type}'); font-weight: {weight}; font-style: {style}; font-display: swap; }}"""
    return css

# --- Generate and Assign the FONT_FACE_CSS variable ---
FONT_FACE_CSS = generate_font_face_css(FONT_CONFIG)
# <-- Font Change End -->

# --- Color Palette ---
NODE_COLOR_PALETTE = ["#005f73", "#7a1a4f", "#a4710a", "#9b2226", "#343a40"]

# --- Helper Functions (Keep get_color, format_json_value, generate_json_tree as before) ---
def get_color(depth):
    palette_index = depth % len(NODE_COLOR_PALETTE)
    return NODE_COLOR_PALETTE[palette_index]

def format_json_value(value):
    # (Keep implementation as before)
    if value is None: return 'null', 'json-value json-null'
    elif isinstance(value, bool): return str(value).lower(), 'json-value json-boolean'
    elif isinstance(value, (int, float)): return escape(str(value)), 'json-value json-number'
    elif isinstance(value, str): return f'"{escape(value)}"', 'json-value json-string'
    else: return escape(str(value)), 'json-value json-unknown'

def generate_json_tree(key, value, depth=0):
    # (Keep implementation as before)
    html = '<li>'
    node_id = f"node-{os.urandom(4).hex()}"
    key_display = f"{escape(str(key))}:" if key is not None else ""
    if isinstance(value, dict):
        item_count = len(value)
        pill_content = f'{escape(str(key))}' if key is not None else 'Object'
        pill_suffix = f' {{{{ {item_count} }}}}' # Escaped braces for display
        html += '<div class="node-content">'
        toggle_class = "toggle" if item_count > 0 else "toggle empty"
        html += f'<span class="{toggle_class}"></span>'
        html += f'<span class="tag-name" style="background-color: {get_color(depth)}; color: #fff;">{pill_content}{pill_suffix}</span>'
        html += '</div>'
        if item_count > 0:
            html += '<ul class="collapsed">'
            for k, v in value.items(): html += generate_json_tree(k, v, depth + 1)
            html += '</ul>'
    elif isinstance(value, list):
        item_count = len(value)
        pill_content = f'{escape(str(key))}' if key is not None else 'Array'
        pill_suffix = f' [ {item_count} ]'
        html += '<div class="node-content">'
        toggle_class = "toggle" if item_count > 0 else "toggle empty"
        html += f'<span class="{toggle_class}"></span>'
        html += f'<span class="tag-name" style="background-color: {get_color(depth)}; color: #fff;">{pill_content}{pill_suffix}</span>'
        html += '</div>'
        if item_count > 0:
            html += '<ul class="collapsed">'
            for i, item in enumerate(value): html += generate_json_tree(f"[{i}]", item, depth + 1)
            html += '</ul>'
    else:
        value_display, value_class = format_json_value(value)
        html += '<div class="node-content simple-value">'
        html += f'<span class="toggle empty"></span>'
        if key is not None: html += f'<span class="json-key">{key_display}</span>'
        html += f'<span class="{value_class}">{value_display}</span>'
        html += '</div>'
    html += '</li>'
    return html


# --- **** MOVED HTML_TEMPLATE DEFINITION HERE **** ---
# --- HTML Template with Corrected Escaping for f-string (including JS) ---
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSON Tree Viewer</title>
    <style>
        /* --- Inject Font Face Rules --- */
        {FONT_FACE_CSS}

        /* --- Base Styles --- */
        body {{ font-family: 'Helvetica Local', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; background-color: #f8f9fa; color: #495057; margin: 0; padding: 20px; }}
        /* --- Other CSS (Keep as before) --- */
        .container {{ max-width: 1000px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); }}
        h1 {{ color: #343a40; text-align: center; margin-bottom: 30px; font-weight: 700; }}
        textarea {{ width: 100%; min-height: 150px; border: 1px solid #ced4da; border-radius: 4px; padding: 10px; font-family: monospace; font-size: 13px; margin-bottom: 15px; box-sizing: border-box; }}
        button {{ display: block; width: 100%; padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: background-color 0.2s ease; font-family: 'Helvetica Local', Helvetica, Arial, sans-serif; font-weight: 700; }}
        button:hover {{ background-color: #0056b3; }}
        .error-message {{ color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; }}
        hr {{ border: none; border-top: 1px solid #dee2e6; margin: 30px 0; }}
        .json-tree {{ margin-top: 20px; padding-left: 0; overflow-x: auto; }}
        .json-tree ul {{ list-style-type: none; padding-left: 28px; margin-top: 5px; border-left: 1px dashed #adb5bd; }}
        .json-tree li {{ position: relative; margin-bottom: 5px; }}
        .json-tree li::before {{ content: ""; position: absolute; top: 11px; left: -16px; width: 16px; height: 1px; background-color: #adb5bd; }}
        .json-tree li:last-child > ul {{ border-left: none; }}
        .json-tree li:last-child::after {{ content: ""; position: absolute; top: 11px; left: -16px; width: 1px; height: calc(50% - 11px); background-color: #ffffff; }}
        .node-content {{ display: flex; align-items: center; flex-wrap: nowrap; cursor: default; min-height: 26px; padding-bottom: 2px; }}
        .node-content.simple-value {{ align-items: baseline; }}
        .toggle {{ display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; width: 18px; height: 18px; cursor: pointer; margin-right: 8px; font-weight: bold; color: #8B0000; user-select: none; font-size: 12px; text-align: center; line-height: 1; transition: opacity 0.2s ease; }}
        .toggle.empty {{ opacity: 0.4; cursor: default; }}
        .toggle::before {{ content: '►'; display: inline-block; }}
        .toggle.expanded::before {{ content: '▼'; }}
        .tag-name {{ color: #ffffff; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.9em; margin-right: 8px; display: inline-block; line-height: 1.3; white-space: nowrap; flex-shrink: 0; }}
        .json-key {{ color: #6f42c1; margin-right: 6px; font-size: 0.9em; flex-shrink: 0; white-space: nowrap; }}
        .json-value {{ display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 0.95em; white-space: pre-wrap; word-break: break-word; flex-shrink: 1; margin-left: 4px; }}
        .json-string {{ color: #28a745; background-color: #e9ecef; }}
        .json-number {{ color: #0d6efd; background-color: #e7f1ff; }}
        .json-boolean {{ color: #fd7e14; font-weight: bold; background-color: #fff8f0; }}
        .json-null {{ color: #6c757d; font-style: italic; background-color: #f8f9fa; }}
        .json-unknown {{ color: #dc3545; }}
        .json-tree ul.collapsed {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>JSON Tree Viewer</h1>
        <form method="post">
            <textarea name="json_data" placeholder="Paste your JSON here...">{{{{ json_input | safe }}}}</textarea>
            <button type="submit">Display Tree</button>
        </form>

        {{% if error %}}
            <div class="error-message">
                <strong>Error parsing JSON:</strong><br>
                {{{{ error }}}}
            </div>
        {{% elif json_tree_html %}}
            <hr>
            <h2>JSON Tree Structure</h2>
            <div id="json-viewer" class="json-tree">
                {{{{ json_tree_html | safe }}}}
            </div>
        {{% endif %}}
    </div>

    <script>
        // (JavaScript remains the same with escaped braces)
        document.addEventListener('DOMContentLoaded', function() {{
            const treeContainer = document.getElementById('json-viewer');
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
                }});
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
                }});
            }}
        }});
    </script>
</body>
</html>
"""

# --- Flask Routes (Keep as before for JSON) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    json_input = ""
    json_tree_html = ""
    error_message = ""
    if request.method == 'POST':
        json_input = request.form.get('json_data', '')
        if json_input:
            try:
                clean_json_input = json_input.strip()
                if not clean_json_input: raise ValueError("Input is empty or only whitespace.")
                data = json.loads(clean_json_input)
                json_tree_html = f'<ul>{generate_json_tree(None, data, depth=0)}</ul>'
            except json.JSONDecodeError as e: error_message = f"Invalid JSON: {escape(str(e))}"
            except ValueError as e: error_message = f"Input Error: {escape(str(e))}"
            except Exception as e: error_message = f"An unexpected error occurred: {escape(str(e))}"
        else: pass
    # Ensure you are passing the correctly defined HTML_TEMPLATE
    return render_template_string(
        HTML_TEMPLATE, # Use the variable defined above
        json_input=json_input,
        json_tree_html=json_tree_html,
        error=error_message
    )


# --- Main Execution (Keep as before) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG') == '1')