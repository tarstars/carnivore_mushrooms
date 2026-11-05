// Three-cell constricting ring (Drechslerella-type), schematic 3D. clock = inflation 0..1
#version 3.7;
#include "colors.inc"
global_settings { assumed_gamma 1.0 max_trace_level 12 }
#declare Infl = clock;

camera { perspective location <3.2, 1.9, -6.6> look_at <0.1, -0.1, 0> angle 34 right x*16/9 }
light_source { <6, 8, -6> rgb <1.0, 0.92, 0.8> * 1.3 area_light <2,0,0>,<0,0,2>, 5, 5 adaptive 1 jitter }
light_source { <-6, 2, -3> rgb <0.5, 0.75, 0.9> * 0.6 shadowless }
light_source { <0, -4, 4> rgb <0.9, 0.6, 0.3> * 0.5 shadowless }
background { rgb <0.05, 0.06, 0.16> }
fog { fog_type 2 distance 16 rgb <0.05,0.06,0.16> fog_offset 0 fog_alt 6 up y }
// faint hyphal lattice behind the scene
#declare LatTex = texture { pigment { rgbf <0.9,0.9,0.85,0.4> } finish { diffuse 0.5 ambient 0.05 } }
#declare seed1 = seed(7);
#local i = 0;
#while (i < 40)
  #local p0 = <rand(seed1)*16-8, rand(seed1)*8-4, 4+rand(seed1)*6>;
  #local p1 = p0 + <rand(seed1)*3-1.5, rand(seed1)*3-1.5, rand(seed1)*2-1>;
  cylinder { p0, p1, 0.035 texture { LatTex } }
  #if (rand(seed1) < 0.5) torus { 0.35+rand(seed1)*0.4, 0.03 rotate <rand(seed1)*180, rand(seed1)*180, 0> translate p1 texture { LatTex } } #end
  #local i = i + 1;
#end

#declare CellTex = texture {
  pigment { rgbf <0.66, 0.87, 0.78, 0.55> }
  finish { ambient 0.08 diffuse 0.6 specular 0.6 roughness 0.02 reflection {0.03,0.12} }
}
#declare CellInt = interior { ior 1.36 fade_distance 1.2 fade_power 2 }

#declare R = 1.0;          // ring radius (centre line of cells)
#declare rCell0 = 0.26;    // resting cell thickness
// each cell: 120 degrees of a torus-like sweep, inflating INWARD (thicker toward the centre)
#macro Cell(a0)
  sphere_sweep { b_spline 12,
    #local i = 0;
    #while (i < 12)
      #local s = i/11;
      #local a = radians(a0 + 2 + s*116);
      #local bump = pow(sin(pi*s), 0.8);
      #local r = rCell0 * (1 + 0.1*sin(pi*s)) + 0.24*Infl*bump;  // cell thickens (volume ~x3)
      #local rc = R - 0.30*Infl*bump;                              // and the growth is INWARD: centreline moves to the lumen
      <rc*cos(a), rc*sin(a), 0>, r
      #local i = i + 1;
    #end
    texture { CellTex } interior { CellInt }
  }
#end
union { Cell(90) Cell(210) Cell(330) }
// stalk + hypha
sphere_sweep { b_spline 6, <0,-1.25,0>,0.09 <0,-1.6,0.05>,0.09 <-0.3,-2.1,0.2>,0.1 <-1.2,-2.4,0.4>,0.1 <-2.6,-2.3,0.6>,0.1 <-4,-2.6,0.9>,0.1
  texture { pigment { rgbf <0.92,0.9,0.82,0.3> } finish { diffuse 0.7 specular 0.4 roughness 0.03 } } interior { ior 1.3 } }
// nematode: tapered sphere_sweep through the ring along z, with an S bend
#declare Pinch = 1 - 0.35*Infl;
sphere_sweep { b_spline 14,
  #local i = 0;
  #while (i < 14)
    #local s = i/13;                 // 0 tail (far, +z) .. 1 head (near, -z)
    #local pz = 5.0 - 11*s;
    #local px = 0.8*sin(s*2*pi*0.9 + 0.4) - 1.2*max(0, s-0.55);
    #local py = 0.25*sin(s*2*pi*0.6) - 0.05;
    #local taper = (s < 0.85 ? pow(sin(pi*(0.08+0.92*s)), 0.5) : pow(1-(s-0.85)/0.15, 0.5)*0.9+0.1);
    #local g = exp(-pow(pz/0.45, 2));
    #local r = 0.30*(0.3 + 0.7*taper) * (1 - (1-Pinch)*g);
    <px, py, pz>, r
    #local i = i + 1;
  #end
  texture { pigment { rgbf <0.95, 0.72, 0.32, 0.45> } finish { ambient 0.05 diffuse 0.6 specular 0.7 roughness 0.015 reflection {0.02,0.1} } }
  interior { ior 1.4 fade_distance 0.6 fade_power 2 fade_color <0.9,0.5,0.1> }
}
// soil floor + dust
plane { y, -3 pigment { rgb <0.09,0.07,0.06> } normal { granite 0.6 scale 0.5 } finish { diffuse 0.5 } }
