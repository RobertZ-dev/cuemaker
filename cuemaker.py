"""
A program for automatically generating CUE files from a list of timestamps and titles, like
those commonly seen in YouTube descriptions.

Original Author: JoshBarrass

Contributing Authors: TheScienceOtter / Januswizard

Last Edit: 7/6/2022

"""
import re
import argparse


def pad_number(number, length=2, padding="0"):
    str_number = str(number)
    if len(str_number) < length:
        str_number = padding + str_number
    return str_number


def make_cue_tracks(inp, pattern="(\[)?((\\d{1,2}):)?(\\d{1,2}):(\\d{1,2})(\])? (.*)",
                    hr=2, m=3, s=4, title=6, artist=None):
    matcher = re.compile(pattern)

    output = ""
    lines = inp.strip("\n").split("\n")
    if len(lines) > 99:
        raise ValueError("A cue sheet cannot contain more than 99 tracks!")
    for line in range(len(lines)):
        lines[line] = lines[line].strip()
        str_track = pad_number(line + 1)

        match = matcher.match(lines[line])
        groups = list(match.groups())
        if groups[hr] == None: groups[hr] = "00"

        output += "\n    TRACK {n} AUDIO\n".format(n=str_track)
        output += "        TITLE \"{title}\"\n".format(title=groups[title])
        if isinstance(artist, int):
            output += "        PERFORMER {artist}\n".format(artist=groups[artist])
        output += "        INDEX 01 {m}:{s}:00".format(m=pad_number(int(groups[hr]) * 60 + int(groups[m])),
                                                       s=pad_number(groups[s]))

    return output


def make_cue(inp, performer, album, filename, form, rems={}, *args, **kwargs):
    """Takes input text, artist, and album name, filename and type to produce a cue sheet. Optionally takes 'pattern'
    argument with 'hr', 'm', 's', and 'title' arguments to specify new regex patterns and group indices. 'artist'
    argument specifies artist regex index for tracks that have different artists. """
    output = "PERFORMER \"{performer}\"\nTITLE \"{album}\"\n".format(performer=performer, album=album)
    for key, item in rems.items():
        output += "REM {k} {i}\n".format(k=key, i=item)

    output += "FILE \"{f}\" {t}".format(t=form.upper(), f=filename)
    output += make_cue_tracks(inp, *args, **kwargs)
    return output


def read_description(path):
    f = open(path, "r")
    description = f.read()
    f.close()
    return description


def save_cue(path, data):
    with open(path, "w") as f:
        f.write(data)
    f.close()
    return True


if __name__ == "__main__":
    # python3 cuemaker "description.txt" "album name" "performer"  
    parser = argparse.ArgumentParser()
    parser.add_argument("description_path", help="Path to the description file containing timestamps.")
    parser.add_argument("album", help="Display name of the album enclosed in quotes.")
    parser.add_argument("performer", help="Display name of the artist/performer, enclosed in quotes.")
    parser.add_argument("--artist",
                        help="A comma separated list of artists. If supplied, the artist for each track should be "
                             "specified in order.")
    parser.add_argument("--pattern", default="(\[)?((\\d{1,2}):)?(\\d{1,2}):(\\d{1,2})(\])? (.*)", nargs='?',
                        help="A Regex pattern to match on the description file. If this is changed the --hr, --m, "
                             "--s, and --title, options should also be defined to capture the correct regex groups.")
    parser.add_argument("--hr", default=2, nargs='?', help="Specify the Regex group corresponding to the hour digit(s).")
    parser.add_argument("--m", default=3, nargs='?',
                        help="Specify the Regex group corresponding to the minutes digit(s).")
    parser.add_argument("--s", default=4, nargs='?',
                        help="Specify the Regex group corresponding to the seconds digit(s).")
    parser.add_argument("--title", default=6, nargs='?', help="Specify the Regex group corresponding to the title.")
    parser.add_argument("--output", default="output", nargs='?',
                        help="THe name of the output file. Defaults to \"output\"")
    args = parser.parse_args()

    # Try read description file
    description = read_description(args.description_path)
    # Read given data
    filename = args.output
    extention = ".cue"

    # make .cue data
    output = make_cue(description, args.performer, args.album, filename, extention,
                      artist=args.artist, pattern=args.pattern, hr=args.hr,
                      m=args.m, s=args.s, title=args.title)

    # Save .cue file
    save_cue(filename + extention, output)
    print("Done!")
