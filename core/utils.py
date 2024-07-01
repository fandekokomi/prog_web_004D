import requests
import aiohttp
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.cache import cache

def get_lastfm_data(method, params):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params['api_key'] = settings.LASTFM_API_KEY
    params['format'] = 'json'
    params['method'] = method

    # Construir la clave para la caché
    cache_key = f"lastfm_data_{method}_{'_'.join(f'{key}={value}' for key, value in params.items())}"
    
    # Intentar obtener datos de la caché
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # Si no está en caché, hacer la solicitud a la API
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Guardar los datos en caché para 24 horas
    cache.set(cache_key, data, timeout=86400)  # 24 horas
    return data

def get_japanese_artists():
    method = 'tag.getTopArtists'
    params = {'tag': 'Japanese'}
    data = get_lastfm_data(method, params)
    
    if 'topartists' not in data or 'artist' not in data['topartists']:
        print("Unexpected API response:", data)
        return None
    
    artists = data['topartists']['artist']
    lastfm_api = []
    
    for artist in artists:
        artist_id = artist.get('mbid') or artist.get('url')  # Usar mbid si está presente, de lo contrario usar url
        nombre_artista = artist['name']
        url_artista = artist.get('url')  # Obtener la URL del artista
        
        lastfm_api.append({
            'id': artist_id,
            'nombre': nombre_artista,
            'url': url_artista
        })
    
    return lastfm_api