# How to update font packs

## FontAwesome

To update _FontAwesome_ icons, one must:

- check what is the latest released version here: https://github.com/FortAwesome/Font-Awesome/releases/
- update font version in \_\_init__.py
- remove outdated files in the fonts dir
- run: `python setup.py update_fa6 --fa-version X.X.X`
- update FA version number, icon counts and URLs inside:
  - README.md
  - qtawesome/docs/source/usage.rst

## Elusive Icons

To update _Elusive Icons_, one must:

- replace the ttf font file with the new version
- regenerate the json charmap with the `icons.yml` file from the upstream repository:
- update Elusive Icons version number, icon counts and URLs inside:
  - README.md
  - qtawesome/docs/source/usage.rst

```Python
import yaml, json

with open('icons.yml', 'r') as file:
    icons = yaml.load(file)['icons']

charmap = {icon['id']: icon['unicode'] for icon in icons}

for icon in icons:
    if 'aliases' in icon:
        for name in icon['aliases']:
            charmap[name] = icon['unicode']

with open('charmap.json', 'w') as file:
    json.dump(charmap, file, indent=4, sort_keys=True)
```

## Material Design Icons

To update _Material Design Icons 6.x_, you must:

- download ttf from <https://raw.githubusercontent.com/Templarian/MaterialDesign-Webfont/master/fonts/materialdesignicons-webfont.ttf>
- regenerate the json charmap with the `materialdesignicons.css` file from <https://raw.githubusercontent.com/Templarian/MaterialDesign-Webfont/master/css/materialdesignicons.css>
- update Material Design Icons version number, icon counts and URLs inside:
  - README.md
  - qtawesome/docs/source/usage.rst

The following script automatically download the last TTF font, generate the json charmap and display md5 hash of the TTF (to update \_\_init__.py)

```Python
import re
import json
import urllib.request
import hashlib


VERSION = '6.9.96'  # Update version as required
TTF_URL = 'https://raw.githubusercontent.com/Templarian/MaterialDesign-Webfont/master/fonts/materialdesignicons-webfont.ttf'
CSS_URL = 'https://raw.githubusercontent.com/Templarian/MaterialDesign-Webfont/master/css/materialdesignicons.css'
FONT_FILENAME = "materialdesignicons6-webfont-{version}.ttf".format(
    version=VERSION
)
FONT_CHARMAP_FILENAME = (
    "materialdesignicons6-webfont-charmap-{version}.json".format(
        version=VERSION
    )
)


with open(FONT_FILENAME, 'wb') as fp:
    req = urllib.request.urlopen(TTF_URL)
    if req.status != 200:
        raise Exception('Failed to download TTF')
    fp.write(req.read())
    req.close()

hasher = hashlib.md5()
with open(FONT_FILENAME, 'rb') as f:
    content = f.read()
    hasher.update(content)

ttf_calculated_hash_code = hasher.hexdigest()
print('MD5 :', ttf_calculated_hash_code)

req = urllib.request.urlopen(CSS_URL)
if req.status != 200:
    raise Exception('Failed to download CSS Charmap')

rawcss = req.read().decode()
req.close()

charmap = {}
pattern = '^\.mdi-(.+)::before {\s*content: "(.+)";\s*}$'
data = re.findall(pattern, rawcss, re.MULTILINE)
for name, key in data:
    key = key.replace('\\F', '0xf').lower()
    key = key.replace('\\', '0x')
    name = name.lower()
    charmap[name] = key

with open(FONT_CHARMAP_FILENAME, 'w') as fp:
    json.dump(charmap, fp, indent=4, sort_keys=True)

```

## Phosphor

To update _Phosphor_, you must:

- download ttf from <https://raw.githubusercontent.com/phosphor-icons/phosphor-icons/master/src/font/phosphor.ttf>
- regenerate the json charmap with the `phosphor.css` file from <https://raw.githubusercontent.com/phosphor-icons/phosphor-icons/master/src/css/phosphor.css>
- update Phosphor version number, icon counts and URLs inside:
  - README.md
  - qtawesome/docs/source/usage.rst

The following script automatically download the last TTF font, generate the json charmap and display md5 hash of the TTF (to update \_\_init__.py)

```Python
import re
import json
import urllib.request
import hashlib

VERSION = '1.3.0'  # Update version as required
TTF_URL = 'https://raw.githubusercontent.com/phosphor-icons/phosphor-icons/master/src/font/phosphor.ttf'
CSS_URL = 'https://raw.githubusercontent.com/phosphor-icons/phosphor-icons/master/src/css/phosphor.css'
FONT_FILENAME = 'phosphor-{version}.ttf'.format(version=VERSION)
FONT_CHARMAP_FILENAME = "phosphor-charmap-{version}.json".format(
    version=VERSION
)

with open(FONT_FILENAME, 'wb') as fp:
    req = urllib.request.urlopen(TTF_URL)
    if req.status != 200:
        raise Exception('Failed to download TTF')
    fp.write(req.read())
    req.close()

hasher = hashlib.md5()
with open(FONT_FILENAME, 'rb') as f:
    content = f.read()
    hasher.update(content)

ttf_calculated_hash_code = hasher.hexdigest()
print('MD5 :', ttf_calculated_hash_code)

req = urllib.request.urlopen(CSS_URL)
if req.status != 200:
    raise Exception('Failed to download CSS Charmap')

rawcss = req.read().decode()
req.close()

charmap = {}
pattern = '^\.ph-(.+):before {\s*content: "(.+)";\s*}$'
data = re.findall(pattern, rawcss, re.MULTILINE)
for name, key in data:
    key = key.replace('\\', '0x')
    name = name.lower()
    charmap[name] = key

with open(FONT_CHARMAP_FILENAME, 'w') as fp:
    json.dump(charmap, fp, indent=4, sort_keys=True)

```

## Remix Icon

To update _Remix Icon_, you must:

- download ttf from <https://raw.githubusercontent.com/Remix-Design/RemixIcon/master/fonts/remixicon.ttf>
- regenerate the json charmap with the `remixicon.css` file from <https://raw.githubusercontent.com/Remix-Design/RemixIcon/master/fonts/remixicon.css>
- update Remix Icon version number, icon counts and URLs inside:
  - README.md
  - qtawesome/docs/source/usage.rst

The following script automatically download the last TTF font, generate the json charmap and display md5 hash of the TTF (to update \_\_init__.py)

```Python
import re
import json
import urllib.request
import hashlib

VERSION = '2.5.0'  # Update version as required
TTF_URL = 'https://raw.githubusercontent.com/Remix-Design/RemixIcon/master/fonts/remixicon.ttf'
CSS_URL = 'https://raw.githubusercontent.com/Remix-Design/RemixIcon/master/fonts/remixicon.css'
FONT_FILENAME = 'remixicon-{version}.ttf'.format(version=VERSION)
FONT_CHARMAP_FILENAME = "remixicon-charmap-{version}.json".format(
    version=VERSION
)

with open(FONT_FILENAME, 'wb') as fp:
    req = urllib.request.urlopen(TTF_URL)
    if req.status != 200:
        raise Exception('Failed to download TTF')
    fp.write(req.read())
    req.close()

hasher = hashlib.md5()
with open(FONT_FILENAME, 'rb') as f:
    content = f.read()
    hasher.update(content)

ttf_calculated_hash_code = hasher.hexdigest()
print('MD5 :', ttf_calculated_hash_code)

req = urllib.request.urlopen(CSS_URL)
if req.status != 200:
    raise Exception('Failed to download CSS Charmap')

rawcss = req.read().decode()
req.close()

charmap = {}
pattern = '^\.ri-(.+):before {\s*content: "(.+)";\s*}$'
data = re.findall(pattern, rawcss, re.MULTILINE)
for name, key in data:
    key = key.replace('\\', '0x')
    name = name.lower()
    charmap[name] = key

with open(FONT_CHARMAP_FILENAME, 'w') as fp:
    json.dump(charmap, fp, indent=4, sort_keys=True)

```

## Microsoft's Codicons

To update _Codicons_ icons, one must:

- check what is the latest released version here: https://github.com/microsoft/vscode-codicons/releases
- update font version in \_\_init__.py
- remove outdated files in the fonts dir
- run: `python setup.py update_msc --msc-version X.X.X`
- update Codicons version number, icon counts and URLs inside:
  - README.md
  - qtawesome/docs/source/usage.rst
