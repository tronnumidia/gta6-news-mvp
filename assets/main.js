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
    if (img.src && img.src.includes('placehold.co')) return;
    const colors = [
        ['15152a', 'a855f7', 'GTA VI'],
        ['15152a', 'ff007f', 'GTA 6'],
        ['15152a', '00f0ff', 'GAME'],
    ];
    const idx = Math.floor(Math.random() * colors.length);
    const [bg, fg, label] = colors[idx];
    img.src = 'data:image/svg+xml,' + encodeURIComponent(
        `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340">
            <rect fill="#${bg}" width="600" height="340"/>
            <text fill="#${fg}" x="300" y="170" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="28" font-weight="bold">${label}</text>
        </svg>`
    );
}

async function loadData() {
    const newsGrid = document.getElementById('newsGrid');
    const videoGrid = document.getElementById('videoGrid');
    try {
        const res = await fetch('data/news.json?' + Date.now());
        if (!res.ok) throw new Error();
        const data = await res.json();

        if (data.news && data.news.length) {
            newsGrid.innerHTML = data.news.map(item => `
                <article class="news-card">
                    <img class="news-img" src="${item.image || ''}" alt="" loading="lazy" onerror="fallbackImg(this)">
                    <div class="news-body">
                        <div class="news-source">${item.source || 'WK'}</div>
                        <h3 class="news-title">${item.title}</h3>
                        <p class="news-desc">${item.description || ''}</p>
                        <div class="news-meta">
                            <span class="news-date">${item.date || ''}</span>
                            <a class="news-link" href="${item.link}" target="_blank" rel="noopener">Ler →</a>
                        </div>
                    </div>
                </article>
            `).join('');
        } else {
            newsGrid.innerHTML = '<div class="loading">Aguardando primeira atualização...</div>';
        }

        if (data.videos && data.videos.length) {
            videoGrid.innerHTML = data.videos.map(v => `
                <a class="video-card" href="${v.link}" target="_blank" rel="noopener">
                    <img class="video-thumb" src="${v.thumbnail || ''}" alt="" loading="lazy" onerror="this.src='data:image/svg+xml,'+encodeURIComponent('<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'600\\' height=\\'340\\'><rect fill=\\'#15152a\\' width=\\'600\\' height=\\'340\\'/><text fill=\\'#ff007f\\' x=\\'300\\' y=\\'170\\' text-anchor=\\'middle\\' dominant-baseline=\\'middle\\' font-family=\\'sans-serif\\' font-size=\\'22\\' font-weight=\\'bold\\'>WK</text></svg>')">
                    <div class="video-body">
                        <div class="video-channel">${v.channel || ''}</div>
                        <div class="video-title">${v.title}</div>
                        <div class="video-date">${v.date || ''}</div>
                    </div>
                </a>
            `).join('');
        } else {
            videoGrid.innerHTML = '<div class="loading">Buscando vídeos...</div>';
        }
    } catch {
        newsGrid.innerHTML = '<div class="loading">Carregando notícias...</div>';
        videoGrid.innerHTML = '<div class="loading">Carregando vídeos...</div>';
    }
}

loadData();