import argparse
# import arwutils.utils as util
import datetime as dt
import logging
import requests
import sys
import yaml

from pathlib import Path


DESCRIPTION = """
Library of Congress (LoC) image retrieval script.

The retriever.py script retrieves a single volume of map images from the
[Library of Congress](https://www.loc.gov/). The script relies on retriever_config.yml to provide
configuration values that "point" the script to the target image collection. The script is run from
the terminal and accepts a number of command line arguments:

1. Required: A < key > (str) value that matches a map key in the companion
   < retriever_config.yml > file. The < 'key' > arg is used to filter the relevant map data
   contained in the loaded YAML file.

2. Optional: A < format > (str) value that sets the image extension. Options: 'jpg', 'gif',
   'jp2', 'tif'. Default: 'jpg'.

3. Optional: A < size > (int) value that sets the width and height of the image scaled to n
   percent of the width and height of the extracted region ('pct:n'). The aspect ratio of the
   returned image is the same as that of the extracted region. Default value = 25.

4. Optional: A < rotation > (int) value that sets the image rotation by degrees (0-360).
   Default value = 0.

5. Optional: A < quality > (str) value that sets the image quality. Options: 'color', 'grey',
   'bitonal', 'default'. Default value = 'default'.

6. Optional: A < output > (str) value corresponding to the filepath for local storage of the
   retrieved images. Default value = './output'.

Once configured, the script retrieves the target images, renames the downloaded files,
stores them locally in the < output > location, and logs the process both via the terminal and
a log file.

LoC URL template

{scheme}://{server}{/id_prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}

LoC URL examples

.jpg (pct:25)

https://tile.loc.gov/image-services/iiif/service:gmd:gmd411m:g4114m:g4114cm:g039611918:03961_1918-0001/full/pct:25/0/default.jpg

.gif

https://tile.loc.gov/storage-services/service/gmd/gmd411m/g4114m/g4114cm/g039611918/03961_1918-0001.gif

.jp2

https://tile.loc.gov/storage-services/service/gmd/gmd411m/g4114m/g4114cm/g039611918/03961_1918-0001.jp2

.tif (master)

https://tile.loc.gov/storage-services/master/gmd/gmd411m/g4114m/g4114cm/g039611918/03961_1918-0001.tif

LoC image retrieval API

For addtional information review the LoC's  IIIF image retrieval
[API](https://iiif.io/api/image/2.1/).

An example LoC Jupyter
[notebook](https://github.com/LibraryOfCongress/data-exploration/blob/master/IIIF.ipynb) is
available that illustrates image retrieval techniques.
"""


def configure_logger(output_path, filename_segments, start_date_time):
    """Returns a logger object with stream and file handlers.

    Parameters:
        output_path (str): relative directory path were file is to be located
        filename_segments (list): filename segments
        start_date_time (datetime): start datetime.

    Returns:
        Path: path object (absolute path)
    """

    # Set logging format and default level
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)

    # Create filename and path
    filename = create_filename(filename_segments, format='log')
    filepath = create_filepath(output_path, filename)

    # Add file and stream handlers
    logger.addHandler(logging.FileHandler(filepath))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger


def create_filename(name_segments, part=None, num=None, format='jpg'):
    """Returns a Path object comprising a filename built up from a list
    of name segments.

    Parameters:
        name_segments (list): file name segments
        part (str): optional LOC image designator (e.g., index)
        num (str): image number (typically zfilled)
        format (str): file extension; defaults to 'jpg'

    Returns:
        Path: path object
    """

    segments = name_segments['name'].copy() # shallow copy

    # Add additional segments
    if name_segments['year']:
        segments.append(str(name_segments['year']))
    if name_segments['vol']:
       segments.append(f"vol_{name_segments['vol']}")

    if format == 'log':
        return Path('-'.join(segments)).with_suffix(f".{format}")

    # Continue adding segments for non-log files
    if name_segments['vol']:
        segments.append(f"vol_{name_segments['vol']}")
    if part:
        segments.append(part)
    if num:
        if len(num) < 4: # pad
            num = num.zfill(4)
        segments.append(num)

    return Path('-'.join(segments)).with_suffix(f".{format}")


def create_filepath(output_path, filename):
    """Return local filepath for image and log files.

    Parameters:
        output_path (str): relative directory path were file is to be located
        filename (str): name of file including extension

    Returns:
        Path: path object (absolute path)
    """

    return Path(Path.cwd(), output_path, filename)


def create_parser(description):
    """Return a custom argument parser.

    Parameters:
       description (str): Script description

    Returns:
        parser (ArgumentParser): parser object
    """

    parser = argparse.ArgumentParser(description)

    parser.add_argument(
        '-k',
        '--key',
        type=str,
        required=True,
        help="Required YAML map key"
        )
    parser.add_argument(
        '-f',
        '--format',
        type=str,
        required=False,
        default='jpg',
        help="Image format"
        )
    parser.add_argument(
        '-r',
        '--region',
        type=str,
        required=False,
        default='full',
        help="Optional region"
        )
    parser.add_argument(
        '-s',
        '--size',
        type=int,
        required=False,
        default=25,
        help="Optional image size (n %)"
        )
    parser.add_argument(
        '-d',
        '--rotation_degrees',
        type=int,
        required=False,
        default=0,
        help="Optional image rotation (degrees)"
        )
    parser.add_argument(
        '-q',
        '--quality',
        type=str,
        required=False,
        default='default',
        help="Optional image quality"
        )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=False,
        default='./output',
        help="Output directory"
	)

    return parser


def create_url(parser, config, gmd, id_prefix, num):
    """ Build Library of Congress image resource URL.

    format: {scheme}://{server}{/id_prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}

    Parameters:
        parser (Parser): parser object containing CLI specified and default args
        config (dict): configuration options sourced from YAML file
        gmd (str): general material description(s)
        id_prefix (str): image index id_prefix
        num (str): zfilled image index

    Returns:
        url (str): LOC url
     """

    if parser.format in ('gif', 'jp2', 'tif'):
        return ''.join([
            f"{config['protocol']}",
            f"://{config['subdomain']}",
            f".{config['domain']}",
            f"/{config['service_path'][parser.format]}",
            f"/{gmd.replace(':', '/')}",
            f"/{id_prefix}{num}",
            f".{parser.format}"
            ])
    else:
        return ''.join([
            f"{config['protocol']}",
            f"://{config['subdomain']}",
            f".{config['domain']}",
            f"/{config['service_path'][parser.format]}",
            f":{gmd}",
            f":{id_prefix}{num}",
            f"/{parser.region}",
            f"/pct:{str(parser.size)}",
            f"/{str(parser.rotation_degrees)}",
            f"/{parser.quality}",
            f".{parser.format}"
            ])


def read_yaml_file(filepath):
    """Read a YAML (Yet Another Markup Language) file given a valid filepath.

    Parameters:
        filepath (str): absolute or relative path to target file

    Returns:
        obj: typically a list or dictionary representation of the file object
    """

    with open(filepath, 'r') as file_object:
        data = yaml.load(file_object, Loader=yaml.FullLoader)

        return data


def write_file(filepath, data, mode='w', chunk_size=1024):
    """Writes content to a target file. Override the optional write mode value
    if binary content <class 'bytes'> is to be written to file (i.e., mode='wb')
    or an append operation is intended on an existing file (i.e., mode='a' or 'ab').

    Parameters:
        filepath (str): absolute or relative path to target file
        data (obj): data to be written to the target file
        mode (str): write operation mode
        chunk_size (int); size of data chunks to stream

    Returns:
       None
    """

    with open(filepath, mode) as file_object:
        for chunk in data.iter_content(chunk_size=chunk_size):
            file_object.write(chunk)


def main(args):
    """Entry point. Orchestrates the workflow.

    Parameters:
        args (list): command line arguments

    Returns:
        None
    """

    # Parse CLI args
    parser = create_parser(DESCRIPTION).parse_args(args)
    output_path = parser.output

    # load YAML config
    filepath = 'retriever_config.yml'
    config = read_yaml_file(filepath)

    # YAML config values
    map_config = config['maps'][parser.key] # filter on CLI arg
    filename_segments = map_config['filename_segments']

    # Configure and start logger
    start_date_time = dt.datetime.now()
    logger = configure_logger(output_path, filename_segments, start_date_time)
    logger.info(f"Start run: {start_date_time.isoformat()}")
    logger.info(f"Digital Id: {map_config['digital_id']}")
    logger.info(f"Manifest: {map_config['manifest']}")

    # Retrieve files
    for path in map_config['path_segments']:

        gmd = path['gmd'] # General Material Designation
        id_prefix = path['id_prefix']
        part = path['part']
        zfill_width = path['index']['zfill_width']

        for i in range(path['index']['start'], path['index']['stop'], 1):

            # Add zfill if required
            num = str(i)
            if zfill_width > 0:
                num = num.zfill(zfill_width)

            # Retrieve binary content
            url = create_url(parser, config, gmd, id_prefix, num)
            response = requests.get(url, stream=True)

            # Create filename and path
            filename = create_filename(filename_segments, part, num, parser.format)
            filepath = create_filepath(output_path, filename)

            # Write binary content (mode=wb)
            write_file(filepath, response, 'wb')
            # write_file(filepath, response.content, 'wb')

            # Log new file name
            logger.info(f"Renamed file to {filepath.name}")

    # End run
    logger.info(f"End run: {dt.datetime.now().isoformat()}")


if __name__ == '__main__':
    main(sys.argv[1:]) # ignore the first element (program name)
