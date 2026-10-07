# Pulberry promo video

Vertical 9:16 promo (1080×1920, 30 fps, 36 s) for Instagram Reels / Stories and Google Play.
Two language builds from the same composition:

| File | Language |
|---|---|
| `out/pulberry_uz.mp4` | Uzbek (Latin), matches the Play Store screenshots |
| `out/pulberry_ru.mp4` | Russian |

## Story (36 s)

| Time | Scene | On-screen |
|---|---|---|
| 0–3 s | Hook | Logo drops in, "Pul kerakmi?" |
| 3–7 s | Partners | Partner tiles fly in, "+100" counter, branches of credit organisations |
| 7–11 s | One application | Real app screen (loan amount form), "Bitta ariza qoldiring" |
| 11–15 s | Fast review | Clock ring fills, "3 daqiqadan boshlab" |
| 15–19 s | Compare | Three offer cards, one gets picked |
| 19–23 s | Loan types | Card / car / gold / real-estate collateral |
| 23–27 s | Pay | Real payment screen, "To'landi ✓" |
| 27–31 s | Coverage | 12 cities, map with partner pins, Central Bank licence line |
| 31–36 s | Outro | Logo, ★ 4,1 · 10 000+ downloads, Google Play, @pulberry.uz |

## Sources used

- Google Play listing `uz.flexsoft.pulberry` — description, rating (4,1 / 65 reviews), 10 000+ downloads, icon, screenshots.
- flexsoft.uz — company info, product description, logo.
- All on-screen claims come from the Play Store listing / screenshots. Offer amounts on the compare cards are the illustrative figures shown in the store screenshots.

## How to rebuild

```bash
node render.js --lang uz --out frames_uz    # frames via headless Chromium
./mix.sh uz                                  # audio mix + H.264 encode -> out/pulberry_uz.mp4
```

- `index.html` — the whole composition. Copy lives in the `COPY` object at the top of the script; edit text there.
- `assets/` — logo and screen crops taken from the Play Store screenshots.
- `audio/` — original synthesized music bed and SFX (no third-party samples). Replace `audio/music.wav` with a licensed track if you prefer.
- Final mix is normalised to −14 LUFS, −1 dBTP.

## Notes

- No voice-over; the reel is text-driven. Add one later by dropping a WAV into `mix.sh`.
- The in-app screens are in Uzbek in both builds (they are the real store screenshots).
