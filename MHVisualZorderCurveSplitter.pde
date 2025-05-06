// PRELIMINARY VERSION, MAY 2025 - MAINLY FOR ASSESSORS of MV's PhD thesis
//
// Algorithms for 1) splitting boxes into ideal boxes, and 2) max-4 splitting
// Determine which one to show by setting the showmode variable below
//
// -- explaining document to become available

// The box on the screen can be modified by dragging sides and corners and be moved dragging inside the box

// Variable *worldsize relates to visual output only; 50 is fine if you want to see what goes on
// but depends also on the size(-,-) setting below
// Larger values may be used for testing splitting of larger boxes

// SEE CONDITIONS AND MORE INFO AT END OF THIS FILE

int worldSize = 50; //300;

int showmode = MAX4SPLIT; final static int MAX4SPLIT = 117, IDEALSPLIT = 118;

Box theBox;

void setup() {
  size(1600,1200);
  frameRate(12);
  initGraphics(worldSize);
  // initial - can be changed by mouse
  //theMBR = new MBR(new XY(127,127), new XY(128,128));
  theBox = new Box(new XY(7,8), new XY(15,13));
  background(backgroundCol);
  drawZcurve(0L, (long)worldSize*worldSize*4, backgroundZCol, thinLineWidth);
  save("backgroundImg.tif");

}

color backgroundCol = color(127),
      backgroundZCol = color(0), 
      butterflyCol = color(255),
      splitBoxCol = color(0,255,0),
      mbrCol = color(255,0,0);

int thinLineWidth = 1;
PImage backgroundImg;
boolean updateScreen = true;

boolean firstTime = true;
boolean lockedForUpdate = false; // to prevent updates due to mouse movement to clutter up with computing of the image
void draw() {
   if(firstTime) {backgroundImg = loadImage("backgroundImg.tif"); firstTime = false;}
   if(!updateScreen) return;
   updateScreen = false;
   lockedForUpdate = true;
   image(backgroundImg,0,0);
   drawExpanded(theBox, mbrCol, 3, 2);

   drawZcurveForBox(theBox, butterflyCol, thinLineWidth*1.5);
   
   // clear image border at top and to the right to produce a nice margin
   fill(backgroundCol); noStroke();
   rect(0,0, width, screenMargin);
   rect(width-screenMargin, 0, screenMargin,height);
   fill(color(0));textSize(40);
   text("Masoumeh's and Henning's visual Z-order curve splitter", screenMargin, screenMargin-10);
   ArrayList<Box> idealBoxes = splitBoxIntoIdealBoxes(theBox);
   ArrayList<Box> max4Boxes = splitBoxIntoMax4(theBox);

   ArrayList<Box> boxesToDraw = showmode == IDEALSPLIT ? idealBoxes : max4Boxes;

   for(int j = 0; j < boxesToDraw.size(); j++) {
     drawExpanded(boxesToDraw.get(j), subBoxColors[j%subBoxColors.length], 3, 1);
     drawZcurveForBox(boxesToDraw.get(j), subBoxColors[j%subBoxColors.length], thinLineWidth*2);
   }
   drawSummaryField(theBox, idealBoxes, max4Boxes);
   lockedForUpdate = false;
}

// Conception: Henning Christiansen & Masoumeh Vahedi
// Coding: Henning Christiansen, henning@ruc.dk

// freely available for use, copying and modification for non-commercial and peaceful purposes
// provided that proper reference is given
