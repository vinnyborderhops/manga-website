from flask import Flask, render_template, request, jsonify, Response
from bs4 import BeautifulSoup
import markdown as md
import requests
import time

app = Flask(__name__)
BASE_URL = "https://api.mangadex.org"
RANDOM_URL = "https://mangapill.com/mangas/random"

cover_cache = {}
page_cache = {}
CACHE_TTL = 60 * 60 * 24

session = requests.Session()


def search_manga(title):
    url = f"{BASE_URL}/manga"
    params = {"title": title, "limit": 5}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["data"]


def get_cover(manga_id):
    url = f"{BASE_URL}/cover"
    params = {"manga[]": manga_id, "limit": 1}

    # Use the session for the first request
    r = session.get(url, params=params)
    r.raise_for_status()
    data = r.json()["data"]
    if not data:
        return None

    cover_file = data[0]["attributes"]["fileName"]
    cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_file}"

    # Use the same session for the image request
    img = session.get(cover_url)
    img.raise_for_status()
    return img.headers["Content-Type"], img.content


def get_chapters(manga_id):
    chapters = []
    limit = 100
    offset = 0

    while True:
        url = f"{BASE_URL}/chapter"
        params = {
            "manga": manga_id,
            "limit": limit,
            "offset": offset,
            "translatedLanguage[]": ["en"],
            "order[chapter]": "asc"
        }

        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()["data"]

        if not data:
            break

        chapters.extend(data)
        offset += len(data)

        if len(data) < limit:
            break

    return chapters


def get_chapter(chapter_id):
    url = f"{BASE_URL}/chapter/{chapter_id}"
    r = requests.get(url)
    r.raise_for_status()
    chapter = r.json()["data"]
    return chapter


def get_chapter_pages(chapter_id):
    url = f"{BASE_URL}/at-home/server/{chapter_id}"
    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError(f"Chapter {chapter_id} has no readable pages.")

    response.raise_for_status()
    data = response.json()
    base_url = data["baseUrl"]
    chapter_hash = data["chapter"]["hash"]
    page_files = data["chapter"]["data"]

    if not page_files:
        raise ValueError(f"Chapter {chapter_id} contains no pages.")

    page_urls = [
        f"{base_url}/data/{chapter_hash}/{page}" for page in page_files
    ]
    return page_urls


def fetch_page(chapter_id, page_index, url):
    now = time.time()
    if chapter_id not in page_cache:
        page_cache[chapter_id] = {}

    if page_index in page_cache[chapter_id]:
        ts, ctype, content = page_cache[chapter_id][page_index]
        if now - ts < CACHE_TTL:
            return ctype, content

    r = requests.get(url)
    r.raise_for_status()
    page_cache[chapter_id][page_index] = (now, r.headers["Content-Type"],
                                          r.content)
    return r.headers["Content-Type"], r.content


def random_manga():
    random_request = requests.get(RANDOM_URL)
    while random_request.url == "https://mangapill.com/manga/0":
        random_request = requests.get(RANDOM_URL)
    random_soup = BeautifulSoup(random_request.text, "html.parser")
    random_title = random_soup.title.string.rstrip(" - Mangapill!")
    return random_title


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    title = request.args.get("title", "")
    if not title:
        return jsonify([])

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    url = f"{BASE_URL}/manga"
    params = {"title": title, "limit": limit, "offset": offset}
    r = requests.get(url, params=params)
    r.raise_for_status()
    manga_results = r.json()["data"]
    results = []

    for manga in manga_results:
        manga_id = manga["id"]
        manga_title = manga["attributes"]["title"].get("en") or list(
            manga["attributes"]["title"].values())[0]
        cover_url = f"/cover/{manga_id}" or "https://via.placeholder.com/128x192?text=No+Cover"
        results.append({
            "id": manga_id,
            "title": manga_title,
            "cover": cover_url
        })

    total = r.json()["total"] if "total" in r.json() else None
    return jsonify({"results": results, "total": total})


@app.route("/cover/<manga_id>")
def proxy_cover(manga_id):
    now = time.time()
    if manga_id in cover_cache:
        ts, ctype, content = cover_cache[manga_id]
        if now - ts < CACHE_TTL:
            return Response(content, content_type=ctype)

    result = get_cover(manga_id)
    if not result:
        return jsonify({"error": "No cover"}), 404

    ctype, content = result
    cover_cache[manga_id] = (now, ctype, content)
    return Response(content, content_type=ctype)


@app.route("/manga/<manga_id>")
def manga_page(manga_id):
    url = f"{BASE_URL}/manga/{manga_id}"
    r = requests.get(url)
    r.raise_for_status()
    manga = r.json()["data"]

    title = manga["attributes"]["title"].get("en") or list(
        manga["attributes"]["title"].values())[0]
    cover_url = f"/cover/{manga_id}"

    # Get description
    desc_dict = manga["attributes"].get("description", {})
    description_md = desc_dict.get("en") or next(iter(desc_dict.values()), "")

    description_html = md.markdown(description_md)

    chapters = get_chapters(manga_id)
    chapter_list = []
    for ch in chapters:
        chap_num = ch["attributes"].get("chapter")
        chap_title = ch["attributes"].get("title")
        chap_id = ch["id"]
        chapter_list.append({
            "id": chap_id,
            "number": chap_num,
            "title": chap_title
        })

    return render_template("manga.html",
                           title=title,
                           cover=cover_url,
                           description=description_html,
                           chapters=chapter_list)


@app.route("/chapter/<chapter_id>")
def chapter_page(chapter_id):
    chapter_url = f"{BASE_URL}/chapter/{chapter_id}"
    chapter_resp = requests.get(chapter_url)
    chapter_resp.raise_for_status()
    chapter_data = chapter_resp.json()["data"]
    chapter_num = chapter_data["attributes"].get("chapter")
    chapter_title = chapter_data["attributes"].get("title", "")

    manga_id = next(
        (rel["id"]
         for rel in chapter_data["relationships"] if rel["type"] == "manga"),
        None)
    if not manga_id:
        return "Manga not found", 404

    manga_url = f"{BASE_URL}/manga/{manga_id}"
    manga_resp = requests.get(manga_url)
    manga_resp.raise_for_status()
    manga_data = manga_resp.json()["data"]
    manga_title = manga_data["attributes"]["title"].get("en") or list(
        manga_data["attributes"]["title"].values())[0]

    chapters = get_chapters(manga_id)

    def safe_chapter_num(ch):
        num = ch["attributes"].get("chapter")
        try:
            return float(num)
        except (TypeError, ValueError):
            return float("inf")

    chapters_sorted = sorted(chapters, key=safe_chapter_num)
    current_index = next(
        (i for i, c in enumerate(chapters_sorted) if c["id"] == chapter_id), 0)

    pages = get_chapter_pages(chapter_id)
    total_pages = len(pages)

    return render_template("chapter.html",
                           manga_title=manga_title,
                           chapter_num=chapter_num,
                           chapter_title=chapter_title,
                           chapter_id=chapter_id,
                           total_pages=total_pages,
                           chapters=chapters_sorted,
                           current_index=current_index)


@app.route("/chapter/<chapter_id>/page/<int:page_index>")
def serve_chapter_page(chapter_id, page_index):
    try:
        urls = get_chapter_pages(chapter_id)
    except ValueError as e:
        return str(e), 404

    if page_index < 0 or page_index >= len(urls):
        return "Page not found", 404

    ctype, content = fetch_page(chapter_id, page_index, urls[page_index])
    return Response(content, content_type=ctype)


@app.route("/random")
def random():
    title = random_manga()
    return jsonify({"title": title})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
