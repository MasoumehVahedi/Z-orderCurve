

// as many colours as we need for indicationg different parts
// of a z-zurve that run out of its box - white for inside
// blue reserved to colour of box;

color[] colors = {/*color(0,255,0), color(0,0,255),*/ color(255,0,0),
                  color(0,255,255),color(255,0,255),color(255,255,0),
                  //color(0),
                  color(127,255,255),color(255,127,255),color(255,255,127),
                  color(127,127,255),color(255,127,127),color(255,127,127)};
// all minus red, and bright colours first
color[] subBoxColors = {color(0,255,0), color(0,0,255), color(255,255,0), color(0,255,255),  color(255,0,255),
                  color(127,255,255),color(255,127,255),color(255,255,127),
                  color(127,127,255),color(255,127,127),color(255,127,127)};

color newColor(int i) {
  return colors[i%colors.length];
}


void initGraphics(int uy) {
  background(backgroundCol);
  unitsOnYAxis = uy;
  unitsOnXAxis = unitsOnYAxis * (width-screenMargin) / (height-screenMargin);
  pixPerUnit = (height-2*screenMargin) / unitsOnYAxis;
  screenOrigo = new ScreenXY(screenMargin,height-screenMargin);
  drawZcurve(0L, (long)unitsOnYAxis*unitsOnXAxis*4, backgroundZCol, 1);
  noStroke();
  fill(backgroundCol);
//  int epsilon = 6; // hack to make top and right part of drawn curve look a bit nicer
  rect(0,0,width,screenMargin/*+epsilon*/);
  rect(width-screenMargin/*-epsilon*/,0,screenMargin/*+epsilon*/,height);
}

void spot(XY xy, color spotCol, float weight) { // with current fill and stroke
  ScreenXY screenXY = new ScreenXY(xy);
  stroke(spotCol); fill(spotCol); strokeWeight(weight);
  circle(screenXY.x, screenXY.y, 3*weight); //println("3*weight " +(3*weight));
}

void line(XY start, XY end, color col, float weight) {
  ScreenXY startScreen = new ScreenXY(start);
  ScreenXY endScreen = new ScreenXY(end);
  stroke(col);
  strokeWeight(weight);
  line(startScreen.x, startScreen.y, endScreen.x, endScreen.y);
}

void drawZcurve(long startIndex, long endIndex, color col, float weight) {
  fill(col);
  XY p0 = Zreversed(startIndex);
  XY p1;
  //spot(p0, col, 1.5*weight);
  for(long i = startIndex+1; i < endIndex; i++) {
    p1 = Zreversed(i) ;
    line(p0,p1, col,weight);
    p0=p1;
  }
}

void drawZcurveForBox(Box box, color col, float weight) {
  long startIndex = zLong(box.minimum);
  long endIndex = zLong(box.maximum);
  XY p0 = box.minimum;
  XY p1 = p0;
  for(long i = startIndex+1; i <= endIndex; i++) {
    p1 = Zreversed(i);
      spot(p0, col, weight);//1.5*weight);
      line(p0,p1, col,weight);
    p0=p1;
  }
  spot(p1, col, weight);//1.5*weight);

}

void drawExpanded(Box box, color col, float weight, int expand ) {
 // last arg: expand*weight determins actual expansion
 // referring to low level, as we need to work with floats (all other stuff concerns integers)
  strokeWeight(weight);
  stroke(col);
  noFill();
  int boxHeight = box.maximum.y - box.minimum.y;
  XY NW = plus( box.minimum, new XY(0,boxHeight));
  XY SE = plus( box.maximum, new XY(0, -boxHeight));
  ScreenXY screenSE = new ScreenXY(NW); 
  ScreenXY screenNW = new ScreenXY(SE); 
  screenNW.x += expand*weight; screenNW.y += expand*weight; 
  screenNW.x += expand*weight; screenNW.y += expand*weight; 
  screenSE.x -= expand*weight; screenSE.y -= expand*weight; 
  screenSE.x -= expand*weight; screenSE.y -= expand*weight; 
  rect(screenSE.x, screenSE.y, screenNW.x-screenSE.x, screenNW.y-screenSE.y, 3*weight);
}

// little helper

float dec4(float f) {return round(f*1000)/1000.0;}
float dec4(double f) {return round((float)(f*1000))/1000.0;}

void drawSummaryField(Box theBox, ArrayList<Box> idealBoxes, ArrayList<Box> max4Boxes) {
  fill(color(220,220,220)); stroke(0);
  rect(width-screenMargin, screenMargin, -175, height - 2*screenMargin, 10);
  int screenX = width-screenMargin+10-175;
  int screenY = screenMargin+30;
  fill(color(0)); textSize(20);
  text("Box",screenX,screenY); screenY+= 30;
  text("   "+theBox,screenX,screenY); screenY+= 30;

  screenY+=10;  
  int areaOfTheMBR = (theBox.maximum.x-theBox.minimum.x+1) * (theBox.maximum.y-theBox.minimum.y+1);
  long zLength = zLong(theBox.maximum)-zLong(theBox.minimum)+1;
  text("Z-badness, box: ", screenX,screenY); screenY+= 30;
  text("   =  " + dec4(zLength/(float)areaOfTheMBR), screenX,screenY); screenY+= 30;

  screenY+=10;  
  text("Z-badness, ideal: ", screenX,screenY); screenY+= 30;
  text("   =  1", screenX,screenY); screenY+= 30;
  text("subboxes: "+idealBoxes.size(), screenX,screenY); screenY+= 30;

  screenY+=10;
  text("Z-badness, max4: ", screenX,screenY); screenY+= 30;
  text("   =  "+dec4(totalBadness(theBox, max4Boxes)), screenX,screenY); screenY+= 30;
  screenY+=20;
  text("Showing", screenX,screenY); screenY+= 30;
  if(showmode == IDEALSPLIT) {
    text("  ideal splitting and", screenX,screenY); screenY+= 30;
    text("  Z-curve for box", screenX,screenY); screenY+= 30;
  }
  else {
    text("  max4 splitting and", screenX,screenY); screenY+= 30;
    text("  Z-curve for box", screenX,screenY); screenY+= 30;
    text("  and splits", screenX,screenY); screenY+= 30;
  }
}
