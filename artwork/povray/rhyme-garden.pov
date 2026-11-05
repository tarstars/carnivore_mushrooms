// ЖИВАЯ РИФМА — a sunlit, fertile, playful revision of the sculptural poem.
// A literary garden inspired by the project, not a biological reconstruction.
#version 3.7;
#declare Font = "DejaVuSerif.ttf";
#declare Cream = <0.97,0.88,0.63>;
#declare Turquoise = <0.015,0.52,0.57>;
#declare Cobalt = <0.025,0.16,0.61>;
#declare Coral = <0.89,0.105,0.04>;
#declare Marigold = <1.0,0.55,0.015>;
#declare Green = <0.18,0.47,0.045>;
#declare Gold = <0.98,0.55,0.10>;
#default { finish { ambient 0 diffuse 0.7 } }

global_settings {
  assumed_gamma 1.0 charset utf8 max_trace_level 9 adc_bailout 0.012
  radiosity {
    pretrace_start 0.08 pretrace_end 0.02 count 45 nearest_count 5
    error_bound 1.4 recursion_limit 1 low_error_factor 0.5
  }
}

#macro Glaze(C)
  texture {
    pigment { color rgb C }
    normal { bumps 0.018 scale 0.05 }
    finish { diffuse 0.65 specular 0.62 roughness 0.025 reflection 0.055 }
  }
#end
#declare Paper = texture {
  pigment { color rgb Cream }
  normal { bumps 0.075 scale 0.018 }
  finish { diffuse 0.81 specular 0.09 roughness 0.1 }
};
#declare Milk = Glaze(<0.98,0.94,0.77>)
#declare RedGlaze = Glaze(Coral)
#declare BlueGlaze = Glaze(Cobalt)
#declare AquaGlaze = Glaze(Turquoise)
#declare YellowGlaze = Glaze(Marigold)
#declare TitleGlaze = texture {
  pigment { color rgb <0.80,0.045,0.018> }
  finish { diffuse 0.70 specular 0.35 roughness 0.03 emission 0.07 }
};
#declare Gilt = texture {
  pigment { color rgb Gold }
  finish { metallic diffuse 0.52 specular 0.6 roughness 0.035 reflection 0.14 }
};
#declare LeafTexture = texture {
  pigment { gradient y color_map {
    [0 color rgb <0.055,0.22,0.018>]
    [0.55 color rgb <0.30,0.61,0.055>]
    [1 color rgb <0.53,0.72,0.09>]
  } scale 1.3 }
  finish { diffuse 0.72 specular 0.32 roughness 0.045 }
};

camera {
  location <6.8,6.7,-13.8>
  look_at <-0.05,2.15,0.15>
  right x*image_width/image_height angle 46
}
sky_sphere {
  pigment { gradient y color_map {
    [0.0 color rgb <1.0,0.79,0.49>]
    [0.45 color rgb <0.86,0.94,0.91>]
    [1.0 color rgb <0.38,0.77,0.91>]
  } scale 2 translate -y }
}
light_source {
  <-5,11,-7> color rgb <1,0.88,0.65>*1.20
  area_light <5,0,0>,<0,0,5>,5,5 adaptive 1
}
light_source {
  <6,8,-1> color rgb <0.69,0.91,1>*0.65
  area_light <4,0,0>,<0,0,4>,4,4 adaptive 1
}
light_source {
  <-1,7,7> color rgb <1,0.66,0.30>*0.85
  area_light <3,0,0>,<0,3,0>,4,4 adaptive 1
}

// Bright water brings movement, moisture and reflected colour into the scene.
plane {
  y,-0.30
  texture {
    pigment { color rgb <0.48,0.84,0.85> }
    normal { ripples 0.13 frequency 1.6 scale 1.2 }
    finish { diffuse 0.63 emission 0.12 specular 0.55 roughness 0.035 reflection 0.08 }
  }
}
#for (Ripple,0,5)
  torus {
    4.7+Ripple*0.44,0.008
    scale <1,1,0.66> translate <0,-0.28,0>
    pigment { color rgb <0.68,0.96,0.91> }
    finish { diffuse 0.6 specular 0.6 }
  }
#end

#macro Type(Text, Width, Depth, Surface, Position)
  #local Glyph = text { ttf Font Text Depth,0 }
  #local Lo = min_extent(Glyph);
  #local Hi = max_extent(Glyph);
  object {
    Glyph translate <-Lo.x,-Lo.y,0> scale Width/(Hi.x-Lo.x)
    translate <-Width/2,0,0> texture { Surface } translate Position
  }
#end

// A painted tile becomes the little island carrying the open book.
box { <-4.88,-0.20,-2.65>,<4.88,0.02,2.65> texture { BlueGlaze } }
#macro Star(P,R,Surface)
  mesh {
    #for (K,0,15)
      #local A = K*2*pi/16;
      #local B = (K+1)*2*pi/16;
      #local RA = R*select(mod(K,2)-0.5,1,0.43);
      #local RB = R*select(mod(K+1,2)-0.5,1,0.43);
      triangle { <0,0,0>,<RA*cos(A),0,RA*sin(A)>,<RB*cos(B),0,RB*sin(B)> }
    #end
    texture { Surface } translate P
  }
#end
#for (Tile,0,14)
  #local X = -4.55+Tile*0.65;
  #for (Side,-1,1,2)
    box { <X-0.29,0.025,Side*2.45-0.16>,<X+0.29,0.045,Side*2.45+0.16> texture { AquaGlaze } }
    Star(<X,0.046,Side*2.45>,0.145,Milk)
    sphere { <X,0.048,Side*2.45>,0.027 scale <1,0.24,1> texture { Gilt } }
  #end
#end

// Warm paper with a red cover and luminous gold edges.
union {
  box { <-4.52,0.025,-2.20>,<-0.06,0.13,2.20> rotate z*-5 texture { RedGlaze } }
  box { <0.06,0.025,-2.20>,<4.52,0.13,2.20> rotate z*5 texture { RedGlaze } }
  #for (Page,0,13)
    #local Y = 0.14+Page*0.012;
    box { <-4.42,Y,-2.09>,<-0.04,Y+0.008,2.09> rotate z*-5 texture { Paper } }
    box { <0.04,Y,-2.09>,<4.42,Y+0.008,2.09> rotate z*5 texture { Paper } }
  #end
  cylinder { <0,0.18,-2.20>,<0,0.18,2.20>,0.065 texture { Gilt } }
}
#macro PageLine(Text,Width,P,Side)
  #local Glyph = text { ttf Font Text 0.003,0 }
  #local Lo = min_extent(Glyph);
  #local Hi = max_extent(Glyph);
  object {
    Glyph translate -Lo scale Width/(Hi.x-Lo.x)
    rotate x*90 rotate z*(Side*5)
    pigment { color rgb <0.30,0.09,0.035> } finish { diffuse 0.8 }
    translate P
  }
#end
PageLine("Кто-то прочёл заглавие вслух.",3.15,<-4.02,0.66,-1.80>,-1)
PageLine("из букв уже тянулись гифы.",3.15,<-4.02,0.66,-1.30>,-1)
PageLine("Сначала ищешь слово.",3.18,<0.62,0.41,-1.80>,1)
PageLine("Потом оно не отпускает.",3.18,<0.62,0.41,-1.30>,1)

// Round, curling hyphae replace the earlier dry starburst.
#for (Vine,0,15)
  #local A = Vine*2*pi/16;
  #local L = 1.8+0.7*mod(Vine,4);
  sphere_sweep {
    cubic_spline 8,
    <0,0.47,0>,0.025,<0,0.47,0>,0.025,
    <0.5*cos(A),0.50,0.35*sin(A)>,0.030,
    <1.5*cos(A+0.25),0.58,0.75*sin(A+0.25)>,0.035,
    <L*cos(A),0.62+0.06*L,1.05*sin(A)>,0.030,
    <L*cos(A)+0.25*cos(A+pi/2),0.66+0.06*L,1.05*sin(A)+0.25*sin(A+pi/2)>,0.023,
    <L*cos(A)+0.18*cos(A+pi),0.73+0.06*L,1.05*sin(A)+0.18*sin(A+pi)>,0.015,
    <L*cos(A),0.77+0.06*L,1.05*sin(A)>,0.009
    #if (mod(Vine,3)=0) texture { Gilt } #else texture { AquaGlaze } #end
  }
#end

// Broad lifted leaves; a curved midrib and folded surfaces catch warm light.
#macro Leaf(P,Len,W,Lean,Turn)
  union {
    mesh {
      #for (I,0,11)
        #local A = I/12;
        #local B = (I+1)/12;
        #local WA = W*pow(sin(pi*A),0.75);
        #local WB = W*pow(sin(pi*B),0.75);
        #local CA = <0,A*Len,0.13*Len*sin(pi*A)>;
        #local CB = <0,B*Len,0.13*Len*sin(pi*B)>;
        #for (S,-1,1,2)
          #local EA = <S*WA,A*Len,0.015*Len*sin(pi*A)>;
          #local EB = <S*WB,B*Len,0.015*Len*sin(pi*B)>;
          triangle { CA,EA,CB }
          triangle { EA,EB,CB }
        #end
      #end
      texture { LeafTexture } double_illuminate
    }
    sphere_sweep {
      cubic_spline 6,
      <0,-0.02,0>,0.012,<0,0,0>,0.012,
      <0,0.3*Len,0.10*Len>,0.012,
      <0,0.7*Len,0.10*Len>,0.009,
      <0,Len,0>,0.004,<0,1.02*Len,-0.01>,0.002
      pigment { color rgb <0.65,0.76,0.18> }
    }
    rotate z*Lean rotate y*Turn translate P
  }
#end
#for (Plant,0,12)
  #local A = Plant*2*pi/13;
  #local P = <3.45*cos(A),0.58+0.06*abs(cos(A)),1.35*sin(A)>;
  Leaf(P,0.75+0.18*mod(Plant,3),0.23,24+mod(Plant,4)*9,-Plant*28)
  Leaf(P,0.58+0.16*mod(Plant,3),0.21,-40,-Plant*28+80)
#end

// An exuberant chorus of leaning ceramic mushrooms, each with painted ornament.
#declare CapColours = array[5] { Turquoise,Coral,Cobalt,Marigold,<0.61,0.12,0.42> }
#macro Mushroom(P,H,Size,Tilt,ColourIndex)
  union {
    sphere_sweep {
      cubic_spline 6,
      <0,-0.03,0>,0.08,<0,0,0>,0.08,
      <0.15,H*0.30,0.08>,0.095,
      <-0.10,H*0.73,-0.04>,0.082,
      <0,H,0>,0.07,<0.03,H+0.05,0>,0.06
      texture { Milk }
    }
    union {
      lathe {
        cubic_spline 10,
        <0,0.40>,<0,0.40>,<0.18,0.40>,<0.54,0.32>,<0.92,0.09>,
        <1,0>,<0.88,-0.04>,<0.36,0.16>,<0,0.19>,<0,0.19>
        Glaze(CapColours[ColourIndex])
      }
      #for (Gill,0,35)
        #local A = Gill*2*pi/36;
        cylinder { <0.14*cos(A),0.09,0.14*sin(A)>,<0.88*cos(A),-0.04,0.88*sin(A)>,0.012 texture { Gilt } }
      #end
      #for (Paint,0,11)
        #local A = Paint*2*pi/12;
        sphere_sweep {
          cubic_spline 7,
          <0.09*cos(A),0.414,0.09*sin(A)>,0.016,
          <0.13*cos(A),0.412,0.13*sin(A)>,0.016,
          <0.38*cos(A),0.385,0.38*sin(A)>,0.020,
          <0.65*cos(A),0.270,0.65*sin(A)>,0.022,
          <0.87*cos(A),0.143,0.87*sin(A)>,0.018,
          <0.97*cos(A),0.065,0.97*sin(A)>,0.012,
          <0.99*cos(A),0.043,0.99*sin(A)>,0.010
          texture { Milk }
        }
      #end
      sphere { <0,0.412,0>,0.085 scale <1,0.24,1> texture { Gilt } }
      scale Size rotate z*Tilt translate y*H
    }
    translate P
  }
#end
Mushroom(<-3.05,0.72,0.72>,2.05,1.02,12,0)
Mushroom(<-1.86,0.61,1.25>,1.36,0.76,-15,1)
Mushroom(<-3.93,0.80,1.25>,1.25,0.61,17,2)
Mushroom(<-1.06,0.55,1.65>,0.91,0.49,11,3)
Mushroom(<-3.61,0.74,-0.28>,0.67,0.56,-14,1)
Mushroom(<-2.33,0.62,-0.35>,0.85,0.46,10,3)
Mushroom(<3.12,0.73,0.95>,1.67,0.91,-13,2)
Mushroom(<2.80,0.65,1.70>,1.04,0.65,16,1)
Mushroom(<3.93,0.81,1.35>,0.93,0.54,-15,0)
Mushroom(<3.70,0.80,-0.43>,0.60,0.43,15,3)
Mushroom(<2.65,0.63,-0.62>,0.56,0.36,-12,4)

// The central rhyme catches a word: three separately modelled glazed cells.
#declare Breath = 0.5-0.5*cos(2*pi*clock);
#declare RingR = 1.08;
#declare Tube = 0.30+0.10*Breath;
#declare RingP = <0.62,2.90,0.37>;
#declare CellColours = array[3] { Turquoise,Coral,Marigold }
union {
  #for (Cell,0,2)
    intersection {
      torus { RingR,Tube rotate x*90 }
      plane { <sin(radians(-59)), -cos(radians(-59)),0>,0 }
      plane { <-sin(radians(59)),cos(radians(59)),0>,0 }
      Glaze(CellColours[Cell])
      rotate z*(Cell*120+30)
    }
  #end
  #for (Bead,0,35)
    #local A = Bead*2*pi/36;
    sphere { <RingR*cos(A),RingR*sin(A),-Tube*0.995>,0.025 texture { Milk } }
  #end
  rotate y*-9 translate RingP
}
sphere_sweep {
  cubic_spline 7,
  <-0.3,0.48,0.45>,0.095,<-0.3,0.48,0.45>,0.095,
  <0.05,0.72,0.43>,0.12,<0.32,1.05,0.40>,0.11,
  <0.55,1.27,0.37>,0.105,<0.62,1.48,0.37>,0.10,
  <0.62,1.58,0.37>,0.09
  texture { Milk }
}
#declare Word = Type("СЛОВО",1.93,0.13,YellowGlaze,<0,0,0>)
object { Word rotate <0,-9,-13> translate <0.62,2.72,-0.10> }
sphere_sweep {
  cubic_spline 9,
  <-2.3,0.78,-0.79>,0.016,<-2.22,0.78,-0.79>,0.020,
  <-1.42,1.04,-0.68>,0.030,<-0.72,1.90,-0.44>,0.044,
  <0.05,2.73,-0.04>,0.047,<0.95,3.10,0.53>,0.038,
  <1.90,3.52,1.0>,0.026,<2.52,3.96,1.13>,0.015,
  <2.70,4.10,1.15>,0.008
  texture { Gilt }
}

// Little pollen-like letters and rosettes give the garden a shared, playful voice.
#declare Letters = array[5] { "Р","И","Ф","М","А" }
#for (L,0,4)
  #declare Letter = Type(Letters[L],0.27,0.14,RedGlaze,<0,0,0>)
  object { Letter rotate <0,(L-2)*12,(L-2)*11> translate <-2.8+L*0.64,1.05+0.22*sin(L),-0.34> }
#end
#macro Flower(P,R,Colour)
  union {
    #for (Petal,0,7)
      #local A = Petal*2*pi/8;
      sphere {
        <0,0,0>,1 scale <R*0.22,R*0.07,R*0.52>
        rotate y*(-Petal*45) translate <R*0.39*sin(A),0,R*0.39*cos(A)>
        Glaze(Colour)
      }
    #end
    sphere { <0,R*0.05,0>,R*0.22 scale <1,0.45,1> texture { YellowGlaze } }
    rotate x*16 translate P
  }
#end
Flower(<-4.12,0.79,-0.98>,0.39,Marigold)
Flower(<-3.10,0.70,-1.04>,0.31,Coral)
Flower(<3.94,0.81,-0.88>,0.32,Coral)
Flower(<1.96,0.70,-0.82>,0.27,Turquoise)

// Dew beads: clear geometry, real refraction, no image maps.
#for (Drop,0,16)
  #local A = Drop*2*pi/17;
  sphere {
    <3.75*cos(A),0.74+0.04*abs(cos(A)),1.42*sin(A)>,0.035+0.012*mod(Drop,3)
    pigment { color rgbf <0.85,0.98,1,0.93> }
    finish { diffuse 0.05 specular 0.95 roughness 0.006 reflection 0.10 }
    interior { ior 1.333 }
  }
#end

Type("ЖИВАЯ",3.00,0.09,TitleGlaze,<-2.65,4.45,0.62>)
Type("РИФМА",2.95,0.10,TitleGlaze,<-2.65,3.72,0.59>)
Type("Хищные грибы Узбекистана",5.32,0.024,Milk,<0,-0.18,-2.71>)
