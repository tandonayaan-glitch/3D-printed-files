// Automatic Filament Cutter + blue mounting clip
// NOTE: dimensions estimated from the reference image (product page was unreachable).
$fn = 48;

show_body = true;
show_clip = true;
show_tube = true;

// ---- Body ----
body_w = 30;   // X
body_d = 14;   // Y
body_h = 42;   // Z
wall_r = 2;

// ---- Tube ----
tube_od = 4;
tube_id = 2;
tube_len = 60;
tube_bend = 14;   // sideways curve at top

module rounded_box(w, d, h, r) {
    hull() for (x = [r, w - r], y = [r, d - r])
        translate([x, y, 0]) cylinder(r = r, h = h);
}

module body() {
    difference() {
        // main block with chamfered top-right corner
        intersection() {
            rounded_box(body_w, body_d, body_h, wall_r);
            // chamfer profile in XZ
            rotate([90, 0, 0]) translate([0, 0, -body_d - 1])
                linear_extrude(body_d + 2)
                    polygon([[0,0],[body_w,0],[body_w,body_h-12],
                             [body_w-10,body_h],[0,body_h]]);
        }
        // filament entry hole on top
        translate([8, body_d/2, body_h - 6]) cylinder(d = tube_od, h = 7);
        // keyhole / finger slot, lower right (through Y)
        hull() {
            translate([body_w - 9, -1, 8])  rotate([-90,0,0]) cylinder(d = 5, h = body_d + 2);
            translate([body_w - 4, -1, 20]) rotate([-90,0,0]) cylinder(d = 5, h = body_d + 2);
        }
        // blue indicator light slots
        for (z = [body_h - 14, body_h - 21])
            translate([8, -0.01, z]) cube([8, 0.8, 1.6]);
    }
    // blue LED strips (inlay)
    color("DeepSkyBlue")
        for (z = [body_h - 14, body_h - 21])
            translate([8, -0.4, z]) cube([8, 0.8, 1.6]);
    // metal cutter pin
    color("Silver")
        translate([body_w - 8, -0.8, 21]) rotate([-90,0,0]) cylinder(d = 4, h = 1.2);
    // blue side button
    color("DeepSkyBlue")
        translate([-1.5, body_d/2 - 2, 26]) cube([2, 4, 6]);
}

module tube() {
    color("LightGray", 0.6)
    translate([8, body_d/2, body_h - 6])
    // gentle arc: stack of angled segments
    for (i = [0 : 11]) {
        t0 = i / 12; t1 = (i + 1) / 12;
        hull() {
            translate([tube_bend * pow(t0, 2), 0, tube_len * t0]) sphere(d = tube_od);
            translate([tube_bend * pow(t1, 2), 0, tube_len * t1]) sphere(d = tube_od);
        }
    }
}

// ---- Blue C-clip (U-shaped bracket with hook ends and centre hole) ----
clip_w = 8;      // extrusion width (Y)
clip_len = 34;   // X span
clip_t = 2;
clip_leg = 9;

module clip() {
    color("RoyalBlue")
    difference() {
        linear_extrude(clip_w)
            union() {
                // base bar
                translate([0, 0]) square([clip_len, clip_t]);
                // left hook
                translate([0, 0]) square([clip_t, clip_leg]);
                translate([0, clip_leg - clip_t]) square([6, clip_t]);
                // right angled leg with grip ribs
                hull() {
                    translate([clip_len - clip_t, 0]) square([clip_t, 1]);
                    translate([clip_len + 3, clip_leg]) square([clip_t, 1]);
                }
                for (i = [0 : 3])
                    translate([clip_len + 1 + i * 1, clip_leg - 1.5 + i * 0.2]) square([0.8, 2.5]);
            }
        // centre screw hole
        translate([clip_len / 2, -1, clip_w / 2]) rotate([-90, 0, 0]) cylinder(d = 3, h = clip_t + 2);
    }
}

if (show_body) body();
if (show_tube) tube();
if (show_clip) translate([-55, 0, 8]) rotate([90, 0, 0]) clip();
