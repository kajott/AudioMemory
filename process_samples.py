#!/usr/bin/env python3
import subprocess
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
        print(f"WARNING: invalid info JSON file '{infofile}' - {e}")
        return expect_type()

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

        for srcfile in sorted(glob.glob(os.path.join(srcdir, "*.wav"))):
            destfile = os.path.join(destdir, os.path.splitext(os.path.basename(srcfile))[0].lower() + ".mp3")

            sample = {}

            sample['filename'] = destfile.replace('\\', '/')
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
