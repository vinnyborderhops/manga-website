const chapterResultsDiv = document.getElementById("chapterResults");

const allChapters = {{ chapters | tojson }};

function renderChapters(chapters) {
    chapterResultsDiv.innerHTML = "";
    chapters.forEach(ch => {
        const div = document.createElement("div");
        div.className = "chapter";
        div.innerHTML = `<a href="/chapter/${ch.id}">Chapter ${ch.number || '?'}</a>`;
        div.onclick = () => window.location.href = `/chapter/${ch.id}`;
        chapterResultsDiv.appendChild(div);
    });
}

renderChapters(allChapters);

document.getElementById("chapterSearch").addEventListener("input", () => {
    const query = document.getElementById("chapterSearch").value.toLowerCase().trim();
    const filtered = allChapters.filter(ch => {
        const title = ch.title || "";
        const number = ch.number || "";
        return title.toLowerCase().includes(query) || number.toString().includes(query);
    });
    renderChapters(filtered);
});
