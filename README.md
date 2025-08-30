# 📖 Manga Website

A lightweight manga reader web app built with **Flask** that integrates with the [MangaDex API](https://api.mangadex.org).  
It allows you to **search manga**, **browse chapters**, and **read pages** directly in the browser with lazy-loading for smooth scrolling.

---

## ✨ Features

- 🔎 **Search Manga** by title (uses MangaDex API)
- 📚 **Browse Chapters** with live chapter search
- 📖 **Read Chapters** with infinite scroll (lazy-loads pages in chunks for performance)
- 🖼️ **Covers** are proxied and cached locally for faster loads
- ⏮️⏭️ **Previous/Next Chapter Navigation** with buttons at top and bottom
- ⚡ **Caching System** for covers and chapter pages (24-hour TTL)

---

## 🛠️ Requirements

- Python **3.8+**
- Flask

Install dependencies:

```bash
pip install flask requests
```

---

## 🚀 Usage
1. Clone the repository
```bash
git clone https://github.com/vinnyborderhops/manga-website.git
cd manga-website
```
2. Run the server
```bash
python main.py
```
3. Open in browser
```cpp
http://127.0.0.1:5500/
```

---

## 🔧 API & Technical Notes
- Uses MangaDex REST API for manga, covers, and chapter data
- Implements local caching (covers + chapter pages) with 24-hour TTL
- Chapter images are lazy-loaded in batches of 5 for performance
- Includes debounced search to reduce API requests

---

## 📜 License
- This project is for educational and personal use only.
- Manga content is served via [MangaDex](https://mangadex.org/) and is not hosted in this repository.
