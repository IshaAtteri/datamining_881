from bs4 import BeautifulSoup
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "..", "data", "tt0074888.html")

def extract_movie_info(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")

    # -----------------------------
    # Title
    # -----------------------------
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    # -----------------------------
    # Genre (first line)
    # -----------------------------
    genre = None

    content = soup.find("div", id="mw-content-text")
    if content:
        first_paragraph = content.find("p")
        if first_paragraph:
            genre = first_paragraph.get_text(" ", strip=True)

    # -----------------------------
    # Infobox: Directed by + Starring
    # -----------------------------
    infobox = soup.find("table", class_="infobox")

    directed_by = None
    cast = []

    if infobox:
        rows = infobox.find_all("tr")

        for row in rows:
            header = row.find("th")
            data = row.find("td")

            if not header or not data:
                continue

            header_text = header.get_text(" ", strip=True)

            if header_text == "Directed by":
                directed_by = data.get_text(" ", strip=True)

            elif header_text == "Starring":
                # Get cast members split by <br> or links/text
                cast_items = list(data.stripped_strings)
                cast = cast_items[:5]

    # -----------------------------
    # Plot section
    # -----------------------------
    plot = ""

    plot_header = soup.find(id="Plot")

    if plot_header:
        # Move to the parent heading container if needed
        current = plot_header.parent

        for sibling in current.find_next_siblings():
            # Stop when next h2 section begins
            if sibling.name == "div" and "mw-heading2" in sibling.get("class", []):
                break
            if sibling.name == "p":
                plot += sibling.get_text(" ", strip=True) + " "

    plot = plot.strip()

    return title, directed_by, cast, genre, plot

# -----------------------------
# Print results
# -----------------------------
title, directed_by, cast, genre, plot = extract_movie_info(file_path)
print("Title:", title)
print("Directed by:", directed_by)
print("Cast:", cast)
print("Genre:", genre)
print("\nPlot:\n", plot)