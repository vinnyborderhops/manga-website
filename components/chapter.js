const chapterPagesDiv = document.getElementById("chapterPages");
let currentIndex = 0;
const CHUNK_SIZE = 5;
const totalPages = "{{ total_pages }}";
const chapterId = "{{ chapter_id }}";
let loading = false;

async function loadNextBatch() {
    if (loading || currentIndex >= totalPages) return;
    loading = true;
    for (let i = 0; i < CHUNK_SIZE && currentIndex < totalPages; i++) {
        const pageIndex = currentIndex;
        const img = document.createElement("img");
        img.src = `/chapter/${chapterId}/page/${pageIndex}`;
        img.alt = `Page ${pageIndex + 1}`;
        img.style.maxWidth = "90%";
        chapterPagesDiv.appendChild(img);
        currentIndex++;
    }
    loading = false;
}

window.addEventListener("scroll", () => {
    if (window.scrollY + window.innerHeight >= document.body.offsetHeight - 200) {
        loadNextBatch();
    }
});

loadNextBatch();

const chapters = {{ chapters| tojson }};
const currentChapterIndex = {{ current_index }};

function goToChapter(index) {
    if (index >= 0 && index < chapters.length) {
        window.location.href = `/chapter/${chapters[index].id}`;
    }
}

document.getElementById("prevChapterTop").onclick = () => goToChapter(currentChapterIndex - 1);
document.getElementById("nextChapterTop").onclick = () => goToChapter(currentChapterIndex + 1);

document.getElementById("prevChapterBottom").onclick = () => goToChapter(currentChapterIndex - 1);
document.getElementById("nextChapterBottom").onclick = () => goToChapter(currentChapterIndex + 1);
