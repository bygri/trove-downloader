'''
Trove newspaper downloader.

Fetches all data and images for a newspaper title.

Run `python trove.py -h` for usage help.
'''
import argparse
import glob
import json
import os
from PIL import Image
import pprint
import requests
import time
from xml.etree import ElementTree

def ndp_request(ndp_uri: str, use_cache=True):
    '''
    Fetch, save and return JSON.
    '''
    # Strip away the `ndp:browse/` prefix
    assert(ndp_uri.startswith('ndp:browse/'))
    ndp = ndp_uri[11:]
    local_path = os.path.join(output_path, ndp)
    local_file = os.path.join(local_path, 'ndp.json')
    trove_uri = 'http://trove.nla.gov.au/newspaper/browse?uri=ndp:browse/' + ndp
    # Check for local file first
    if use_cache and os.path.exists(os.path.join(local_file)):
        print('NDP: {} (local)'.format(ndp))
        with open(local_file, 'r') as f:
            obj = json.load(f)
    # Get from Trove
    else:
        time.sleep(1)
        print('NDP: {} (remote)'.format(ndp))
        obj = requests.get(trove_uri).json()
        # Store locally
        os.makedirs(local_path, exist_ok=True)
        with open(local_file, 'w') as f:
            json.dump(obj, f, indent=2)
    return obj

def image_request(ndp_uri: str):
    '''
    Given the NDP to a Page, fetch images for it.
    '''
    # Strip away the `ndp:browse/` prefix
    assert(ndp_uri.startswith('ndp:browse/'))
    ndp = ndp_uri[11:]
    page_id = os.path.basename(ndp)
    local_path = os.path.join(output_path, ndp)
    image_filename = os.path.join(local_path, 'page.jpg')
    if os.path.exists(image_filename):
        # No need to continue
        # Delete tiles no longer needed
        for tile in glob.glob(os.path.join(local_path, 'tile*.jpg')):
            os.remove(tile)
        return
    # Get the page info XML
    xml_filename = os.path.join(local_path, 'image.xml')
    if os.path.exists(xml_filename):
        print('Image Info: {} (local)'.format(ndp))
        root = ElementTree.parse(xml_filename)
    else:
        print('Image Info: {} (remote)'.format(ndp))
        info_url = 'http://trove.nla.gov.au/newspaper/image/info/' + page_id
        r = requests.get(info_url)
        root = ElementTree.fromstring(r.content)
        with open(xml_filename, 'wb') as f:
            f.write(r.content)
    # Get base image details
    tilesize = int(root.find('.//tilesize').text)
    # Get the max zoom
    zoom_root = root.find('.//maxlevel')
    zoom_col = int(zoom_root.find('col').text)
    zoom_row = int(zoom_root.find('row').text)
    assert(zoom_col == zoom_row)
    zoom_level = zoom_col
    # Get the parameters for the max zoom level
    level_root = root.find(".//level[@id='{}']".format(zoom_level))
    colmin = int(level_root.find('colmin').text)
    colmax = int(level_root.find('colmax').text)
    rowmin = int(level_root.find('rowmin').text)
    rowmax = int(level_root.find('rowmax').text)
    width = int(level_root.find('width').text)
    height = int(level_root.find('height').text)
    xoffset = int(level_root.find('xoffset').text)
    yoffset = int(level_root.find('yoffset').text)
    # Now fetch, save and compile image parts
    image = Image.new(mode='L', size=(width, height))
    for row in range(rowmin, rowmax):
        for col in range(colmin, colmax):
            tile_name = 'tile{}-{}-{}'.format(zoom_level, col, row)
            tile_filename = os.path.join(local_path, tile_name + '.jpg')
            if not os.path.exists(tile_filename):
                print('Tile: {}/{} (remote)'.format(page_id, tile_name))
                r = requests.get('http://trove.nla.gov.au/ndp/imageservice/nla.news-page{}/{}'.format(
                    page_id, tile_name
                ))
                with open(tile_filename, 'wb') as fp:
                    fp.write(r.content)
            else:
                print('Tile: {}/{} (local)'.format(page_id, tile_name))
            with Image.open(tile_filename) as tile:
                image.paste(tile, box=(
                    col*tilesize - xoffset,
                    row*tilesize - yoffset,
                ))
    image.save(image_filename)
    # Delete tiles no longer needed
    for tile in glob.glob(os.path.join(local_path, 'tile*.jpg')):
        os.remove(tile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download newspaper title from Trove.')
    parser.add_argument('initial', type=str, help='First letter of title')
    parser.add_argument('id', type=int, help='Title ID number (from the Trove newspaper detail page)')
    parser.add_argument('--out', type=str, help='Directory to use for storage')
    args = parser.parse_args()
    title_char = args.initial
    title_id = args.id
    output_path = os.path.expanduser(args.out or 'out')
    # Begin the fetch
    title_data = ndp_request('ndp:browse/title/{0}/title/{1}'.format(title_char, title_id))
    for year_data in [ndp_request(d['ndp:uri']) for d in title_data['skos:narrower']]:
        for issue_data in [ndp_request(d['ndp:uri']) for d in year_data['skos:narrower']]:
            for page_data in [ndp_request(d['ndp:uri']) for d in issue_data['skos:narrower']]:
                # Fetch articles
                [ndp_request(d['ndp:uri']) for d in page_data['skos:narrower']]
                # Fetch images
                image_request(page_data['ndp:uri'])
