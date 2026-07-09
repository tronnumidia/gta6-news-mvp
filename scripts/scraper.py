import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from xml.etree import ElementTree

try:
    import requests
except ImportError:
    os.system(f'{sys.executable} -m pip install requests')
    import requests

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'news.json')
MAX_NEWS = 30
MAX_VIDEOS_PER_CHANNEL = 6

YOUTUBE_API_KEY = os.environ.get('YT_API_KEY', 'AIzaSyBU7SK3OcfBkYuPtPiK9_XZ8xo5wXb_jSs')
YOUTUBE_CHANNELS = {
    'UCJAbkIY17zAmCTNQHH0bQoQ': 'GamplayRJ',
    'UCUZfhX79dQrJvAgYefiXCCA': 'FLOW GAMES',
    'UC5YhmSFDiIFSgCq2rRVTzbA': 'DebYte',
}

RSS_FEEDS = [
    'https://news.google.com/rss/search?q=GTA+6+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://news.google.com/rss/search?q=Grand+Theft+Auto+VI+lan%C3%A7amento&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://news.google.com/rss/search?q=GTA+VI+not%C3%ADcias&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://br.ign.com/feeds/rss/gta-6',
    'https://meups.com.br/feed/',
    'https://www.tecmundo.com.br/feed/',
    'https://www.adrenaline.com.br/feed/',
]

GTA_KEYWORDS = [
    'gta 6', 'gta vi', 'gta6', 'grand theft auto vi', 'grand theft auto 6',
    'rockstar games', 'vice city', 'leonida', 'gta online',
    'gta 6 lançamento', 'gta 6 trailer', 'gta 6 gameplay',
]

def generate_thumbnail(source, title):
    text = urllib.parse.quote(title[:40])
    colors = [
        ('1a0030', 'ff007f', 'GTA+VI'),
        ('0a0015', '00f0ff', 'GTA+6'),
        ('1a0030', 'a855f7', 'GTA'),
        ('0a0015', 'facc15', 'GTA+VI'),
        ('1a0030', 'ff6b00', 'GTA+6'),
    ]
    import hashlib
    idx = hashlib.md5(title.encode()).digest()[0] % len(colors)
    bg, fg, label = colors[idx]
    return f'https://placehold.co/600x340/{bg}/{fg}?text={label}'

def parse_date(date_str):
    meses_en = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
    }
    if not date_str:
        return ''
    match = re.search(r'(\d{2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', date_str, re.I)
    if match:
        d, m, y = match.group(1), meses_en.get(match.group(2).title(), '01'), match.group(3)
        return f'{y}-{m}-{d}'
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if match:
        return f'{match.group(1)}-{match.group(2)}-{match.group(3)}'
    match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_str)
    if match:
        return f'{match.group(3)}-{match.group(2)}-{match.group(1)}'
    return date_str[:10]

def is_gta_related(text):
    text_lower = text.lower()
    for kw in GTA_KEYWORDS:
        if kw in text_lower:
            return True
    return False

def fetch_rss(url):
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.content)
        items = []
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}
        entries = root.findall('.//item') or root.findall('.//entry', ns)
        for entry in entries:
            title = entry.findtext('title', '')
            if not title and entry.find('atom:title', ns) is not None:
                title = entry.find('atom:title', ns).text or ''
            link_el = entry.find('link')
            link = ''
            if link_el is not None:
                link = link_el.get('href', '') or link_el.text or ''
            desc = entry.findtext('description', '') or entry.findtext('summary', '') or ''
            desc = re.sub(r'<[^>]+>', '', desc)[:300]
            pub_date = entry.findtext('pubDate', '') or entry.findtext('published', '') or ''
            pub_date = parse_date(pub_date)
            source_tag = entry.findtext('source', '') or ''
            source_name = source_tag or urllib.parse.urlparse(url).netloc.replace('www.', '').split('.')[0].upper()
            if 'google' in source_name.lower():
                source_name = 'GTA 6 BR'
            source_name = {
                'br': 'IGN BR',
                'meups': 'MeuPS',
                'tecmundo': 'TecMundo',
                'adrenaline': 'Adrenaline',
            }.get(source_name.lower(), source_name)

            text_content = f'{title} {desc}'
            if not is_gta_related(text_content):
                continue

            media = ''
            media_el = entry.find('enclosure')
            if media_el is not None:
                media = media_el.get('url', '')
            media_content = entry.find('media:content', ns)
            if media_content is not None:
                media = media_content.get('url', '')
            media_group = entry.find('media:group', ns)
            if media_group is not None:
                mc = media_group.find('media:content', ns)
                if mc is not None:
                    media = mc.get('url', '')
            media_thumbnail = entry.find('media:thumbnail', ns)
            if media_thumbnail is not None:
                media = media_thumbnail.get('url', '')

            if not media:
                media = generate_thumbnail(source_name, title)

            if title and link:
                items.append({
                    'title': title.strip()[:120],
                    'link': link,
                    'description': desc.strip()[:200],
                    'date': pub_date,
                    'source': source_name,
                    'image': media,
                })
        return items
    except Exception as e:
        print(f'RSS error {url}: {e}')
        return []

def fetch_channel_videos(channel_id, channel_name):
    if not YOUTUBE_API_KEY:
        return []
    try:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'maxResults': MAX_VIDEOS_PER_CHANNEL,
            'order': 'date',
            'type': 'video',
            'key': YOUTUBE_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        videos = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            vid = item.get('id', {}).get('videoId', '')
            if not vid:
                continue
            thumb = (snippet.get('thumbnails', {}).get('high', {}) or {}).get('url', '') or \
                    (snippet.get('thumbnails', {}).get('medium', {}) or {}).get('url', '') or \
                    (snippet.get('thumbnails', {}).get('default', {}) or {}).get('url', '')
            videos.append({
                'title': snippet.get('title', '')[:120],
                'link': f'https://youtube.com/watch?v={vid}',
                'thumbnail': thumb,
                'channel': channel_name,
                'date': (snippet.get('publishedAt', '') or '')[:10],
            })
        print(f'  {channel_name}: {len(videos)} vídeos')
        return videos
    except Exception as e:
        print(f'YouTube error ({channel_name}): {e}')
        return []

def deduplicate(items, key='link'):
    seen = set()
    unique = []
    for item in items:
        k = item.get(key, '')
        if k not in seen:
            seen.add(k)
            unique.append(item)
    return unique

def main():
    print('Buscando notícias em Português (BR)...')
    all_news = []
    for feed in RSS_FEEDS:
        items = fetch_rss(feed)
        all_news.extend(items)
        print(f'  {feed}: {len(items)} itens')

    all_news = deduplicate(all_news)
    all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
    all_news = all_news[:MAX_NEWS]

    print('\nBuscando vídeos dos canais...')
    all_videos = []
    for channel_id, channel_name in YOUTUBE_CHANNELS.items():
        videos = fetch_channel_videos(channel_id, channel_name)
        all_videos.extend(videos)

    all_videos = deduplicate(all_videos)
    all_videos = all_videos[:MAX_VIDEOS_PER_CHANNEL * len(YOUTUBE_CHANNELS)]

    output = {
        'news': all_news,
        'videos': all_videos,
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f'\n Total notícias (PT-BR): {len(all_news)}')
    print(f' Total vídeos: {len(all_videos)}')
    print(f' Arquivo salvo: {DATA_FILE}')

if __name__ == '__main__':
    main()