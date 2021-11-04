# loc-image-retriever

Library of Congress (LoC) image retrieval script.

The `retriever.py` script retrieves a single volume of map images from the
[Library of Congress](https://www.loc.gov/). The script relies on `retriever_config.yml` to provide
configuration values that "point" the script to the target image collection. The script is run from
the terminal and accepts a number of command line arguments:

1. Required: A `< key >` (`str`) value that matches a map key in the companion
   `< retriever_config.yml >` file. The `< 'key' >` arg is used to filter the relevant map data
   contained in the loaded YAML file.

2. Optional: A `< format >` (`str`) value that sets the image extension. Options: 'jpg', 'gif',
   'jp2', 'tif'. Default: 'jpg'.

3. Optional: A `< size >` (`int`) value that sets the width and height of the image scaled to `n`
   percent of the width and height of the extracted region ('pct:n'). The aspect ratio of the
   returned image is the same as that of the extracted region. Default value = `25`.

4. Optional: A `< rotation >` (`int`) value that sets the image rotation by degrees (`0-360`).
   Default value = `0`.

5. Optional: A `< quality >` (`str`) value that sets the image quality. Options: 'color', 'grey',
   'bitonal', 'default'. Default value = `'default'`.

6. Optional: A `< output >` (`str`) value corresponding to the filepath for local storage of the
   retrieved images. Default value = `'./output'`.

Once configured, the script retrieves the target images, renames the downloaded files,
stores them locally in the `< output >` location, and logs the process both via the terminal and
a log file.

## LoC URL template

`{scheme}://{server}{/id_prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}`

## LoC URL examples

`.jpg` (pct:25)

https://tile.loc.gov/image-services/iiif/service:gmd:gmd411m:g4114m:g4114cm:g039611918:03961_1918-0001/full/pct:25/0/default.jpg

`.gif`

https://tile.loc.gov/storage-services/service/gmd/gmd411m/g4114m/g4114cm/g039611918/03961_1918-0001.gif

`.jp2`

https://tile.loc.gov/storage-services/service/gmd/gmd411m/g4114m/g4114cm/g039611918/03961_1918-0001.jp2

`.tif` (master)

https://tile.loc.gov/storage-services/master/gmd/gmd411m/g4114m/g4114cm/g039611918/03961_1918-0001.tif

## LoC image retrieval API

For addtional information review the LoC's  IIIF image retrieval
[API](https://iiif.io/api/image/2.1/).

An example LoC Jupyter
[notebook](https://github.com/LibraryOfCongress/data-exploration/blob/master/IIIF.ipynb) is
available that illustrates image retrieval techniques.
