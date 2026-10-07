# QA: motion continuity (no static holds) + contact strip from the final mp4
import subprocess, sys, numpy as np, os
from PIL import Image
mp4 = sys.argv[1]; out = sys.argv[2]
os.makedirs(out, exist_ok=True)
# extract 10 fps small frames
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp4, '-vf', 'fps=10,scale=135:240', f'{out}/q%04d.png'], check=True)
fs = sorted(f for f in os.listdir(out) if f.startswith('q'))
prev = None; diffs = []
for f in fs:
    a = np.asarray(Image.open(f'{out}/{f}').convert('L'), dtype=float)
    if prev is not None: diffs.append(np.abs(a - prev).mean())
    prev = a
diffs = np.array(diffs)
static = [(i / 10, d) for i, d in enumerate(diffs) if d < 0.15]
print(f'frames={len(fs)} mean_diff={diffs.mean():.2f} min={diffs.min():.3f}')
print('near-static 100ms windows (t, diff):', [(round(t, 1), round(d, 3)) for t, d in static][:40], '... count', len(static))
# longest static run
run = best = 0; bt = 0
for i, d in enumerate(diffs):
    run = run + 1 if d < 0.15 else 0
    if run > best: best, bt = run, i / 10
print(f'longest static run: {best/10:.1f}s ending at {bt:.1f}s')
# contact strip every 1.5 s
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp4, '-vf', 'fps=1/1.5,scale=270:-1,tile=11x2', f'{out}/strip.png'], check=True)
print('strip ->', f'{out}/strip.png')
