document.getElementById('year').textContent = new Date().getFullYear();

const releaseDate = new Date('2026-12-31T00:00:00-03:00');

function pad(n) {
    return String(n).padStart(2, '0');
}

function updateCountdown() {
    const now = new Date();
    const diff = releaseDate - now;
    if (diff <= 0) {
        document.getElementById('days').textContent = '00';
        document.getElementById('hours').textContent = '00';
        document.getElementById('minutes').textContent = '00';
        document.getElementById('seconds').textContent = '00';
        return;
    }
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    document.getElementById('days').textContent = pad(d);
    document.getElementById('hours').textContent = pad(h);
    document.getElementById('minutes').textContent = pad(m);
    document.getElementById('seconds').textContent = pad(s);
}

updateCountdown();
setInterval(updateCountdown, 1000);

async function loadData() {
    const newsGrid = document.getElementById('newsGrid');
    const videoGrid = document.getElementById('videoGrid');
    try {
        const res = await fetch('data/news.json?' + Date.now());
        if (!res.ok) throw new Error('Sem dados');
        const data = await res.json();

        if (data.news && data.news.length) {
            newsGrid.innerHTML = data.news.map(item => {
                const img = item.image || '';
                return `<article class="news-card">
                    <img class="news-img" src="${img}" alt="${item.title}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'600\\' height=\\'180\\'><rect fill=\\'%231a0030\\' width=\\'600\\' height=\\'180\\'/><text fill=\\'%23a855f7\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\' dy=\\'.1em\\' font-size=\\'20\\'>GTA VI</text></svg>'">
                    <div class="news-body">
                        <div class="news-source">${item.source || 'WK Games'}</div>
                        <h3 class="news-title">${item.title}</h3>
                        <p class="news-desc">${item.description || ''}</p>
                        <div class="news-date">${item.date || ''}</div>
                        <a class="news-link" href="${item.link}" target="_blank" rel="noopener">Ler mais →</a>
                    </div>
                </article>`;
            }).join('');
        } else {
            newsGrid.innerHTML = '<div class="loading">Aguardando primeira atualização do robô...</div>';
        }

        if (data.videos && data.videos.length) {
            videoGrid.innerHTML = data.videos.map(v => {
                const thumb = v.thumbnail || '';
                return `<a class="video-card" href="${v.link}" target="_blank" rel="noopener">
                    <img class="video-thumb" src="${thumb}" alt="${v.title}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'600\\' height=\\'180\\'><rect fill=\\'%231a0030\\' width=\\'600\\' height=\\'180\\'/><text fill=\\'%23ff007f\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\' dy=\\'.1em\\' font-size=\\'18\\'>WK Video</text></svg>'">
                    <div class="video-body">
                        <div class="video-channel">${v.channel || 'YouTube'}</div>
                        <h3 class="video-title">${v.title}</h3>
                        <div class="news-date">${v.date || ''}</div>
                    </div>
                </a>`;
            }).join('');
        } else {
            videoGrid.innerHTML = '<div class="loading">Buscando vídeos dos canais...</div>';
        }
    } catch {
        newsGrid.innerHTML = '<div class="loading">Ainda sem notícias. O robô está preparando as primeiras atualizações...</div>';
        videoGrid.innerHTML = '<div class="loading">Aguardando vídeos...</div>';
    }
}

loadData();