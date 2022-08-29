#!/usr/bin/env python3
import subprocess
import shutil
import json
import glob
import sys
import os
import re

def ffmpeg_error(task, srcfile, out):
    print("[FAILED]")
    print(f"ERROR while {task} '{srcfile}' - FFmpeg output is:")
    print(out)
    sys.exit(1)

def run_ffmpeg(task, srcfile, *opts):
    res = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-y", "-i", srcfile] + list(opts),
        capture_output=True)
    out = (res.stdout + res.stderr).decode(errors='ignore')
    if res.returncode != 0:
        ffmpeg_error(task, srcfile, out)
    return out

def load_json(filename, expect_type=dict):
    if not os.path.exists(filename): return expect_type()
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        assert isinstance(data, expect_type), "not a valid JSON object"
        return data
    except (EnvironmentError, AssertionError) as e:
        print(f"WARNING: invalid info JSON file '{filename}' - {e}")
        return expect_type()

def load_csv(filename):
    if not os.path.exists(filename): return {}
    try:
        with open(filename, 'rb') as f:
            header = None
            data = {}
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    line = line.decode('utf-8')
                except UnicodeDecodeError:
                    line = line.decode('windows-1252', 'replace')
                sep = ';' if (line.count(';') > line.count(',')) else ','
                if line.count('\t') > line.count(sep):
                    cells = line.split('\t')
                else:
                    parts = re.split(r'(("[^"]*")+|[^!]*)!'.replace('!', sep), line + sep)
                    assert not(any(parts[::3])), "syntax error (unexpected data between cells)"
                    cells = [c.replace('""', '"').strip('"') for c in parts[1::3]]
                if not header:
                    header = cells
                    assert 'sample' in header, "'sample' column missing"
                else:
                    row = dict(zip(header, cells))
                    key = row.pop('sample').lower()
                    if key.endswith(".wav"): key = key[:4]
                    data[key] = row
        return data
    except (EnvironmentError, AssertionError) as e:
        print(f"WARNING: invalid metadata CSV file '{filename}' - {e}")
        raise
        return {}

if __name__ == "__main__":
    sets = []
    for srcdir in glob.glob(os.path.join("_rawsamples", "*")):
        if not os.path.isdir(srcdir): continue
        dirbase = os.path.basename(srcdir).lower()
        destdir = os.path.join("samples", dirbase)
        if not os.path.isdir(destdir):
            os.mkdir(destdir)

        samples = []
        info = load_json(os.path.join(srcdir, "_info.json"))
        ss = {
            'name':    dirbase,
            'samples': samples,
            'desc':    info.get('name',  dirbase.capitalize()),
            'order':   info.get('order', 0),
            'music':   info.get('music', False),
        }
        metadata = load_csv(os.path.join(srcdir, "_metadata.csv"))

        for srcfile in sorted(glob.glob(os.path.join(srcdir, "*.wav"))):
            wavbase = os.path.basename(srcfile)
            srcprefix = os.path.splitext(srcfile)[0]
            samplename = os.path.basename(srcprefix).lower()
            destfile = os.path.join(destdir, samplename + ".mp3")

            # prepare sample record; try to get metadata from various sources
            sample = {}
            sample.update(metadata.get(samplename, {}))
            sample.update(info.get(wavbase, {}))
            sample.update(info.get(samplename, {}))
            sample.update(load_json(srcprefix + ".json"))
            sample['filename'] = destfile.replace('\\', '/')
            if not sample.get('image'):
                # try to copy and associate local image file
                for ext in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'avif'):
                    imgsrc = srcprefix + '.' + ext
                    if os.path.isfile(imgsrc):
                        imgdest = os.path.join(destdir, os.path.basename(imgsrc).lower())
                        print(imgsrc, '->', imgdest, end=' ')
                        if os.path.exists(imgdest) and (os.path.getmtime(imgdest) >= os.path.getmtime(imgsrc)):
                            print("[skip]")
                        else:
                            try:
                                shutil.copy(imgsrc, imgdest)
                                print("[OK]")
                            except EnvironmentError as e:
                                print("[FAILED: {}]".format(e))
                        sample['image'] = imgdest.replace('\\', '/')
                        break
            samples.append(sample)

            # don't process sample again if already done so
            if os.path.exists(destfile) and (os.path.getmtime(destfile) > os.path.getmtime(srcfile)):
                print(srcfile, "->", destfile, "[skip]")
                continue

            # ReplayGain analysis
            sys.stdout.write(f"{srcfile} ")
            sys.stdout.flush()
            out = run_ffmpeg("analyzing", srcfile,
                "-af", "replaygain",
                "-f", "null", "nul:" if (sys.platform == "win32") else "/dev/null")
            m = re.search(r'track_gain\s*=\s*([-+]?\d+\.\d+)\s*d[bB]', out)
            if not m: ffmpeg_error("analyzing", srcfile, out)
            db = m.group(1)

            # output file generation
            sys.stdout.write(f"({db} dB) -> {destfile} ")
            sys.stdout.flush()
            run_ffmpeg("processing", srcfile,
                "-af", f"volume={db}dB",
                "-c:a", "libmp3lame", "-b:a", "128k",
                "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact",
                destfile)
            print("[OK]")
        sets.append(ss)
    sets.sort(key=lambda ss: (ss['order'], ss['name']))

    with open("samplesets.js", "w") as f:
        f.write("// This file has been automatically generated by " + os.path.basename(sys.argv[0]) + ". DO NOT EDIT!\n")
        f.write("const SampleSets=")
        json.dump(sets, f)
        f.write(";\n")
