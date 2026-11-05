// Рифма — ловчее кольцо / A sculptural poem, not a biological reconstruction.
// Pure POV-Ray geometry, materials, lighting and Cyrillic TrueType text.
// Render with render.py; clock=0..1 gently changes the ring aperture.
#version 3.7;

#declare Font = "DejaVuSerif.ttf";
#declare Ink = <0.016, 0.020, 0.025>;
#declare Ivory = <0.83, 0.74, 0.56>;
#declare Gold = <0.78, 0.43, 0.12>;
#declare Cinnabar = <0.46, 0.035, 0.022>;
#declare Jade = <0.15, 0.49, 0.40>;

#default { finish { ambient 0 diffuse 0.65 } }

global_settings {
  assumed_gamma 1.0
  charset utf8
  max_trace_level 10
  adc_bailout 0.015
  radiosity {
    pretrace_start 0.08 pretrace_end 0.02
    count 35 nearest_count 5 error_bound 1.4
    recursion_limit 1 low_error_factor 0.5
  }
}

#declare Paper = texture {
  pigment { color rgb Ivory }
  normal { bumps 0.15 scale 0.025 }
  finish { diffuse 0.80 specular 0.06 roughness 0.10 }
};
#declare Porcelain = texture {
  pigment { color rgb <0.79,0.81,0.70> }
  normal { bumps 0.035 scale 0.035 }
  finish { diffuse 0.62 specular 0.42 roughness 0.025 reflection 0.045 }
};
#declare Gilt = texture {
  pigment { color rgb Gold }
  normal { bumps 0.08 scale 0.023 }
  finish { metallic diffuse 0.32 specular 0.75 roughness 0.035 reflection 0.24 }
};
#declare RedCloth = texture {
  pigment { color rgb Cinnabar }
  normal { bumps 0.24 scale 0.026 }
  finish { diffuse 0.76 specular 0.1 roughness 0.15 }
};

camera {
  location <6.9, 6.5, -13.5>
  look_at <0.0, 2.0, 0.0>
  right x*image_width/image_height
  angle 46
}
background { color rgb Ink }
light_source {
  <-5.5, 9, -6> color rgb <1.0,0.82,0.61>*1.45
  area_light <4,0,0>,<0,0,4>,5,5 adaptive 1
}
light_source {
  <5, 6, 5> color rgb <0.37,0.76,0.78>*1.6
  area_light <3,0,0>,<0,3,0>,4,4 adaptive 1
}
light_source { <2.0,3.0,-8> color rgb <0.82,0.86,1.0>*0.28 shadowless }

plane {
  y,-0.1
  texture {
    pigment { color rgb <0.022,0.026,0.030> }
    normal { bumps 0.12 scale 0.12 }
    finish { diffuse 0.57 reflection 0.12 roughness 0.10 specular 0.18 }
  }
}

// Width-normalized, genuinely extruded text. Front faces point towards -z.
#macro Type(Text, Width, Depth, Surface, Position)
  #local Glyphs = text { ttf Font Text Depth,0 }
  #local Lo = min_extent(Glyphs);
  #local Hi = max_extent(Glyphs);
  #local S = Width/(Hi.x-Lo.x);
  object {
    Glyphs translate <-Lo.x,-Lo.y,0>
    scale S translate <-Width/2,0,0>
    texture { Surface }
    translate Position
  }
#end

// A cloth-bound open book: individual thin leaves catch side-light.
union {
  box { <-4.55,-0.08,-2.25>,<-0.06,0.045,2.25> rotate z*-5 texture { RedCloth } }
  box { <0.06,-0.08,-2.25>,<4.55,0.045,2.25> rotate z*5 texture { RedCloth } }
  #for (Leaf,0,14)
    #local Y = 0.055+Leaf*0.011;
    box { <-4.45,Y,-2.14>,<-0.04,Y+0.007,2.14> rotate z*-5 texture { Paper } }
    box { <0.04,Y,-2.14>,<4.45,Y+0.007,2.14> rotate z*5 texture { Paper } }
  #end
  cylinder { <0,0.025,-2.25>,<0,0.025,2.25>,0.07 texture { Gilt } }
}

// A few lines of the project's own poem rest on the pages, as raised print.
#macro PageLine(Text, Width, Position, Side)
  #local Glyphs = text { ttf Font Text 0.003,0 }
  #local Lo = min_extent(Glyphs);
  #local Hi = max_extent(Glyphs);
  object {
    Glyphs translate -Lo
    scale Width/(Hi.x-Lo.x)
    rotate x*90 rotate z*(Side*5)
    pigment { color rgb <0.12,0.08,0.045> }
    finish { diffuse 0.8 }
    translate Position
  }
#end
PageLine("В каталоге было тихо.",3.25,<-4.02,0.57,-1.75>,-1)
PageLine("Кто-то прочёл заглавие вслух.",3.25,<-4.02,0.57,-1.25>,-1)
PageLine("из букв уже тянулись гифы.",3.25,<-4.02,0.57,-0.75>,-1)
PageLine("Сначала ищешь слово.",3.22,<0.65,0.32,-1.75>,1)
PageLine("Потом оно не отпускает.",3.22,<0.65,0.32,-1.25>,1)

// Root-like handwriting branches across the paper; no bitmap textures.
#declare Seed = seed(4217);
#for (Root,0,34)
  #local A = Root*2*pi/35 + rand(Seed)*0.15;
  #local L = 1.6+rand(Seed)*2.8;
  #local EX = cos(A)*L;
  #local EZ = sin(A)*L*0.52;
  sphere_sweep {
    cubic_spline 7,
    <0,0.38,0>,0.022,
    <0,0.38,0>,0.022,
    <EX*0.28,0.38+abs(EX)*0.02,EZ*0.35>,0.028,
    <EX*0.60,0.34+abs(EX)*0.05,EZ*0.65+0.12*sin(A*4)>,0.024,
    <EX*0.85,0.32+abs(EX)*0.075,EZ*0.85>,0.017,
    <EX,0.32+abs(EX)*0.086,EZ>,0.009,
    <EX*1.03,0.32+abs(EX)*0.086,EZ*1.03>,0.006
    texture { Paper }
  }
  #if (mod(Root,2)=0)
    sphere_sweep {
      cubic_spline 5,
      <EX*0.45,0.39+abs(EX)*0.04,EZ*0.5>,0.012,
      <EX*0.50,0.39+abs(EX)*0.04,EZ*0.5>,0.012,
      <EX*0.65+0.20,0.36+abs(EX)*0.065,EZ*0.75-0.32>,0.011,
      <EX*0.8+0.40,0.35+abs(EX)*0.08,EZ*0.9-0.50>,0.005,
      <EX*0.9+0.50,0.35+abs(EX)*0.08,EZ-0.55>,0.003
      texture { Gilt }
    }
  #end
#end

// Porcelain mushrooms are deliberate literary fantasy, not a species claim.
#macro Mushroom(P, Height, CapSize, Tilt)
  union {
    sphere_sweep {
      cubic_spline 5,
      <0,-0.05,0>,0.065,
      <0,0,0>,0.065,
      <0.07,Height*0.5,0.05>,0.085,
      <0,Height,0>,0.068,
      <-0.03,Height+0.1,0>,0.06
      texture { Porcelain }
    }
    union {
      lathe {
        cubic_spline 10,
        <0,0.36>,<0,0.36>,<0.18,0.36>,<0.54,0.29>,<0.92,0.08>,
        <1,0>,<0.88,-0.05>,<0.36,0.15>,<0,0.18>,<0,0.18>
        texture { Porcelain }
      }
      #for (Gill,0,39)
        #local A = Gill*2*pi/40;
        cylinder {
          <0.14*cos(A),0.08,0.14*sin(A)>,
          <0.88*cos(A),-0.045,0.88*sin(A)>,0.012
          pigment { color rgb <0.35,0.16,0.065> }
          finish { diffuse 0.65 specular 0.22 }
        }
      #end
      scale CapSize rotate z*Tilt translate y*Height
    }
    translate P
  }
#end
Mushroom(<-3.2,0.63,0.70>,1.25,0.88,8)
Mushroom(<-2.05,0.54,1.16>,1.05,0.64,-9)
Mushroom(<-3.95,0.7,1.25>,0.80,0.50,11)
Mushroom(<-1.25,0.46,1.55>,0.69,0.43,-5)
Mushroom(<3.35,0.62,1.10>,0.70,0.48,9)
Mushroom(<2.70,0.57,1.55>,0.51,0.34,-7)

// Exactly three adjacent annular cells, each cut from a torus with planar septa.
// clock gives a reversible poetic breathing loop; not the timing of a live trap.
#declare Breath = 0.5-0.5*cos(2*pi*clock);
#declare Radius = 1.03;
#declare Tube = 0.27+0.10*Breath;
#declare RingCenter = <1.22,2.25,0.35>;
#declare Ring = union {
  #for (Cell,0,2)
    intersection {
      torus { Radius,Tube rotate x*90 }
      plane { <sin(radians(-59)), -cos(radians(-59)),0>,0 }
      plane { <-sin(radians(59)), cos(radians(59)),0>,0 }
      texture {
        pigment { color rgbf <0.19+Cell*0.012,0.55,0.44,0.16> }
        normal { bumps 0.025 scale 0.08 }
        finish { diffuse 0.51 specular 0.66 roughness 0.014 reflection 0.15 conserve_energy }
      }
      interior { ior 1.38 fade_color <0.25,0.7,0.5> fade_distance 0.8 fade_power 2 }
      rotate z*(Cell*120+30)
    }
  #end
};
object { Ring rotate y*-10 translate RingCenter }
sphere_sweep {
  cubic_spline 6,
  <0.2,0.38,0.45>,0.085,
  <0.2,0.38,0.45>,0.085,
  <0.75,0.57,0.40>,0.09,
  <1.12,0.76,0.36>,0.085,
  <1.22,0.96,0.35>,0.09,
  <1.25,1.10,0.35>,0.09
  texture { Porcelain }
}

// A word is the prey: gold, depth, shadows and reflections are all ray-traced.
#declare CapturedWord = Type("СЛОВО",1.88,0.12,Gilt,<0,0,0>)
object {
  CapturedWord
  rotate <0,-10,-12>
  translate <1.22,2.09,-0.12>
}
sphere_sweep {
  cubic_spline 8,
  <-1.22,0.55,-0.82>,0.017,
  <-1.16,0.57,-0.82>,0.02,
  <-0.52,0.86,-0.70>,0.03,
  <0.10,1.56,-0.32>,0.04,
  <0.72,2.12,-0.06>,0.035,
  <1.55,2.36,0.46>,0.028,
  <2.42,2.69,0.96>,0.02,
  <3.12,3.08,1.16>,0.012
  texture { Gilt }
}

// Sculptural title and scattered letters make language part of the still life.
Type("РИФМА",3.55,0.11,Porcelain,<-2.34,3.60,0.65>)
Type("ловчее кольцо",3.42,0.045,Gilt,<-2.34,3.12,0.60>)
Type("Хищные грибы Узбекистана",5.20,0.022,Porcelain,<0.15,0.04,-2.70>)

#declare Letters = array[5] { "Р", "И", "Ф", "М", "А" }
#for (L,0,4)
  #declare LooseGlyph = Type(Letters[L],0.23+mod(L,2)*0.05,0.12,Gilt,<0,0,0>)
  object {
    LooseGlyph
    rotate <0,(L-2)*12,(L-2)*8>
    translate <-3.55+L*0.72,0.69-L*0.025,-0.18+sin(L*1.2)*0.28>
  }
#end
