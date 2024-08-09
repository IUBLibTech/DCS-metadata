"""Engine for performing QC on a file"""
import subprocess
import logging
from pydantic import BaseModel, Field, PrivateAttr
import json
from pathlib import Path
import magic
import jsonpath_ng

class Probulator:
    binaries = {
        'ffprobe': 'ffprobe'
    }

    def configure_binaries(self, binaries: dict):
        """Update the paths for any binaries used by the Probulator"""
        self._binaries.update(**binaries)


    def get_metadata(self, file: Path) -> dict:
        """Get structured technical metadata from a file"""
        mime = magic.from_file(file, mime=True)
        family, fmt = mime.split('/')
        if family in ('audio', 'video'):
            return self._get_av_metadata(file, mime)
        else:
            raise NotImplementedError(f"Cannot handle files with family mime {family}")


    def _get_av_metadata(self, file: Path, mime: str) -> dict:
        """Get the structured metadata for an audio or video file"""
        data = {'format': {
                    'mime': mime,
                    'stream_count': 0,
                    'video_stream_count': 0,
                    'audio_stream_count': 0,
                },
                'audio': [],
                'video': []}

        p = subprocess.run([self.binaries['ffprobe'], 
                            '-show_format', '-show_streams', '-print_format', 'json',
                            '-loglevel', 'quiet', str(file)], 
                            stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                            check=True, encoding='utf8')
        pdata = json.loads(p.stdout)
        formatters = {'s': lambda x: None if x is None else str(x), 
                      'f': lambda x: None if x is None else float(x), 
                      'i': lambda x: None if x is None else int(x),
                      'd': lambda x: None if x is None else x}
        # copy the format stuff...
        for k in ('format_name,s', 'duration,f','size,i', 'bitrate,i'):
            k, f = k.split(',')
            data['format'][k] = formatters[f](pdata['format'].get(k, None))

        for s in pdata['streams']:
            match s['codec_type']:
                case 'audio':
                    data['format']['audio_stream_count'] += 1
                    data['format']['stream_count'] += 1
                    sdata = {}
                    for k in ('index,i', 'codec_name,s', 'profile,s', 'sample_fmt,s', 
                              'sample_rate,i', 'channels,i', 'channel_layout,s',
                              'bits_per_sample,i', 'duration,f', 'bit_rate,i', 'tags,d'):
                        k, f = k.split(',')
                        sdata[k] = formatters[f](s.get(k, None))
                    data['audio'].append(sdata)
                case 'video':
                    data['format']['video_stream_count'] += 1
                    data['format']['stream_count'] += 1
                    sdata = {}
                    for k in ('index,i', 'codec_name,s', 'profile,s', 'width,i', 'height,i',
                              'coded_width,i', 'coded_height,i', 'sample_aspect_ratio,s',
                              'display_aspect_ratio,s', 'pix_fmt,s', 'field_order,s',
                              'duration,f', 'bit_rate,i', 'bits_per_sample,i', 'tags,d'):
                        k, f = k.split(',')
                        sdata[k] = formatters[f](s.get(k, None))
                    frame_rate = [float(x) for x in s.get('r_frame_rate', '1/1').split('/', 1)]
                    sdata['fps'] = float(format(frame_rate[0] / frame_rate[1], "0.2f"))
                    data['video'].append(sdata)
                case _:
                    logging.debug(f"Skipping unknown stream type: {s['codec_type']}")
        return data


if __name__ == "__main__":
    import argparse
    import yaml
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="File to probulate")
    args = parser.parse_args()
    p = Probulator()
    print(yaml.safe_dump(p.get_metadata(args.file), default_flow_style=False))
