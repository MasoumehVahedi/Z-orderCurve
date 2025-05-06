//// The algorithm is given in two versions
//// 1. The recursive algoritm shown in the dissertation in Java; the most readable version
//// 2. An efficient, iterative version in Java (some 50% or so faster - no detailed measurements made so far)


ArrayList<Box> splitBoxIntoIdealBoxes(Box box) {
  ArrayList<Box> container = new ArrayList<Box>(200) ;
  //splitBoxToIdealBoxesRecursive(box, container);
  splitBoxToIdealBoxesFastest(box, container);
  return container;
}

void splitBoxToIdealBoxesRecursive(Box box, ArrayList<Box> container) {
   Box largestIdeal = findLargestIdeal(box);
   container.add(largestIdeal);

   if(box.minimum.x<=largestIdeal.minimum.x-1) {
      Box west = new Box( box.minimum, new XY(largestIdeal.minimum.x-1,box.maximum.y));
      splitBoxToIdealBoxesRecursive(west, container);
   }

   if(largestIdeal.maximum.x+1 <= box.maximum.x) {
     Box east = new Box( new XY(largestIdeal.maximum.x+1, box.minimum.y), box.maximum);
     splitBoxToIdealBoxesRecursive(east, container);
   }
   
   if(largestIdeal.maximum.y+1 <= box.maximum.y) {
     Box north = new Box( new XY(largestIdeal.minimum.x, largestIdeal.maximum.y+1),
                          new XY(largestIdeal.maximum.x, box.maximum.y));
     splitBoxToIdealBoxesRecursive(north, container);
   }

   if(box.minimum.y <= largestIdeal.minimum.y -1) {
     Box south = new Box( new XY(largestIdeal.minimum.x, box.minimum.y),
                        new XY(largestIdeal.maximum.x, largestIdeal.minimum.y -1));
     splitBoxToIdealBoxesRecursive(south, container);
   }
}

void splitBoxToIdealBoxesFastest(Box box, ArrayList<Box> container) {
   Box largestIdeal = findLargestIdeal(box); //
   addColumn(largestIdeal, box.minimum.y, box.maximum.y, container);
   int left =  largestIdeal.maximum.x+1;
   int right = largestIdeal.minimum.x-1;
   Box qBox;
   // add columns to the right
   if(left <= box.maximum.x) { 
     qBox = new Box(new XY(left, box.minimum.y), box.maximum);
     while(true) {
       largestIdeal = findLargestIdeal(qBox); //
       addColumn(largestIdeal, box.minimum.y, box.maximum.y, container);
       left = largestIdeal.maximum.x+1;
       if(left > box.maximum.x) break;
       qBox = new Box(new XY(left, box.minimum.y), box.maximum);
     } //while
   } //if

   // add columns to the left
   if(right>=box.minimum.x) {
     qBox = new Box(box.minimum, new XY(right, box.maximum.y));
     while(true) {
       largestIdeal = findLargestIdeal(qBox); // give it detailed arguments
       addColumn(largestIdeal, box.minimum.y, box.maximum.y, container);
       right = largestIdeal.minimum.x-1;
       if(right < box.minimum.x) break;
       qBox = new Box(box.minimum, new XY(right, box.maximum.y));
     }//while
   }//if
}

void addColumn(Box midBox, int bot, int top, ArrayList<Box> container) {
  // midX, midY represent the box from which we work opwards and downwards
  int midBoxMinX = midBox.minimum.x,  midBoxMinY = midBox.minimum.y; 
  int midBoxMaxX = midBox.maximum.x,  midBoxMaxY = midBox.maximum.y; 
  int columnWidth = midBox.maximum.x - midBox.minimum.x +1;
  int initHeight  = midBox.maximum.y - midBox.minimum.y +1;

  
  int nextBoxWidth = columnWidth;
  // build stack of boxes with midBox in the middle
  int currentSubboxMinY; // declare out here so we can refer to it afterwards
  // First, as many as possible of same size as midBox
  for(currentSubboxMinY = midBoxMinY; currentSubboxMinY + initHeight -1 <= top; currentSubboxMinY+= initHeight){
    container.add( new Box(new XY(midBoxMinX,currentSubboxMinY), new XY(midBoxMaxX,currentSubboxMinY+initHeight-1)) );
  }
  // second, possibly smaller boxes on top the previous
  int nextRowHeight = largestPow2LessEq(top - currentSubboxMinY+1);
  nextBoxWidth = columnWidth >= 2 * nextRowHeight ? columnWidth : columnWidth/2;
  while(nextRowHeight > 0) {
    for(int x = midBoxMinX; x<midBoxMaxX ; x += 2*nextRowHeight)
       container.add( new Box(new XY(x,currentSubboxMinY),
                          new XY(x+ 2*nextRowHeight-1,currentSubboxMinY+nextRowHeight-1)) );
    currentSubboxMinY+=nextRowHeight;
    nextRowHeight = largestPow2LessEq(top - currentSubboxMinY+1);
  }
  // third, possibly smaller boxes below the midBox
  int nextRowY = midBoxMinY;
  while(true) {
    nextRowHeight = min(columnWidth, largestPow2LessEq(nextRowY -bot));  //
    if(nextRowHeight<0) break;
    nextBoxWidth = columnWidth > nextRowHeight ? 2*nextRowHeight : nextRowHeight;
    int nBoxesAcross = columnWidth/nextBoxWidth;
    nextRowY -= nextRowHeight;
    for(int k=0; k<nBoxesAcross ; k++)
       container.add( new Box(new XY(midBoxMinX +k*nextBoxWidth,nextRowY),
                          new XY(midBoxMinX +k*nextBoxWidth+ 2*nextRowHeight-1, nextRowY+nextRowHeight-1)) );
  }  
}


Box findLargestIdeal(Box box) {
   int boxMinX = box.minimum.x, boxMinY = box.minimum.y, boxMaxX = box.maximum.x, boxMaxY = box.maximum.y;
   int pow = largestPow2LessEq(min(boxMaxY - boxMinY+1,boxMaxX - boxMinX+1)); // expected side of ideal quadrate
   int multiplyerX = smallestMultiplierToMakeGreaterEq(pow, boxMinX);
   int zIdealBoxMinX = multiplyerX * pow;
   int multiplyerY = smallestMultiplierToMakeGreaterEq(pow, boxMinY);
   int zIdealBoxMinY = multiplyerY * pow;
   // Unless the big new box can be inside box at an "ideal position", we need to halve the size
   if(zIdealBoxMinX+pow>boxMaxX+1 || zIdealBoxMinY+pow>boxMaxY+1) {
     pow=pow/2;
     // recalculate zIdealBoxMinX, zIdealBoxMinY
     multiplyerX = smallestMultiplierToMakeGreaterEq(pow, boxMinX);
     zIdealBoxMinX = multiplyerX * pow;
     multiplyerY = smallestMultiplierToMakeGreaterEq(pow, boxMinY);
     zIdealBoxMinY = multiplyerY * pow;
   }
   XY zIdealBoxMin = new XY(zIdealBoxMinX, zIdealBoxMinY);
   int zIdealBoxMaxX;
   if(multiplyerX%2 == 0  &&  zIdealBoxMinX + 2* pow -1 <= boxMaxX) {
     // if room for extending to an ideal rectangle, do so 
     zIdealBoxMaxX = zIdealBoxMinX + max(0,2*pow-1);
   } else {
     zIdealBoxMaxX = zIdealBoxMinX + max(0,pow-1);
   } 
   int zIdealBoxMaxY = zIdealBoxMinY + max(0,pow-1);
   XY zIdealBoxMax = new XY(zIdealBoxMaxX, zIdealBoxMaxY);
   return new Box(zIdealBoxMin,  zIdealBoxMax);  
}





int largestPow2LessEq(int n) {
        //if (n == 0) return -1; NO REASON FOR THIS AS line below yields -2147483648, so caller can test <0 for valid/nonvalid
        return 1 << (31 - Integer.numberOfLeadingZeros(n));
    }



int smallestMultiplierToMakeGreaterEq(int factor, int x){
  if(factor==0) return 1;
  return (x+factor-1)/factor;
}
 
 
 
 
 
 
 
 
 
 
