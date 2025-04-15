import os
from flask import Flask, request, render_template_string
from markupsafe import escape
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Color Palette (Keep as before)
NODE_COLOR_PALETTE = ["#005f73", "#7a1a4f", "#a4710a", "#9b2226", "#343a40"]

# --- HTML Template with Updated CSS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XML Tree Viewer</title>
    <style>
        /* --- Base Styles (Keep as before) --- */
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            background-color: #f8f9fa;
            color: #495057;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 20px auto;
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        h1 {
            color: #343a40;
            text-align: center;
            margin-bottom: 30px;
        }
        textarea {
            width: 100%;
            min-height: 150px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            font-size: 13px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        button {
            display: block;
            width: 100%;
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        button:hover {
            background-color: #0056b3;
        }
        .error-message {
            color: #dc3545;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 20px;
            white-space: pre-wrap;
        }
        hr {
            border: none;
            border-top: 1px solid #dee2e6;
            margin: 30px 0;
        }

        /* --- XML Tree Styles (Only Toggle.empty updated) --- */
        .xml-tree {
            margin-top: 20px;
            padding-left: 0;
            overflow-x: auto;
        }
        .xml-tree ul {
            list-style-type: none;
            padding-left: 28px;
            margin-top: 5px;
            border-left: 1px dashed #adb5bd;
        }
        .xml-tree li {
            position: relative;
            margin-bottom: 5px;
        }
        .xml-tree li::before {
            content: "";
            position: absolute;
            top: 11px;
            left: -16px;
            width: 16px;
            height: 1px;
            background-color: #adb5bd;
        }
        .xml-tree li:last-child > ul {
            border-left: none;
        }
        .xml-tree li:last-child::after {
            content: "";
            position: absolute;
            top: 11px;
            left: -16px;
            width: 1px;
            height: calc(50% - 11px);
            background-color: #ffffff;
        }

        .node-content {
            display: flex;
            align-items: center;
            flex-wrap: nowrap;
            cursor: default;
            min-height: 26px;
            padding-bottom: 2px;
        }

        /* --- Toggle Arrow Styling --- */
        .toggle {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            width: 18px;
            height: 18px;
            cursor: pointer;
            margin-right: 8px;
            font-weight: bold;
            color: #8B0000; /* Dark Cherry / DarkRed for clickable toggles */
            user-select: none;
            font-size: 12px;
            text-align: center;
            line-height: 1;
            transition: opacity 0.2s ease; /* Add transition for opacity */
        }
        /* --- Style for NON-EXPANDABLE nodes (leaf nodes) --- */
        .toggle.empty {
             opacity: 0.4; /* Make it visible but faded */
             cursor: default; /* Keep non-clickable cursor */
             /* color: #b0a0a0; */ /* Alternative: use a faded color instead of opacity */
        }
        .toggle::before {
            content: '►'; /* Default (collapsed) state: Right arrow */
            display: inline-block;
        }
        /* Style for EXPANDED nodes (only applies if not .empty) */
        .toggle.expanded::before {
            content: '▼'; /* Expanded state: Down arrow */
        }

        /* --- Pill Style for Tag Names (Keep as before) --- */
        .tag-name {
            color: #ffffff;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.9em;
            margin-right: 8px;
            display: inline-block;
            line-height: 1.3;
            white-space: nowrap;
            flex-shrink: 0;
        }

        /* --- Styling for Attributes (Keep as before) --- */
        .attributes {
            margin-left: 5px;
            display: inline-flex;
            flex-wrap: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex-shrink: 1;
        }
        .attribute {
            margin-right: 12px;
            font-size: 0.85em;
            display: inline-block;
            white-space: nowrap;
        }
        .attr-name {
            color: #6f42c1;
        }
        .attr-equals {
            color: #adb5bd;
            margin: 0 2px;
        }
        .attr-value {
            color: #198754;
            font-style: normal;
        }

        /* --- Styling for Text Content (Keep as before) --- */
        .text-content {
            color: #5a6268;
            margin-left: 8px;
            font-style: italic;
            word-break: break-word;
            background-color: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
            border: 1px solid #dee2e6;
            line-height: 1.4;
            white-space: normal;
            flex-shrink: 1;
            overflow-wrap: break-word;
        }

        /* Hide children initially */
        .xml-tree ul.collapsed {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>XML Tree Viewer</h1>
        <form method="post">
            <textarea name="xml_data" placeholder="Paste your XML here (Namespaced XML recommended for color variation)...">{{ xml_input | safe }}</textarea>
            <button type="submit">Display Tree</button>
        </form>

        {% if error %}
            <div class="error-message">
                <strong>Error parsing XML:</strong><br>
                {{ error }}
            </div>
        {% elif xml_tree_html %}
            <hr>
            <h2>XML Tree Structure</h2>
            <div id="xml-viewer">
                {{ xml_tree_html | safe }}
            </div>
        {% endif %}
    </div>

    <script>
        // --- Keep JavaScript Exactly the Same ---
        document.addEventListener('DOMContentLoaded', function() {
            const treeContainer = document.getElementById('xml-viewer');
            if (treeContainer) {
                treeContainer.addEventListener('click', function(event) {
                    const toggle = event.target.closest('.toggle');
                    // Important: Only proceed if toggle exists AND is NOT empty
                    if (toggle && !toggle.classList.contains('empty')) {
                        const parentLi = toggle.closest('li');
                        const childUl = parentLi.querySelector(':scope > ul');
                        if (childUl) {
                            childUl.classList.toggle('collapsed');
                            toggle.classList.toggle('expanded');
                            const isExpanded = !childUl.classList.contains('collapsed');
                            parentLi.setAttribute('aria-expanded', isExpanded.toString());
                        }
                    }
                });

                const allToggles = treeContainer.querySelectorAll('.toggle');
                allToggles.forEach(toggle => {
                    // Only add collapsed class logic to non-empty toggles
                    if (!toggle.classList.contains('empty')) {
                         const parentLi = toggle.closest('li');
                         const childUl = parentLi.querySelector(':scope > ul');
                         if (childUl) {
                             childUl.classList.add('collapsed');
                             parentLi.setAttribute('aria-expanded', 'false');
                         }
                    } else {
                        // Mark empty toggles for accessibility, but don't add expand/collapse logic
                         toggle.setAttribute('aria-hidden', 'true');
                    }
                });
            }
        });
    </script>
</body>
</html>
"""

# --- Helper Function (Keep as before) ---
def generate_html_tree(element, depth=0):
    html = f'<li>'
    has_children = len(element) > 0
    # Treat as having text only if it's not just whitespace
    has_text = element.text and element.text.strip()
    full_tag = element.tag
    local_tag = full_tag.split('}')[-1] if '}' in full_tag else full_tag
    palette_index = depth % len(NODE_COLOR_PALETTE)
    bg_color = NODE_COLOR_PALETTE[palette_index]
    text_color = "#ffffff"

    html += '<div class="node-content">'
    toggle_class = "toggle"
    # Add .empty class ONLY if there are NO children elements.
    # The presence of text doesn't prevent it from being .empty in terms of expandability.
    if not has_children:
        toggle_class += " empty"
    html += f'<span class="{toggle_class}"></span>'
    html += f'<span class="tag-name" style="background-color: {bg_color}; color: {text_color};">{escape(local_tag)}</span>'

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

    if has_text:
        html += f'<span class="text-content">{escape(element.text.strip())}</span>'

    html += '</div>' # End Node Content

    if has_children:
        html += '<ul class="collapsed">'
        for child in element:
            html += generate_html_tree(child, depth + 1)
            if child.tail and child.tail.strip():
                 html += f'<li><div class="node-content"><span class="toggle empty"></span><span class="text-content" style="margin-left: 0;">{escape(child.tail.strip())}</span></div></li>'
        html += '</ul>'

    html += '</li>'
    return html

# --- Flask Routes (Keep as before) ---
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
                root = ET.fromstring(clean_xml_input)
                xml_tree_html = f'<ul class="xml-tree">{generate_html_tree(root, depth=0)}</ul>'
            except ET.ParseError as e:
                error_message = f"Invalid XML: {escape(str(e))}"
            except ValueError as e:
                 error_message = f"Input Error: {escape(str(e))}"
            except Exception as e:
                error_message = f"An unexpected error occurred: {escape(str(e))}"
        else:
            pass
    return render_template_string(
        HTML_TEMPLATE,
        xml_input=xml_input,
        xml_tree_html=xml_tree_html,
        error=error_message
    )

# --- Main Execution (Keep as before) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG') == '1')