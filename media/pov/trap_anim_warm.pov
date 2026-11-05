// Three-cell constricting ring (Drechslerella-type) — 3D schematic animation.
// clock T in [0,1] over the clip: worm threads the ring, cells inflate INWARD, worm is held.
// Artistic schematic, time-stylised; not a reconstruction of an observed experiment.
#version 3.7;
global_settings { assumed_gamma 1.0 max_trace_level 10 }

#declare T = clock;
#macro Sm(a) (a*a*(3-2*a)) #end
#macro Seg(tt,a,b) (min(1, max(0, (tt-a)/(b-a)))) #end

// --- timeline ---------------------------------------------------------------
#declare Infl   = Sm(Seg(T, 0.46, 0.58));                     // ~1 s of an 8 s clip
#declare Enter  = Sm(Seg(T, 0.00, 0.47));                     // worm approach, eases in
#declare Held   = max(0, T - 0.50);
#declare HeadZ  = 6.5 - 10.3*Enter + 0.25*(1 - exp(-Held*6)); // head position along path (z)
#declare Wrig   = 0.22 * Infl * exp(-Held*4.0);               // decaying struggle after capture

// --- camera: slow orbit -------------------------------------------------------
#declare Az = radians(-30 + 50*Sm(T));
#declare CamR = 7.4;
camera { perspective location <sin(Az)*CamR, 1.8 + 0.3*Sm(T), -cos(Az)*CamR> look_at <0.1, -0.15, 0> angle 33 right x*16/9 }

light_source { <5, 9, -7> rgb <1.0, 0.95, 0.85> * 1.6 area_light <2,0,0>,<0,0,2>, 3, 3 adaptive 1 jitter }
light_source { <-6, 3, -3> rgb <0.9, 0.8, 0.6> * 0.5 shadowless }
light_source { <0, -4, 4> rgb <1.0, 0.8, 0.5> * 0.4 shadowless }
background { rgb <0.93, 0.87, 0.72> }
fog { fog_type 2 distance 22 rgb <0.93,0.87,0.72> fog_offset 0 fog_alt 6 up y }

// --- background hyphal lattice (static) ----------------------------------------
#declare LatTex = texture { pigment { rgbf <0.45,0.33,0.22,0.3> } finish { diffuse 0.6 ambient 0.1 } }
#declare S1 = seed(7);
#local i = 0;
#while (i < 40)
  #local p0 = <rand(S1)*16-8, rand(S1)*8-4, 4+rand(S1)*6>;
  #local p1 = p0 + <rand(S1)*3-1.5, rand(S1)*3-1.5, rand(S1)*2-1>;
  cylinder { p0, p1, 0.035 texture { LatTex } }
  #if (rand(S1) < 0.5) torus { 0.35+rand(S1)*0.4, 0.03 rotate <rand(S1)*180, rand(S1)*180, 0> translate p1 texture { LatTex } } #end
  #local i = i + 1;
#end
// drifting dust motes
#declare S2 = seed(3);
#local i = 0;
#while (i < 60)
  #local q = <rand(S2)*10-5, rand(S2)*6-3 + 0.3*sin(T*6.28 + i), rand(S2)*8-2>;
  sphere { q, 0.012 + 0.01*rand(S2) pigment { rgb <0.25,0.45,0.75> } finish { ambient 1 diffuse 0 } }
  #local i = i + 1;
#end

// --- ring cells ------------------------------------------------------------------
#declare CellTex = texture {
  pigment { rgbf <0.30, 0.68, 0.56, 0.45> }
  finish { ambient 0.15 diffuse 0.7 specular 0.6 roughness 0.02 reflection {0.03,0.10} }
}
#declare CellInt = interior { ior 1.36 fade_distance 1.2 fade_power 2 }
#declare R = 1.0;
#declare rCell0 = 0.26;
#macro Cell(a0)
  sphere_sweep { b_spline 12,
    #local i = 0;
    #while (i < 12)
      #local s = i/11;
      #local a = radians(a0 + 2 + s*116);
      #local bump = pow(sin(pi*s), 0.8);
      #local r  = rCell0 * (1 + 0.1*sin(pi*s)) + 0.24*Infl*bump;   // cell thickens (volume ~x3)
      #local rc = R - 0.30*Infl*bump;                               // growth is inward: centreline moves to the lumen
      <rc*cos(a), rc*sin(a), 0>, r
      #local i = i + 1;
    #end
    texture { CellTex } interior { CellInt }
  }
#end
union { Cell(90) Cell(210) Cell(330) }
// septa hint: thin darker discs at the three cell boundaries
#macro Septum(a0) cylinder { <R*cos(radians(a0)), R*sin(radians(a0)), -0.02>, <R*cos(radians(a0)), R*sin(radians(a0)), 0.02>, rCell0*0.98 + 0.02*Infl
  pigment { rgbf <0.2,0.35,0.3,0.6> } finish { diffuse 0.3 } } #end
Septum(90) Septum(210) Septum(330)
// stalk + supporting hypha
sphere_sweep { b_spline 6, <0,-1.25,0>,0.09 <0,-1.6,0.05>,0.09 <-0.3,-2.1,0.2>,0.1 <-1.2,-2.4,0.4>,0.1 <-2.6,-2.3,0.6>,0.1 <-4,-2.6,0.9>,0.1
  texture { pigment { rgbf <0.92,0.9,0.82,0.3> } finish { diffuse 0.7 specular 0.4 roughness 0.03 } } interior { ior 1.3 } }

// --- nematode ----------------------------------------------------------------------
// path parameter u = z. Body from the head back along +z. Smooth, legless, tapered both ends,
// anterior blunter than the posterior.
#declare BodyLen = 9.5;
#macro WormPt(s)   // s: 0 head .. 1 tail
  #local pz = HeadZ + BodyLen*s;
  #local px = 0.8*sin(pz*0.6 + 0.4) - 1.3*max(0, (-pz-0.3))*0.5 + Wrig*sin(Held*40 + pz*1.5);
  #local py = 0.18*sin(pz*0.45 + 1.0) - 0.05 + 0.5*Wrig*cos(Held*33 + pz*1.2);
  <px, py, pz>
#end
#macro WormR(s)
  #local pz = HeadZ + BodyLen*s;
  #local taper = (s < 0.08 ? pow(s/0.08, 0.45)*0.95 + 0.05 : (s > 0.72 ? pow(1-(s-0.72)/0.28, 0.75) : 1));
  #local g  = exp(-pow(pz/0.42, 2));
  #local gb = exp(-pow((abs(pz)-0.85)/0.32, 2));
  0.30*(0.08 + 0.92*taper) * (1 - 0.40*Infl*g) * (1 + 0.10*Infl*gb)
#end
sphere_sweep { b_spline 26,
  #local i = 0;
  #while (i < 26)
    #local s = i/25;
    WormPt(s), WormR(s)
    #local i = i + 1;
  #end
  tolerance 1e-5
  texture { pigment { rgbf <0.98, 0.62, 0.20, 0.35> } finish { ambient 0.12 diffuse 0.7 specular 0.7 roughness 0.015 reflection {0.02,0.08} } }
  interior { ior 1.4 fade_distance 0.6 fade_power 2 fade_color <0.9,0.5,0.1> }
}
plane { y, -3 pigment { rgb <0.90,0.82,0.62> } normal { bumps 0.3 scale 0.4 } finish { diffuse 0.75 ambient 0.2 } }
// patterned ceramic rim far behind: cobalt and white stripes
plane { z, 14 pigment { gradient x color_map { [0 rgb <0.55,0.66,0.86>] [0.5 rgb <0.55,0.66,0.86>] [0.5 rgb <0.95,0.92,0.84>] [1 rgb <0.95,0.92,0.84>] } scale 1.2 } finish { diffuse 0.7 ambient 0.2 } }
