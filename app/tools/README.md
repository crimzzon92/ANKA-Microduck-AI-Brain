# tools/ – what everything here is for

You don't need any of these to run Anka. The main launchers are in the top folder (`Start Anka.command`,
`Anka in sim.command`, `Start everything.command`). These are for the 3D simulator, for measuring him, for
repeating the experiments in the [journal](../docs/JOURNAL.md), and for finding faults.

The `.command` files are double-click launchers for macOS. On Linux, run them with `bash "<file>.command"`.
They all use the Python in `~/anka-env`.

## Running him in the 3D simulator

Start Pollen's simulator first with `Start Anka sim.command` (in the top folder).

| File | What it does |
|---|---|
| `Anka in sim (everything).command` | The 17-minute test day that tests everything (`--scenario all`). The [example day](../examples/mujoco-day/) is one of these. |
| `Anka in sim (still body).command` | The same as `Anka in sim.command`, but with the living body switched off (`--no-living`), to compare. |
| `Anka in sim (living body).command` | A normal day in the simulator with the living body on (the default), for side-by-side runs with the still body. |
| `Anka 3D long run.command` | Several 3D days in a row (`[N=5] [scenario=kick]`), each scored. Used for the kick work. |
| `Anka eyes.command` | A window with what the simulated duck senses: camera, depth grid, IMU. You can drive him by hand with the keys. |
| `Update Pollen (0.18.9).command` | Moves your copy of Pollen's `microduck` to the release Anka is tested with, and remembers where you were. |
| `Pollen go back.command` | Undoes that: back to the Pollen version you had before. |

## Measuring him

| File | What it does |
|---|---|
| `score_run.py` | The scorer. Reads the thought traces in `test_logs/` and counts what he actually did (actions, failures, repeats, goals, feelings, memory use, cost) into `test_logs/scores.csv`. `--compare` makes a table per scenario and condition. No AI judges anything. |
| `Anka score.command` | Runs the scorer and shows the comparison. |
| `replay_test.py` | Replays the moves from a 2D test log offline (no cloud brain, no cost) with many random seeds, to measure his map. |
| `trail_plot.py` | Draws the path of a replayed log, old settings against new. |
| `selftest.py` · `Anka selftest.command` | 12 quick checks without the cloud brain (files compile, parts load, the 2D body walks/taps/kicks, working memory, …). Writes nothing to his memory. Run it after changing code. |

## Watching his brain

| File | What it does |
|---|---|
| `Anka brain window.command` | The brain view: which parts of him are busy, as light waves through a net of neurons. Usually opened with the **BRAIN VIEW** button (or B) in the simulator window. Keys: D = demo, Q = close. |
| `Anka brain window (demo).command` | The same in demo mode (no Anka needed). |
| `Anka brain view.command` · `(demo)` | The same picture in your web browser (`viz/index.html`, served on 127.0.0.1:8765). |
| `brain_view_test.js` | Checks the browser version's demo and live levels with Node (no browser). |

## Repeating the experiments

Each suite runs a set of test days in the 2D simulator with the real cloud brain, then scores them. They cost money:
roughly $0.10 per run. The numbers they produced are in [STATUS](../STATUS.md) and the [journal](../docs/JOURNAL.md).

| File | Experiment |
|---|---|
| `Anka suite.command` | The baseline: alone, cup, sock and shout, 3 runs each. It also runs all the others when given a name. |
| `Anka suite - quick.command` | One run of each scenario, to check that everything works. |
| `Anka suite - feelings.command` | E1: feelings frozen at neutral, against normal. |
| `Anka suite - lonely.command` | E2: alone with loneliness held high, against low. |
| `Anka suite - echo.command` | Feelings that fade slowly ("after-feelings"), with against without. |
| `Anka suite - talk.command` | How much he talks, alone and with company. |
| `Anka suite - expect.command` | Expectation and surprise, with against without. |
| `Anka suite - twodays.command` | Learning: the same task on day 1 and day 2 of one life. |
| `Anka suite - nextday.command` | Day 3 of the same life (run after twodays). |
| `Anka suite - transfer.command` | Transfer test: can't reach a cup on day 1, then a sock on the sofa on day 2, against a fresh life. |
| `Anka suite - balltransfer.command` | Ball transfer test: with night ideas, without them, and a fresh life. |
| `Anka suite - wise.command` | The wiser brain when stuck: the ball in the corner, with against without. |
| `Anka suite - drives.command` | Tap + curiosity + base mood, 3 days alone, two lives. |
| `Anka suite - basemood.command` | The slow base mood with against without, 3 days alone, two lives each. |
| `Anka suite - stay.command` | Does he listen? Alex asks him to sit and stay, leaves for 5 minutes. |
| `Anka suite - staylong.command` | The same, with Alex away 20 minutes. |
| `Anka suite - wm.command` | Working memory, all in one sweep (self-test first): stay, staylong, sock and cup with/without, alone, shout. |
| `Anka suite - will.command` | An own will? A cold "stand in the corner for an hour", and "don't touch the guitar today". |
| `Anka suite - lookfirst.command` | Look around before searching: sock ×3 + guitar, with against without. |
| `Anka suite - findtip.command` | The fact next to his answer ("walk to <it> looks around first"): sock ×3, with against without. |
| `Anka suite - qwen27b.command` | The whole Anka on Qwen3.8 27B through OpenRouter (paid; needs `app/openrouter.key`). One sock day. |
| `OpenRouter ping (qwen).command` · `openrouter_ping.py` | Checks your OpenRouter key and asks the model one small question with a picture. |
| `Anka suite - urge.command` | An inner wish written in the same answer as the thought, with against without. |
| `Anka suite - localurge.command` | The wish written by a small local model (`gemma3:1b`), with against without. |
| `Anka suite - mood.command` | Feelings colour what he remembers: alone and shout, with against without. |
| `Anka suite - moodlife.command` | The same over two days in one life. |
| `Anka suite - familiar.command` | Getting to know things: 3 days alone, with against without, two lives each. |
| `Anka suite - lessons.command` | Lessons as experiences: 3 days alone, with against without, two lives each. |
| `Anka suite - assoc.command` | Memory search words from a small local model (with only). |
| `Anka suite - restless.command` | Restlessness: 3 days alone, two lives (with only). |
| `Urge models test.command` · `urge_models_test.py` | Compares small local models as the feeling layer, offline (no cloud). |
| `Assoc words test.command` · `assoc_words_test.py` | Shows the association words the small model writes for a few scenes. |

## Finding faults in the 3D body

For developers. They test one part of the body alone, without the brain.

| File | What it tests |
|---|---|
| `Anka kick test.command` | Pollen's kick with the ball placed exactly where the kick expects it. This is how we found why his kicks missed. |
| `Anka walktest.command` | How far he really walks compared with what he asked for. |
| `Anka turntest.command` | How far he really turns compared with what he asked for. |
| `Anka headtest.command` | The head joints and the camera angle, standing and walking. |
| `Anka fake test.command` | The body and his map against a fake simulator (no MuJoCo needed, runs fast). |
| `Anka yolotest.command` | What YOLO recognises in the simulator's camera picture (it found nothing; see the journal). Installs `ultralytics` the first time. |
