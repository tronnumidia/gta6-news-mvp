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
MAX_NEWS = 45
MAX_VIDEOS_PER_CHANNEL = 8

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
    'https://news.google.com/rss/search?q=PlayStation+5+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://news.google.com/rss/search?q=Xbox+Series+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://news.google.com/rss/search?q=PlayStation+Brasil+games&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://news.google.com/rss/search?q=Xbox+Brasil+games&hl=pt-BR&gl=BR&ceid=BR:pt-BR',
    'https://br.ign.com/feeds/rss/gta-6',
    'https://br.ign.com/feeds/rss/ps5',
    'https://br.ign.com/feeds/rss/xbox',
    'https://meups.com.br/feed/',
    'https://www.tecmundo.com.br/feed/',
    'https://www.adrenaline.com.br/feed/',
]

KEYWORDS_GTA = [
    'gta 6', 'gta vi', 'gta6', 'grand theft auto vi', 'grand theft auto 6',
    'rockstar games', 'vice city', 'leonida', 'gta online',
    'gta 6 lançamento', 'gta 6 trailer', 'gta 6 gameplay',
]

KEYWORDS_PS = [
    'playstation', 'ps5', 'playstation 5', 'ps4', 'playstation 4',
    'sony', 'playstation plus', 'ps plus', 'playstation store',
    'playstation vr', 'ps vr', 'dualsense', 'playstation network',
]

KEYWORDS_XBOX = [
    'xbox', 'xbox series', 'xbox series x', 'xbox series s', 'xbox one',
    'microsoft', 'xbox game pass', 'game pass', 'xbox live',
    'xcloud', 'xbox cloud', 'bethesda', 'activision',
    'xbox wire', 'xbox series',
]

WIKI_GTA_IMAGES = None

def get_wiki_images():
    global WIKI_GTA_IMAGES
    if WIKI_GTA_IMAGES is not None:
        return WIKI_GTA_IMAGES
    try:
        url = 'https://en.wikipedia.org/w/api.php?action=query&titles=Grand_Theft_Auto_VI&prop=images&format=json&imlimit=20'
        resp = requests.get(url, timeout=10)
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        images = []
        for pid, page in pages.items():
            for img in page.get('images', []):
                title = img.get('title', '')
                if any(x in title.lower() for x in ['.jpg', '.png', '.webp']):
                    img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
                    img_resp = requests.get(img_url, timeout=10)
                    img_data = img_resp.json()
                    for pid2, page2 in img_data.get('query', {}).get('pages', {}).items():
                        info = page2.get('imageinfo', [])
                        if info and info[0].get('url'):
                            images.append(info[0]['url'])
        WIKI_GTA_IMAGES = images[:10]
        if WIKI_GTA_IMAGES:
            print(f'  Wikipedia: {len(WIKI_GTA_IMAGES)} imagens do GTA VI')
    except:
        WIKI_GTA_IMAGES = []
    if not WIKI_GTA_IMAGES:
        WIKI_GTA_IMAGES = [
            'https://upload.wikimedia.org/wikipedia/en/4/4c/GTA_VI_cover.jpg',
            'https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/GTA_VI_cover.jpg/640px-GTA_VI_cover.jpg',
        ]
    return WIKI_GTA_IMAGES

img_fallback_index = 0

def next_fallback():
    global img_fallback_index
    images = get_wiki_images()
    url = images[img_fallback_index % len(images)]
    img_fallback_index += 1
    return url

def extract_img_from_html(html):
    if not html:
        return ''
    match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']', html, re.I)
    if match:
        return match.group(1)
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I)
    if match:
        src = match.group(1)
        if src.startswith('//'):
            src = 'https:' + src
        if src.startswith('http') and 'placehold.co' not in src:
            return src
    match = re.search(r'srcset=["\']([^"\']+)["\']', html, re.I)
    if match:
        parts = match.group(1).split(',')
        for part in parts:
            urls = re.findall(r'(https?://[^\s]+)', part)
            if urls:
                return urls[0]
    return ''

def fetch_og_image(url):
    try:
        api = f'https://api.microlink.io/?url={urllib.parse.quote(url)}&video=false&audio=false&screenshot=false'
        resp = requests.get(api, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        data = resp.json()
        if data.get('status') == 'success':
            img = data.get('data', {}).get('image', {})
            if img and img.get('url'):
                return img['url']
    except:
        pass
    try:
        resp = requests.get(url, timeout=6, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        resp.raise_for_status()
        text = resp.text
        for pattern in [
            r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
            r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']',
            r'<meta\s+name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']',
            r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']twitter:image["\']',
        ]:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1)
    except:
        pass
    return ''

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

def is_relevant(text):
    text_lower = text.lower()
    for kw in KEYWORDS_GTA + KEYWORDS_PS + KEYWORDS_XBOX:
        if kw in text_lower:
            return True
    return False

def get_category(text):
    text_lower = text.lower()
    for kw in KEYWORDS_GTA:
        if kw in text_lower:
            return 'GTA 6'
    for kw in KEYWORDS_PS:
        if kw in text_lower:
            return 'PlayStation'
    for kw in KEYWORDS_XBOX:
        if kw in text_lower:
            return 'Xbox'
    return 'Games'

def clean_source_name(url, source_tag):
    name = source_tag or urllib.parse.urlparse(url).netloc.replace('www.', '').split('.')[0].upper()
    if 'google' in name.lower() or 'news' in name.lower():
        return 'Games BR'
    mapping = {
        'br': 'IGN BR', 'meups': 'MeuPS', 'tecmundo': 'TecMundo',
        'adrenaline': 'Adrenaline', 'hardware': 'Hardware BR',
        'tudocelular': 'TudoCelular', 'canaltech': 'Canaltech',
        'olhardigital': 'Olhar Digital', 'd24horas': 'Diário 24h',
        'ultimaficha': 'Última Ficha', 'jornadageek': 'Jornada Geek',
        'transmissao': 'Trans. Política', 'notebookcheck': 'Notebook Check',
        'jornalcorreio': 'Jornal Correio', 'dol': 'DOL',
        'portal': 'Portal BR', 'fastcompany': 'Fast Company',
        'ncnews': 'NC News', 'investing': 'Investing BR',
    }
    for key, val in mapping.items():
        if key in name.lower():
            return val
    return name

def fetch_rss(url):
    try:
        resp = requests.get(url, timeout=20, headers={
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
            raw_desc = entry.findtext('description', '') or entry.findtext('summary', '') or ''
            desc = re.sub(r'<[^>]+>', '', raw_desc)[:300]
            pub_date = entry.findtext('pubDate', '') or entry.findtext('published', '') or ''
            pub_date = parse_date(pub_date)
            source_tag = entry.findtext('source', '') or ''
            source_name = clean_source_name(url, source_tag)

            text_content = f'{title} {desc}'
            if not is_relevant(text_content):
                continue

            category = get_category(text_content)
            source_display = f'{source_name} • {category}'

            media = ''
            media_el = entry.find('enclosure')
            if media_el is not None:
                media = media_el.get('url', '')
            if not media:
                mc = entry.find('media:content', ns)
                if mc is not None:
                    media = mc.get('url', '')
            if not media:
                mg = entry.find('media:group', ns)
                if mg is not None:
                    mc = mg.find('media:content', ns)
                    if mc is not None:
                        media = mc.get('url', '')
            if not media:
                mt = entry.find('media:thumbnail', ns)
                if mt is not None:
                    media = mt.get('url', '')

            if not media:
                media = extract_img_from_html(raw_desc)

            if not media and link and link != '#':
                print(f'  Buscando imagem: {title[:40]}...')
                media = fetch_og_image(link)
                if media:
                    print(f'    OK')
                else:
                    print(f'    Sem imagem OG')

            if not media:
                media = next_fallback()

            if title and link:
                items.append({
                    'title': title.strip()[:120],
                    'link': link,
                    'description': desc.strip()[:200],
                    'date': pub_date,
                    'source': source_display,
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
    print('Buscando imagens do Wikipedia (GTA VI)...')
    get_wiki_images()

    print('\nBuscando notícias em Português (GTA 6 + PS5 + Xbox)...')
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

    print(f'\n Total notícias (GTA 6 + PS + Xbox): {len(all_news)}')
    print(f' Total vídeos: {len(all_videos)}')
    print(f' Arquivo salvo: {DATA_FILE}')

if __name__ == '__main__':
    main()