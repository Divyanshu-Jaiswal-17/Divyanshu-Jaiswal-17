import os
import sys

# Configuration variables at top of file
HOST = "divyanshu@siemens-sts"
USER_NAME = "Divyanshu Jaiswal"

# Neofetch-style rows: (Key, Value, Color)
ROWS = [
    ("OS", "GitHub Profile OS x86_64", "#58a6ff"),
    ("Host", HOST, "#79c0ff"),
    ("User", f"{USER_NAME} (Divyanshu-Jaiswal-17)", "#3fb950"),
    ("Now", "Technical Intern @ Siemens Technology & Services (Full Stack & Data Analyst)", "#ffa657"),
    ("Edu", "B.Tech CSE, Tula's Institute, Dehradun", "#d2a8ff"),
    ("Languages", "Python, JavaScript, SQL", "#58a6ff"),
    ("Frontend", "HTML, CSS, React", "#3fb950"),
    ("Backend", "Node.js, Express.js", "#ffa657"),
    ("Database", "MySQL, MongoDB", "#79c0ff"),
    ("AI / GenAI", "LLM APIs, Generative AI, Prompt Engineering, RAG", "#d2a8ff"),
    ("BI / Tools", "Power BI, MS Excel, REST APIs", "#58a6ff"),
    ("Project 1", "METER/OPS — Multi-tenant billing platform (React, Node, MongoDB)", "#3fb950"),
    ("Project 2", "GenAI Academic Doc Generator — RAG + Gemini API (200+ users)", "#ffa657"),
]

def generate_info_card_svg(output_path: str) -> None:
    """Renders a neofetch-style animated info card SVG."""
    width = 570
    header_height = 40
    row_height = 23
    padding_x = 20
    padding_y = 20
    
    height = padding_y * 2 + header_height + len(ROWS) * row_height + 35
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<defs>')
    svg.append('  <style>')
    svg.append('    @keyframes cardFadeIn { 0% { opacity: 0; transform: translateY(5px); } 100% { opacity: 1; transform: translateY(0); } }')
    svg.append('    .card-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 12px; ry: 12px; }')
    svg.append('    .card-header-bar { fill: #161b22; rx: 12px; ry: 12px; }')
    svg.append('    .dot-red { fill: #ff5f56; }')
    svg.append('    .dot-yellow { fill: #ffbd2e; }')
    svg.append('    .dot-green { fill: #27c93f; }')
    svg.append('    .title-text { font-family: "Fira Code", Consolas, monospace; font-size: 12.5px; fill: #8b949e; font-weight: 600; }')
    svg.append('    .host-header { font-family: "Fira Code", Consolas, monospace; font-size: 13.5px; fill: #58a6ff; font-weight: bold; }')
    svg.append('    .separator { stroke: #30363d; stroke-width: 1; stroke-dasharray: 4 2; }')
    svg.append('    .key-text { font-family: "Fira Code", Consolas, monospace; font-size: 11.5px; font-weight: bold; }')
    svg.append('    .val-text { font-family: "Fira Code", Consolas, monospace; font-size: 11.5px; font-weight: 500; fill: #c9d1d9; }')
    svg.append('    .row-anim { opacity: 0; animation: cardFadeIn 0.25s ease-out forwards; }')
    svg.append('  </style>')
    svg.append('</defs>')
    
    # Outer Frame
    svg.append(f'<rect width="{width}" height="{height}" class="card-bg" />')
    # Top Bar
    svg.append(f'<path d="M 0 0 h {width} v 32 h -{width} Z" class="card-header-bar" />')
    svg.append('<circle cx="18" cy="16" r="5" class="dot-red" />')
    svg.append('<circle cx="34" cy="16" r="5" class="dot-yellow" />')
    svg.append('<circle cx="50" cy="16" r="5" class="dot-green" />')
    svg.append(f'<text x="{width / 2}" y="20" text-anchor="middle" class="title-text">neofetch — {HOST}</text>')
    
    curr_y = 56
    
    # Host header title inside terminal
    svg.append(f'<text x="{padding_x}" y="{curr_y}" class="host-header row-anim" style="animation-delay: 0.05s;">{HOST}</text>')
    curr_y += 10
    svg.append(f'<line x1="{padding_x}" y1="{curr_y}" x2="{width - padding_x}" y2="{curr_y}" class="separator row-anim" style="animation-delay: 0.08s;" />')
    curr_y += 20
    
    # Render rows
    delay = 0.10
    for key, val, color in ROWS:
        # Key column
        svg.append(f'<g class="row-anim" style="animation-delay: {delay:.2f}s;">')
        svg.append(f'  <text x="{padding_x}" y="{curr_y}" class="key-text" fill="{color}">{key}:</text>')
        # Value column
        escaped_val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        svg.append(f'  <text x="{padding_x + 105}" y="{curr_y}" class="val-text">{escaped_val}</text>')
        svg.append('</g>')
        curr_y += row_height
        delay += 0.03
        
    # Color palette footer blocks
    curr_y += 4
    svg.append(f'<g class="row-anim" style="animation-delay: {delay:.2f}s;">')
    colors = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#bc8cff", "#39d353", "#e34c26", "#f1e05a"]
    box_x = padding_x
    for c in colors:
        svg.append(f'  <rect x="{box_x}" y="{curr_y}" width="16" height="11" rx="3" fill="{c}" />')
        box_x += 22
    svg.append('</g>')
    
    svg.append('</svg>')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
        
    print(f"Generated info card SVG at: {output_path}")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_svg = os.path.join(repo_root, "info-card.svg")
    generate_info_card_svg(out_svg)
