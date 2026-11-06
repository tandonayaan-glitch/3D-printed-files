# GoCricket coin rack – 148 coins, 6.6 mm level pitch, 245.8 mm tall (Bambu Lab A1, 0.4 mm nozzle)

**Print `rack/gocricket_rack_2x37.3mf`** (STL inside `rack/gocricket_rack_2x37.stl.zip`). Do not arrange, scale or rotate. **Supports OFF.**
This replaces the earlier `tower/` design (180 coins, 5.8 mm pitch) – that one is still there as the lower-risk alternative (see "Honest limits").

## Vertical spacing (as requested)
`pitch = 6.6 mm` = floor **1.6** + 0.2 print gap + coin **3.6** + **1.2** free headroom. Consecutive coins are 3.0 mm apart, the thin floor lives inside that 3.0 mm. Everything is on the 0.2 mm layer grid (1.6 = 8 layers, 6.6 = 33 layers).
Levels that fit: `H(n) = 6.6·n + 1.6 ≤ 250` → **n = 37** (245.8 mm; 38 would be 252.4 mm).

| | |
|---|---|
| Coins | **148** = 37 floors × 4 (2 towers × front/rear coin), each the complete joined 32 × 3.6 mm coin |
| Size | 74.4 × 73.0 mm footprint (+4 mm brim), **245.8 mm** tall, centred on the bed |
| Layers | 1,229 × 0.2 mm |
| Filament | **869.6 g** (14 % of a 1 kg spool spare) |
| Time | ≈ **45.4 h** (PrusaSlicer estimate; Bambu Studio will differ) |

## Structure
* **Support beams on both sides** (and a shared one in the middle): full-height truss beams along Y – posts every 17 mm, a band at every floor, X-braced diagonals every 3 floors.
* **Thin floors, 1.6 mm**, span between the beams (33.6 mm clear). Open ends (±Y).
* A truss X-brace in the 6 mm lane between the front and rear coin stiffens the rack across its width.
* Studs (0.6 mm) on each floor hold the wide empty TAILS field of the coin above it (bridge ≤ 4.9 mm instead of 14 mm).

## Removing coins (any order)
Each coin only rests on its floor. Lift it ~1 mm (there is 1.2 mm of headroom), then slide it out of the open end: front coins toward −Y, rear coins toward +Y. Nothing else has to be broken.

## Bambu Studio settings
A1 0.4 nozzle · PLA · `0.20mm Standard @BBL A1` with: **Support OFF** · fixed 0.2 mm layers (no adaptive/variable height) · walls 3 · top 5 / bottom 4 · infill 15 % gyroid · brim outer 4 mm · **bridge speed 30–40 mm/s, thick bridges ON, bridge flow ≤ 0.9, part fan 100 %** · acceleration ≤ 3000 (outer wall ≤ 2000) · **timelapse OFF** · pause on runout ON · auto bed level + flow calibration · clean textured PEI + glue stick · weigh the spool first (≥ 920 g).

## Verification (`slicing/results/rack_*`)
* Geometry (`verify_rack.py`): watertight; 149 bodies = 1 structure + 148 free coins, each exactly the joined coin (2246.5 mm³, 3.6 mm thick), 37 levels at a 6.6 mm pitch; coins touch nothing; ±0.19 mm vertical and 0.7 mm lateral nudges (beam clearance 0.8 mm) give 0 overlap; **slide-out sweep (lift 0.7 mm, travel 50 mm in ±Y, all 148 coins at once): 0 mm³ overlap.**
* Slicer (PrusaSlicer 2.7.2, A1-equivalent profile): 1,229 layers to Z = 245.8; real G-code checks (`check_rack_gcode.py`): all 148 coin positions have the identical gap layer (studs only), coin first layer present, **6 headroom layers above every coin contain no extrusion**, and the first layer of every floor runs 100 % across the tower, i.e. both ends of every bridge line sit on a beam.
* Layer analysis (`analyze_gcode.py`): the only wide unsupported regions are the 37 floor bridges (33.6 mm); everything else ≤ 4.9 mm; no floating islands.
* Stiffness (beam model, E = 2 GPa, conservative): first sway modes 64 Hz (X) and 71 Hz (Y) – about twice as stiff as the earlier tower.

## Honest limits
* **The 37 floor bridges are 33.6 mm wide and unsupported from below** – with 1.2 mm of headroom nothing can hold a floor up except the two beams. They are anchored at both ends and the slicer treats them as bridges, but sag/quality is physically unproven; keep the bridge settings above. If you want a lower-risk print, use `tower/gocricket_tower_3x2x30` (floors held by the coin below, widest bridge 7.6 mm, 180 coins, 5.8 mm pitch, 176 mm).
* Bambu Studio could not be installed here (GitHub blocked); validation used PrusaSlicer 2.7.2 with A1-equivalent settings. No physical print was possible.
* Count is limited by one spool, not by space: a third tower (`python3 coin_rack.py 3 37`, 222 coins) needs ≈ 1.3 kg and was not sliced here.

Files: `coin_rack.py` (generator, constants at the top), `slicing/` (profile, checkers, frame model, results), `previews/rack_*.png`.
