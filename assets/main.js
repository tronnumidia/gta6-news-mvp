document.getElementById('year').textContent = new Date().getFullYear();

const releaseDate = new Date('2026-12-31T00:00:00');

function updateCountdown() {
    const now = new Date();
    const diff = releaseDate - now;
    if (diff <= 0) {
        document.getElementById('countdown-title').textContent = 'GTA 6 JÁ ESTÁ ENTRE NÓS!';
        document.querySelectorAll('.count-item span').forEach(el => el.textContent = '00');
        return;
    }
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    document.getElementById('days').textContent = String(d).padStart(2, '0');
    document.getElementById('hours').textContent = String(h).padStart(2, '0');
    document.getElementById('minutes').textContent = String(m).padStart(2, '0');
    document.getElementById('seconds').textContent = String(s).padStart(2, '0');
}

updateCountdown();
setInterval(updateCountdown, 1000);

async function loadData() {
    try {
        const res = await fetch('data/news.json');
        if (!res.ok) throw new Error('Sem dados ainda');
        const data = await res.json();

        const newsGrid = document.getElementById('newsGrid');
        newsGrid.innerHTML = data.news.map(item => `
            <article class="news-card">
                <img class="news-img" src="${item.image || 'https://placehold.co/600x340/13131a/00ff88?text=GTA+6'}" alt="${item.title}" loading="lazy" onerror="this.src='https://placehold.co/600x180/13131a/00ff88?text=GTA+6'">
                <div class="news-body">
                    <div class="news-source">${item.source || 'WK Games'}</div>
                    <h3 class="news-title">${item.title}</h3>
                    <p class="news-desc">${item.description || ''}</p>
                    <div class="news-date">${item.date || ''}</div>
                    <a class="news-link" href="${item.link}" target="_blank" rel="noopener">Ler mais →</a>
                </div>
            </article>
        `).join('');

        const videoGrid = document.getElementById('videoGrid');
        videoGrid.innerHTML = (data.videos || []).map(v => `
            <a class="video-card" href="${v.link}" target="_blank" rel="noopener">
                <img class="video-thumb" src="${v.thumbnail}" alt="${v.title}" loading="lazy" onerror="this.src='https://placehold.co/600x180/13131a/ff0066?text=Video'">
                <div class="video-body">
                    <div class="video-channel">${v.channel || 'YouTube'}</div>
                    <h3 class="video-title">${v.title}</h3>
                    <div class="news-date">${v.date || ''}</div>
                </div>
            </a>
        `).join('');
    } catch (e) {
        document.getElementById('newsGrid').innerHTML = '<div class="loading">Ainda sem notícias. O robô está preparando as primeiras atualizações...</div>';
        document.getElementById('videoGrid').innerHTML = '<div class="loading">Buscando vídeos...</div>';
    }
}

loadData();