// =====================================================================
// Cricket bails + stump top covers (off / middle / leg) with A1334 Hall
// sensor pockets and 2x2 mm magnet pockets.  All units mm.
//
// PART = "plate" | "bails" | "off_cap" | "middle_cap" | "leg_cap"
//        | "assembly" (visual check only, not for printing)
//
// Coordinate convention (wicket line = X axis, +Z up):
//   off stump centre  x = 0
//   middle stump      x = stump_spacing
//   leg stump         x = 2*stump_spacing
//   Bail 1 spans off->middle (long spigot on off stump).
//   Bail 2 spans leg->middle (long spigot on leg stump).
//   Both short spigots land on the middle stump from opposite sides.
//   Z = 0 is the apex of the stump-top dome ("stump top" reference).
// =====================================================================

PART = "plate";

$fn = 96;

/* ---------------- Bail (all lathe-turned dimensions) --------------- */
barrel_len      = 54;     // central barrel
spigot_long     = 35;
spigot_short    = 20.6;
// total = 35 + 54 + 20.6 = 109.6 (allowed 109.5 .. 111.13)
bail_target_len = 109.6;

max_projection  = 12.7;   // highest point of bail above stump top (Z=0)
barrel_r        = 10.5;   // radius of the main beads
barrel_r_end    = 9.9;    // slightly smaller end beads
groove_r        = 8.3;    // radius at the bottom of the narrow grooves
groove_w        = 1.6;    // groove width (>= 4 extrusion widths)
bead_count      = 4;
spigot_r        = 5.5;    // spigot radius (dia 11)
cove_r          = 2.8;    // smooth cove from spigot up to barrel (= groove_r - spigot_r)
spigot_chamfer  = 0.8;
print_flat      = 0.9;    // flat on the bottom of the bail (bed + seat contact)

/* ---------------- Magnets ------------------------------------------ */
mag_d           = 2.0;
mag_h           = 2.0;
mag_tol         = 0.15;   // radial clearance per side (hole = 2.3 mm)
mag_recess      = 0.3;    // magnet face sits this far above the bail flat
mag_from_tip_long  = 6;   // magnet centre distance from long-spigot tip
mag_from_tip_short = 5;   // ... from short-spigot tip
// Magnet axis is vertical. Install ALL FOUR magnets with the SAME pole
// facing down (towards the sensor). Mark that pole with a marker first.

/* ---------------- Stump / PVC pipe --------------------------------- */
pipe_od         = 33.5;
pipe_id         = 31.2;
plug_fit        = 0.40;   // ADJUST: plug OD = pipe_id - plug_fit. Larger = looser.
plug_len        = 16;
plug_bore_d     = 10;     // weight/material saving bore from underside (0 = none)
plug_bore_depth = 10;
plug_chamfer    = 1.0;    // lead-in at the bottom of the plug
stump_spacing   = 97.55;  // centre-to-centre: (228.6 - 33.5)/2 (laws of cricket width)

/* ---------------- Cap head ----------------------------------------- */
head_h          = 10;     // visible head height below the dome apex
dome_sag        = 2.2;    // dome drop from apex to rim start
edge_round      = 1.5;    // rim roundover
ring_z          = -6.5;   // turned decorative ring groove position (0 = off via ring_depth)
ring_depth      = 0.6;

/* ---------------- Bail seats --------------------------------------- */
seat_clear      = 0.30;   // radial clearance round spigot
seat_end_clear  = 0.40;   // clearance between spigot tip and seat end wall
tip_inset       = 2.0;    // long spigot tip sits this far inside the outer rim
min_ridge       = 1.0;    // min half-width of ridge between the two middle seats

/* ---------------- Hall sensor pocket (CHECK against your PCB!) ----- */
sens_len        = 6.0;    // PCB size along the bail axis (X)
sens_wid        = 5.0;    // PCB size across the bail (Y)
sens_pcb_t      = 1.0;    // PCB thickness
sens_comp_h     = 1.2;    // component height above PCB (IC side faces UP to magnet)
sens_clear      = 0.25;   // clearance per side
sens_ic_dx      = 0;      // IC centre offset from PCB centre (X)
sens_ic_dy      = 0;      // IC centre offset from PCB centre (Y)
sens_floor      = 0.8;    // plastic between seat floor and sensor pocket (4 layers)
min_wall        = 1.2;    // min wall between sensor shaft and pipe-fit plug surface

/* ---------------- Print plate -------------------------------------- */
plate_bail_x    = [-30, -60];
plate_cap_x     = 32;
plate_cap_y     = [-45, 0, 45];

// ===================== DERIVED VALUES (do not edit) ================
bail_len   = spigot_long + barrel_len + spigot_short;
axis_h     = max_projection - barrel_r;            // bail axis above Z=0
seat_floor = axis_h - spigot_r + print_flat;        // Z of seat floor (flat contact)
sens_ceil  = seat_floor - sens_floor;               // top of sensor pocket
Rh         = pipe_od/2;
Rp         = (pipe_id - plug_fit)/2;
x_tip      = -Rh + tip_inset;                       // long tip in off-cap local X
x_tip_mid  = x_tip + bail_len - stump_spacing;      // short tip in middle-cap local X
sens_pocket_h = sens_pcb_t + sens_comp_h + 0.3;     // info: should be <= depth you have
mag_x_long  = x_tip + mag_from_tip_long;            // magnet X in off-cap local
mag_x_short = x_tip_mid - mag_from_tip_short;       // magnet X in middle-cap (left seat)

// ---- sanity checks (fail loudly instead of rendering a bad part) ----
assert(abs(bail_len - bail_target_len) < 0.01, "bail length != target");
assert(bail_len >= 109.5 && bail_len <= 111.13, "bail length outside 109.5..111.13");
assert(abs(axis_h + barrel_r - max_projection) < 1e-6, "projection mismatch");
assert(axis_h > 0, "barrel too large for max_projection");
assert(groove_r - spigot_r >= cove_r - 1e-6, "cove_r too large");
assert(Rp < pipe_id/2, "plug does not fit inside pipe");
assert(x_tip + spigot_long >= Rh + 0.5, "barrel face collides with off stump");
assert(x_tip + spigot_long + barrel_len <= stump_spacing - Rh - 0.5, "barrel collides with middle stump");
assert(x_tip_mid + seat_end_clear <= -min_ridge, "middle seats collide - increase stump_spacing or shorten spigot");
assert(sqrt(pow(abs(mag_x_long)+sens_len/2+sens_clear,2)+pow(sens_wid/2+sens_clear,2)) + min_wall <= Rp, "long-side sensor shaft too close to plug wall");
assert(sqrt(pow(abs(mag_x_short)+sens_len/2+sens_clear,2)+pow(sens_wid/2+sens_clear,2)) + min_wall <= Rp, "middle sensor shaft too close to plug wall");
assert(sens_pocket_h <= (head_h + plug_len) - 0, "sensor pocket too tall");

// ============================ BAIL =================================
// Local frame: X along bail, 0 = long-spigot tip, axis at Y=Z=0.
function arc_pts(cx, cy, r, a0, a1, n=14) =
    [for (i=[0:n]) let(a = a0 + (a1-a0)*i/n) [cx + r*cos(a), cy + r*sin(a)]];

function bead_pts(x0, bw, rb, rg) =
    let(h = rb - rg,
        R = (bw*bw/4 + h*h)/(2*h),
        th = asin((bw/2)/R),
        cx = x0 + bw/2, cy = rb - R)
    arc_pts(cx, cy, R, 90+th, 90-th, 16);

function barrel_pts(xf) =
    let(n = bead_count,
        bw = (barrel_len - (n-1)*groove_w)/n)
    [ for (i=[0:n-1])
        let(x0 = xf + i*(bw+groove_w),
            rb = (i==0 || i==n-1) ? barrel_r_end : barrel_r)
        each concat(bead_pts(x0, bw, rb, groove_r),
                    (i<n-1) ? [[x0+bw+groove_w, groove_r]] : [])
    ];

// polygon in (radius, x) for rotate_extrude
function bail_poly() =
    let(xf1 = spigot_long,
        xf2 = spigot_long + barrel_len,
        L   = bail_len)
    concat(
        [[0,0], [spigot_r - spigot_chamfer, 0], [spigot_r, spigot_chamfer]],
        // cove up from long spigot into barrel
        [for (p = arc_pts(xf1-cove_r, spigot_r+cove_r, cove_r, -90, 0, 12)) [p[1], p[0]]],
        [for (p = barrel_pts(xf1)) [p[1], p[0]]],
        // cove down to short spigot
        [for (p = arc_pts(xf2+cove_r, spigot_r+cove_r, cove_r, 180, 270, 12)) [p[1], p[0]]],
        [[spigot_r, L - spigot_chamfer], [spigot_r - spigot_chamfer, L], [0, L]]
    );

module bail_solid() {            // uncut lathe body, axis along +X
    rotate([0,90,0]) rotate_extrude() polygon(bail_poly());
}

module bail_magnet_pockets() {
    zb = -(spigot_r - print_flat);
    for (x = [mag_from_tip_long, bail_len - mag_from_tip_short])
        translate([x, 0, zb - 0.01])
            cylinder(d = mag_d + 2*mag_tol, h = mag_h + mag_recess + 0.01, $fn = 32);
}

module bail() {                  // axis on Z=0, flat underside at Z = -(spigot_r-print_flat)
    zb = -(spigot_r - print_flat);
    difference() {
        bail_solid();
        translate([-1, -50, zb - 50]) cube([bail_len + 2, 100, 50]);
        bail_magnet_pockets();
    }
}

// ============================ CAPS =================================
module head_profile() {
    Rd = Rh - edge_round;
    Rs = (Rd*Rd + dome_sag*dome_sag) / (2*dome_sag);
    zs = -dome_sag - edge_round;
    ring = (ring_depth > 0)
        ? [[Rh, ring_z - 0.9], [Rh - ring_depth, ring_z], [Rh, ring_z + 0.9]] : [];
    dome = [for (i=[0:24]) let(r = Rd*(1 - i/24)) [r, -(Rs - sqrt(Rs*Rs - r*r))]];
    fil  = [for (i=[0:10]) let(a = 90*i/10) [Rd + edge_round*sin(a), -dome_sag - edge_round + edge_round*cos(a)]];
    polygon(concat([[0, -head_h], [Rh, -head_h]], ring, [[Rh, zs]], fil, dome));
}

module cap_body() {
    rotate_extrude() head_profile();
    // pipe plug
    translate([0, 0, -head_h - plug_len])
        rotate_extrude() polygon([[0,0],[Rp - plug_chamfer,0],[Rp,plug_chamfer],[Rp,plug_len+0.01],[0,plug_len+0.01]]);
}

// seat channel along X from xa to xb (xa<xb), centred on Y=0
module seat_channel(xa, xb) {
    rg = spigot_r + seat_clear;
    len = xb - xa;
    intersection() {
        union() {
            translate([xa, 0, axis_h]) rotate([0,90,0]) cylinder(r = rg, h = len);
            translate([xa, -rg, axis_h]) cube([len, 2*rg, 30]);
        }
        translate([xa - 1, -50, seat_floor]) cube([len + 2, 100, 100]);
    }
}

// vertical sensor shaft from underside of plug up to the pocket ceiling
module sensor_shaft(xm) {
    zbot = -head_h - plug_len - 1;
    // PCB centre = IC centre (under the magnet) minus the IC offset on the PCB
    translate([xm - sens_ic_dx - sens_len/2 - sens_clear,
               - sens_ic_dy - sens_wid/2 - sens_clear,
               zbot])
        cube([sens_len + 2*sens_clear, sens_wid + 2*sens_clear, sens_ceil - zbot]);
}

module wire_bore() {
    if (plug_bore_d > 0)
        translate([0, 0, -head_h - plug_len - 0.01])
            cylinder(d = plug_bore_d, h = plug_bore_depth, $fn = 48);
}

// side = +1 : seat open towards +X (off stump).  side = -1 : mirrored (leg stump).
module cap_single(side) {
    mirror([side < 0 ? 1 : 0, 0, 0])
    difference() {
        cap_body();
        seat_channel(x_tip - seat_end_clear, Rh + 3);
        sensor_shaft(mag_x_long);
        wire_bore();
    }
}

module off_cap()  { cap_single(+1); }
module leg_cap()  { cap_single(-1); }

module middle_cap() {
    difference() {
        cap_body();
        // bail 1 arrives from -X, bail 2 from +X
        seat_channel(-Rh - 3, x_tip_mid + seat_end_clear);
        seat_channel(-(x_tip_mid + seat_end_clear), Rh + 3);
        sensor_shaft(mag_x_short);
        sensor_shaft(-mag_x_short);
        wire_bore();
    }
}

// ======================= PRINT PLATE / PARTS =======================
module bail_print() {   // flat side down, axis along Y
    rotate([0,0,90]) translate([-bail_len/2, 0, spigot_r - print_flat]) bail();
}
module cap_print(c) {   // plug on the bed, dome up
    translate([0,0, head_h + plug_len]) {
        if (c == "off")    off_cap();
        if (c == "middle") middle_cap();
        if (c == "leg")    leg_cap();
    }
}

module bails_print()  { for (x = plate_bail_x) translate([x, 0, 0]) bail_print(); }
module caps_print() {
    translate([plate_cap_x, plate_cap_y[0], 0]) cap_print("off");
    translate([plate_cap_x, plate_cap_y[1], 0]) cap_print("middle");
    translate([plate_cap_x, plate_cap_y[2], 0]) cap_print("leg");
}

// bails in assembled (world) position, for the visual/clash check
module bail1_world() translate([x_tip, 0, axis_h]) bail();
module bail2_world() translate([2*stump_spacing - x_tip, 0, axis_h]) rotate([0,0,180]) bail();

module assembly() {
    off_cap();
    translate([stump_spacing, 0, 0]) middle_cap();
    translate([2*stump_spacing, 0, 0]) leg_cap();
    color("Tan") { bail1_world(); bail2_world(); }
}

if (PART == "plate")           { bails_print(); caps_print(); }
else if (PART == "bails")      { bails_print(); }
else if (PART == "off_cap")    { cap_print("off"); }
else if (PART == "middle_cap") { cap_print("middle"); }
else if (PART == "leg_cap")    { cap_print("leg"); }
else if (PART == "assembly")   { assembly(); }
else echo("Unknown PART:", PART);

echo(bail_len = bail_len, axis_h = axis_h, seat_floor = seat_floor,
     sens_ceiling = sens_ceil, plug_od = 2*Rp, x_tip = x_tip, x_tip_mid = x_tip_mid,
     mag_x_long = mag_x_long, mag_x_short = mag_x_short);
