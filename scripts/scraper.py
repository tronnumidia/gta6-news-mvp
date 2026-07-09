import json
import os
import re
import sys
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
    'https://www.ign.com/feeds/rss/ign-gta6-news',
    'https://www.gamespot.com/feeds/rss/gta-6-news',
    'https://gta6news.com/rss',
    'https://www.eurogamer.net/feed/gta-6',
    'https://www.pcgamer.com/rss/gta-6/',
    'https://feeds.feedburner.com/gta6news',
    'https://www.gtaboom.com/feed/',
    'https://gtaforums.com/rss/',
    'https://www.gtabase.com/feed/',
]

def fetch_rss(url):
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.content)
        items = []
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
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
            media = ''
            media_el = entry.find('enclosure')
            if media_el is not None:
                media = media_el.get('url', '')
            media_content = entry.find('{http://search.yahoo.com/mrss/}content')
            if media_content is not None:
                media = media_content.get('url', '')
            if title and link:
                if not re.search(r'(gta|grand theft auto|rockstar|gta 6|gta vi|gta6)', title + desc, re.I):
                    if not any(kw in (title + link).lower() for kw in ['gta', 'grand theft', 'rockstar']):
                        continue
                items.append({
                    'title': title.strip(),
                    'link': link,
                    'description': desc.strip(),
                    'date': pub_date.strip(),
                    'source': url.split('/')[2] if '//' in url else 'Games',
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
            videos.append({
                'title': snippet.get('title', ''),
                'link': f'https://youtube.com/watch?v={vid}',
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', '') or
                             snippet.get('thumbnails', {}).get('medium', {}).get('url', '') or
                             snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                'channel': channel_name,
                'date': snippet.get('publishedAt', '')[:10],
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
    print('Buscando notícias RSS...')
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

    print(f'\n Total notícias: {len(all_news)}')
    print(f' Total vídeos: {len(all_videos)}')
    print(f' Arquivo salvo: {DATA_FILE}')

if __name__ == '__main__':
    main()