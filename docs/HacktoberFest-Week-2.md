# Round 2 pick: BibLocal, an offline race-photo bib tagger

**Build BibLocal: a free, open-source desktop tool that reads runners' bib numbers in thousands of race photos on an ordinary laptop, offline, and writes them into the photo files as Lightroom keywords. Do this today: run kill tests K1 and K2 on 50 public bib photos, using CPU only.**

## TL;DR
- **Pick: BibLocal.** Small race photographers shoot 1,000–5,000 photos an event. Then they spend hours typing bib numbers so runners can find their photos. Free ChatGPT can't take 3,000 photos and write keywords into each file. The cloud tools upload photos of the public, children included.
- **Why open matters, and it's true here:** the open-weight OCR models (PP-OCR, Apache-2.0) are small. The PP-OCRv4 mobile ONNX files total about 12.4 MB: a 4.75 MB detector (ch_PP-OCRv4_det_infer.onnx) and a 7.65 MB recognizer (en_PP-OCRv4_rec_mobile.onnx), per the SWHL/RapidOCR and Docling-RapidOcr file listings on Hugging Face. They run on CPU through ONNX Runtime. It works with Wi-Fi off and costs $0 per 1,000 photos. Paid alternatives cost 2–5¢ per photo or need paid credits. You can swap the model by changing one file.
- **Backups:** #2 is MaskPaste, which removes client names in the browser before you paste into a chatbot. #3 is Critter Sieve, a filter that drops empty trail-camera frames for hobbyists. Both pass the hard filters, but crowded markets and weaker originality score them lower.

## The top 3 (main body, about 3 minutes)

**#1 BibLocal (recommended)**
- **Who:** freelance and small-team race photographers anywhere: 5Ks, trail runs, triathlons, ski and MTB races.
- **Their boring task today:** opening each photo, zooming in on the bib and typing the number. One ski-race shooter on a forum spends about 90 minutes per race. Others describe hours.\[1\]
- **What the tool does:** point it at a folder and an optional start list (CSV). It reads the bibs, keeps only numbers that are on the start list, and writes keywords into each file plus a CSV. Anything it isn't sure about goes in a "review" pile.
- **Why free chatbots can't:** volume (2,000+ photos per event), output (keywords written into the files Lightroom reads), and privacy (photos of the public, often including minors).
- **Why open matters:** the photos never leave the laptop. It works at a venue with no signal. It costs $0 per event. The OCR model can be swapped (PP-OCRv4 → v5 → v6) or fine-tuned on bib fonts.
- **Runs on:** any CPU laptop. RapidOCR's PP-OCRv4 ONNX benchmark (as quoted by polyreid.com) gives 0.2256 s per image for the 4.5 MB detector and 0.6836 s per test image for the 10 MB recognizer, with "83.23 percent exact matches and 93.55 percent correct characters" (Vendor claim). Your K2 test measures the real number.
- **Build hours by Friday:** about 13 h.
- **First users:** dgrin sports forum, Adobe Lightroom Community threads asking for exactly this, talkphotography.co.uk, r/sportsphotography (check its rules first), and running clubs in your own network.

**#2 MaskPaste**
- **Who:** freelancers, translators and consultants under an NDA or GDPR.
- **Their boring task today:** deleting client names, emails and IBANs by hand before pasting text into ChatGPT, then putting them back afterwards.
- **What the tool does:** a browser page swaps personal details for tokens like [CLIENT_1]. You paste the safe text into any chatbot, paste the answer back, and it restores the real names locally.\[2\]\[3\]
- **Why free chatbots can't:** the whole point is that the chatbot never sees the data.
- **Why open matters:** an open PII model (GLiNER) runs inside the browser, and you can prove nothing is sent by switching to airplane mode.\[4\]
- **Runs on:** any browser. The GLiNER-small INT8 ONNX model is 187 MB and takes 59 ms per turn on CPU, but its recall drops to 53% (FP32: 71%, 583 MB) (Vendor claim).\[5\]
- **Build hours:** about 12 h. **Users:** ProZ translator forums and freelancer subreddits. **Risk:** Amaze, ONYRI Sanitize and PrivacyScrubber already do this.\[2\]\[6\]

**#3 Critter Sieve**
- **Who:** hobbyist trail-camera owners, small land managers and wildlife volunteers.
- **Their boring task today:** clicking through SD cards where 70–95% of frames are empty, set off by wind or rain.\[7\]
- **What the tool does:** runs Microsoft's open MegaDetector on the CPU, moves empty frames to a folder and makes a "best animal shots" contact sheet.
- **Why free chatbots can't:** a single card holds thousands of images. Chatbots have no batch file moves. Upload is slow from rural internet.
- **Why open matters:** it works offline with no per-image cost, and the open model can be swapped.
- **Runs on:** CPU laptops. The microsoft/MegaDetector README lists the compact MDV6-yolov10-c (2.3M params) at "~2–5 images/sec" on a modern CPU with no GPU, and says a million images take "roughly 3.9 days" on CPU with that model (Vendor claim).
- **Build hours:** about 10 h. **Users:** WILDLABS forum and trail-camera and hunting forums. **Risk:** free research tools like Timelapse plus MegaDetector already exist.\[8\]

**Why BibLocal wins:** it is the only finalist where all three things are true at once. The pain is measured in hours per event. The existing tools are either cloud-based, credit-priced or motorsport-only. And no Week 2 entry on DEV touches it. Most Week 2 entries are invoice sorters, listing writers and scope-creep tools.\[9\] BibLocal's AI is a specialized open vision model, not a Gemma chat wrapper. It also carries a deterministic check: a number only counts if it is on the start list. That gives the write-up a sharp open-vs-closed story. One competitor's own comparison page says it sends the full image to Google Gemini.\[10\]\[11\] BibLocal sends nothing.

---

## Rules check (re-verified 13 Oct 2026)

- **Rules page now loads.** The contest-specific rules page works. The entry period runs from 12 Oct 12:00 PM PDT to 18 Oct 11:59 PM PDT, which is 19 Oct 12:29 PM IST. (Verified)\[12\]
- **Open weights count.** A required element reads: "A brand-new project built during the Entry Period that uses open-weight models and/or open-source AI tools (such as open-source agent harnesses, frameworks, or local inference) as a core part of the project." So an open-weight model alone is enough. (Verified)\[12\]
- **Your code must be linked.** "A link to, or embed of, the project's code repository" is required.\[12\] No specific open-source licence is named, so add MIT or Apache-2.0 anyway; it matches the theme. (Verified; the licence advice is my recommendation)
- **The demo and the paying user.** A deployed link or a video demo is required. The project must offer "something a real person or business would plausibly pay for". A first user earns bonus points but is optional. (Verified)\[12\]\[13\]
- **Limits.** One entry per person. Each participant can win at most one prize. Writing quality is weighted most heavily. (Verified)\[12\]

## Evidence: BibLocal

**User posts describing the pain** (Verified unless noted; checked 13 Oct 2026)

| Date | Where | What they said |
|---|---|---|
| around 4 Apr 2011 | dgrin, "Automatic number plate recognition for photographers?" (dgrin.com/discussion/194321) | Motocross shooter, 1,000–2,000 photos: wants to show racers "the day of without having myself or an assistant tag photos for hours."\[1\] |
| 9–10 Aug 2011 | same thread | Enduro/MTB, 1,000–3,000 photos per multiday race: "taging every picture takes alot of time… what a pain!!!"\[1\] |
| 20 Mar 2012 | same thread | Ski races, 2,000–3,000 images, Photo Mechanic: "maybe 90 minutes to keyword a race."\[1\] |
| 18 Apr 2019 | Adobe Community, "OCR and Facial Recognition for Sports Photography" | Asks for a Lightroom plugin or app that uses OCR to tag numbers in metadata.\[14\] |
| 20 Feb 2024 | Adobe Community, "Identify participant's numbers (jersey)" | "Is there a plug in for LRC that could recognize the race bib number." The Community Expert answered: "No."\[15\] |

- **Counterpoint (Verified, 3 Sep 2026, Adobe Community):** "numbers are occluded, motion-blurred or at an angle… you end up hand-checking anyway."\[14\] This is why BibLocal is designed to abstain and send unsure photos to review.
- **Gap:** I found no Reddit posts. The evidence is forum posts, and some are old. Read it as long-running pain, not new demand.

**Existing tools and their gaps** (checked 13 Oct 2026)

| Tool | Price | Gap |
|---|---|---|
| RaceTagger | 500 free credits, 100 free analyses a month, packs from €39 (Vendor claim) | Its own comparison page says photos go to Google Gemini; other pages say "local". The claims contradict each other.\[10\]\[11\]\[16\] |
| TagMyRun | Free (Vendor claim) | Cloud upload, 1,000-photo batch limit, no start-list matching (per a competitor's review)\[16\]\[17\] |
| TrackAction.AI | $10–299 a month (competitor's review)\[16\] | Cloud number reading, mainly motorsport\[11\] |
| MyRun | First 5,000 photos free, then pay per volume (Vendor claim)\[18\] | Hosted gallery platform, not a tool for your own files\[18\] |
| Manual tagging services | $0.02 per image (Bib Number Entry), $0.05 per image (CapCity, dgrin 2016), 1–3¢ per tag (FlashFrame figure) | Slow and costly; a person sees every photo\[19\]\[20\]\[21\] |

- **TagOmatic LITE** is free, local and Ollama-based, but built for motorsport (Vendor claim).\[22\] It is the closest local rival, so be honest about it in the write-up.

## Evidence: MaskPaste and Critter Sieve

- **MaskPaste pain (Verified):**
  - A ProZ translator forum thread quotes an agency NDA that bans "uploading onto machine translation systems on the internet of texts and documents - even in part".\[23\]
  - Spellbook's guide for lawyers says pasting client facts into consumer ChatGPT is "disclosing confidential information to a third party".\[24\]
  - Nigeria's NITDA advises removing or pseudonymising personal data before using AI (Pulse.ng, Oct 2026).\[25\]
  - Gap: I found only one first-person user post. The rest are guidance articles.
- **MaskPaste competitors:** Amaze, ONYRI Sanitize and PrivacyScrubber already offer local masking that runs in the browser (Vendor claims).\[2\]\[3\]\[6\] The market is crowded.
- **Critter Sieve pain (Verified):**
  - WILDLABS threads on video camera-trap analysis and on running MegaDetector on edge devices.\[8\]\[26\]
  - A 2024 WILDLABS review calls MegaDetector "a huge time saver".\[27\]
  - The microsoft/MegaDetector README says "in typical deployments 70–95% are empty, frames triggered by wind, rain, or moving vegetation" (Vendor claim).
- **Critter Sieve competitors:** MegaDetector itself is free. Timelapse already filters images using MegaDetector results.\[8\] A hobbyist-friendly wrapper is the only gap. (Hypothesis)

## Exact tech per idea

| | BibLocal | MaskPaste | Critter Sieve |
|---|---|---|---|
| Model | PP-OCRv5 mobile det + rec through RapidOCR (v6 small is the new default) | GLiNER small v2.5 PII, ONNX INT8; nvidia/gliner-PII as the accuracy option\[5\]\[28\] | MegaDetector V6 compact (MDV6-yolov10-c, 2.3M params) |
| Weight licence | Apache-2.0: RapidOCR README says converted ONNX weights carry PaddleOCR's Apache-2.0 (Verified) | nvidia/gliner-PII "ready for commercial/non-commercial use" (Verified);\[29\]\[30\] exact licence name for each checkpoint must be checked | MDV6-yolov10-c is AGPL-3.0, per the licence table in microsoft/MegaDetector's training_guide.md. Microsoft lists MDV6-mit-yolov9-c as the MIT option and MDV6-apa-rtdetr-e as Apache-2.0, so use one of those for a permissive licence |
| Runtime | Python + onnxruntime (CPU), exiftool for metadata | GLiNER.js / ONNX Runtime Web (WebGPU, falls back to WASM)\[4\] | Python, the MegaDetector package, CPU |
| Speed (CPU) | RapidOCR v4 ONNX: 0.2256 s per image for the detector and 0.6836 s per test image for the recognizer (RapidOCR benchmark, quoted by polyreid.com); 0.21 s for one invoice on Apple M-series (third-party) | 59 ms per turn INT8, 94 ms FP32 (model card) | MDv6 compact: "~2–5 images/sec" on a modern CPU (microsoft/MegaDetector README); MDv5: 0.5 images/s on one i7-12700 core |
| Download | wheel about 29 MB with v6 models\[31\] | 187 MB (INT8)\[5\]\[28\] | small (compact model) |
| Offline | Fully, after install | Fully, after the first model load | Fully |
| Prize fit | Best Use of GitHub Copilot (only if you really use Actions to build the .exe) | Best Use of Gemma: no, not natural | none |

- **Every Week 2 prize category, as listed on the challenge page:**
  - Featured ($200 each): Render, TabPFN, Tinker, Arduino, DigitalOcean, Gemma.\[13\]
  - Partner ($100 each): Backboard, ElevenLabs, Entire, GitHub Copilot, Mastra, MongoDB Atlas, Sentry Agent Tracing, SerpApi, .tech Domain, Temporal, Tiger Data.\[13\]
- **Requirements by category:**
  - Render: host the AI runtime or the agent front end.\[13\]
  - TabPFN: use it on tabular data (free non-commercial licence).\[13\]
  - Tinker: fine-tune and show an improvement over a baseline.\[13\]
  - Arduino: needs an UNO Q board.\[13\]
  - DigitalOcean: host or deploy on DO.\[13\]
  - Gemma: use Gemma.\[13\]
  - Backboard: R-CLI, its API, or memory/RAG.\[13\]
  - ElevenLabs: voice or transcription.\[13\]
  - Entire: share your agent sessions.\[13\]
  - Copilot: the coding agent, CLI, app, or Actions.\[13\]
  - Mastra: agent orchestration.\[13\]
  - MongoDB: Atlas as the data layer.\[13\]
  - Sentry: agent traces.\[13\]
  - SerpApi: web search.\[13\]
  - .tech: deploy live on a claimed .tech domain.\[13\]
  - Temporal: durable workflows.\[13\]
  - Tiger Data: pgvector or Tiger MCP.\[13\]
- **My advice:** aim for the overall prize. Don't bolt on hosting.

## Friday MVP: BibLocal

**Five features**
1. Pick a photo folder and, optionally, a start-list CSV (bib, name, category).
2. Offline bib reading with RapidOCR on the CPU. Shrink each image to about 2,000 px on the long side and tile it so small bibs stay readable.
3. Validate: keep digit-only reads that are on the start list (or a length rule if there is no list). Below the confidence threshold, the tool abstains.
4. Write the results: keywords like "bib:247" and the runner's name. RAW files get an .xmp sidecar. JPEGs get keywords embedded with exiftool, because Lightroom ignores sidecars for JPEGs (Hypothesis from experience; K5 tests it). Also a CSV.
5. Review page: a local HTML grid of the "unsure" photos with a quick-fix box.

**Not in the MVP:** face recognition, cloud anything, galleries or sales, video, motorsport plates, accounts and payments, any GPU path.

**Test data**
- Roboflow Universe bib datasets, listed as CC BY 4.0.\[32\] Credit them.
- RBNR (217 images).\[33\] Its licence is unknown, so use it for testing only and do not redistribute it.
- 40 photos of your own: friends wearing printed bibs, with some occluded, angled or muddy, plus a 10-row start list.

**60-second demo script**
1. 0–10 s: "Race photographers spend hours typing bib numbers." Show a folder of 300 photos. Turn Wi-Fi off on camera.
2. 10–30 s: run BibLocal with the start list and show the progress bar and the elapsed time.
3. 30–45 s: open Lightroom (or digiKam), filter by keyword "bib:247", and show that runner's photos.
4. 45–55 s: honest failure. A runner's arm covers the bib. BibLocal says "not sure" and puts the photo in review. It does not guess.
5. 55–60 s: "Zero uploads. Zero cost. Open model you can swap."

## Kill tests (by Wednesday night)

1. **K1 accuracy:** 100 test photos, CPU only. Pass if the right bib is found in at least 70% of photos where a person can read it, and fewer than 3% are wrong after start-list filtering. Kill below 50%.
2. **K2 speed:** use the onnxruntime CPU package with the GPU hidden. Pass if the median is 2 s or less per 24 MP JPEG including the resize, so 1,000 photos take 35 minutes or less. Kill above 5 s.
3. **K3 chatbot head-to-head:** put the same 20 photos into free ChatGPT, Gemini and Claude. Record accuracy, minutes spent, and any upload cap you hit. Then ask each one to tag 2,000 files with keywords. BibLocal passes if the chatbots can't handle the volume or the file output.
   - If a chatbot's accuracy is more than 20 points higher, keep going anyway, but say so in the post.
4. **K4 metadata:** keywords written by BibLocal show up in Lightroom Classic, or in digiKam or darktable if you don't have Lightroom. Pass or fail.
5. **K5 demand ping:** post one question (not a promotion) on dgrin: "How do you tag bibs today?" Pass if 2 or more people reply by Friday. This is a soft test, so don't kill on it alone.

## Schedule (IST)

| Block | Hours | Work |
|---|---|---|
| Tue 13 Oct night | 2 | Python venv on D:, RapidOCR, K1 + K2 on 50 images |
| Wed 14 | 3 | K3, K4 setup; core OCR + tiling + digit filter |
| Thu 15 | 4 | Start-list match, abstain logic, CSV + exiftool/XMP writer, K4 |
| Fri 16 | 4 | Review HTML page, README, MIT licence, Windows build (PyInstaller) |
| Sat 17 | 3–4 | Post in communities (US morning is about 7–9 PM IST), fix bugs, record demo |
| Sun 18 | 3–4 | Write the DEV post and the first-user section; submit by 10 PM IST |

- **Hard deadline:** 19 Oct, 12:29 PM IST. Don't use the buffer.
- **If you have fewer hours:**
  - **About 8 h:** make it command-line only, with CSV + exiftool output and no review page.
  - **About 5 h:** CSV output only. Make the demo the Wi-Fi-off run.

## First-user plan

**Where to post**
1. **dgrin sports forum:** the existing bib-tagging thread proves the audience is there. Rules not verified, so read them first.
2. **Adobe Lightroom Community:** reply on the threads asking for a bib plugin (2019, 2024).\[14\]\[15\] Answer the question; don't spam.
3. **talkphotography.co.uk:** there is a bib-tagging thread.\[34\]\[35\] Read the forum's rules first.
4. **r/sportsphotography and r/AskPhotography:** I could not verify their rules. A third-party guide says r/photography restricts self-promotion and bans AI-written posts, so write the post yourself.\[36\]
5. **Your own network:** running-club friends, charity-run organisers, and anyone who photographs school or office sports days.

**Post template**
> I'm a developer and I built a free, open-source tool for a contest (DEV Hacktoberfest). It reads bib numbers in race photos on your own laptop, offline, and writes them as keywords Lightroom can filter. No upload, no account. It says "not sure" instead of guessing. Could you try it on an old event folder and tell me what broke? Link: [repo]. I used AI coding help to build it.

**Three questions to ask users**
1. Did it save you time on a real folder? How many minutes?
2. Would you pay for this? How much: one-time, or per event?
3. What should it do next?

**Be honest with yourself:** photographers rarely test a new tool within 48 hours. Ask them to run it on a past event folder. That needs no race this weekend.

## Write-up angle: why open innovation matters

1. **Data:** photos of the public, often including children, never leave the laptop. A cloud competitor's own page says it sends the full image to Gemini.
2. **Offline:** show the Wi-Fi-off run on 300 photos with the timer on screen.
3. **Cost per 1,000 photos:**
   - BibLocal: $0.
   - Manual tagging: $20 at 2¢ a photo, $50 at 5¢.
   - AWS Rekognition: $1.00 per 1,000 images. DetectText is a Group 2 API, priced at "Tier 1 of up to 1 million images per month at $0.001 per image" in AWS's November 2021 pricing announcement. I couldn't verify the rate for the London region.
   - Most of all, the photographer's own hours.
4. **Control:** swap PP-OCRv4 → v5 by changing one file and show the accuracy difference from K1. Fine-tuning on bib fonts is a next step.
5. **Consistency:** the same folder gives the same output on every run. Report the K3 chatbot comparison honestly.

## Caveats
- **The OCR may fail:** small, muddy or angled bibs may score low. The abstain-and-review design limits the damage, but K1 decides the go/no-go.
- **Installing is a hurdle:** non-technical photographers may struggle with Python. A Windows .exe via PyInstaller is the main risk on Friday.
- **Old evidence:** the pain posts are forum posts and some are old. I verified no Reddit posts. Competitor blog figures (for example "14 hours") are marketing, so I didn't use them as evidence.\[11\]
- **Employer fit:** consumer sports photography is far from IBM's products. Keep the project unpaid and open source. Disclose your AI help in the post and don't pitch a business.

## Appendix A: Score table (0–5; weights pain ×4, beats chatbot ×4, open essential ×3, hardware ×3, buildable ×3, users ×2, originality ×2, story ×2; max 115)

| Idea | Pain | Chatbot | Open | HW | Build | Users | Orig | Story | Total |
|---|---|---|---|---|---|---|---|---|---|
| BibLocal | 5 | 5 | 4 | 4 | 4 | 3 | 5 | 5 | **102** |
| MaskPaste | 4 | 5 | 5 | 4 | 4 | 3 | 2 | 4 | 93 |
| Critter Sieve | 4 | 5 | 4 | 3 | 4 | 4 | 3 | 3 | 89 |
| Bird burst culler | 4 | 5 | 4 | 3 | 2 | 3 | 1 | 3 | 77 |
| Offline interview transcriber | 3 | 3 | 4 | 3 | 4 | 3 | 1 | 3 | 71 |
| TTRPG session scribe | 3 | 3 | 4 | 2 | 3 | 4 | 1 | 3 | 67 |
| Local microstock keyworder | 3 | 3 | 3 | 2 | 3 | 3 | 2 | 2 | 62 |
| Youth jersey tagger | n/a | | | | | | | | killed (minors' data) |

**Six hats on the top 3**
- **White (facts):** BibLocal has OCR weights under Apache-2.0 and verified forum pain. MaskPaste and Critter Sieve both have crowded tool lists.
- **Red (user's reaction):** a photographer feels relief at getting a weekend back. A freelancer feels "nice, but I already use one."
- **Black (risks):** BibLocal: OCR accuracy and installing. MaskPaste: recall of 53–71%. Critter Sieve: overlap with Timelapse.
- **Yellow (value):** BibLocal turns hours into minutes at $0.
- **Green (twists):** later, add a burst-consensus step that spreads a confident read to neighbouring frames, marked as "suggested".
- **Blue (decision):** BibLocal, run as a go/no-go on K1 and K2.

**Blue Ocean grid against RaceTagger and TagMyRun**
- **Eliminate:** cloud, accounts, credits.
- **Reduce:** galleries, faces.
- **Raise:** privacy, offline use, start-list validation.
- **Create:** an open model you can swap, and a review flow that abstains first.

## Appendix B: Long list (35 ideas, one-line kill reasons)

**Photo and media**
- BibLocal: **finalist**.
- Youth jersey-number tagger: killed, minors' data.
- Bird burst culler: killed, Project Kestrel is already free, open and local.\[37\]
- Local microstock keyworder: killed, dozens of free cloud tools, and a vision-language model is too slow on CPU.
- Motorsport plate tagger: killed, TagOmatic and RaceTagger already exist.\[16\]\[22\]

**Audio and voice**
- TTRPG session scribe: killed, Dungeon Scribe, summarize-session-slop and CharGen exist, and summarizing a 4-hour session on CPU is slow.\[38\]\[39\]\[40\]
- Rehearsal take finder: killed, no evidence of pain.
- Offline interview transcriber: killed, Whisper apps are everywhere.
- Podcast ad-read finder: killed, weak evidence.
- Tradesperson voice job log: killed, phone dictation does 80% of it.

**Freelancer privacy**
- MaskPaste: **finalist**.
- Local invoice sorter: killed, it's the challenge's own example and Week 2 is saturated with it.\[41\]
- Scope-creep detector: killed, duplicates OuttaScope, HustleLedger and BriefBill.\[9\]\[42\]\[43\]
- NDA-safe glossary extractor: killed, CAT tools already do it.
- Contract clause diff: killed, legal-advice risk.

**Small sellers**
- Photo-to-listing writer: killed, the challenge example plus ListingLift, ListingCraft and DukaanWriter.\[44\]\[45\]\[46\]
- Review reply drafter: killed, a Week 2 duplicate and a chatbot does it.\[47\]
- Menu translator: killed, the challenge example.\[41\]
- Background remover: killed, free tools are everywhere.
- Catalog Fact Check: killed, a chatbot handles a single listing.

**Hobby groups**
- Critter Sieve: **finalist**.
- WhatsApp club newsletter: killed, a chatbot does it.
- Board-game rules Q&A: killed, a chatbot does it.
- Coin/stamp catalog reader: killed, weak evidence and hard recognition.
- Catch-photo fishing log: killed, weak evidence.

**Field and events**
- Finish-line video bib logger: killed, timing chips already exceed 99.8% detection (MYLAPS) and it's too big.\[48\]
- Volunteer sign-in sheet reader: killed, a chatbot does one page.
- Event lost-and-found matcher: killed, weak evidence.
- Nursery label reader: killed, too close to Touch Grass.
- Garden walkthrough: killed, it repeats your Week 1 entry.

**Creators**
- Subtitle Delivery QA: killed in round 1.
- B-roll CLIP search: killed, too close to PhotoProof.\[49\]
- Thumbnail legibility checker: killed, weak evidence.
- Sponsor-logo screen-time counter: killed, MyRun offers it.\[18\]
- Screenshot PII scrubber: merged into MaskPaste.

## Appendix C: Which creativity pass produced each finalist

**BibLocal**
- **Empathize:** forum complaints about tagging.
- **Analogy:** "Shazam for bibs" and an airport scanner that waves through only numbers on the start list.
- **Random stimulus:** "mud" led to abstain-first design, "ice" to ski-race bibs, "bicycle" to cycling plates.
- **PO "the data is illegal to upload":** photos of the public and of minors.
- **Blue Ocean grid.**

**MaskPaste**
- **Inversion:** "the free chatbot does it" became "make the chatbot safe to use".
- **SCAMPER Reverse:** the AI hides data instead of reading it.
- **Random stimulus:** "receipt" led to scrubbing receipt screenshots.

**Critter Sieve**
- **Concept fan:** "turn messy media into usable records".
- **PO "the user has no internet":** rural cameras.
- **Random stimulus:** "lighthouse" led to night-time IR frames.

**Inversion pass (how entries fail → design rule)**
- Needs a GPU → CPU-only models.
- A chatbot already does it → volume plus file output.
- Cloud-only → Wi-Fi-off demo.
- Thin wrapper → specialized model plus a deterministic check.
- Too big → five features.

**Lateral thinking:** the AI doesn't have to be an LLM, and the buyer doesn't have to be a business.

**Next action: tonight, install RapidOCR in a venv on D:, run it on CPU only on 50 bib photos, and record the hit rate (K1) and seconds per photo (K2).**

## Sources

1. <https://dgrin.com/discussion/194321/automatic-number-plate-recognition-for-photographers>
2. [How to Anonymize Your ChatGPT Prompts (Step by Step) · ONYRI Sanitize](https://onyri-sanitize.com/blog/how-to-anonymize-your-chatgpt-prompts)
3. [How to anonymize data before pasting it into ChatGPT, Claude & Gemini: Amaze](https://heyamaze.com/blog/anonymize-data-before-chatgpt-claude-gemini/)
4. [GitHub - Knowledgator/GLiNER.js: GLiNER inference in JavaScript · GitHub](https://github.com/Knowledgator/GLiNER.js)
5. [prvn-ramesh/gliner-small-v2.5-onnx · Hugging Face](https://huggingface.co/prvn-ramesh/gliner-small-v2.5-onnx)
6. [Google Gemini Data Privacy and Masking: What Happens to Your Prompts?](https://privacyscrubber.com/solutions/comparison/gemini-data-privacy/)
7. [GitHub - microsoft/MegaDetector: MegaDetector V6 — Microsoft AI for Good Lab's open-source model that detects animals, people, and vehicles in camera-trap images, filtering blanks to speed wildlife research.](https://github.com/microsoft/megadetector)
8. [Video camera trap analysis help](https://wildlabs.net/discussion/video-camera-trap-analysis-help)
9. [Hacktoberfest 2026 Challenge - DEV Community](https://dev.to/t/hf26challenge)
10. [RaceTagger vs TrackAction.AI: Which Race Photo Tagging Tool Is Right for You?](https://racetagger.cloud/blog/35-RaceTagger-vs-TrackAction-AI)
11. [Auto-Tag Race Photos: AI Bib Detection Guide for Photographers](https://racetagger.cloud/blog/32-Tag-Race-Photos-Automatically)
12. [Hacktoberfest Open-Source AI Challenge: Week 2 Contest Rules — DEV Community](https://dev.to/page/hacktoberfest-week2-2026-10-12-contest-rules)
13. [Hacktoberfest Open-Source AI Challenge: Week 2 - DEV Challenge — DEV Community](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)
14. [OCR and Facial Recognition for Sports Photography | Community](https://community.adobe.com/questions-675/ocr-and-facial-recognition-for-sports-photography-939641)
15. [identify particpant s numbers jersey 975061](https://community.adobe.com/questions-675/identify-particpant-s-numbers-jersey-975061)
16. [Best Race Photo Tagging Software 2026: 8 Tools Honestly Compared](https://racetagger.cloud/blog/30-Best-Race-Photo-Tagging-Software-2026)
17. [FindMe Photo — Event & Wedding Photo Delivery for Photographers](https://findme.photo/blog/best-photo-delivery-software-sports-photographers-2026)
18. [MyRun - Automated Photo Tagging for Sports Event Galleries (Bib & Selfie/Face Recognition)](https://myrun.eu/)
19. [Bib Tagging Smugmug - CapCity Sports Photography](https://www.capcitysportsmedia.com/Bib-Tagging-Smugmug)
20. [FlashFrame](https://www.flashframe.io/blog/the-cutting-edge-of-race-photo-tagging-software/)
21. [Race Photo Tagging - BIB Number Data Entry](https://www.bibnumberentry.com/race-photo-tagging/)
22. [TagOmatic LITE v5.0 - Free AI Photo Tagging](https://www.tagomatic.co.uk/)
23. [MT and Confidentiality Agreements (Machine Translation (MT))](https://www.proz.com/forum/machine_translation_mt/207130-mt_and_confidentiality_agreements-page2.html)
24. [Is ChatGPT Private? A Lawyer's Guide to Securing Confidential Client Data - Spellbook](https://spellbook.com/learn/is-chatgpt-private)
25. [WARNING: Never share these 5 things with ChatGPT, Gemini and other AI tools](https://pulse.ng/story/things-you-should-never-share-with-chatgpt-gemini-ai-tools-2026100612131067931)
26. [MegaDetector on Edge Devices ??](https://wildlabs.net/en/discussion/megadetector-edge-devices)
27. [MegaDetector on The Inventory](https://wildlabs.net/node/6445)
28. [GitHub - BobLd/RapidOcrNet: Cross-platform OCR processing using PaddleOCR ONNX models (v4 / v5 / v6). Based on RapidAI's RapidOCR · GitHub](https://github.com/BobLd/RapidOcrNet)
29. [GitHub - RapidAI/RapidOCR: 📄 Awesome OCR multiple programing languages toolkits based on ONNX Runtime, OpenVINO, MNN, PaddlePaddle, TensorRT and PyTorch.](https://github.com/rapidai/rapidocr)
30. [nvidia/gliner-PII · Hugging Face](https://huggingface.co/nvidia/gliner-PII)
31. [Releases · RapidAI/RapidOCR](https://github.com/RapidAI/RapidOCR/releases)
32. [Bib Number Object Detection Model by Veloezdach](https://universe.roboflow.com/veloezdach/bib-number-qli1t)
33. [GitHub - ericBayless/bib-detector: Object detection project to identify race bib numbers for order of finish · GitHub](https://github.com/ericBayless/bib-detector)
34. [Automatic tagging of cars and bikes](https://www.talkphotography.co.uk/threads/automatic-tagging-of-cars-and-bikes.771092/)
35. [automatic event/race bib number tagging](https://www.talkphotography.co.uk/threads/automatic-event-race-bib-number-tagging.758881/)
36. [Reddit for Photographers: The Ultimate Guide (2026)](https://trovatten.com/blog/reddit)
37. [Project Kestrel](https://projectkestrel.org/)
38. [GitHub - Shiroko7/summarize-session-slop: Turns D&D session recordings into structured notes - Whisper plus a local Ollama model, fully offline · GitHub](https://github.com/Shiroko7/summarize-session-slop)
39. [Best DnD Session Summary Tool Options for Busy DMs](https://char-gen.com/blogs/best-dnd-session-summary-tool-options-2026)
40. [initial release](https://fynflood.itch.io/dungeon-scribe/devlog/999745/initial-release)
41. [Join the Hacktoberfest Open-Source AI Challenge: Side Hustle! \$2,550 in Prizes Across 18 Winners. - DEV Community](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-side-hustle-2550-in-prizes-across-18-winners-55ba)
42. [HustleLedger AI — Privacy-First Financial Sentinel & Scope Defender for Side Hustlers - DEV Community](https://dev.to/dien/hustleledger-ai-privacy-first-financial-sentinel-scope-defender-for-side-hustlers-3a24)
43. [OuttaScope: The Client Scope Creep & Unpaid Revision Shield for Freelancers - DEV Community](https://dev.to/sachin-alt/outtascope-the-client-scope-creep-unpaid-revision-shield-for-freelancers-2fpc)
44. [ListingLift: a local AI listing writer for resellers (Hacktoberfest HF26 Week 2 — Side Hustle) - DEV Community](https://dev.to/tharun634/listinglift-a-local-ai-listing-writer-for-resellers-hacktoberfest-hf26-week-2-side-hustle-5b1o)
45. [DukaanWriter: WhatsApp-Ready Product Listings in English and Hindi - DEV Community](https://dev.to/happybeingpranjal/dukaanwriter-whatsapp-ready-product-listings-in-english-and-hindi-generated-on-your-own-laptop-2cbe)
46. [ListingCraft AI: Turn Product Photos into High-Converting Etsy & eBay Listings in Seconds - DEV Community](https://dev.to/hao610/listingcraft-ai-turn-product-photos-into-high-converting-etsy-ebay-listings-in-seconds-45el)
47. [Week 2 hacktoberfest challenge post - DEV Community](https://dev.to/nayeemul_islam_220588ffa5/week-3-hacktoberfest-challenge-post-1hfg)
48. [Timing System for Running](https://mylaps.com/active-sports/sports/running/)
49. [Photo Proof 📸 - DEV Community](https://dev.to/aimanfazal/photo-proof-2le1)
