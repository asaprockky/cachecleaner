#!/usr/bin/env bash
# Usage: ./mix.sh uz   -> out/pulberry_uz.mp4
set -euo pipefail
cd "$(dirname "$0")"
LANG_=${1:-uz}
mkdir -p out
A=audio

# SFX cue sheet (seconds). Scene starts get a whoosh; impacts get a bass hit; chips/paid get ticks; riser into the outro.
WHOOSH="3.2 7.0 11.0 14.8 19.0 23.0 27.0"
HIT="0.45 4.75 13.9 17.6 31.25"
TICK="25.8 27.6 27.73 27.86 27.99 28.12 28.25 28.38 28.51 28.64 28.77 28.90 29.03"
RISER="30.0"

inputs=(-i "$A/music.wav")
filters=""
n=1
mixlist="[m]"
add() { # file time gain
  inputs+=(-i "$A/$1")
  ms=$(python3 -c "print(int($2*1000))")
  filters+="[$n:a]adelay=${ms}|${ms},volume=$3[s$n];"
  mixlist+="[s$n]"; n=$((n+1))
}
for t in $WHOOSH; do add whoosh.wav "$t" 0.5; done
for t in $HIT;    do add hit.wav    "$t" 0.9; done
for t in $TICK;   do add tick.wav   "$t" 0.45; done
for t in $RISER;  do add riser.wav  "$t" 0.5; done
filters="[0:a]volume=0.85[m];${filters}${mixlist}amix=inputs=$n:normalize=0:duration=first,atrim=0:36,loudnorm=I=-14:TP=-1:LRA=9[a]"

ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$filters" -map "[a]" -ar 48000 out/mix_${LANG_}.wav
[ "${AUDIO_ONLY:-0}" = 1 ] && exit 0
ffmpeg -y -loglevel error -framerate 30 -i frames_${LANG_}/f%05d.png -i out/mix_${LANG_}.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart -r 30 \
  -c:a aac -b:a 256k -shortest out/pulberry_${LANG_}.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of default=nw=1 out/pulberry_${LANG_}.mp4
