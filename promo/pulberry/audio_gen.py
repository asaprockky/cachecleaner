# Original synthesized music bed + SFX for the Pulberry promo v2 (no third-party samples).
import numpy as np, wave, os
SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(42)

def save(name, x):
    x = np.clip(x, -1, 1); d = (x * 32767).astype('<i2')
    if d.ndim == 1: d = np.column_stack([d, d])
    with wave.open(os.path.join(OUT, name), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
    print('wrote', name, round(len(d) / SR, 2), 's')

def t_(n): return np.arange(n) / SR
def m2f(m): return 440 * 2 ** ((m - 69) / 12)
def adsr(n, a, d, s, r):
    e = np.zeros(n); A = max(1, int(a * SR)); D = max(1, int(d * SR)); R = max(1, int(r * SR))
    e[:A] = np.linspace(0, 1, A)
    e[A:A + D] = np.linspace(1, s, D)[:max(0, n - A)]
    e[A + D:] = s
    if R < n: e[-R:] *= np.linspace(1, 0, R)
    return e[:n]
def onepole_lp(x, cutoff):
    """time-varying one-pole lowpass; cutoff scalar or array (Hz)"""
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * c / SR); y = np.zeros_like(x); z = 0.0
    for i in range(len(x)):
        z = a[i] * z + (1 - a[i]) * x[i]; y[i] = z
    return y
def lp_fast(x, cutoff):
    # fixed-cutoff lowpass via FFT (fast, used for long signals)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    H = 1 / np.sqrt(1 + (f / cutoff) ** 4); return np.fft.irfft(X * H, len(x))
def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    H = 1 / np.sqrt(1 + (cutoff / np.maximum(f, 1e-3)) ** 4); return np.fft.irfft(X * H, len(x))
def bp_fast(x, lo, hi): return hp_fast(lp_fast(x, hi), lo)
def reverb(x, sec=0.8, mixv=0.25):
    n = int(sec * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * (4 / sec)); ir[0] = 1
    y = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[:len(x)]
    return x + mixv * y / (np.abs(y).max() + 1e-9) * np.abs(x).max()
def saw(f, n, detune=(0.995, 1, 1.005)):
    t = t_(n); x = 0
    for d in detune: x = x + 2 * ((t * f * d) % 1) - 1
    return x / len(detune)
def sq(f, n): return np.sign(np.sin(2 * np.pi * f * t_(n)))
def sine(f, n): return np.sin(2 * np.pi * f * t_(n))

# ------------------------------------------------------------------ MUSIC
BPM = 120; beat = 60 / BPM; bar = 4 * beat; BARS = 16; TOTAL = BARS * bar + 1.5
N = int(TOTAL * SR); mix = np.zeros(N)
def at(sec): return int(sec * SR)
def add(sig, sec, gain=1.0):
    s = at(sec); L = min(len(sig), N - s)
    if L > 0: mix[s:s + L] += sig[:L] * gain
# A minor progression: Am  F  C  G  (roots 57 53 48 55)
CH = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 60], [55, 59, 62, 66]]
# drums
def kick():
    n = at(0.35); t = t_(n); f = 48 + 160 * np.exp(-t * 32)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = rng.standard_normal(n) * np.exp(-t * 400) * 0.6
    return np.tanh((x + click) * 1.8)
def clap():
    n = at(0.25); t = t_(n); x = np.zeros(n)
    for off in (0, 0.012, 0.024, 0.036):
        s = at(off); x[s:] += rng.standard_normal(n - s) * np.exp(-t[:n - s] * 28)
    return bp_fast(x, 900, 7000) * 0.9
def hat(open_=False):
    n = at(0.35 if open_ else 0.07); t = t_(n)
    x = rng.standard_normal(n) * np.exp(-t * (9 if open_ else 80)); return hp_fast(x, 7000) * 0.55
def pluck(f, dur):
    n = at(dur); t = t_(n); x = (sine(f, n) + 0.5 * sine(2 * f, n) + 0.25 * sine(3 * f, n) + 0.12 * sine(4 * f, n))
    return x * np.exp(-t * 11) * 0.35
def bass(f, dur):
    n = at(dur); t = t_(n); x = saw(f, n, (1,)) * 0.7 + sq(f / 2, n) * 0.3
    cut = 220 + 1800 * np.exp(-t * 14); return onepole_lp(x, cut) * adsr(n, 0.004, 0.08, 0.7, 0.03)
def stab(notes, dur):
    n = at(dur); x = sum(saw(m2f(m), n) for m in notes) / len(notes)
    return lp_fast(x, 2600) * adsr(n, 0.005, 0.12, 0.5, 0.05) * 0.45
def pad(notes, dur):
    n = at(dur); x = sum(saw(m2f(m), n, (0.993, 1, 1.007)) + 0.4 * saw(m2f(m + 12), n, (0.996, 1.004)) for m in notes) / len(notes)
    return lp_fast(x, 1400) * adsr(n, 0.3, 0.3, 0.9, 0.3) * 0.5

KICK, CLAP, HATC, HATO = kick(), clap(), hat(), hat(True)
for b in range(BARS):
    ch = CH[b % 4]; bs = b * bar
    full = b >= 2; brk = b in (10, 11)
    # pad every bar
    add(pad(ch, bar), bs, 0.55 if not brk else 0.35)
    # arpeggio 16ths
    pat = [0, 1, 2, 3, 2, 1, 0, 2, 1, 3, 2, 0, 1, 2, 3, 1]
    for i in range(16):
        f = m2f(ch[pat[i]] + 12 + (12 if i % 7 == 0 else 0))
        add(pluck(f, beat / 2), bs + i * beat / 4, 0.9 if i % 4 == 0 else 0.6)
    if brk:
        continue
    # bass 8ths with octave bounce
    for i in range(8):
        add(bass(m2f(ch[0] - 24 + (12 if i in (3, 7) else 0)), beat / 2 * 0.95), bs + i * beat / 2, 0.55)
    if full:
        for i in range(4):
            add(KICK, bs + i * beat, 1.0)
            if i in (1, 3): add(CLAP, bs + i * beat, 0.8)
        for i in range(8):
            add(HATC, bs + i * beat / 2 + beat / 4, 0.7 if i % 2 else 0.45)
        add(HATO, bs + 2 * beat + beat / 2, 0.5)
        if b % 2 == 1:
            add(stab(ch, beat / 2), bs + 2.5 * beat, 0.8)
            add(stab(ch, beat / 4), bs + 3.5 * beat, 0.6)
    else:
        for i in range(4): add(KICK, bs + i * beat, 0.55)
# risers into bar 2 (drop) and bar 12 (second drop)
def riser(dur):
    n = at(dur); t = t_(n); x = rng.standard_normal(n)
    cut = 300 + 6000 * (t / dur) ** 2; x = onepole_lp(x, cut) * (t / dur) ** 1.5
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * (t / dur) ** 2) / SR) * (t / dur) ** 2 * 0.3
    return (x / (np.abs(x).max() + 1e-9) + tone) * 0.5
add(riser(2 * bar), 0, 0.9); add(riser(bar), 11 * bar, 0.8)
# sidechain pump
t = t_(N); pump = 1 - 0.5 * np.exp(-((t % beat) / 0.11)); mix *= pump
# final hit + tail at end of bar 16
end = BARS * bar
mix[at(end):] *= 0.2
add(KICK, end - beat * 0.0, 1.0)
mix = np.tanh(mix * 1.4) * 0.85
mix = reverb(mix, 0.25, 0.08)
fade = at(1.0); mix[-fade:] *= np.linspace(1, 0, fade)
save('music.wav', mix)

# ------------------------------------------------------------------ SFX
def norm(x, g=0.9): return x / (np.abs(x).max() + 1e-9) * g
def whoosh(dur=0.5, up=False, lo=200, hi=6000):
    n = at(dur); t = t_(n); x = rng.standard_normal(n)
    sweep = (t / dur) if up else (1 - t / dur)
    cut = lo + (hi - lo) * sweep ** 2
    x = onepole_lp(x, cut); env = np.exp(-((t / dur - (0.6 if up else 0.3)) / 0.22) ** 2)
    return norm(x * env)
def impact(dur=0.9):
    n = at(dur); t = t_(n); f = 42 + 140 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    noise = rng.standard_normal(n) * np.exp(-t * 30) * 0.5
    click = rng.standard_normal(n) * np.exp(-t * 600)
    return norm(reverb(np.tanh((sub * 1.6 + noise + click) * 1.5), 0.6, 0.35))
def pop(dur=0.14):
    n = at(dur); t = t_(n); f = 900 * np.exp(-t * 40) + 250
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) + rng.standard_normal(n) * np.exp(-t * 500) * 0.4
    return norm(x, 0.8)
def bell(f, dur=1.2, I=2.0):
    n = at(dur); t = t_(n); mod = np.sin(2 * np.pi * f * 1.41 * t) * I * np.exp(-t * 3)
    return np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 2.6)
def coin():
    x = bell(m2f(88), 0.9); b2 = bell(m2f(93), 0.8); s0 = at(0.07); L = min(len(b2), len(x) - s0); x[s0:s0 + L] += b2[:L]
    return norm(reverb(x, 0.6, 0.3), 0.8)
def success():
    notes = [76, 80, 83, 88]; dur = 1.6; n = at(dur); x = np.zeros(n)
    for i, m in enumerate(notes):
        s = at(i * 0.07); b = bell(m2f(m), dur - i * 0.07, 1.5); x[s:s + len(b)] += b
    return norm(reverb(x, 0.9, 0.35), 0.85)
def swipe():
    return norm(whoosh(0.3, up=True, lo=800, hi=9000), 0.8)
def tick_count(dur=0.03):
    n = at(dur); t = t_(n); return norm(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 300), 0.5)
def click():
    n = at(0.06); t = t_(n); x = rng.standard_normal(n) * np.exp(-t * 350); return norm(bp_fast(x, 1500, 8000), 0.7)
def shine():
    n = at(0.7); t = t_(n); f = 1800 + 2600 * (t / 0.7)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-((t - 0.3) / 0.18) ** 2) * 0.5 + onepole_lp(rng.standard_normal(n), 3000 + 9000 * t / 0.7) * np.exp(-((t - 0.35) / 0.2) ** 2) * 0.6
    return norm(x, 0.7)
def boom_riser(dur=1.4):
    r = riser(dur); return norm(r, 0.9)

save('whoosh.wav', whoosh()); save('whoosh_up.wav', whoosh(0.5, True)); save('impact.wav', impact()); save('pop.wav', pop())
save('coin.wav', coin()); save('success.wav', success()); save('swipe.wav', swipe()); save('tick.wav', tick_count()); save('click.wav', click())
save('shine.wav', shine()); save('riser.wav', boom_riser())
