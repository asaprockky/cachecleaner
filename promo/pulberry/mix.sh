#!/usr/bin/env bash
# ./mix.sh uz  -> out/pulberry_uz_1080p.mp4 + out/pulberry_uz_4k.mp4
set -euo pipefail
cd "$(dirname "$0")"
L=${1:-uz}; mkdir -p out; A=audio; END=32.2

inputs=(-i "$A/music.wav"); filters=""; n=1; mixlist="[m]"
add() { inputs+=(-i "$A/$1"); ms=$(python3 -c "print(int($2*1000))"); filters+="[$n:a]adelay=${ms}|${ms},volume=$3[s$n];"; mixlist+="[s$n]"; n=$((n+1)); }
cue() { f=$1; g=$2; shift 2; for t in "$@"; do add "$f" "$t" "$g"; done; }

# ---- cue sheet (seconds) ----
cue whoosh_up.wav 0.9  0.05                       # logo drops in
cue impact.wav    1.2  0.55 11.7 22.6 27.8        # logo slam, approved, paid, outro logo
cue tick.wav      0.6  $(python3 -c "print(' '.join(f'{0.6+i*0.04:.2f}' for i in range(8)))")   # wordmark letters
cue pop.wav       0.7  $(python3 -c "print(' '.join(f'{1.3+i*0.05:.2f}' for i in range(12)))")  # Pul kerakmi? letters
cue whoosh.wav    1.0  2.6 27.6                   # red wipes
cue swipe.wav     0.8  2.9 3.1                     # phone + ring in
cue tick.wav      0.7  $(python3 -c "print(' '.join(f'{3.4+i*0.05:.2f}' for i in range(18)))")  # +100 counter
cue impact.wav    0.8  4.3                         # counter lands
cue whoosh.wav    0.6  5.4                         # tiles fly out
cue click.wav     1.1  6.0 8.4 9.1 9.5 15.2 16.2 22.4   # taps
cue swipe.wav     0.6  6.12 8.5 9.62 12.6 16.8 20.2 24.0  # screen pushes
cue tick.wav      0.6  $(python3 -c "print(' '.join(f'{6.8+i*0.06:.2f}' for i in range(20)))")  # slider drag
cue pop.wav       0.8  9.15                        # chip select
cue riser.wav     0.7  10.2                        # processing ring
cue success.wav   1.0  11.7 22.6                   # approved, paid
cue pop.wav       0.9  12.0                        # toast
cue swipe.wav     0.5  12.9 13.18 13.46            # offer cards in
cue tick.wav      0.5  $(python3 -c "print(' '.join(f'{13.0+i*0.07:.2f}' for i in range(12)))")  # amounts counting
cue whoosh_up.wav 0.5  14.0                        # scroll
cue shine.wav     0.8  15.3                        # card expands
cue coin.wav      1.0  16.25 22.9                  # accepted, paid
cue swipe.wav     0.5  17.15 17.37 17.59 17.81     # type cards flip in
cue whoosh_up.wav 0.5  18.6                        # scroll
cue tick.wav      0.5  $(python3 -c "print(' '.join(f'{20.6+i*0.07:.2f}' for i in range(12)))")  # pay amounts
cue impact.wav    0.7  24.3                        # map lands
cue pop.wav       0.8  $(python3 -c "print(' '.join(f'{24.8+i*0.11:.2f}' for i in range(12)))")  # city chips
cue shine.wav     0.7  26.3                        # shield
cue tick.wav      0.9  29.0 29.14 29.28 29.42 29.56   # stars
cue shine.wav     0.9  30.6                        # badge shine
cue pop.wav       0.7  30.5 30.8                   # handle, footer

filters="[0:a]volume=0.9[m];${filters}${mixlist}amix=inputs=$n:normalize=0:duration=first,atrim=0:${END},afade=t=out:st=31.4:d=0.8,loudnorm=I=-14:TP=-1:LRA=9[a]"
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$filters" -map "[a]" -ar 48000 out/mix_${L}.wav
[ "${AUDIO_ONLY:-0}" = 1 ] && exit 0

# 1080p first (single pass from 2x frames), then the 4K master
ffmpeg -y -loglevel error -framerate 30 -i frames_${L}/f%05d.jpg -i out/mix_${L}.wav -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -movflags +faststart -r 30 -c:a aac -b:a 256k -shortest out/pulberry_${L}_1080p.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of default=nw=1 out/pulberry_${L}_1080p.mp4
[ "${SKIP_4K:-0}" = 1 ] && exit 0
ffmpeg -y -loglevel error -framerate 30 -i frames_${L}/f%05d.jpg -i out/mix_${L}.wav \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -movflags +faststart -r 30 -c:a aac -b:a 256k -shortest out/pulberry_${L}_4k.mp4
