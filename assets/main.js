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
    const colors = [
        ['#1a0030', '#ff007f', 'GTA VI'],
        ['#0a0015', '#00f0ff', 'GTA 6'],
        ['#1a0030', '#a855f7', 'GAME'],
        ['#0a0015', '#facc15', 'GTA VI'],
        ['#1a0030', '#ff6b00', 'GTA 6'],
    ];
    const idx = Math.floor(Math.random() * colors.length);
    const [bg, fg, label] = colors[idx];
    img.src = 'data:image/svg+xml,' + encodeURIComponent(
        `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340">
            <defs>
                <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:${bg};stop-opacity:1"/>
                    <stop offset="100%" style="stop-color:#0a0015;stop-opacity:1"/>
                </linearGradient>
            </defs>
            <rect fill="url(#g)" width="600" height="340"/>
            <text fill="${fg}" x="300" y="160" text-anchor="middle" dominant-baseline="middle" font-family="monospace" font-size="36" font-weight="bold" opacity="0.9">${label}</text>
            <text fill="#8a7aa0" x="300" y="200" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="14" opacity="0.5">WK GAMES NEWS</text>
        </svg>`
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
                    <img class="video-thumb" src="${v.thumbnail || ''}" alt="${v.title}" loading="lazy" onerror="this.src='data:image/svg+xml,'+encodeURIComponent('<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'600\\' height=\\'340\\'><rect fill=\\'#0f0020\\' width=\\'600\\' height=\\'340\\'/><text fill=\\'#ff007f\\' x=\\'300\\' y=\\'170\\' text-anchor=\\'middle\\' dominant-baseline=\\'middle\\' font-family=\\'monospace\\' font-size=\\'22\\' font-weight=\\'bold\\'>WK Video</text></svg>')">
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