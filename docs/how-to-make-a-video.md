# How to Make a Video

## Prerequisites

- Claude Code open in the toolkit root (`/Users/rubens/DATA/claude-code-video-toolkit`)
- `.env` configured (R2 + RunPod — already done)
- Node.js 18+ and Python 3.10+ installed

---

## Step 1 — Create a project

In Claude Code, type:

```
/video
```

Claude Code will ask:
- What the video is about
- Which template (`sprint-review`, `product-demo`, or `concept-explainer-short`)
- Which brand (`default` or create one)

It creates `projects/your-video-name/` with a `VOICEOVER-SCRIPT.md` and `project.json`.

---

## Step 2 — Write the script

Open `projects/your-video-name/VOICEOVER-SCRIPT.md` and fill in the narration for each scene.

**Timing rule:** ~150 words = ~1 minute. Each scene section maps to one slide.

---

## Step 3 — Gather assets (optional)

**Record a browser demo:**
```
/record-demo
```
Playwright opens a browser. Interact with whatever you want to demo. The recording saves as a `.webm` in your project's `public/` folder.

**Or add existing video files** directly to `public/` and reference them in the config.

---

## Step 4 — Generate voiceover

```
/generate-voiceover
```

This runs Qwen3-TTS via your RunPod endpoint and produces one MP3 per scene in `public/audio/scenes/`.

Then sync timing so scene durations match the actual audio:

```bash
cd projects/your-video-name
python3 ../../tools/sync_timing.py --apply
```

---

## Step 5 — Preview

```bash
cd projects/your-video-name
npm install   # first time only
npm run studio
```

Opens Remotion Studio at `http://localhost:3000` — frame-accurate live preview. Scrub through, check timing, adjust narration or config as needed.

---

## Step 6 — Iterate with Claude Code

Ask Claude Code to adjust anything:
- "Make the title slide stay for 5 seconds"
- "The demo scene feels rushed, slow it down"
- "Change the background colour to dark blue"

For visual refinement run `/design` or `/scene-review` for a guided scene-by-scene pass.

---

## Step 7 — Render

```bash
cd projects/your-video-name
npm run render
```

Output: `projects/your-video-name/out/video.mp4`

Render takes 1-5 minutes depending on video length.

---

## Step 8 — Publish (optional)

```
/publish
```

Uploads to YouTube. Title, description, and tags are auto-filled from `project.json`. Requires YouTube OAuth setup (`docs/youtube-upload.md`).

---

## Quick reference

| What | How |
|------|-----|
| New project | `/video` in Claude Code |
| Record browser demo | `/record-demo` |
| Generate voiceover | `/generate-voiceover` |
| Fix timing after audio | `python3 ../../tools/sync_timing.py --apply` |
| Live preview | `npm run studio` |
| Final render | `npm run render` |
| Publish to YouTube | `/publish` |
| Generate music | `python3 ../../tools/music_gen.py --preset corporate-bg --duration 60 --output public/music.mp3` |
| Generate image | `python3 ../../tools/flux2.py --preset title-bg --cloud runpod` |

---

## Costs (per video, approx.)

| Item | Cost |
|------|------|
| Voiceover (Qwen3-TTS, 5 scenes) | ~$0.10 |
| Background music (acemusic.ai) | Free |
| Title background image (FLUX.2) | ~$0.02 |
| Render (local CPU) | Free |
| R2 storage | Free (under 10GB) |
| **Total** | **~$0.12** |
