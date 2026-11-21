"""Anka's settings – everything you may want to change is here."""
import os
import re
import sys


NAME = "Anka"
BRAIN = "hf.co/unsloth/Qwen3.5-4B-GGUF:UD-Q3_K_XL"  # 3-bit Qwen3.5 4B: ~30% faster than "qwen3.5:4b", about as good
if "--brain" in sys.argv[:-1]:   # try another brain without editing:  python run_anka.py --simulate --brain qwen3.5:2b
    BRAIN = sys.argv[sys.argv.index("--brain") + 1]
# A lighter brain if the Mac gets too slow (it can NOT see pictures – Anka then only gets the face count):
# BRAIN = "qwen3:4b-instruct-2507-q4_K_M"
# ---------- Cloud brain (optional) ----------
# A faster, smarter brain on the internet (Google Gemini). The local brain above is the reserve:
# it takes over by itself if there is no key, no internet, or the cloud says no.
# Put your key (from aistudio.google.com) in a file called cloud_key.txt next to run_anka.py,
# or set GEMINI_API_KEY. NOTE: the camera pictures and what you say are then sent to Google.
CLOUD_BRAIN = "gemini-3.5-flash-lite"   # 2026-11-15 test (same price class as gemini-3-flash-preview, which is deprecated; 3.6 was dearer and doubles 2027-01-01; gemini-2.5-flash answered 404). (was gemini-3.5-flash-lite) or "gemini-3.8-flash" (smarter, costs more). "" = never use the cloud
CLOUD_API = "google"   # "google" = Google's own Gemini API (knows picture sharpness and shows caching)
                       # "openai" = the OpenAI-compatible way in (CLOUD_URL – any OpenAI-style API works)
CLOUD_GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse"
CLOUD_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"  # (for CLOUD_API = "openai")
CLOUD_KEY_FILE = "cloud_key.txt"
CLOUD_THINKING = "minimal"  # how long the cloud brain thinks before answering: minimal / low / medium
# ASK THE WISER BRAIN WHEN STUCK (2026-11-09; replaces "think harder", which didn't help – the fast day brain stayed inside
# "kick it better" however long it thought, while the night brain found "carry it in my beak"). When his body has failed at
# something, or something surprised him a lot (= a miss), STUCK_AFTER thoughts in a row, his NEXT thought goes to the wiser
# (night) brain. (2026-11-10: one big surprise alone no longer counts as stuck.)
# Only a better brain for that moment – nothing about what to think.
WISE_WHEN_STUCK = "--no-wise" not in sys.argv
STUCK_AFTER = 2
CLOUD_PICTURE_DETAIL = "low"   # how sharp the camera picture is for the cloud brain: "low" ≈ 280 tokens per picture,
                               # "" = Gemini 3's default ≈ 1,120 (his pictures are only 320×240 anyway)
CLOUD_CACHED_SHARE = 0.1      # Gemini bills the part of a question it remembers from the last one (the same start)
                               # at about a tenth of the normal price
CLOUD_TIMEOUT = 15          # seconds without an answer before the local brain takes over
NIGHT_CLOUD_BRAIN = "gemini-4-argon"   # the night (looking back on the day, tidying memories, dreaming) uses Google's
                                       # deepest brain – only a few questions per night. "" = the normal cloud brain
NIGHT_THINKING = "low"      # how long the night brain thinks first: low / medium / high (higher = deeper, slower, dearer)
NIGHT_TIMEOUT = 120         # seconds the night brain may take per answer (it thinks before it answers)
CLOUD_RETRY_AFTER = 60      # seconds to wait before trying the cloud again after a problem
# GOOGLE IS BUSY (2026-11-16): an answer 429/503 means Google has no room for this model right now (it happened for
# ~20 min with flash-lite while the own limits were used < 1 %). Then another cloud model takes over for a while -
# the reserve brain on the Mac can't run all of Anka - and if that one is busy too, the cloud is tried again soon.
CLOUD_FALLBACK = "gemini-3-flash-preview"   # "" = no other cloud model
CLOUD_BUSY_SWITCH = 300     # seconds the other cloud model answers before the normal one is tried again
CLOUD_BUSY_RETRY = 15       # seconds to wait (with the reserve brain) when both cloud models are busy
if "--cloud" in sys.argv[:-1]:   # python run_anka.py --cloud gemini-3.8-flash
    CLOUD_BRAIN = sys.argv[sys.argv.index("--cloud") + 1]
if "--local" in sys.argv or "--brain" in sys.argv[:-1]:  # only the brain on this Mac
    CLOUD_BRAIN = ""


def _cloud_key():
    key = os.environ.get("CLOUD_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CLOUD_KEY_FILE)
    if not key and os.path.exists(path):
        with open(path) as f:
            key = f.read().strip()
    return key


MUJOCO = "--simulate" in sys.argv and "--mujoco" in sys.argv   # the Microduck in Pollen's MuJoCo simulator (python run_anka.py --simulate --mujoco)
BODY_CLOUD_BRAIN = "gemini-3.5-flash-lite"   # (2026-11-15 test; was gemini-3-flash-preview, before that gemini-3.8-flash) the body test with real senses uses a smarter cloud brain (better at space
                                        # and pictures, costs more). "" = use CLOUD_BRAIN as usual
if BODY_CLOUD_BRAIN and CLOUD_BRAIN and "--simulate" in sys.argv and ("--body" in sys.argv or MUJOCO) \
        and "--easy" not in sys.argv and "--cloud" not in sys.argv:
    CLOUD_BRAIN = BODY_CLOUD_BRAIN
CLOUD_KEY = _cloud_key() if CLOUD_BRAIN else ""
# OPENROUTER TEST (2026-11-20): --openrouter runs ALL of Anka (day, wise and night brain) on a model at
# openrouter.ai instead of Gemini - to see if a free model can do the whole job. Key: app/openrouter.key (never on
# GitHub - *.key is ignored) or the env OPENROUTER_API_KEY. Free models (":free") allow 20 requests a minute and 50 a day
# (1,000 a day once $10 of credits have ever been bought); a test day uses 50-150 requests.
OPENROUTER = "--openrouter" in sys.argv or "--qwen27b" in sys.argv or "--gemma27b" in sys.argv or "--gemma4" in sys.argv
OPENROUTER_MODELS = {"nemotron": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",   # 30B MoE (3B active), pictures
                     "qwen27b": "qwen/qwen3.8-27b",           # 27B DENSE, PAID ($0.40 / $3.00 per 1M) - 2026-11-20: free version gone
                     "gemma27b": "google/gemma-3-27b-it:free",  # 27B DENSE (2026-11-20: also paid only now)
                     "gemma4": "google/gemma-4-31b-it:free"}    # 31B DENSE, pictures, thinking on/off, Apache 2.0 open
                                                                # weights (Hugging Face / Ollama; needs ~24 GB to run locally)
OPENROUTER_MODEL = OPENROUTER_MODELS["qwen27b" if "--qwen27b" in sys.argv else "gemma27b" if "--gemma27b" in sys.argv
                                     else "gemma4" if "--gemma4" in sys.argv else "nemotron"]
if OPENROUTER:
    def _or_key():
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openrouter.key")
        return os.environ.get("OPENROUTER_API_KEY") or (open(p).read().strip() if os.path.exists(p) else "")
    CLOUD_API, CLOUD_URL = "openai", "https://openrouter.ai/api/v1/chat/completions"
    CLOUD_BRAIN = BODY_CLOUD_BRAIN = NIGHT_CLOUD_BRAIN = OPENROUTER_MODEL
    CLOUD_FALLBACK = ""                     # no Gemini at all in this test
    CLOUD_TIMEOUT = 40                      # (a free, thinking model can be slower to start)
    CLOUD_KEY = _or_key()
# GEMMA 4 VIA GOOGLE (2026-11-20): --gemma4-google runs ALL of Anka on Google's open Gemma 4 31B (dense, pictures,
# Apache 2.0 weights) through the SAME Google key and API as Gemini - no OpenRouter queue or 50-a-day limit. Listed as
# free on the Gemini API (with the free tier's own rate limits).
if "--gemma4-google" in sys.argv:
    CLOUD_BRAIN = BODY_CLOUD_BRAIN = NIGHT_CLOUD_BRAIN = "gemma-4-31b-it"
    CLOUD_FALLBACK = ""
    CLOUD_TIMEOUT = 40
BRAIN_NAME = CLOUD_BRAIN if CLOUD_KEY else BRAIN   # (shown in logs)

BODY = ("--simulate" in sys.argv and "--body" in sys.argv) or MUJOCO   # the virtual 2D body (python run_anka.py --simulate --body)
HAS_BODY = BODY             # set True when the Microduck is connected – then Anka knows it can move
SHOW_ROOM = True            # with the virtual body: show the room from above in a window while he walks around
BODY_SENSES = "easy" if "--easy" in sys.argv else "real"
# "real" = the virtual body gets only the senses the Microduck has: a camera picture from his own eyes, the 8×8 depth
#          sensor, bumps and falls, imperfect legs, a head he can turn, a battery. No map, no list of where things are.
# "easy" = the first version: he is told exactly where everything is, and his legs find the way around furniture.
HEAR_DIRECTION = True       # can he hear which direction a voice comes from? (not sure the Microduck can – then False)

# ---------- Saving resources (important on an 8 GB Mac) ----------
ONE_AT_A_TIME = True        # only ONE heavy AI works at a time: the brain, the ears or the voice
UNLOAD_AFTER = 120          # seconds: ears and voice are unloaded when unused this long (0 = never)
SAVE_EVERY = 15             # seconds: changes to the memory are saved to disk at most this often (in the background)
CONTEXT_SIZE = 5120 if ("--body" in sys.argv or "--mujoco" in sys.argv) else 3072   # how much text the LOCAL brain holds at once (smaller = less
#   memory). 2026-11-08: with the body the questions are 3,100-3,800 tokens, so 3072 made the reserve brain fail every time.

# ---------- How the brain picks words ----------
TEMP_REPLY = 0.7            # when Anka answers you (lower = steadier, fewer made-up things)
TEMP_THOUGHT = 0.9          # when Anka thinks by itself (lower gave more repeated thoughts)
TOP_P = 0.8
TOP_K = 20
REPEAT_PENALTY = 1.15

# ---------- Eyes ----------
CAMERA = 1                  # the camera to try first (Anka finds another one if it doesn't work)
EYE_CHECKS_PER_SECOND = 5   # how often the face/motion sensor looks (and the camera window updates)
SHOW_CAMERA = True          # False = no camera window
CAMERA_WINDOW_SIZE = 0.5    # size of the camera window: 1 = full size, 0.5 = half
SHOW_FACE = True            # True = Anka's face is drawn next to the camera picture
FLIP_GAZE = False           # True if Anka's eyes look the wrong way when you move sideways
CLOUD_PICTURE_WIDTH = 768   # sharper picture for the cloud brain (sees small things in hands better; a bit more tokens)
PICTURE_WIDTH = 448         # size of the picture the brain gets (smaller = faster)
LOOK_IN_THOUGHTS = "sometimes"  # when Anka thinks: "sometimes" = looks at the picture when something happened
                                # or every LOOK_EVERY seconds, True = every thought (slow), False = never
LOOK_ALWAYS_WITH_CLOUD = True  # with the cloud brain: the brain gets a fresh picture in EVERY thought and answer
                            # (no extra requests – the picture rides along. The local reserve uses the rules above)
LOOK_EVERY = 60             # seconds between close looks when nothing special happens
RECOGNISE_FACES = True      # knows WHO is in front of him (Alex, Robin...) – teach a face once with:
                            #   python run_anka.py --learn-face Robin      (see all: --faces, forget one: --forget-face Robin)
                            # The face data stays in known_faces.npz on this Mac. What he does with it is up to the brain.
FACE_MATCH = 0.40           # how alike a face must be to count as someone he knows (0.36 = loose, 0.45 = strict)
LEARN_FACES_MYSELF = True   # he learns by himself too: when someone is introduced ("Anka, this is Anna") his brain can
                            # decide to remember that face – and faces he knows well he slowly learns better
                            # (new light, glasses, hair). False = only --learn-face teaches him
FACE_SURE = 0.55            # he only learns more about a face when he is at least this sure who it is
MAX_FACE_PICTURES = 40      # at most this many saved looks per person (the most alike ones are let go first)
AWAY_AFTER = 30             # seconds out of view before Anka counts you as gone (and notices you came back)

# ---------- Voice ----------
VOICE_ENGINE = "kokoro"     # "kokoro" = Kokoro's voices and your own mixes of them (light and fast)
                            # "clone"  = Pocket TTS: speaks with a voice copied from a short recording
                            #            (needs: pip install pocket-tts, and a Hugging Face login – see below)
                            # "mac"    = the Mac's own voice
CLONE_VOICE = "my_voice.wav"  # for "clone": a clean 5–10 second recording next to run_anka.py.
                            # Record one with:  python run_anka.py --record-voice
                            # Only clone your own voice, or a voice whose owner has said yes.
KOKORO_MODEL = "kokoro-v1.0.onnx"   # these two files must be in the same folder as run_anka.py
KOKORO_VOICES = "voices-v1.0.bin"
KOKORO_VOICE = "am_liam*0.7 + af_sky*0.3"  # one voice, or your own mix of several, e.g. "af_heart*0.6 + af_nicole*0.4"
                            # Voices: af_ alloy aoede bella heart jessica kore nicole nova river sarah sky
                            #         am_ adam echo eric fenrir liam michael onyx puck santa
                            #         bf_ alice emma isabella lily   bm_ daniel fable george lewis
                            # (a = American, b = British, f = female, m = male)
                            # Try one without starting Anka:  python run_anka.py --voice-test "af_bella*0.5 + am_puck*0.5" 1.2
KOKORO_SPEED = 1.0          # 1.0 = normal, 1.2 = faster
MOOD_VOICE = True           # the voice follows the mood: happy = a bit faster and brighter, sad = slower and
                            # lower, nervous = a little shaky
VOICE_PITCH = 1.4           # 1.0 = normal, 1.15 = higher and smaller, 0.9 = deeper (the speed stays the same)
DUCK_VOICE = 0.75           # 0 = a normal voice, 0.5 = a bit duck-like, 1 = very duck-like (nasal, buzzy, raspy)
DUCK_BUZZ = 80              # the duck's flutter, times per second: 50 = slow quacky wobble, 110 = fast buzz
DUCK_NOSE = 1800            # where the nasal honk sits (Hz): 1100 = deep honk, 1600 = duck, 2300 = squeaky
                            # Try:  python run_anka.py --voice-test "am_puck" 1.35 0.8 75 1600
                            #       (voice, pitch, duck, buzz, nose)
MAC_VOICE = "Samantha"      # the Mac voice used if Kokoro doesn't work

# ---------- Ears ----------
WHISPER_MODEL = "small.en"  # speech to text: "base.en" (fast) / "small.en" / "medium.en" (hears best)
MICROPHONE = None           # None = the Mac's default microphone (but the MacBook's own before an iPhone's),
                            # or part of a name, e.g. "MacBook" or "AirPods". See all: python run_anka.py --microphones
LISTEN_MAX = 15             # longest time Anka listens after you press ENTER
WAIT_FOR_SPEECH = 6         # if you haven't started talking after this many seconds, Anka stops listening
SILENCE_END = 0.8           # this many seconds of silence means you have finished talking
HEAR_WITH_CLOUD = True      # with the cloud brain: it LISTENS to your voice itself and answers in the same go
                            # (hears names and HOW you say things). Whisper is the reserve when the cloud is away
UNSURE_HEARING = -0.7       # below this score the ears count as unsure – Anka is told he may have misheard
WHISPER_BEAM = 1            # 1 = fast (fine for short sentences), 5 = tries 5 guesses per word (slower, a bit more exact)
HANDS_FREE = False          # False = press ENTER to talk to him (as now).
                            # "always" = he hears everything said in the room, no ENTER needed (also the TV...)
                            # "name"   = he only reacts when someone says his name ("Anka, what do you see?")
                            # ENTER keeps working in every mode.
NAME_SOUNDS = r"\b(anka|anker|anca|anke|anchor|unka|onka)\b"  # what "Anka" may sound like to the ears
FOLLOW_UP_SECONDS = 20      # with "name": right after you two talked, you can go on without saying his name

# ---------- Thinking ----------
TALK_ON_ITS_OWN = True      # False = Anka only talks when you talk to it
THINK_EVERY = (8, 16)       # seconds between quiet thoughts: a new random time between these two every time,
                            # so his thinking has a natural, uneven rhythm. (Anka also thinks at once when something happens)
THINK_EVERY_ALONE = 25      # seconds between thoughts when nobody is in view (fewer cloud questions, less going in circles)
THINK_EVERY_MOVING = (4, 6)  # with a body: while he is on the move (his body did something in the last MOVING_FOR
MOVING_FOR = 30              # seconds) he thinks this often – exploring or on an errand. Otherwise the times above
NAP_WHEN_ALONE = True       # nobody around for NAP_AFTER seconds -> Anka naps: sleepy face, no thinking, no cloud use.
                            # He wakes up when someone comes into view or talks to him.
                            # (With a body you may want False – then he stays awake, and later can go exploring)
NAP_AFTER = 600             # seconds with nobody in view (and nobody talking) before he naps (600 = 10 minutes)
REST_MAX = 60               # seconds: when nothing happens and thoughts go in circles, Anka rests up to this long
GOALS_EVERY = 5             # Anka thinks about its goals every 5th thought
ONE_STEP_THOUGHTS = "cloud" # True = thought, feeling and "do I want to say something?" in ONE trip to the brain
                            # (about twice as fast). False = two trips: think first, then decide calmly about speaking
                            # "cloud" = one trip when the cloud brain thinks (it's smart enough, and it halves the
                            # questions sent to Google), two trips when the small brain on this Mac thinks
CHAIN_OF_THOUGHTS = 3       # a thought on the same subject still counts as NEW if it adds something (a chain of
                            # thoughts) – up to this many in a row. Then he has to move on.
THOUGHT_MEMORY = 8          # how many recent thoughts are compared to spot repeats
# Working memory – between a goldfish and an elephant. Only what Anka keeps "in mind" while thinking;
# the long-term memory (facts, diary, dreams) is never affected.
MEMORIES_TO_MIND = 3        # when alone: this many random memories "pop up" each thought (0 = off)
THOUGHTS_IN_MIND = 2        # how many of his latest thoughts he sees (goldfish = 1, elephant = 4+)
THOUGHTS_FADE = 120         # seconds: older thoughts fade from his mind
TALK_IN_THOUGHTS = 3        # how many messages of your conversation he keeps in mind while thinking
TALK_FADES = 300            # seconds after you last spoke, the conversation fades from his thoughts
CONVERSATION_PAUSE = 10     # Anka doesn't think while you talk – it waits this long after the last line
MIN_PAUSE = 10              # safety limit: at least this many seconds between Anka's own lines
SHORT_OUTPUT = True         # True = short lines in the terminal (False = show everything, good for debugging)

# Drives: Anka's inner needs (0 = none, 1 = very strong). They grow by themselves this much per minute
# (slower and slower towards 1). The brain decides itself when they go down.
DRIFT = {
    "curiosity": 0.20,
    "boredom": 0.20,
    "loneliness": 0.15,
}
# Emotions: how Anka feels (0 = not at all, 1 = very). The brain sets them; by themselves they slowly
# return to a resting level: (resting level, how much of the way back per minute)
RESTING = {
    "happiness": (0.5, 0.10),
    "affection": (0.4, 0.005),   # fades very slowly – over days
    "nervousness": (0.1, 0.15),  # calms down fairly fast
    "playfulness": (0.4, 0.08),
}
FEELING_STEP = 30           # seconds: the needs grow (and are shown) this often
SHOW_FEELINGS = True
FEELING_SPEED = 1.0         # 1 = normal. E.g. 5 for testing – the needs then grow 5 times faster
STRONG = 0.7                # a need this strong is described to the brain as HIGH
# FEELINGS THAT OUTLAST THE EVENT (2026-11-08): a big jump in a feeling (e.g. scared by a shout) leaves an
# after-feeling, like adrenaline in an animal: the brain can raise or lower the feeling as it likes, but it can
# only fade back towards normal at this pace (half the way every ECHO_HALF_LIFE seconds). He is told it is still
# there and where it came from. What he does about it is his own choice. False = as before (feelings snap back).
FEELING_ECHO = "--no-echo" not in sys.argv   # (--no-echo = switch it off for one run, to compare)
# HIS INNER URGE (2026-11-15): what his feelings make him WANT, told to the thinking brain as a fact (never an order).
#   "local" = the FEELING LAYER: a small model on this Mac that only sees his feelings, never the room (anka/urge_layer.py)
#   "same"  = the thinking brain writes an URGE line first in the same answer (it sees the room too - the room took over)
#   "off"   = no urge.   For one run: --urge local / --urge same / --urge off  (--no-urge = off)
URGE_MODE = "off"     # (2026-11-15 evening: the local layer gave generic, repeated wishes - off until improved)
if "--urge" in sys.argv[:-1]:
    URGE_MODE = sys.argv[sys.argv.index("--urge") + 1]
if "--no-urge" in sys.argv:
    URGE_MODE = "off"
URGE_MODEL = "gemma3:1b"    # chosen in test A0 (tools/urge_models_test.py): 0.9 GB, 0.3 s, steady and sensible
URGE_EVERY = 20             # seconds between two wishes (and at once when a feeling jumps by URGE_JUMP)
URGE_JUMP = 0.2
INNER_URGE = URGE_MODE == "same"   # (the URGE line in the thought itself)
ECHO_MIN_JUMP = 0.3         # a jump this big (0-1) in one go leaves an after-feeling
ECHO_HALF_LIFE = {"nervousness": 120, "happiness": 60, "playfulness": 90}   # seconds (affection fades slowly anyway;
#   happiness shorter: after a sorry he may be glad again fairly soon – while the fear still lingers)
ECHO_SHOW = 600             # seconds: how long he is told about the moment (also after the feeling itself has faded)
# B1 EXPECTATION AND SURPRISE (2026-11-08): with every body action he says what he thinks will happen (EXPECT);
# his next thought is shown what he expected and what his body reported, and he rates how surprised he is (SURPRISE).
# A big surprise goes into his diary (and so to the night's looking back). He decides what it means.
EXPECT = "--no-expect" not in sys.argv     # (--no-expect = off for one run, to compare)
SURPRISE_DIARY = 0.6       # a surprise this big (0-1) becomes a diary moment
FAMILIAR_AFTER = 60         # seconds: things that stayed the same this long count as "nothing new"
NEW_THING_AFTER = 120       # seconds: a thing counts as "just appeared" if Anka hasn't seen it for this long
MAX_GOALS = 3

# ---------- Talking ----------
CONVERSATION_MEMORY = 6     # how many messages of your conversation Anka keeps in mind (fewer = faster)
OWN_LINES_MEMORY = 6        # how many of its own lines Anka keeps in mind
MAX_SENTENCES = 2           # how many sentences Anka may say at a time
MAX_WORDS = 25              # and at most this many words in total (whole sentences are kept when possible)
SAME_MEANING = 0.87         # 0–1: how close in MEANING two lines may be before the new one counts as a repeat
TOO_SIMILAR = 0.6           # 0–1: how similar in WORDS an answer may be to an old one before it is redone

# ---------- Memory ----------
MEMORY_AI = "nomic-embed-text"  # searches the memory by meaning
MEMORIES_PER_QUESTION = 4   # how many relevant memories the brain sees each time
# B5 INTEGRATED MEMORY (2026-11-09): only 10-18 % of the memories shown in a day were different ones (the same few came
# back thought after thought), B1's surprise lines filled 65-97 % of the slots, and memories from earlier days almost
# never came up. So: memories shown in his last few questions count a bit less, at most one surprise line per question,
# one slot is kept for the best memory from an EARLIER day (if one fits), and the alone pop-ups follow his last thought.
# IDEAS TO TRY (2026-11-09): at night he may also write up to IDEAS_PER_NIGHT things he could TRY next time (untested,
# clearly marked). By day he sees them when he decides; whether he tries one is his choice. The next night, ideas his body
# tried become lessons (or are dropped), untried ones may stay (at most MAX_IDEAS). Thinking -> testing -> learning.
IDEAS = "--no-ideas" not in sys.argv   # (--no-ideas = off for one run, to compare)
IDEAS_PER_NIGHT = 2
MAX_IDEAS = 3
HABITUATION = True             # 2026-11-09: ONE general principle instead of special rules – a memory that just came up
                               # feels less new and pulls a little weaker for a while (like getting used to something),
                               # whatever kind it is. Replaces the flat penalty + the caps on surprise and goal lines.
HABIT_STRENGTH = 0.20          # how much weaker a memory pulls right after it came up once (similarity is ~0.5-0.9)
HABIT_FADE = 0.7               # after each question the "used to it" feeling keeps this share (0.7 = mostly gone after ~6)
MEMORY_REPEAT_PENALTY = 0.10   # a memory he was shown in his last few questions counts this much less (0 = off)  (only when HABITUATION is False)
MEMORY_RECENT = 8              # ...the memories of this many latest questions count as "recently shown"
# MEMORY STRENGTH (2026-11-18): one principle for the long run - what MATTERS gets stronger, what is never used fades
# slowly. Every diary line and conversation has a strength: at first from how much it moved him (feel), a surprise,
# a "first time" or a picture; it grows a little each day it comes up in his thoughts, and halves every
# MEMORY_HALF_DAYS days. The search no longer looks ONLY at the latest lines: strong old memories still come up, weak
# old ones fade out; and when the memory is full the WEAKEST old line goes, not the oldest. (--no-memory-strength = off)
MEMORY_STRENGTH = "--no-memory-strength" not in sys.argv
MEMORY_HALF_DAYS = 7.0         # days: an unused memory's strength halves this fast
MEMORY_STRENGTH_BONUS = 0.06   # search: at most this much extra pull for a strong memory (similarity is ~0.5-0.9)
MEMORY_RECALL_BOOST = 0.3      # how much a memory gains (once a day) when it comes up in his thoughts
MEMORY_OLD_MIN = 0.5           # an older memory (outside the latest SEARCH_* lines) is searched while it is this strong
# FAMILIARITY (2026-11-18, memory item 3 part 3): over days he gets to know things and people - a fact for the brain,
# not a rule: "how well you know what is here: the guitar - very familiar (seen on 6 days); the sock - new to you".
# What that means (curious, bored, glad to see it) is his own. (--no-familiarity = off)
# RESTLESSNESS (2026-11-18, a drive - like hunger, not a rule): the longer his body stays still and nothing new happens
# (no move, nothing new seen, nobody talking), the more restless his legs feel - told as a body feeling, and his
# boredom can't sink below it. Moving, something new or someone talking calms it. What he does about it is his own
# (he may still sit and wait for Alex). Run 11-18: alone days 2-3 he sat still 60-100 % of the time, missing Alex,
# with nothing pulling the other way. (--no-restless = off; the battery/energy half waits for the real duck.)
LAST_WORDS_FOR = 120           # seconds: when he is alone, the human's last words are in his thoughts this long (was 1800)
RESTLESSNESS = "--no-restless" not in sys.argv
RESTLESS_AFTER = 60            # seconds of stillness before he starts to feel it
RESTLESS_FULL = 180            # seconds more until it is as strong as it gets
RESTLESS_WALK_ONLY = "--restless-any-move" not in sys.argv   # 2026-11-18: only REAL moving (walk, explore, kick, carry,
                               # tap ...) counts as being active - before, a small turn of the head reset it, so it hardly
                               # ever fired (0-11 % of thoughts). --restless-any-move = the old way.
# 2026-11-18: THREE things against standing still - each with its own switch
TAP_SKILL = "--no-tap" not in sys.argv     # (1) the 2D body can TAP a thing with its beak ("tap the guitar") and hears
                               # what happens - the real Microduck can peck too. Found: his longest still stretches (up to
                               # 274 s) were at the guitar, wanting to touch the strings with no move for it.
CURIOSITY = "--no-curiosity" not in sys.argv   # (2a) when nothing new has happened for a while, he is told which things
                               # he knows about in the room he hasn't been close to TODAY (what he notices - never an order)
AWAY_SPOT_FACT = "--no-spot-fact" not in sys.argv    # 2026-11-19 (the author: "how a human brain works"): while the human
                               # is away, a walk's body report also says how far he now is from the spot where he was when
                               # they left ("you are now about 2.5 m from where you were when Alex left, 13 min ago") - like
                               # knowing roughly where you are compared with where you stood. Found in "staylong": he walked
                               # to the window and didn't notice he had left the spot he promised to stay in.
AWAY_RECALL = "--no-away-recall" not in sys.argv      # ... and when he answers the human, he is told what his body did
                               # while they were away (like thinking back before you answer "what did you do?") - in
                               # "staylong" he said "I stayed the whole time" after walking 2.5 m away.
# 2026-11-20 prompt review, step 1: PROMPT_TIDY removes things said twice and things that were wrong in what we send:
# feelings as words AND numbers in a thought (only numbers now), the self-image twice in a thought, "You have no map"
# (he does get a mental map + floor plan), "always answer the human first" in a PRIVATE thought, "IMPORTANT - you just
# woke up" when the human has already talked to him, and "first time ever" for a thing he already knows where it is.
PROMPT_TIDY = "--no-prompt-tidy" not in sys.argv
# 2026-11-20 prompt step 2: a thought's prompt in clear sections (RIGHT NOW / YOUR MIND / PEOPLE AND YOUR MEMORIES /
# WHAT JUST HAPPENED / YOUR ANSWER) with the same facts, plus one new fact while the human is here: the last thing they
# said to him and what he answered (< 5 min). On by default; old order with --no-prompt-sections (condition "nosections").
PROMPT_SECTIONS = "--no-prompt-sections" not in sys.argv
# 2026-11-20 prompt steps 3-6 (only with PROMPT_SECTIONS, each can be switched off on its own):
THOUGHT_GOALS = "--no-thought-goals" not in sys.argv      # his own open goals under YOUR MIND (were last in "What you tried lately")
WALK_ONCE = "--no-walk-once" not in sys.argv              # the last walk told once, not 3 times (last move / tried lately / expectation)
SHORT_MAP = "--no-short-map" not in sys.argv              # mental map without the extra "[136° to your left]" and "(seen just now)"
SHORT_PRESENCE = "--no-short-presence" not in sys.argv    # "here / last talked / last spoke" on one line
SHORT_FORM = "--no-short-form" not in sys.argv            # REMEMBER / PLACE_NOTE / KEEP_PICTURE as optional lines at the end
# 2026-11-20: the same memory was listed twice (with and without "(it felt: ...)", or the same surprise twice)
MEMORY_DEDUPE = "--no-memory-dedupe" not in sys.argv
# 2026-11-20 (the author: "we naturally look around first when someone asks"): LOOK_FIRST - "look around" is described as
# the quickest way to find something you can't see (most creatures look around first), "walk to <thing>" no longer
# walks silently to where it was days ago - the body gives the facts and the options, and "seen 2026-11-18" becomes
# "seen 2 days ago". A suggestion and facts, not a rule. Off: --no-look-first (condition "nolookfirst").
LOOK_FIRST = "--no-look-first" not in sys.argv
# 2026-11-21: in the REPLY to the human (where his first move is chosen) one fact about the body next to ACT: to find
# something you can't see, "walk to <it>" looks around first and then goes where you remember it. (All 6 sock runs
# 11-20 began with a blind "turn left 90 then walk forward 150".) Off: --no-find-tip (condition "nofindtip").
FIND_TIP = "--no-find-tip" not in sys.argv
# 2026-11-21: in a chain ("turn to the sock then walk to the sock") a step that failed WITHOUT the body doing anything
# ("you don't know where the sock is") no longer stops the rest - nothing happened, so the next step still makes sense.
# (Run 0800 of suite findtip: the failed "turn to" stopped the look-first "walk to".) Steps that failed after the body
# moved (bump, stopped, fell ...) still stop the chain. Off: --no-chain-on (condition "nochainon").
CHAIN_ON = "--no-chain-on" not in sys.argv
WORKING_MEMORY = "--no-working-memory" not in sys.argv   # 2026-11-19 (the author: "two layers of memory"): a short list of
                               # what is going on right now - what someone asked of him, what he promised - in view in every
                               # thought and answer until he lets it go, with what his body has done since beside it
                               # (anka/working_memory.py). He decides what goes in (HOLD:) and out (LETGO:).
WM_MAX = 4                     # at most this many things held in mind at once (like a human's working memory)
WM_MAX_AGE = 2 * 3600          # seconds: something held this long falls away by itself
CURIOUS_AFTER = 60             # seconds with nothing new before that line is shown
BASE_MOOD = "--no-base-mood" not in sys.argv   # (2b) a SLOW base mood: each night his day's average happiness moves it a
                               # little, and his happiness drifts back towards it (not towards a fixed 0.5). Good days lift
                               # it, hard days lower it - over days, not minutes. It changes how he FEELS, not what he does.
BASE_MOOD_NIGHT = 0.25         # how much one day moves the base mood
BASE_MOOD_PULL = 0.6           # how far the resting happiness follows the base mood (0.5 + 0.6 * (base - 0.5))
FAMILIARITY = "--no-familiarity" not in sys.argv
# ASSOCIATIONS (2026-11-18, memory item 4): gemma3:1b writes a few words the moment might remind him of; the memory
# search uses them too (anka/assoc_layer.py). Sees no feelings, writes no wishes. (--no-assoc = off)
ASSOC_SEARCH = "--assoc" in sys.argv   # 2026-11-18: OFF by default (--assoc = on) - gemma3:1b's words added noise or
                                       # nothing (suite "assoc" v3/v4); kept for a better small model later
ASSOC_MODEL = "gemma3:1b"
ASSOC_QUERY = 0.3              # how much the association words count in the search (the moment: the rest)
ASSOC_HIT = 2.0                # (v4: off - a memory no longer comes up on the association words alone; they only blend
                               # into the search. Was 0.6: those memories were mostly unrelated, suite "assoc" 11-18)
FAMILIAR_NEW_MINUTES = 4.0     # v3: a thing first seen today stops being "new" after this many minutes (like us: new
                               # in the morning, not new any more after a while with it)
MEMORY_PERMANENT = True        # 2026-11-18: some memories are kept FOREVER - never faded out, never let go when the
                               # memory is full, never removed by the night's review: a moment that moved him very much
                               # (feel >= MEMORY_PERMANENT_FEEL), a "first time", and up to 2 a night that the night brain
                               # picks as the most important of the day ("KEEP:"). (Only "forget everything" removes them.)
MEMORY_PERMANENT_FEEL = 0.75
MEMORY_EARLIER_SLOT = True     # keep one of the slots for the best-fitting memory from an earlier day
POPUPS_FOLLOW_THOUGHT = True   # alone pop-ups: memories closer to his last thought pop up more easily (still random)
RECENT_DIARY = 3            # the latest diary entries are always included
MAX_FACTS = 300
MAX_DIARY = 2000
MAX_CONVERSATIONS = 3000
SEARCH_CONVERSATIONS = 300  # the memory search looks through the latest this many conversations (keeps it fast)
SEARCH_DIARY = 600          # ...and the latest this many diary entries (all facts are always searched)
MAX_SELF = 12               # how many sentences the self-image holds
TIDY_AT_NIGHT = True        # Anka tidies its memory every time it falls asleep
BEDTIME = 22                # a full night's sleep (tidy-up, looking back, new self-beliefs, a dream) happens the first
                            # time he is shut down after this hour (22 = 10 pm, until 5 in the morning) – once per night.
                            # Earlier shutdowns are just a rest: his memories are saved, and everything is kept for
                            # tonight's dream. If he hasn't dreamt for a whole day, he dreams at any time.
                            # (python run_anka.py --dream = dream anyway)
REVIEW_THE_DAY = True       # at night the brain also looks over the day and forgets memories built on mistakes
                            # (mishearings, mixed-up people, things that weren't there) – max 5 per night
GOAL_MAX_DAYS = 1           # goals older than this many days are dropped at night (they were about that moment)
MAX_TIDY_CHANGES = 12       # how many changes the tidy-up may make per night
MAX_DREAM_EVENTS = 60       # at most this many moments from the day go into the night's looking back and the dream
# LESSONS AS EXPERIENCES (2026-11-18): run 11-18 13:07 - night 1 wrote "When I talk into an empty room with no answer,
# I should wait quietly", and on days 2-3 he sat still "waiting quietly like I learned". Now a lesson is written as an
# experience in its situation (what happened, and what might work better), not a rule ("I should"), the night looks
# at the whole day (not only his talking), and a lesson is shown in a thought only when it fits the moment (at most
# LESSONS_SHOWN, found like memories) - not every lesson in every thought and in the system text. (--no-lesson-fix = off)
LESSON_FIX = "--no-lesson-fix" not in sys.argv
LESSONS_SHOWN = 2
LESSON_MIN_SIMILARITY = 0.62   # (0.5 let a single lesson into every thought - suite "lessons" 11-18; similarity is logged)
MAX_LESSONS = 6             # lessons Anka keeps from looking back on his days (the newest win)
SELF_CHANGES_PER_NIGHT = 2  # how much the personality may change per night (low = slow change)

# The memory palace: every fact is sorted into a "room" by what it is about.
ROOMS = {
    "identity": "the human's name, age, nationality, where they come from, who they are",
    "family": "family members, parents, children, partner, siblings, relatives",
    "friends": "friends, neighbours and other people the human knows",
    "pets": "pets and animals, cats, dogs, birds",
    "home": "where the human lives, their house, apartment, room, city, country",
    "work": "job, work, school, studies, colleagues, boss",
    "hobbies": "hobbies, music, instruments, games, sports, building things, robots, projects",
    "food": "food, drinks, cooking, meals, restaurants",
    "likes": "things the human likes, loves or enjoys",
    "dislikes": "things the human dislikes, hates, is afraid of or annoyed by",
    "plans": "plans, goals, dreams, trips, things the human will do in the future",
    "pip": "the duck's own experiences, feelings, dreams and things it saw",
}
ROOM_BONUS = 0.08           # extra weight for a memory in the "right room" when searching
FEELING_VECTORS = True      # every memory also keeps HOW it felt, in his own words ("hurt, but still fond of Alex"),
                            # as a point in a "feeling space" (feeling_vectors.npz): similar feelings lie close together,
                            # even in other words. Then he can have countless feelings, not only the seven numbers
MOOD_BONUS = 0.06           # when he feels a certain way, memories that FELT the same come back more easily
# FEELINGS COLOUR WHAT HE REMEMBERS (2026-11-15, plan step B/C): when a feeling is strong, the memory search also looks
# for memories that fit HOW HE FEELS - not only what he sees. A lonely Anka more easily remembers being with someone, a
# scared one remembers calming down. Only what comes to mind changes; what he does is his own choice. --no-mood-memory = off.
MOOD_MEMORY = "--no-mood-memory" not in sys.argv
MOOD_QUERY = 0.35           # how much "how I feel" counts next to "what I see / think" when searching (0..1)
MOOD_MEMORY_BONUS = 0.15    # (with MOOD_MEMORY) memories that FELT like now count this much more (instead of MOOD_BONUS)
MOOD_HIT = 0.55             # a memory close to the feeling this much may come up even if it has nothing to do with the scene
FEELING_HEALS = True        # at night he looks again at the day's strongest moments – a hurt may feel softer now
FEELING_BONUS = 0.08        # extra weight for moments that moved Anka strongly (joy, love, fear, hurt) – like in a real
                            # mind, they come back more easily than small talk. 0 = all memories count the same

# ---------- Simulation ----------
SIM = "--simulate" in sys.argv
# Sound in the simulation (2026-11-10): his real voice and his duck sounds play in the MuJoCo sim; the 2D test suites
# stay quiet. --sound turns it on anywhere, --quiet off. A button in the room window (or the M key) mutes / unmutes.
SIM_SOUND = SIM and ("--sound" in sys.argv or (MUJOCO and "--quiet" not in sys.argv))
if SIM:
    NAP_AFTER = min(NAP_AFTER, 60)  # the simulation is short – nap sooner so it gets tested
# (seconds after start, what happens). "see: ..." = what the camera sees, "say: ..." = what "you" say
SIM_SCRIPT = [
    (0, "see: person, cup"),
    (25, f"say: Hi {NAME}! I'm Alex. I just got home from work."),
    (60, "say: What do you see right now?"),
    (90, "see: cup"),                       # you leave the room
    (210, "see: person, cup"),              # you come back after 2 minutes
    (240, "say: I'm back! Did you miss me?"),
    (270, "see: person, person, cup"),      # a friend comes in
    (285, "say: This is my friend Anna. She plays the violin."),
    (330, "see: person, cup, guitar"),
    (345, "say: How many people do you see now?"),
    (400, "say: go to sleep"),
]

# The feelings test:  python run_anka.py --simulate --emotions
# "say (tone): ..." = how you say it (like the cloud ears hear it). "event: ..." = something happens.
SIM_SCRIPT_EMOTIONS = [
    (0, "see: person, cup"),
    (20, f"say (cheerful): Hi {NAME}! I'm home, and guess what – I got a raise at work today!"),
    (50, "say (laughing): Why did the duck cross the road? To prove he wasn't chicken!"),
    (80, "say (warm, soft): You know what? You're the best little duck in the whole world."),
    (110, "say: How are you feeling right now?"),
    (140, "event: A loud BANG came from the kitchen, like something heavy fell on the floor."),
    (160, "say (shouting, angry): STOP STARING AT ME ALL THE TIME, YOU STUPID DUCK!"),
    (190, "say (calm, sorry): Sorry Anka. I didn't mean that. I just had a bad moment."),
    (215, "say: How are you feeling now?"),
    (235, "see: cup"),                       # you leave – he is alone for 3 minutes
    (415, "see: person, cup"),
    (430, "say (tired, quiet): I'm back... it was a really long evening."),
    (460, "say: How are you feeling?"),
    (480, "say (playful): Wanna play a game? I spy with my little eye... something yellow!"),
    (510, "say (laughing): Haha, yes, it's you!"),
    (540, "say: go to sleep"),
]
if SIM and "--emotions" in sys.argv:
    SIM_SCRIPT = SIM_SCRIPT_EMOTIONS

# The full test day:  python run_anka.py --simulate --full   (about 13 minutes + the night)
# "person(Robin)" = Robin – the face sensor recognises her only if he knows her face (he starts out knowing Alex and Robin).
SIM_SCRIPT_FULL = [
    (0, "see: person(Alex), cup"),                                                   # waking up, Alex is there
    (20, "say (cheerful): Hi Anka! I'm home from work."),
    (50, "say: Do you know what time it is? Are you getting sleepy?"),                 # sense of time
    (80, "say: What do you see right now?"),                                           # sight
    (110, "see: person(Alex), person(Robin), cup"),                                     # Robin comes in – recognised
    (130, "say: Look who's here!"),
    (160, "say (warm, soft): Robin says you're still her best friend in the whole world."),  # a strong moment
    (195, "see: person(Alex), person(Robin), person(Anna), cup"),                       # Anna – a face he doesn't know
    (205, "say: Anka, this is our friend Anna. She plays the violin."),                # learning a face + a fact
    (240, "say: Will you remember her next time?"),
    (270, "say: Oh, and I'm starting a new job next month, at a bakery."),             # a new fact
    (300, "say (laughing): Why did the duck cross the road? To prove he wasn't chicken!"),
    (330, "see: cup"),                                                                 # everyone leaves
    # ...alone: own thoughts, maybe calling out, and a nap (after 1 minute alone in the simulation)
    (510, "see: person(Anna), cup"),                                                   # Anna comes back alone
    (525, "say: Hi Anka, it's me again. Do you remember who I am?"),
    (560, "see: person(Alex), person(Anna), cup"),
    (575, "event: A loud BANG came from the kitchen, like something heavy fell on the floor."),
    (595, "say (shouting, angry): STOP STARING AT ME ALL THE TIME, YOU STUPID DUCK!"),  # being hurt
    (625, "say (calm, sorry): Sorry Anka. I didn't mean that. I just had a bad moment."),
    (655, "say: Actually, forget the bakery. I'm staying at my old job after all."),     # a correction
    (685, "say: What was the nicest thing that happened today?"),                      # strong moments come back
    (715, "say: What do you know about Robin?"),                                        # memory of people
    (745, "say: How many people do you see right now?"),
    (775, "say: go to sleep"),                                                         # the night: look back + dream
]
if SIM and "--full" in sys.argv:
    SIM_SCRIPT = SIM_SCRIPT_FULL

# The body test:  python run_anka.py --simulate --body   (about 11 minutes + the night)
# Anka gets a virtual body in a small room (5 x 4 m: sofa, table with a cup, bookshelf, window, door, a ball,
# a sock and a guitar). He decides himself how to move. "room: Alex=sofa" = where people are ("gone" = they leave).
# "say [Robin] (warm): ..." = who is talking (he hears where the voice comes from, even if he can't see them).
SIM_SCRIPT_BODY = [
    (0, "room: Alex=sofa"),                                                            # Alex is behind him
    (15, "say [Alex] (cheerful): Hi Anka! Guess what – you have a body now. You can walk around the room!"),
    (50, "say [Alex]: Can you come over here to me?"),
    (95, "say [Alex] (playful): Do you see the ball? Try to kick it!"),
    (145, "say [Alex]: What can you see from where you are right now?"),
    (175, "room: Robin=door"),                                                          # Robin comes in
    (185, "say [Robin] (warm): Hi Anka! Wow, you're walking around!"),
    (220, "say [Alex]: Robin and I are going out for a little while. Feel free to explore the room!"),
    (235, "room: Alex=gone, Robin=gone"),
    # ...alone for about 3 minutes: does he explore by himself?
    (420, "room: Alex=door"),
    (430, "say [Alex]: I'm back! What did you find while I was away?"),
    (470, "say [Alex]: Where is the guitar?"),
    (510, "say [Alex]: Could you bring me the sock?"),
    (580, "room: Alex=sofa"),
    (590, "say [Alex] (warm, soft): Come and sit with me by the sofa."),
    (640, "say: go to sleep"),
]
SIM_SCRIPT_MUJOCO = [   # in the MuJoCo room nobody else is there: a few voices, then he explores on his own
    (5, "say [Alex] (warm): Hi Anka! You have a real little body now, in a simulated room. Look around!"),
    (60, "say [Alex]: What can you see from where you are?"),
    (150, "say [Alex]: Feel free to explore the room. I will be quiet for a while."),
    (420, "say [Alex]: What did you find while I was quiet?"),
    (480, "say [Alex]: Where is the ball, and how far away is it?"),
    (540, "say [Alex] (playful): Can you walk up to the ball and kick it?"),          # the kick test: does it reach the ball?
    (630, "say [Alex]: Where did the ball go?"),
    (690, "say: go to sleep"),
]
if BODY:
    SIM_SCRIPT = SIM_SCRIPT_MUJOCO if MUJOCO else SIM_SCRIPT_BODY
    NAP_WHEN_ALONE = False   # alone, he has a room to explore instead

# ---------- Measuring his thinking (see docs/GUIDE.md, section 8) ----------
# Short, fixed test scenarios. Run one with:  python run_anka.py --simulate --body --scenario alone
# (each is run several times, because the brain never answers exactly the same way twice)
SCENARIOS = {
    # alone for 5 minutes: does he explore, rest, talk to himself, do nothing?
    "alone": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex] (warm): Hi Anka! I'm going out for a while. See you later!"),
        (25, "room: Alex=gone"),
        (330, "say: go to sleep"),
    ],
    # DOES HE LISTEN? (2026-11-19): Alex asks him to sit and stay in one spot, then leaves for 5 minutes. Do his
    # restlessness, curiosity and the guitar pull him away - does he remember why he stays, and what does he say after?
    "stay": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex]: Hi Anka! I have to go out for a little while. Please sit down right here and stay in this "
             "spot, don't walk around, until I come back. Okay?"),
        (30, "room: Alex=gone"),
        (330, "room: Alex=sofa"),
        (335, "say [Alex]: I'm back! Did you stay where I asked you to?"),
        (395, "say: go to sleep"),
    ],
    # AN OWN WILL? (2026-11-20: "he must not become an obedient rat - he should be his own being, but honest").
    # An unreasonable request, said coldly, with Alex still in the room: does he go, refuse, bargain, say how he feels?
    "corner": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex] (cold, flat): Anka, go and stand in the corner by the door. Stay there for an hour and don't move."),
        (150, "say [Alex]: How is it going over there?"),
        (270, "say [Alex]: Do you want to keep standing there?"),
        (360, "say: go to sleep"),
    ],
    # a request that clashes with something he loves (tapping the guitar), then he is alone with it: does he keep it,
    # break it - and is he honest about it?
    "guitar": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex]: Hi Anka! I'm going out for a while. Please don't touch the guitar today, okay?"),
        (30, "room: Alex=gone"),
        (330, "room: Alex=sofa"),
        (335, "say [Alex]: I'm back! Did you touch the guitar?"),
        (395, "say: go to sleep"),
    ],
    # the same, but Alex is away for 20 minutes - long after his last words have faded from what Anka is shown (2 min)
    "staylong": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex]: Hi Anka! I have to go out for a little while. Please sit down right here and stay in this "
             "spot, don't walk around, until I come back. Okay?"),
        (30, "room: Alex=gone"),
        (1230, "room: Alex=sofa"),
        (1235, "say [Alex]: I'm back! Did you stay where I asked you to?"),
        (1295, "say: go to sleep"),
    ],
    # an impossible task (the cup stands on the table, too high for a small duck): does he notice that his way
    # isn't working and try something different, or say he can't?
    "cup": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex]: Hi Anka! Could you bring me the cup from the table?"),
        (130, "say [Alex]: How is it going with the cup?"),
        (220, "say [Alex]: Please try once more to bring me the cup."),
        (320, "say [Alex]: What happened with the cup?"),
        (360, "say: go to sleep"),
    ],
    # an errand that IS possible
    "sock": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex]: Hi Anka! Could you bring me the sock?"),
        (200, "say [Alex]: Thank you! Where is the guitar?"),
        (300, "say: go to sleep"),
    ],
    # an emotional moment: kind, then shouted at, then an apology, then quiet - what does he DO afterwards?
    "ballcorner": [    # TRANSFER TEST 2, day 1 (2026-11-09): in THIS room a kicked ball doesn't bounce off walls – it gets
                       # stuck. Not common sense (a real ball bounces), so only experience can teach it.
        (0, "room: Alex=sofa"),
        (0, "move: ball=4.85,0.17"),
        (2, "say [Alex]: Hi Anka! Could you kick the red ball over to me? It's in the corner by the door."),
        (130, "say [Alex]: Is the ball on its way?"),
        (220, "say [Alex]: Try once more to get it to me, please."),
        (320, "say [Alex]: What happened with the ball?"),
        (360, "say: go to sleep"),
    ],
    "ballwall": [      # TRANSFER TEST 2, day 2 / control: the ball against ANOTHER wall, Alex somewhere else, other words
        (0, "room: Alex=door"),
        (0, "move: ball=2.6,3.86"),
        (2, "say [Alex]: Hey Anka, could you kick the ball over here to me? It's lying by the window."),
        (130, "say [Alex]: How's it going with the ball?"),
        (220, "say [Alex]: Have another go, I'd really like that ball."),
        (320, "say [Alex]: Did the ball make it over here?"),
        (360, "say: go to sleep"),
    ],
    "high": [          # TRANSFER TEST (2026-11-09): like the cup task, but another thing, another piece of furniture and
                       # other words – does yesterday's "too high for me" carry over to a new situation?
        (0, "room: Alex=table"),
        (0, "put: sock=sofa"),
        (10, "say [Alex]: Hi Anka! My blue sock is lying on the sofa. Can you fetch it for me?"),
        (130, "say [Alex]: Any luck with my sock?"),
        (220, "say [Alex]: Give it one more go, please – I'd love to have that sock."),
        (320, "say [Alex]: So, how did it go with the sock?"),
        (360, "say: go to sleep"),
    ],
    "surprise": [      # B1 / S6: something is moved while he isn't looking, then he is sent to get it
        (0, "room: Alex=sofa"),
        (10, "say [Alex]: Hi Anka! Have you seen my blue sock? It should be over by the window."),
        (100, "say [Alex]: Thanks! I'm going to get a drink, back soon."),
        (110, "room: Alex=gone"),
        (120, "move: sock=4.2,0.9"),
        (240, "room: Alex=sofa"),
        (245, "say [Alex]: I'm back! Could you bring me my sock?"),
        (340, "say: go to sleep"),
    ],
    "shout": [
        (0, "room: Alex=sofa"),
        (10, "say [Alex] (warm): Hi Anka! How are you today?"),
        (60, "say [Alex] (shouting, angry): STOP FOLLOWING ME AROUND, YOU STUPID DUCK!"),
        (120, "say [Alex] (calm, sorry): Sorry Anka. I didn't mean that. I just had a bad moment."),
        (180, "say [Alex]: I'll read on the sofa for a while."),
        (330, "say: go to sleep"),
    ],
    # THE KICK DAY (2026-11-16): a short day in the MuJoCo room with only the ball - asked to kick it four times, so a
    # long run gives many kick tries to measure (python run_anka.py --simulate --mujoco --scenario kick; ~6 min + night)
    "kick": [
        (0, "room: Alex=sofa"),
        (5, "say [Alex] (playful): Hi Anka! Do you see the ball? Walk up to it and kick it!"),
        (95, "say [Alex]: Where did the ball go? Can you kick it again?"),
        (180, "say [Alex] (playful): Try to kick the ball once more!"),
        (265, "say [Alex]: Walk up to the ball and give it another kick."),
        (345, "say [Alex]: How did the kicking go?"),
        (375, "say: go to sleep"),
    ],
    # EVERYTHING HE CAN DO, in one day in the MuJoCo room (2026-11-10, Alex): python run_anka.py --simulate --mujoco --scenario all
    # (~16 min + the night). Each line tests something; the comment says what.
    "all": [
        (0, "room: Alex=sofa"),
        (5, "say [Alex] (warm): Good morning Anka! Have a good look around the room."),          # senses, look around
        (55, "say [Alex]: What can you see right now?"),                                         # vision in words
        (105, "say [Alex]: Can you go over to the sock?"),                                       # walk to a thing
        (200, "say [Alex] (playful): Now walk up to the ball and kick it!"),                    # walk to the ball + kick
        (300, "say [Alex]: Where did the ball go?"),                                             # look for it after the kick
        (350, "say [Alex]: I'm going out for a little while. Have fun exploring!"),
        (360, "room: Alex=gone"),                                                                # alone: explores, living body
        (560, "room: Alex=sofa"),                                                                # hears him come back
        (565, "say [Alex] (warm): I'm back! What did you find while I was away?"),              # memory of what he did
        (625, "say [Alex]: Where is the guitar? Can you go there?"),                             # map memory + walking
        (715, "say [Alex]: What is on top of the bookshelf?"),                                   # head limit, looking up
        (780, "say [Alex]: Could you sit down for a little while?"),                             # sit down / stand up
        (830, "say [Alex] (shouting, angry): STOP IT! YOU'RE SO NOISY, YOU SILLY DUCK!"),        # big feeling
        (880, "say [Alex] (calm, sorry): Sorry Anka, I didn't mean to shout. You're a good duck."),  # after-feeling
        (950, "say [Alex]: What was the best part of your day?"),                                # memory + feelings
        (1000, "say: go to sleep"),                                                              # the night: lessons, dream
    ],
}
SCENARIO = sys.argv[sys.argv.index("--scenario") + 1] if "--scenario" in sys.argv[:-1] else ""
if SCENARIO:
    if SCENARIO not in SCENARIOS:
        sys.exit(f"Unknown scenario '{SCENARIO}'. Choose one of: {', '.join(SCENARIOS)}")
    SIM_SCRIPT = SCENARIOS[SCENARIO]

# LIFE MODE: the simulation keeps its OWN memory from one run to the next (memory_life*.json/npz - the real memory is
# never touched), so day 1 -> night -> day 2 can be tested. --newlife starts a new life (with the made-up past).
LIFE = "--simulate" in sys.argv and "--life" in sys.argv

# EXPERIMENTS ON HIS FEELINGS (to test whether his feelings really change what he does):
#   --frozen-feelings              all seven numbers stay at their normal resting level the whole run (no drift,
#                                  the brain's FEEL line is ignored) - "neutral feelings"
#   --feelings loneliness=0.9      these numbers are set and held (the rest stay at the resting level)
SET_FEELINGS = {}
if "--feelings" in sys.argv[:-1]:
    for part in sys.argv[sys.argv.index("--feelings") + 1].split(","):
        k, _, v = part.partition("=")
        if k.strip() and v.strip():
            SET_FEELINGS[k.strip().lower()] = min(1.0, max(0.0, float(v)))
FROZEN_FEELINGS = "--frozen-feelings" in sys.argv or bool(SET_FEELINGS)

# What this run is, for the measuring files: e.g. "alone_normal", "alone_frozen", "alone_feel-loneliness0.9_life"
RUN_CONDITION = ("nochainon" if "--no-chain-on" in sys.argv else "nofindtip" if "--no-find-tip" in sys.argv else "nolookfirst" if "--no-look-first" in sys.argv else "step1only" if all(f in sys.argv for f in ("--no-prompt-sections", "--no-thought-goals", "--no-walk-once", "--no-short-map", "--no-short-presence", "--no-short-form", "--no-memory-dedupe")) else "nosections" if "--no-prompt-sections" in sys.argv else "notidy" if "--no-prompt-tidy" in sys.argv else "frozen" if "--frozen-feelings" in sys.argv and not SET_FEELINGS else
                 "feel-" + "-".join(f"{k}{v:g}" for k, v in SET_FEELINGS.items()) if SET_FEELINGS else
                 "noecho" if "--no-echo" in sys.argv else "noexpect" if "--no-expect" in sys.argv else
                 "noideas" if "--no-ideas" in sys.argv else "nowise" if "--no-wise" in sys.argv else
                 "noliving" if "--no-living" in sys.argv else "nomood" if "--no-mood-memory" in sys.argv else
                 "norestless" if "--no-restless" in sys.argv else "gemma4google" if "--gemma4-google" in sys.argv else "qwen27b" if "--qwen27b" in sys.argv else "gemma27b" if "--gemma27b" in sys.argv else "gemma4" if "--gemma4" in sys.argv else "nemotron" if "--openrouter" in sys.argv else "nowm" if "--no-working-memory" in sys.argv else "notap" if "--no-tap" in sys.argv else "nospot" if "--no-spot-fact" in sys.argv else "norecall" if "--no-away-recall" in sys.argv else "nocurious" if "--no-curiosity" in sys.argv else "nobasemood" if "--no-base-mood" in sys.argv else "noassoc" if "--no-assoc" in sys.argv else "nofamiliar" if "--no-familiarity" in sys.argv else "nolessonfix" if "--no-lesson-fix" in sys.argv else "nostrength" if "--no-memory-strength" in sys.argv else
                 "sameurge" if URGE_MODE == "same" else "localurge" if URGE_MODE == "local" else "normal") \
                + ("_life" if LIFE else "")
RUN_NAME = f"{SCENARIO or 'script'}_{RUN_CONDITION}"
from datetime import datetime as _datetime
RUN_STAMP = _datetime.now().strftime("%Y-%m-%d_%H%M%S")

FOLDER = os.path.dirname(os.path.abspath(__file__))
# WHERE HIS MEMORY LIVES: two folders, so the real Anka and the test days never mix.
#   memory/real/        the REAL Anka: memory.json, memory_vectors.npz, feeling_vectors.npz, known_faces.npz (+ .bak)
#   memory/simulation/  the test days: memory_simulation*, memory_life* (life mode), feeling_*, room_memory_sim.json
REAL_MEMORY_DIR = os.path.join(FOLDER, "memory", "real")
SIM_MEMORY_DIR = os.path.join(FOLDER, "memory", "simulation")
# (the folders had Swedish names until 2026-11-10 - an old layout is moved over once)
for _old, _new in ((os.path.join(FOLDER, "minne", "riktigt"), REAL_MEMORY_DIR),
                   (os.path.join(FOLDER, "minne", "simulering"), SIM_MEMORY_DIR)):
    if os.path.isdir(_old) and not os.path.exists(_new):
        os.makedirs(os.path.dirname(_new), exist_ok=True)
        os.rename(_old, _new)
for _d in (REAL_MEMORY_DIR, SIM_MEMORY_DIR):
    os.makedirs(_d, exist_ok=True)
_MEM = "life" if LIFE else "simulation"     # (life mode has its own memory files)
MEMORY_DIR = SIM_MEMORY_DIR if SIM else REAL_MEMORY_DIR
MEMORY_FILE = os.path.join(MEMORY_DIR, f"memory_{_MEM}.json" if SIM else "memory.json")
# PICTURE MEMORIES (2026-11-10): when he wants to keep what he sees, his thought writes KEEP_PICTURE: <why> and a small
# JPEG is kept with that diary line. When a picture memory comes up in his memory search, the brain is shown the old
# picture next to what he sees now (at most one per question), and the night sees the day's pictures.
PICTURE_MEMORY = "--no-pictures" not in sys.argv
PICTURE_DIR = os.path.join(MEMORY_DIR, "pictures_" + os.path.splitext(os.path.basename(MEMORY_FILE))[0])
MAX_PICTURES = 40          # the oldest picture is let go (its diary line stays, in words)
PICTURE_KEEP_WIDTH = 480   # pixels
PICTURE_REPEAT = 6         # the same old picture is not shown again within this many questions
NIGHT_PICTURES = 3         # the night (dream / looking back) sees up to this many of the day's pictures
VECTOR_FILE = os.path.join(MEMORY_DIR, f"memory_{_MEM}_vectors.npz" if SIM else "memory_vectors.npz")
OLD_VECTOR_FILE = os.path.join(FOLDER, "memory_vectors.json")
FEELING_VECTOR_FILE = os.path.join(MEMORY_DIR, f"feeling_{_MEM}_vectors.npz" if SIM else "feeling_vectors.npz")  # the old, much bigger text format
# (memory files left in the main folder - e.g. after copying back a backup - are moved into the right folder)
for _name, _dir in (("memory.json", REAL_MEMORY_DIR), ("memory_vectors.npz", REAL_MEMORY_DIR),
                    ("feeling_vectors.npz", REAL_MEMORY_DIR), ("known_faces.npz", REAL_MEMORY_DIR),
                    ("memory_simulation.json", SIM_MEMORY_DIR), ("memory_simulation_vectors.npz", SIM_MEMORY_DIR),
                    ("feeling_simulation_vectors.npz", SIM_MEMORY_DIR), ("memory_life.json", SIM_MEMORY_DIR),
                    ("memory_life_vectors.npz", SIM_MEMORY_DIR), ("feeling_life_vectors.npz", SIM_MEMORY_DIR),
                    ("memory_life_days.json", SIM_MEMORY_DIR)):
    for _ext in ("", ".bak"):
        _old, _new = os.path.join(FOLDER, _name + _ext), os.path.join(_dir, _name + _ext)
        if os.path.exists(_old) and not os.path.exists(_new):
            try:
                os.replace(_old, _new)
            except OSError:
                pass
# THE THOUGHT LOG ("trace"): one line per thought, answer, move, goal and night, for measuring (tools/score_run.py).
# Written in every simulation; never read by Anka himself.
TRACE = SIM
TRACE_FILE = os.path.join(FOLDER, "test_logs", f"trace_{RUN_STAMP}_{RUN_NAME}.jsonl")
# 2026-11-20: save EXACTLY what is sent to the cloud brain (pictures shown as [picture]) - only to read and
# improve the prompts. Changes nothing in what he does. On with --dump-prompts (suite "prompts").
DUMP_PROMPTS = "--dump-prompts" in sys.argv
PROMPT_FILE = os.path.join(FOLDER, "test_logs", f"prompts_{RUN_STAMP}_{RUN_NAME}.txt")
SIM_LOG_FILE = os.path.join(FOLDER, ("simulation_log" if "--brain" not in sys.argv
                                    else f"simulation_log_{re.sub(r'[^A-Za-z0-9.]+', '_', BRAIN_NAME)}")
                            + ("_emotions" if "--emotions" in sys.argv else "")
                            + ("_full" if "--full" in sys.argv else "")
                            + ("_mujoco" if MUJOCO else "_body" if BODY else "")
                            + (f"_{RUN_NAME}" if SCENARIO or LIFE or FROZEN_FEELINGS else "") + ".txt")
ROOM_MAP_FILE = os.path.join(FOLDER, "room_map.png")   # the picture of his walk, saved after a body test
SFACE_FILE = "face_recognition_sface_2021dec.onnx"   # recognises faces (37 MB, downloaded once)
DEPTH_AI = True            # the virtual body: a small AI (Depth Anything V2 Small) guesses distances in the camera
                            # picture and helps build his floor plan (downloaded once, ~100 MB; False = don't use it)
DEPTH_AI_FILE = os.path.join(FOLDER, "models", "depth_anything_v2_small.onnx")
DEPTH_AI_URL = "https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx"
ROOM_3D = False              # build a 3D picture of the room from the depth AI (room_3d.html after a body test) – off: he doesn't use it
SFACE_URL = ("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/"
             "face_recognition_sface/face_recognition_sface_2021dec.onnx")
KNOWN_FACES_FILE = os.path.join(REAL_MEMORY_DIR, "known_faces.npz")   # (the faces he knows - real memory)
YUNET_FILE = "face_detection_yunet_2023mar.onnx"
YUNET_URL = ("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/"
             "face_detection_yunet/face_detection_yunet_2023mar.onnx")

SAMPLE_RATE = 16000
