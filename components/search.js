let debounceTimer;
let offset = 0;
const limit = 10;
let currentQuery = "";

const searchBox = document.getElementById("searchBox");
const resultsDiv = document.getElementById("results");
const loadMoreBtn = document.getElementById("loadMore");

function fetchManga(query, reset = false) {
    if (reset) {
        resultsDiv.innerHTML = "";
        offset = 0;
    }

    fetch(`/search?title=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`)
        .then(res => res.json())
        .then(data => {
            data.results.forEach(manga => {
                const div = document.createElement("div");
                div.className = "result";
                div.innerHTML = `
                    <img src="${manga.cover}" alt="cover">
                    <span>${manga.title}</span>
                `;
                div.onclick = () => window.location.href = `/manga/${manga.id}`;
                resultsDiv.appendChild(div);
            });

            if (data.total && offset + limit < data.total) {
                loadMoreBtn.style.display = "block";
                offset += limit;
            } else {
                loadMoreBtn.style.display = "none";
            }
        });
}

searchBox.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = searchBox.value.trim();
    currentQuery = query;
    if (!query) {
        resultsDiv.innerHTML = "";
        loadMoreBtn.style.display = "none";
        return;
    }

    debounceTimer = setTimeout(() => fetchManga(query, true), 400);
});

loadMoreBtn.addEventListener("click", () => fetchManga(currentQuery));
