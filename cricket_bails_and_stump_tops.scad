// =====================================================================
// Cricket bails (fully round, lathe-turned) + six stump tops
// with an A1344 (UA package) Hall-sensor pocket and 2x2 mm magnet pockets.   Units: mm
//
// PART = "plate"     2 bails + 3 covers (A1-sized layout, ~130 x 120 mm)
//        "bail_1" | "bail_2"
//        "cover_1" | "cover_2" | "cover_3"   off-stump cover, 34.9 mm head,
//                                               insert diameter 28 / 29 / 30 mm
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
mag_tip_long   = 7;             // magnet centre from long-spigot tip
mag_tip_short  = 5;             // magnet centre from short-spigot tip
// POLARITY: all four magnets go in with the SAME pole facing DOWN (towards the
// sensor). Which pole (N or S) is a matter of your A1334 variant/switch
// direction - mark that pole with a marker before inserting, identical on all.
// Pockets are blind: opening only on the underside, closed everywhere else.
// Magnets exist ONLY in the bails (one near each end). NO magnets in the caps.
pocket_extra   = 0.2;           // cavity height beyond mag_h (glue room)

/* ------------------------- STUMP TOP SIZES ------------------------ */
top_d_big      = 34.9;          // head diameter (fixed); INSERT diameters are plug_ods below
plug_ods        = [28.2, 28.2, 28.2]; // insert diameter of each of the 3 covers
cone_r          = 15.0;         // 45 deg lead-in cone under the head stops at this radius (must be < pipe bore radius)
cavity_flat_r   = 5;            // flat part of the cavity ceiling (rest is a 45 deg cone = no bridging)
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

/* ------------- Allegro A1344 Hall sensor, UA 3-pin SIP package ------
   Dimensions from Allegro UA-package drawings (A1321/A3144/A1318 series, same
   package; A1344 datasheet itself not retrieved - verify with calipers):
   body 4.09 (along leads) x 3.02 (wide) x 1.52 (thick), leads 1.27 mm pitch,
   ~0.41 mm wide. Hall element is ~0.5 mm under the MARKED (printed) FACE.
   The marked face goes UP, towards the bail magnet. Sensor is pushed in
   from the underside of the cap, leads trailing down the shaft.          */
sens_w         = 3.02;          // body width  (across bail, Y)
sens_l         = 4.09;          // body length (along bail, X); leads leave the end nearest stump centre
sens_d         = 1.52;          // body thickness (marked face to back, Z)
sens_clear     = 0.20;          // clearance per side (FDM holes print slightly small)
sens_lead_room = 3.0;           // room beyond the body for the leads to bend down
sens_lead_w    = 3.6;           // lead channel width (3 leads span 2.54 + 0.41)
sens_lead_top  = 0.5;           // lead channel stops this far below the pocket ceiling
sens_floor     = 0.84;          // plastic between seat and sensing face (3 layers @0.28, reliable bridge)
min_wall       = 1.2;           // min wall between sensor shaft and plug surface
arrow_depth    = 0.5;           // engraved lead-direction arrow on plug underside

/* ------------------------- HOLLOWING (fast print) ------------------
   Wall values are multiples of the 0.4 mm nozzle line width (5 lines = 2.0 mm).
   Caps: big cavity open at the underside (no trapped void) under a solid roof.
   Bails: closed teardrop-section void in the barrel only (spigots stay solid
   round the magnet pockets). The teardrop apex points UP in print orientation,
   so the void is self-supporting. Set hollow_* = false for solid parts.      */
hollow_caps     = true;
cap_wall        = 2.0;          // wall of the plug/head round the cavity
cap_roof_z      = -6.0;         // cavity ceiling Z (seat floor is ~-3.35 -> ~2.6 mm roof)
boss_wall       = 2.0;          // solid wall kept round the sensor shaft
hollow_bail     = true;
bail_void_r     = 4.6;          // teardrop circle radius (apex = 1.414 * r above axis)
bail_void_margin= 5;            // keep this far from each barrel end (also the 45 deg taper)
bail_void_min_wall = 1.6;       // min plastic between void apex and groove bottom

/* ------------------------- PRINT PLATE ---------------------------- */
bail_print_roll = 90;           // roll about bail axis so magnet holes print sideways
plate_bail_x    = [-30, -60];
plate_big_x     = 25;           // column of 34.9 tops
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
function plug_r(d, pod) = pod/2;
function mag_x_long(d)  = x_tip(d) + mag_tip_long;

assert(abs(bail_len - bail_target) < 0.01, "bail length != 109.6");
assert(bail_len >= 109.5 && bail_len <= 111.13, "bail length outside 109.5..111.13");
assert(axis_h > 0, "barrel too big for max_projection");
assert(abs(groove_r - spigot_r - cove_r) < 1e-6, "cove_r must equal groove_r - spigot_r");
assert(pocket_depth + 3 < spigot_r*2, "magnet pocket too deep for spigot");
for (d = [top_d_big]) {
    assert(x_tip(d) + spigot_long >= d/2 + 0.5, "barrel face collides with off stump");
    assert(x_tip(d) + spigot_long + barrel_len <= spacing(d) - d/2 - 0.5, "barrel collides with middle stump");
    assert(x_tip_mid(d) + seat_end_clear <= -min_ridge, "middle seats collide");
}
// radial check of sensor shafts against plug wall (worst case = long-side shaft)
function shaft_reach(xm, d) =
    sqrt(pow(abs(xm) + sens_l/2 + sens_clear, 2) + pow(max(sens_w, sens_lead_w)/2 + sens_clear, 2));
for (pod = plug_ods)
    assert(shaft_reach(mag_x_long(top_d_big), top_d_big) + min_wall <= pod/2, "sensor shaft too close to plug pod");
assert(sens_ceil - (sens_d + sens_clear) > -head_h - plug_len + 3, "sensor pocket too deep for cap");
assert(!hollow_caps || (seat_bot - seat_rest_gap) - cap_roof_z >= 2.0, "cap roof thinner than 2 mm under the seat floor");
assert(!hollow_bail || groove_r - 1.4142*bail_void_r >= bail_void_min_wall, "bail void too close to groove bottom");
assert(!hollow_bail || bail_void_r + 3 <= groove_r, "bail void too big");

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

function td_apex() = 1.4142*bail_void_r;
module td2d() { hull() { circle(r = bail_void_r, $fn = 48); translate([0, td_apex()]) circle(r = 0.01, $fn = 8); } }
module void_slice(x, sc) {   // teardrop section; apex ends up pointing UP in the print orientation
    translate([x, 0, 0]) rotate([0,90,0]) rotate([0,0,90 - bail_print_roll])
        linear_extrude(0.01) scale([sc, sc]) td2d();
}
module bail_void() {         // closed void inside the barrel, 45 deg tapered ends
    xa = spigot_long + bail_void_margin;
    xb = spigot_long + barrel_len - bail_void_margin;
    t  = td_apex();
    hull() { void_slice(xa, 0.05); void_slice(xa + t, 1); void_slice(xb - t, 1); void_slice(xb, 0.05); }
}

module bail() {
    difference() {
        bail_solid();
        bail_pockets();
        if (hollow_bail) bail_void();
    }
}

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

module cap_body(d, pod) {
    Rp = plug_r(d, pod);
    rotate_extrude() head_profile(d/2);
    // 45 deg cone under the head: inside the pipe bore, makes the head underside self-supporting
    if (cone_r > Rp + 0.05)
        translate([0,0,-head_h])
            rotate_extrude() polygon([[Rp - 0.01, -(cone_r - Rp)], [cone_r, 0.01], [Rp - 0.01, 0.01]]);
    translate([0,0,-head_h - plug_len])
        rotate_extrude()
            polygon([[0,0],[Rp - plug_chamfer,0],[Rp,plug_chamfer],[Rp,plug_len+0.01],[0,plug_len+0.01]]);
}

// round cradle for the spigot, open upward, closed at the inner end by a pod
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

// hollow interior of the cap: open at the underside, solid roof, solid boss round the sensor shaft
module shaft_boss(xm, dir) {
    c = sens_clear; zb = -head_h - plug_len;
    w = max(sens_w, sens_lead_w) + 2*c + 2*boss_wall;
    L = sens_l + 2*c + sens_lead_room + 2*boss_wall;
    x0 = (dir > 0) ? xm - sens_l/2 - c - boss_wall : xm - sens_l/2 - c - sens_lead_room - boss_wall;
    translate([x0, -w/2, zb - 1]) cube([L, w, 40]);
}
module cap_cavity(d, pod, with_boss, xm = 0, dir = 1) {
    zb = -head_h - plug_len; Rc = plug_r(d, pod) - cap_wall;
    difference() {
        // wall cylinder, then a 45 deg cone up to a small flat ceiling (self-supporting)
        rotate_extrude($fn = 96)
            polygon([[0, zb - 0.01], [Rc, zb - 0.01], [Rc, cap_roof_z - (Rc - cavity_flat_r)],
                     [cavity_flat_r, cap_roof_z], [0, cap_roof_z]]);
        if (with_boss) shaft_boss(xm, dir);
    }
}

module wire_bore() {
    if (plug_bore_d > 0)
        translate([0,0,-head_h - plug_len - 0.01]) cylinder(d = plug_bore_d, h = plug_bore_depth, $fn = 48);
}

// kind: "off" | "middle" | "leg"
module stump_top(d, pod, kind) {
    Rh = d/2;
    xo = x_tip(d); xt = x_tip_mid(d);
    mirror([kind == "leg" ? 1 : 0, 0, 0])
    difference() {
        cap_body(d, pod);
        if (kind == "middle") {
            seat_channel(-Rh - 3, xt + seat_end_clear);          // bail 1 arrives from -X
            seat_channel(-(xt + seat_end_clear), Rh + 3);        // bail 2 arrives from +X
            // middle stump: NO Hall sensor, NO sensor pocket, NO wire channel
            if (hollow_caps) cap_cavity(d, pod, false);
        } else {
            seat_channel(xo - seat_end_clear, Rh + 3);           // open towards the gap
            sensor_cut(mag_x_long(d), +1);                       // only outer stumps carry a sensor
            if (hollow_caps) cap_cavity(d, pod, true, mag_x_long(d), +1);
            else wire_bore();
        }
    }
}

// ======================= PREVIEW HELPERS ============================
module sensor_ghost() {          // UA package: body + 3 leads, marked face at Z=0 (up)
    color("DimGray") translate([-sens_l/2, -sens_w/2, -sens_d]) cube([sens_l, sens_w, sens_d]);
    for (y = [-1.27, 0, 1.27]) color("Silver") translate([sens_l/2, y - 0.205, -sens_d/2 - 0.125]) cube([sens_lead_room, 0.41, 0.25]);
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

module assembly(d, pod) {
    stump_top(d, pod, "off");
    translate([sp(d),0,0]) stump_top(d, pod, "middle");
    translate([2*sp(d),0,0]) stump_top(d, pod, "leg");
    color("Tan") { bail1_world(d); bail2_world(d); }
    ghosts(d);
}

// ======================= PRINT ORIENTATION ==========================
module bail_print() {   // round bail, supports under it; axis along Y; lowest point on bed
    translate([0, 0, barrel_r])
        rotate([0,0,90]) translate([-bail_len/2, 0, 0]) rotate([bail_print_roll, 0, 0]) bail();
}
module top_print(d, pod, kind) { translate([0,0,head_h + plug_len]) stump_top(d, pod, kind); }

module cover(i) top_print(top_d_big, plug_ods[i], "off");   // off-stump cover, 34.9 head, insert = plug_ods[i]

module plate() {
    for (k = [0:1]) translate([plate_bail_x[k], 0, 0]) bail_print();
    for (k = [0:2]) translate([plate_big_x, plate_y[k], 0]) cover(k);
}

if      (PART == "plate")  plate();
else if (PART == "bail_1" || PART == "bail_2") bail_print();
else if (PART == "cover_1") cover(0);
else if (PART == "cover_2") cover(1);
else if (PART == "cover_3") cover(2);
else echo("Unknown PART:", PART);

echo(bail_len = bail_len, axis_h = axis_h, seat_bottom = seat_bot, sensor_ceiling = sens_ceil,
     plug_ods = plug_ods,
     spacing_big = spacing(top_d_big),
     x_tip_big = x_tip(top_d_big), x_tip_mid_big = x_tip_mid(top_d_big));

