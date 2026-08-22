import os
import sys

USER_NAME = "Divyanshu Jaiswal"
GITHUB_HANDLE = "Divyanshu-Jaiswal-17"
HOST_COMMAND = "divyanshu@github:~$ ./portrait.sh"
INK_COLOR = "#c9d1d9"

def generate_ascii_svg_from_file(ascii_txt_path: str, output_path: str) -> None:
    """
    Reads raw ASCII art text directly from ascii-art.txt and renders an animated 
    terminal SVG card (avi-ascii.svg) with single ink color #c9d1d9, title-bar controls,
    and row-by-row reveal animation.
    """
    if not os.path.exists(ascii_txt_path):
        raise FileNotFoundError(f"ASCII text file not found at: {ascii_txt_path}")
        
    with open(ascii_txt_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f.readlines() if line.strip("\r\n") != ""]
        
    if not lines:
        raise ValueError("ASCII text file is empty!")
        
    cols = max(len(line) for line in lines)
    rows = len(lines)
    
    # Precise character & line dimensions for crisp terminal rendering
    font_size = 7.5
    char_width = 4.8
    line_height = 9.2
    padding_x = 20
    padding_y = 45
    
    svg_width = int(cols * char_width + padding_x * 2 + 10)
    svg_height = int(rows * line_height + padding_y + 35)
    
    animation_duration_per_line = 0.025
    
    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">')
    svg_lines.append('<defs>')
    svg_lines.append('  <style>')
    svg_lines.append('    @keyframes lineFadeIn {')
    svg_lines.append('      0% { opacity: 0; transform: translateY(2px); }')
    svg_lines.append('      100% { opacity: 1; transform: translateY(0); }')
    svg_lines.append('    }')
    svg_lines.append('    @keyframes cursorBlink {')
    svg_lines.append('      0%, 100% { opacity: 1; }')
    svg_lines.append('      50% { opacity: 0; }')
    svg_lines.append('    }')
    svg_lines.append('    .terminal-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 10px; ry: 10px; }')
    svg_lines.append('    .terminal-header { fill: #161b22; rx: 10px; ry: 10px; }')
    svg_lines.append('    .btn-red { fill: #ff5f56; }')
    svg_lines.append('    .btn-yellow { fill: #ffbd2e; }')
    svg_lines.append('    .btn-green { fill: #27c93f; }')
    svg_lines.append('    .cmd-text { font-family: "Fira Code", "Courier New", Consolas, monospace; font-size: 11px; fill: #58a6ff; font-weight: 600; }')
    svg_lines.append('    .user-text { font-family: "Fira Code", "Courier New", Consolas, monospace; font-size: 11px; fill: #3fb950; font-weight: bold; }')
    svg_lines.append(f'    .ascii-line {{ font-family: "Fira Code", "Courier New", Consolas, monospace; font-size: {font_size}px; fill: {INK_COLOR}; opacity: 0; animation: lineFadeIn 0.1s ease-out forwards; white-space: pre; }}')
    svg_lines.append('    .cursor { fill: #58a6ff; animation: cursorBlink 1s infinite; }')
    svg_lines.append('  </style>')
    svg_lines.append('</defs>')
    
    # Terminal Window Background & Header
    svg_lines.append(f'<rect width="{svg_width}" height="{svg_height}" class="terminal-bg" />')
    svg_lines.append(f'<path d="M 0 0 h {svg_width} v 30 h -{svg_width} Z" class="terminal-header" />')
    svg_lines.append('<circle cx="18" cy="15" r="5.5" class="btn-red" />')
    svg_lines.append('<circle cx="34" cy="15" r="5.5" class="btn-yellow" />')
    svg_lines.append('<circle cx="50" cy="15" r="5.5" class="btn-green" />')
    svg_lines.append(f'<text x="{svg_width / 2}" y="19" text-anchor="middle" fill="#8b949e" font-family="Fira Code, monospace" font-size="11px">{USER_NAME} — ascii-art</text>')
    
    y_pos = padding_y
    delay = 0.10
    
    # Command prompt
    svg_lines.append(f'<text x="{padding_x}" y="{y_pos}" class="cmd-text" style="animation: lineFadeIn 0.15s ease-out {delay:.2f}s forwards; opacity: 0;">{HOST_COMMAND}</text>')
    y_pos += line_height + 4
    delay += animation_duration_per_line
    
    # ASCII Art Rows
    for line in lines:
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        svg_lines.append(f'<text x="{padding_x}" y="{y_pos:.1f}" class="ascii-line" style="animation-delay: {delay:.2f}s;">{escaped_line}</text>')
        y_pos += line_height
        delay += animation_duration_per_line
        
    # Output name & cursor
    y_pos += 6
    svg_lines.append(f'<text x="{padding_x}" y="{y_pos:.1f}" class="user-text" style="animation: lineFadeIn 0.15s ease-out {delay:.2f}s forwards; opacity: 0;">[ identity: {USER_NAME} ]</text>')
    svg_lines.append(f'<rect x="{padding_x + 175}" y="{y_pos - 10:.1f}" width="7" height="11" class="cursor" />')
    
    svg_lines.append('</svg>')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
        
    print(f"Generated animated ASCII SVG from '{ascii_txt_path}' at: {output_path}")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ascii_txt = os.path.join(repo_root, "ascii-art.txt")
    if not os.path.exists(ascii_txt):
        ascii_txt = os.path.join(repo_root, "scripts", "ascii-art.txt")
    out_svg = os.path.join(repo_root, "avi-ascii.svg")
    
    generate_ascii_svg_from_file(ascii_txt, out_svg)
