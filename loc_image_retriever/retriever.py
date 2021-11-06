import datetime as dt
import logging
import requests
import sys
import yaml

from argparser import create_parser
from pathlib import Path


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
            # f"/{config['service_path'][parser.format]}",
            f"/{gmd.replace(':', '/')}",
            f"/{id_prefix}{num}",
            f".{parser.format}"
            ])
    else:
        return ''.join([
            f"{config['protocol']}",
            f"://{config['subdomain']}",
            f".{config['domain']}",
            # f"/{config['service_path'][parser.format]}",
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
    parser = create_parser().parse_args(args)
    output_path = parser.output

    # load YAML config
    config = read_yaml_file('./music_config.yml')

    # YAML config values
    music_config = config['music'][parser.key] # filter on CLI arg
    filename_segments = music_config['filename_segments']

    # Configure logger: set format and default level
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    # Create logger
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)

    # Create logger filename and path
    filename = create_filename(filename_segments, format='log')
    filepath = create_filepath(output_path, filename)

    # Add logger file and stream handlers
    logger.addHandler(logging.FileHandler(filepath))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    #$logger = configure_logger(output_path, filename_segments, start_date_time)

    # Start logger
    start_date_time = dt.datetime.now()
    logger.info(f"Start run: {start_date_time.isoformat()}")
    logger.info(f"Digital Id: {music_config['digital_id']}")
    logger.info(f"Manifest: {music_config['manifest']}")

    # Retrieve files
    for path in music_config['path_segments']:

        gmd = path['gmd'] # General Material Designation
        id_prefix = path['id_prefix']
        part = path['part']
        zfill_width = path['index']['zfill_width']

        for i in range(path['index']['start'], path['index']['stop'], 1):

            # Add zfill if required
            num = str(i) + 'u'
            if zfill_width > 0:
                num = num.zfill(zfill_width)

            # Retrieve binary content
            url = create_url(parser, config, gmd, id_prefix, num)
            print(f"\nURL={url}")
            response = requests.get(url, stream=True)

            # Log URL
            logger.info(f"Target URL: {url}")

            # Create filename and path
            filename = create_filename(filename_segments, part, num, parser.format)
            filepath = create_filepath(output_path, filename)

            # Log filename
            logger.info(f"Image renamed to {filepath.name}")

            # Write binary content (mode=wb)
            write_file(filepath, response, 'wb')
            # write_file(filepath, response.content, 'wb')

    # End run
    logger.info(f"End run: {dt.datetime.now().isoformat()}")


if __name__ == '__main__':
    main(sys.argv[1:]) # ignore the first element (program name)
