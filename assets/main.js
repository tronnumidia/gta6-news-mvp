document.getElementById('year').textContent = new Date().getFullYear();

const releaseDate = new Date('2026-12-31T00:00:00-03:00');

function pad(n) {
    return String(n).padStart(2, '0');
}

function updateCountdown() {
    const now = new Date();
    const diff = releaseDate - now;
    if (diff <= 0) {
        ['days','hours','minutes','seconds'].forEach(id => document.getElementById(id).textContent = '00');
        return;
    }
    document.getElementById('days').textContent = pad(Math.floor(diff / 86400000));
    document.getElementById('hours').textContent = pad(Math.floor((diff % 86400000) / 3600000));
    document.getElementById('minutes').textContent = pad(Math.floor((diff % 3600000) / 60000));
    document.getElementById('seconds').textContent = pad(Math.floor((diff % 60000) / 1000));
}

updateCountdown();
setInterval(updateCountdown, 1000);

function fallbackImg(img) {
    if (!img.src || img.src.includes('placehold.co')) return;
    img.src = 'data:image/svg+xml,' + encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340"><rect fill="#0f0020" width="600" height="340"/><text fill="#a855f7" x="300" y="170" text-anchor="middle" dominant-baseline="middle" font-family="monospace" font-size="22" font-weight="bold">GTA VI</text></svg>'
    );
}

async function loadData() {
    const newsGrid = document.getElementById('newsGrid');
    const videoGrid = document.getElementById('videoGrid');
    try {
        const res = await fetch('data/news.json?' + Date.now());
        if (!res.ok) throw new Error('Sem dados');
        const data = await res.json();

        if (data.news && data.news.length) {
            newsGrid.innerHTML = data.news.map(item => `
                <article class="news-card">
                    <img class="news-img" src="${item.image || ''}" alt="${item.title}" loading="lazy" onerror="fallbackImg(this)">
                    <div class="news-body">
                        <div class="news-source">${item.source || 'WK Games'}</div>
                        <h3 class="news-title">${item.title}</h3>
                        <p class="news-desc">${item.description || ''}</p>
                        <div class="news-date">${item.date || ''}</div>
                        <a class="news-link" href="${item.link}" target="_blank" rel="noopener">Ler mais →</a>
                    </div>
                </article>
            `).join('');
        } else {
            newsGrid.innerHTML = '<div class="loading">Aguardando primeira atualização do robô...</div>';
        }

        if (data.videos && data.videos.length) {
            videoGrid.innerHTML = data.videos.map(v => `
                <a class="video-card" href="${v.link}" target="_blank" rel="noopener">
                    <img class="video-thumb" src="${v.thumbnail || ''}" alt="${v.title}" loading="lazy" onerror="fallbackImg(this)">
                    <div class="video-body">
                        <div class="video-channel">${v.channel || 'YouTube'}</div>
                        <h3 class="video-title">${v.title}</h3>
                        <div class="news-date">${v.date || ''}</div>
                    </div>
                </a>
            `).join('');
        } else {
            videoGrid.innerHTML = '<div class="loading">Buscando vídeos dos canais...</div>';
        }
    } catch {
        newsGrid.innerHTML = '<div class="loading">Aguardando notícias em português...</div>';
        videoGrid.innerHTML = '<div class="loading">Buscando vídeos...</div>';
    }
}

loadData();