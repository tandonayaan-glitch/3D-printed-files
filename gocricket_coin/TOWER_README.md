# GoCricket coin tower – 180 coins in one print (Bambu Lab A1, 0.4 mm nozzle, single colour)

**Print `tower/gocricket_tower_3x2x30.3mf`** (or the STL inside `tower/gocricket_tower_3x2x30.stl.zip`). Do not arrange, scale or rotate it.

| | |
|---|---|
| Coins | **180** = 30 floors × 6 coins, every coin the complete 32 × 3.6 mm joined coin (`gocricket_coin_joined.stl`) |
| Size | 65.2 × 134.6 mm footprint, **176.0 mm tall**, centred on the bed (+4 mm brim) |
| Layers | 880 × 0.2 mm (first layer 0.2) |
| Filament | **920.6 g** (742 cm³) – fits one 1 kg spool with 79 g (7.9 %) spare |
| Time | ≈ **51 h** (PrusaSlicer estimate with A1-like speeds; Bambu Studio will differ) |
| Per coin | ≈ 5.1 g all-in (coin 2.8 g, floor/pillars 2.3 g) |

## Why 180 coins / 176 mm and not 250 mm
Material and time, not space, limit the count. The A1 bed would take 42 coins per floor × 42 floors = 1,764 coins at 245.6 mm, but that is ≈ 9 kg of PLA and ≈ 10 days. One spool is the largest job with no mid-print spool change, so the generator is sized to it: `levels = floor((≈930 g − 5.5 g) / 30.6 g per floor)`. More height would only add sway risk; more coins need more spools. Other sizes: `python3 coin_tower.py COLS ROWS LEVELS` (≈ 5.1 g and ≈ 17 min per coin).

## How it works (no slicer supports needed)
* Each floor: coin (TAILS face down) rests on a 1.8 mm **pad** with a 0.2 mm air gap (one layer), exactly like a slicer support interface; the pad is printed over the coin below it with a 0.2 mm gap. Pitch 5.8 mm = 29 layers, so every gap lands on a layer boundary.
* 6 small 0.6 mm studs per pad hold the wide empty TAILS field (without them a 14.4 mm bridge; with them ≤ 4.9 mm).
* Pads hang on a honeycomb of 3 mm ribs and 14 × 7 mm pillars by 1.2 × 0.8 mm break-away webs. A top cap ties the pillars together; a 2 mm base plate (92 cm² first layer with brim) is the bed contact.
* **Supports must be OFF** – everything is modelled.

## Removing coins
Work from the top: lift the coin out (it only rests on the pad), snap the pad's 3–4 webs with your fingers/flush cutters and lift the pad off, then the next coin. The pad stubs stay on the ribs; nothing touches the coin faces.

## Bambu Studio settings
Printer A1 0.4 nozzle · PLA 1.75 · process `0.20mm Standard @BBL A1` with:
**Support OFF** · layer height 0.2 fixed, **no adaptive/variable layer height** · wall loops 3 · top 5 / bottom 4 shell layers · infill 15 % gyroid · brim outer 4 mm · bridge speed ≤ 50 mm/s, thick bridges on · bridge/part fan 100 % · **acceleration ≤ 3000 (outer wall ≤ 2000)**, outer wall ≤ 100 mm/s · **timelapse OFF** · pause on filament runout ON · auto bed level + flow calibration ON · clean textured PEI + glue stick · weigh the spool first (needs ≥ 950 g) · keep the printer out of draughts.

## Verification evidence (`slicing/results/`)
* Joined coin: 2251.8 mm³ = 2 × 1125.9 mm³, 3.6 mm thick, halves overlap 0.000 mm³, difference to halves-union 0.002 mm³ (`coin_join_verification.txt`).
* Tower mesh: watertight, 2.34 M faces, within the bed (X 95–161, Y 61–195, Z 0–176); 181 bodies = 1 structure + 180 free coins; 0 mm³ contact; ±0.19 mm vertical and 0.9 mm lateral nudges give 0 overlap; coin-to-pillar 1.28 mm (`geometry_verification.txt`).
* Slicer (PrusaSlicer 2.7.2, A1-equivalent profile `a1_pla_0.4_validation.ini`): 880 layers to Z = 176.0, all 0.2 mm. Real G-code checks (`check_gaps.py`): all 180 coin positions have an identical gap layer (only the 6 studs, 34 mm of extrusion), coin first layer present, nothing between coin top and the next pad; base top layer 100 % solid; all break-away webs printed on the right 4 layers (`gap_check.txt`, `previews/gcode_gap_layers_Z2.0_vs_Z2.2.png`).
* Layer-by-layer support analysis of the whole G-code (`analyze_gcode.py`): widest unsupported region **7.6 mm** (pad undersides over the coin below, 1 layer per floor); TAILS field ≤ 4.9 mm; no region wider than 10 mm; no isolated floating islands (`layer_analysis_summary.txt`).
* Stiffness (beam-frame model, E = 2 GPa): first sway mode ≈ 32 Hz → ≈ 0.1 mm quasi-static sway at 5000 mm/s² (`frame_modes.txt`).

## Honest limits – what could not be proven here
* **Bambu Studio itself could not be installed** (GitHub is blocked in this environment); validation used PrusaSlicer 2.7.2 (the engine Bambu Studio descends from) with A1-equivalent settings. Bambu's toolpaths and time estimate will differ; the design depends only on the 0.2 mm layer grid, supports off and spans ≤ 7.6 mm.
* No physical print was possible: bridge quality over the 0.2 mm gaps, coin-to-pad stickiness and real vibration of a 176 mm tower are modelled/estimated, not measured. A ~51 h print also carries power/filament risk (A1 has power-loss recovery and runout pause).
* Coins come off top-down, not in any order.

## Files
`make_coin.py` (coin + halves), `join_coin.py` (join proof), `coin_tower.py` (tower generator – edit constants at the top), `slicing/` (validation profile, G-code analysers, frame model, results), `previews/`.
