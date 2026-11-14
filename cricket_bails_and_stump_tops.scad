// =====================================================================
// Cricket bails (fully round, lathe-turned) + six stump tops
// with A1334 Hall-sensor pockets and 2x2 mm magnet pockets.   Units: mm
//
// PART = "plate"                       all 8 parts, print layout
//        "bail_1" | "bail_2"
//        "top_1" | "top_2" | "top_3"   34.9 mm : off / middle / leg
//        "top_4" | "top_5" | "top_6"   32.5 mm : off / middle / leg
//        "assembly_34_9" | "assembly_32_5"   preview only (ghost sensors/magnets)
//
// Wicket frame (assembly): X = wicket line, Z up, Z=0 = apex of stump-top dome.
//   off stump x=0, middle x=spacing, leg x=2*spacing.
//   Bail 1 spans off->middle (long spigot on off).
//   Bail 2 spans leg->middle (long spigot on leg). Bail 1 and Bail 2 are the
//   same shape; bail 2 is simply turned end-for-end on the wicket.
//
// Designed for: 0.4 mm nozzle, 0.28 mm layers, PETG, supports ENABLED.
// =====================================================================

PART = "plate";
$fn  = 96;

/* ------------------------- BAIL ----------------------------------- */
barrel_len     = 54;
spigot_long    = 35;
spigot_short   = 20.6;          // total = 109.6
bail_target    = 109.6;
max_projection = 12.7;          // top of bail above stump top (Z=0)
barrel_r       = 10.5;          // main bead radius
barrel_r_end   = 9.9;           // end beads slightly smaller
groove_r       = 8.3;           // radius at bottom of narrow grooves
groove_w       = 1.6;
bead_count     = 4;
spigot_r       = 5.5;           // 11 mm spigot
cove_r         = 2.8;           // cove from spigot up to barrel (groove_r - spigot_r)
spigot_chamfer = 0.8;

/* ------------------------- MAGNETS -------------------------------- */
mag_d          = 2.0;
mag_h          = 2.0;
mag_tol        = 0.15;          // per side -> 2.3 mm hole (tune after test print)
mag_lip_h      = 0.5;           // retention lip at the pocket mouth; magnet sits above it
mag_lip        = 0.10;          // lip overhang per side: mouth = mag_d - 2*lip = 1.8 mm.
                                // Magnet is pressed past the lip (PETG flexes) and snaps in;
                                // add a dab of CA/epoxy for permanent security.
mag_tip_long   = 6;             // magnet centre from long-spigot tip
mag_tip_short  = 5;             // magnet centre from short-spigot tip
// POLARITY: all four magnets go in with the SAME pole facing DOWN (towards the
// sensor). Which pole (N or S) is a matter of your A1334 variant/switch
// direction - mark that pole with a marker before inserting, identical on all.
// Pockets are blind: opening only on the underside, closed everywhere else.
// Magnets exist ONLY in the bails (one near each end). NO magnets in the caps.
pocket_extra   = 0.2;           // cavity height beyond mag_h (glue room)

/* ------------------------- STUMP TOP SIZES ------------------------ */
top_d_big      = 34.9;
top_d_small    = 32.5;
// Pipe wall is NOT given for these sizes. Assumed same wall as your earlier
// 33.5 OD / 31.2 ID pipe (1.15 mm). CHECK and edit if the pipes differ:
pipe_wall_big   = 1.15;
pipe_wall_small = 1.15;
plug_fit        = 0.40;         // plug dia = OD - 2*wall - plug_fit. Larger = looser
plug_len        = 16;
plug_chamfer    = 1.0;
plug_bore_d     = 10;           // material-saving / wire bore from below (0 = none)
plug_bore_depth = 10;
wicket_width    = 228.6;        // outer edge to outer edge; spacing = (W - d)/2

/* ------------------------- HEAD SHAPE ----------------------------- */
head_h         = 12;            // head height below dome apex
dome_sag       = 2.2;
edge_round     = 1.5;
ring_z         = -7.0;          // turned ring groove (set ring_depth=0 to remove)
ring_depth     = 0.6;

/* ------------------------- BAIL SEATS ----------------------------- */
seat_clear     = 0.30;          // radial clearance, round cradle around spigot
seat_end_clear = 0.40;
seat_rest_gap  = 0.05;          // tiny gap so bail never fuses to the cradle (also kills tangent facet slivers)
tip_inset      = 3.0;           // long spigot tip sits this far inside outer rim
min_ridge      = 1.0;

/* ------------- A1334 SENSOR MODULE (TSOP1738-style, 3 pins) --------
   PLACEHOLDER sizes - MEASURE YOUR MODULE and edit.                    */
sens_w         = 5.0;           // body width  (across bail, Y)
sens_l         = 6.0;           // body length (along bail, X) - lead end is at the stump-centre side
sens_d         = 4.5;           // body depth, sensing face to back (Z)
sens_clear     = 0.25;          // clearance per side
sens_lead_room = 3.5;           // extra room beyond the body for the 3 leads/wires
sens_lead_w    = 5.6;           // width of lead/wire channel (3 pins @2.54 = 5.08)
sens_lead_top  = 1.0;           // lead channel stops this far below pocket ceiling
sens_floor     = 0.84;          // plastic between seat and sensing face (3 layers @0.28)
min_wall       = 1.2;           // min wall between sensor shaft and plug surface
arrow_depth    = 0.5;           // engraved lead-direction arrow on plug underside

/* ------------------------- PRINT PLATE ---------------------------- */
bail_print_roll = 90;           // roll about bail axis so magnet holes print sideways
plate_bail_x    = [-30, -60];
plate_big_x     = 25;           // column of 34.9 tops
plate_small_x   = 65;           // column of 32.5 tops
plate_y         = [-42, 0, 42];

// ======================= DERIVED / CHECKS ===========================
bail_len   = spigot_long + barrel_len + spigot_short;
axis_h     = max_projection - barrel_r;           // bail axis height when seated
seat_bot   = axis_h - spigot_r;                   // lowest point of seated spigot (cradle floor is seat_rest_gap below)
sens_ceil  = seat_bot - seat_rest_gap - sens_floor;               // top (sensing-face level) of sensor pocket
pocket_depth = mag_lip_h + mag_h + pocket_extra;

function x_tip(d)     = -d/2 + tip_inset;                       // long tip, off-cap local X
function spacing(d)   = (wicket_width - d)/2;
function x_tip_mid(d) = x_tip(d) + bail_len - spacing(d);       // short tip, middle-cap local X
function plug_r(d, wall) = (d - 2*wall - plug_fit)/2;
function mag_x_long(d)  = x_tip(d) + mag_tip_long;

assert(abs(bail_len - bail_target) < 0.01, "bail length != 109.6");
assert(bail_len >= 109.5 && bail_len <= 111.13, "bail length outside 109.5..111.13");
assert(axis_h > 0, "barrel too big for max_projection");
assert(abs(groove_r - spigot_r - cove_r) < 1e-6, "cove_r must equal groove_r - spigot_r");
assert(pocket_depth + 3 < spigot_r*2, "magnet pocket too deep for spigot");
for (d = [top_d_big, top_d_small]) {
    assert(x_tip(d) + spigot_long >= d/2 + 0.5, "barrel face collides with off stump");
    assert(x_tip(d) + spigot_long + barrel_len <= spacing(d) - d/2 - 0.5, "barrel collides with middle stump");
    assert(x_tip_mid(d) + seat_end_clear <= -min_ridge, "middle seats collide");
}
// radial check of sensor shafts against plug wall (worst case = long-side shaft)
function shaft_reach(xm, d) =
    sqrt(pow(abs(xm) + sens_l/2 + sens_clear, 2) + pow(max(sens_w, sens_lead_w)/2 + sens_clear, 2));
assert(shaft_reach(mag_x_long(top_d_small), top_d_small) + min_wall <= plug_r(top_d_small, pipe_wall_small),
       "32.5 sensor shaft too close to plug wall");
assert(shaft_reach(mag_x_long(top_d_big), top_d_big) + min_wall <= plug_r(top_d_big, pipe_wall_big),
       "34.9 sensor shaft too close to plug wall");
assert(sens_ceil - (sens_d + sens_clear) > -head_h - plug_len + 3, "sensor pocket too deep for cap");

// ============================= BAIL =================================
function arc_pts(cx, cy, r, a0, a1, n=14) =
    [for (i=[0:n]) let(a = a0 + (a1-a0)*i/n) [cx + r*cos(a), cy + r*sin(a)]];

function bead_pts(x0, bw, rb, rg) =
    let(h = rb - rg, R = (bw*bw/4 + h*h)/(2*h), th = asin((bw/2)/R))
    arc_pts(x0 + bw/2, rb - R, R, 90+th, 90-th, 16);

function barrel_pts(xf) =
    let(n = bead_count, bw = (barrel_len - (n-1)*groove_w)/n)
    [ for (i=[0:n-1])
        let(x0 = xf + i*(bw + groove_w), rb = (i==0 || i==n-1) ? barrel_r_end : barrel_r)
        each concat(bead_pts(x0, bw, rb, groove_r), (i<n-1) ? [[x0+bw+groove_w, groove_r]] : [])
    ];

// polygon in (radius, x) -> revolved around the bail axis: complete 360 deg solid
function bail_poly() =
    let(xf1 = spigot_long, xf2 = spigot_long + barrel_len, L = bail_len)
    concat(
        [[0,0], [spigot_r - spigot_chamfer, 0], [spigot_r, spigot_chamfer]],
        [for (p = arc_pts(xf1 - cove_r, spigot_r + cove_r, cove_r, -90, 0, 12)) [p[1], p[0]]],
        [for (p = barrel_pts(xf1)) [p[1], p[0]]],
        [for (p = arc_pts(xf2 + cove_r, spigot_r + cove_r, cove_r, 180, 270, 12)) [p[1], p[0]]],
        [[spigot_r, L - spigot_chamfer], [spigot_r - spigot_chamfer, L], [0, L]]
    );

module bail_solid() { rotate([0,90,0]) rotate_extrude() polygon(bail_poly()); }

// blind pockets, entered from the underside (-Z) of the spigots
module bail_pockets() {
    for (x = [mag_tip_long, bail_len - mag_tip_short]) translate([x, 0, 0]) {
        translate([0, 0, -spigot_r + mag_lip_h])                     // magnet cavity
            cylinder(d = mag_d + 2*mag_tol, h = mag_h + pocket_extra, $fn = 40);
        translate([0, 0, -spigot_r - 0.5])                           // mouth with retention lip
            cylinder(d = mag_d - 2*mag_lip, h = 0.5 + mag_lip_h + 0.01, $fn = 40);
    }
}

module bail() { difference() { bail_solid(); bail_pockets(); } }

// ============================ STUMP TOP =============================
module head_profile(Rh) {
    Rd = Rh - edge_round;
    Rs = (Rd*Rd + dome_sag*dome_sag) / (2*dome_sag);
    zs = -dome_sag - edge_round;
    ring = (ring_depth > 0) ? [[Rh, ring_z - 0.9], [Rh - ring_depth, ring_z], [Rh, ring_z + 0.9]] : [];
    dome = [for (i=[0:24]) let(r = Rd*(1 - i/24)) [r, -(Rs - sqrt(Rs*Rs - r*r))]];
    fil  = [for (i=[0:10]) let(a = 90*i/10) [Rd + edge_round*sin(a), -dome_sag - edge_round + edge_round*cos(a)]];
    polygon(concat([[0, -head_h], [Rh, -head_h]], ring, [[Rh, zs]], fil, dome));
}

module cap_body(d, wall) {
    Rp = plug_r(d, wall);
    rotate_extrude() head_profile(d/2);
    translate([0,0,-head_h - plug_len])
        rotate_extrude()
            polygon([[0,0],[Rp - plug_chamfer,0],[Rp,plug_chamfer],[Rp,plug_len+0.01],[0,plug_len+0.01]]);
}

// round cradle for the spigot, open upward, closed at the inner end by a wall
module seat_channel(xa, xb) {
    rg = spigot_r + seat_clear; len = xb - xa;
    zg = axis_h + seat_clear - seat_rest_gap;   // spigot bottom rests just above the cradle floor
    translate([xa, 0, zg]) rotate([0,90,0]) cylinder(r = rg, h = len);
    translate([xa, -rg, zg]) cube([len, 2*rg, 30]);
}

// sensor pocket+shaft. xm = magnet X. dir = +1 : leads exit towards +X.
module sensor_cut(xm, dir) {
    zbot = -head_h - plug_len - 1;
    c = sens_clear;
    // body pocket: sensing face up, at the ceiling just under the seat floor
    translate([xm - sens_l/2 - c, -sens_w/2 - c, sens_ceil - sens_d - c])
        cube([sens_l + 2*c, sens_w + 2*c, sens_d + c + 0.001]);
    // vertical access / wire shaft down through the plug (body footprint + lead room)
    x0 = (dir > 0) ? xm - sens_l/2 - c : xm - sens_l/2 - c - sens_lead_room;
    translate([x0, -max(sens_w, sens_lead_w)/2 - c, zbot])
        cube([sens_l + 2*c + sens_lead_room, max(sens_w, sens_lead_w) + 2*c,
              (sens_ceil - sens_d - c) - zbot + 0.001]);
    // lead channel up beside the body
    xl = (dir > 0) ? xm + sens_l/2 : xm - sens_l/2 - sens_lead_room;
    translate([xl, -sens_lead_w/2 - c, sens_ceil - sens_d - c])
        cube([sens_lead_room, sens_lead_w + 2*c, sens_d + c - sens_lead_top]);
    // engraved arrow on the plug underside: points the way the leads exit
    translate([xm + dir*(sens_l/2 + sens_lead_room/2), max(sens_w, sens_lead_w)/2 + c + 2.4, -head_h - plug_len - 0.01])
        linear_extrude(arrow_depth + 0.01)
            polygon([[dir*1.8, 0], [-dir*1.2, 1.3], [-dir*1.2, -1.3]]);
}

module wire_bore() {
    if (plug_bore_d > 0)
        translate([0,0,-head_h - plug_len - 0.01]) cylinder(d = plug_bore_d, h = plug_bore_depth, $fn = 48);
}

// kind: "off" | "middle" | "leg"
module stump_top(d, wall, kind) {
    Rh = d/2;
    xo = x_tip(d); xt = x_tip_mid(d);
    mirror([kind == "leg" ? 1 : 0, 0, 0])
    difference() {
        cap_body(d, wall);
        if (kind == "middle") {
            seat_channel(-Rh - 3, xt + seat_end_clear);          // bail 1 arrives from -X
            seat_channel(-(xt + seat_end_clear), Rh + 3);        // bail 2 arrives from +X
            // middle stump: NO Hall sensor, NO sensor pocket, NO wire channel
        } else {
            seat_channel(xo - seat_end_clear, Rh + 3);           // open towards the gap
            sensor_cut(mag_x_long(d), +1);                       // only outer stumps carry a sensor
            wire_bore();
        }
    }
}

// ======================= PREVIEW HELPERS ============================
module sensor_ghost() {          // TSOP-style: body, lens dome on sensing face, 3 leads
    color("DimGray") translate([-sens_l/2, -sens_w/2, -sens_d]) cube([sens_l, sens_w, sens_d]);
    color("Red") translate([0,0,0]) cylinder(d = 2, h = 0.4, $fn = 24);
    for (y = [-2.54, 0, 2.54]) color("Silver") translate([sens_l/2, y - 0.25, -sens_d/2 - 0.25]) cube([sens_lead_room + 3, 0.5, 0.5]);
}
module magnet_ghost() color("Gold") cylinder(d = mag_d, h = mag_h, $fn = 24);

function sp(d) = spacing(d);
module bail1_world(d) translate([x_tip(d), 0, axis_h]) bail();
module bail2_world(d) translate([2*sp(d) - x_tip(d), 0, axis_h]) rotate([0,0,180]) bail();

module ghosts(d) {
    // ONLY 2 sensors (off + leg, long-spigot side); 4 magnets (2 per bail)
    translate([mag_x_long(d), 0, sens_ceil]) sensor_ghost();          // off stump
    translate([2*sp(d) - mag_x_long(d), 0, sens_ceil]) mirror([1,0,0]) sensor_ghost();
    for (p = [[x_tip(d) + mag_tip_long], [x_tip(d) + bail_len - mag_tip_short],
              [2*sp(d) - x_tip(d) - mag_tip_long], [2*sp(d) - x_tip(d) - bail_len + mag_tip_short]])
        translate([p[0], 0, seat_bot + mag_lip_h]) magnet_ghost();
}

module assembly(d, wall) {
    stump_top(d, wall, "off");
    translate([sp(d),0,0]) stump_top(d, wall, "middle");
    translate([2*sp(d),0,0]) stump_top(d, wall, "leg");
    color("Tan") { bail1_world(d); bail2_world(d); }
    ghosts(d);
}

// ======================= PRINT ORIENTATION ==========================
module bail_print() {   // round bail, supports under it; axis along Y; lowest point on bed
    translate([0, 0, barrel_r])
        rotate([0,0,90]) translate([-bail_len/2, 0, 0]) rotate([bail_print_roll, 0, 0]) bail();
}
module top_print(d, wall, kind) { translate([0,0,head_h + plug_len]) stump_top(d, wall, kind); }

module top_part(i) {
    if (i == 1) top_print(top_d_big,   pipe_wall_big,   "off");
    if (i == 2) top_print(top_d_big,   pipe_wall_big,   "middle");
    if (i == 3) top_print(top_d_big,   pipe_wall_big,   "leg");
    if (i == 4) top_print(top_d_small, pipe_wall_small, "off");
    if (i == 5) top_print(top_d_small, pipe_wall_small, "middle");
    if (i == 6) top_print(top_d_small, pipe_wall_small, "leg");
}

module plate() {
    for (k = [0:1]) translate([plate_bail_x[k], 0, 0]) bail_print();
    for (k = [0:2]) {
        translate([plate_big_x,   plate_y[k], 0]) top_part(k + 1);
        translate([plate_small_x, plate_y[k], 0]) top_part(k + 4);
    }
}

if      (PART == "plate")  plate();
else if (PART == "bail_1" || PART == "bail_2") bail_print();
else if (PART == "top_1") top_part(1);
else if (PART == "top_2") top_part(2);
else if (PART == "top_3") top_part(3);
else if (PART == "top_4") top_part(4);
else if (PART == "top_5") top_part(5);
else if (PART == "top_6") top_part(6);
else if (PART == "assembly_34_9") assembly(top_d_big, pipe_wall_big);
else if (PART == "assembly_32_5") assembly(top_d_small, pipe_wall_small);
else echo("Unknown PART:", PART);

echo(bail_len = bail_len, axis_h = axis_h, seat_bottom = seat_bot, sensor_ceiling = sens_ceil,
     plug_od_big = 2*plug_r(top_d_big, pipe_wall_big), plug_od_small = 2*plug_r(top_d_small, pipe_wall_small),
     spacing_big = spacing(top_d_big), spacing_small = spacing(top_d_small),
     x_tip_big = x_tip(top_d_big), x_tip_mid_big = x_tip_mid(top_d_big));
