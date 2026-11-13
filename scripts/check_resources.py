"""Verifica os links editoriais sem alterar a lista de conteúdos fornecida."""
import concurrent.futures
import argparse
from datetime import date
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parent.parent

def playlist_status(body, url):
    match = re.search(r'ytInitialData\s*=\s*', body)
    if not match:
        return {'status': 'unverified', 'url': url}
    data, _ = json.JSONDecoder().raw_decode(body[match.end():])
    alerts = json.dumps(data.get('alerts', []), ensure_ascii=False).lower()
    if any(term in alerts for term in ['does not exist', 'não existe', 'private', 'privada', 'unavailable', 'indisponível']):
        return {'status': 'unavailable', 'url': url}
    metadata = data.get('metadata', {}).get('playlistMetadataRenderer', {})
    # O YouTube também usa lockupViewModel; playlistVideoRenderer sozinho
    # não identifica as playlists no formato atual da página pública.
    def video_ids(node):
        if isinstance(node, dict):
            endpoint = node.get('watchEndpoint', {})
            if endpoint.get('videoId'):
                yield endpoint['videoId']
            for value in node.values():
                yield from video_ids(value)
        elif isinstance(node, list):
            for value in node:
                yield from video_ids(value)
    videos = set(video_ids(data.get('contents', {})))
    if metadata.get('title') and videos:
        return {'status':'available', 'url':url, 'title':metadata['title'],
                'publisher':'Playlist indicada pelo grupo · disponibilidade confirmada', 'visible_videos':len(videos)}
    return {'status':'unverified', 'url':url, 'title':metadata.get('title', '')}

def check_video(topic):
    url = topic['video_url']
    if not url:
        return topic['slug'], {'status': 'not_provided'}
    if 'playlist?' in url:
        # oEmbed do YouTube não suporta playlists; examinar a página pública.
        target = url
    else:
        target = 'https://www.youtube.com/oembed?format=json&url=' + quote(url, safe='')
    try:
        with urlopen(Request(target, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15) as response:
            body = response.read().decode('utf-8', 'replace')
        if 'playlist?' in url:
            return topic['slug'], playlist_status(body, url)
        metadata = json.loads(body)
        return topic['slug'], {'status': 'available', 'url': url, 'title': metadata.get('title'), 'publisher': metadata.get('author_name')}
    except HTTPError as error:
        return topic['slug'], {'status': 'unavailable' if error.code in (400, 404, 410) else 'unverified', 'url': url, 'http': error.code}
    except Exception as error:
        return topic['slug'], {'status': 'unverified', 'url': url, 'error': type(error).__name__}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checked-on', required=True, type=date.fromisoformat, help='Data da verificação no fuso do projeto (AAAA-MM-DD).')
    checked_on = parser.parse_args().checked_on.isoformat()
    catalog = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
    topics = [t for subject in catalog for t in subject['topics']]
    previous_file = ROOT / 'data/resource_checks.json'
    result = json.loads(previous_file.read_text(encoding='utf-8')) if previous_file.exists() else {}
    pending = [t for t in topics if result.get(t['slug'], {}).get('status') not in {'available', 'not_provided'}]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for slug, check in pool.map(check_video, pending):
            check['checked_on'] = checked_on
            result[slug] = check
    (ROOT / 'data/resource_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    from collections import Counter
    print(dict(Counter(v['status'] for v in result.values())))

if __name__ == '__main__':
    main()
