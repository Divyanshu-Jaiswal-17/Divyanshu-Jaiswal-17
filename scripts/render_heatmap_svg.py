import os
import sys
import json
from datetime import datetime

# GitHub Dark Mode Heatmap Palette
COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353"
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

def render_heatmap_svg(json_path: str, output_path: str) -> None:
    """Reads contributions JSON and renders an animated SVG heatmap."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Contributions JSON not found at: {json_path}")
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    days = data.get("days", [])
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    username = data.get("username", "Divyanshu-Jaiswal-17")

    # Dimensions
    cell_size = 11
    cell_gap = 3
    padding_x = 35
    padding_y = 55
    header_height = 45
    
    # Organize days into weeks (53 weeks max)
    weeks = []
    current_week = []
    
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        wday = dt.weekday()  # Mon=0..Sun=6
        # Align with Sun=0..Sat=6
        wday_sun = (wday + 1) % 7
        d["wday"] = wday_sun
        d["dt"] = dt
        
    # Group into weeks
    if days:
        first_wday = days[0]["wday"]
        # Fill leading blank days in first week
        current_week = [None] * first_wday
        for d in days:
            current_week.append(d)
            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []
        if current_week:
            while len(current_week) < 7:
                current_week.append(None)
            weeks.append(current_week)

    cols = len(weeks)
    grid_width = cols * (cell_size + cell_gap)
    width = grid_width + padding_x + 30
    height = 7 * (cell_size + cell_gap) + padding_y + 60

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<defs>')
    svg.append('  <style>')
    svg.append('    @keyframes cellFade { 0% { opacity: 0; transform: scale(0.5); } 100% { opacity: 1; transform: scale(1); } }')
    svg.append('    .heatmap-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 12px; ry: 12px; }')
    svg.append('    .heatmap-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #c9d1d9; font-weight: 600; }')
    svg.append('    .heatmap-stat-val { font-family: "Fira Code", Consolas, monospace; font-size: 13px; fill: #58a6ff; font-weight: bold; }')
    svg.append('    .heatmap-stat-lbl { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; fill: #8b949e; }')
    svg.append('    .label-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 10px; fill: #8b949e; }')
    svg.append('    .cell { rx: 2px; ry: 2px; transition: transform 0.2s ease, stroke 0.2s ease; cursor: pointer; transform-origin: center; }')
    svg.append('    .cell:hover { stroke: #58a6ff; stroke-width: 1.5px; transform: scale(1.3); z-index: 10; }')
    svg.append('  </style>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{width}" height="{height}" class="heatmap-bg" />')
    
    # Title & Stats Header
    svg.append(f'<text x="{padding_x}" y="28" class="heatmap-title">Contribution Activity — <tspan class="heatmap-stat-val">{username}</tspan></text>')
    
    # Stats Badges (Right Aligned)
    stats_str = f'Total: {total_contribs}  |  Current Streak: {current_streak} days  |  Longest Streak: {longest_streak} days'
    svg.append(f'<text x="{width - 25}" y="28" text-anchor="end" class="heatmap-stat-lbl">{stats_str}</text>')
    
    # Month Labels
    curr_month = -1
    for w_idx, week in enumerate(weeks):
        for day in week:
            if day and day["dt"].day <= 7 and day["dt"].month != curr_month:
                curr_month = day["dt"].month
                month_str = MONTH_NAMES[curr_month - 1]
                x_pos = padding_x + w_idx * (cell_size + cell_gap)
                svg.append(f'<text x="{x_pos}" y="48" class="label-text">{month_str}</text>')
                break

    # Day Labels (Mon, Wed, Fri)
    day_indices = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for d_idx, d_name in day_indices:
        y_pos = padding_y + d_idx * (cell_size + cell_gap) + 9
        svg.append(f'<text x="{padding_x - 22}" y="{y_pos}" class="label-text">{d_name}</text>')

    # Render Cells
    for w_idx, week in enumerate(weeks):
        x_pos = padding_x + w_idx * (cell_size + cell_gap)
        for d_idx, day in enumerate(week):
            if day is None:
                continue
            y_pos = padding_y + d_idx * (cell_size + cell_gap)
            level = day.get("level", 0)
            count = day.get("count", 0)
            date_str = day.get("date", "")
            fill_color = COLORS.get(level, COLORS[0])
            
            tooltip_txt = f"{count} contributions on {date_str}"
            svg.append(f'  <rect x="{x_pos}" y="{y_pos}" width="{cell_size}" height="{cell_size}" fill="{fill_color}" class="cell"><title>{tooltip_txt}</title></rect>')

    # Legend at bottom right
    legend_y = height - 20
    legend_x = width - 170
    svg.append(f'<text x="{legend_x - 30}" y="{legend_y + 9}" class="label-text">Less</text>')
    for lvl in range(5):
        lx = legend_x + lvl * (cell_size + 3)
        svg.append(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" fill="{COLORS[lvl]}" class="cell" />')
    svg.append(f'<text x="{legend_x + 5 * (cell_size + 3) + 5}" y="{legend_y + 9}" class="label-text">More</text>')

    svg.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
        
    print(f"Generated heatmap SVG at: {output_path}")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = os.path.join(repo_root, "data", "contributions.json")
    out_svg = os.path.join(repo_root, "contrib-heatmap.svg")
    
    render_heatmap_svg(json_path, out_svg)
