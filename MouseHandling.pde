 
// screen xy to XY internal units

XY mousePositionInternalCoordicates() {
  // mousex mousex are screen coordibates
  int internalX = mouseX-screenMargin;
  int internalY = height-screenMargin-mouseY;

  internalX = internalX / pixPerUnit; 
  internalY = internalY / pixPerUnit;
  
  //internalX = min(max(0, internalX),internalUnitsOnXAxis);
  //internalY = min(max(0, internalY),internalUnitsOnYAxis);

  return new XY(internalX,internalY);
}


boolean MouseInsideTheMBR(XY pos) {
  return pos.x > theBox.minimum.x
      && pos.x < theBox.maximum.x
      && pos.y > theBox.minimum.y
      && pos.y < theBox.maximum.y;
}

boolean MouseAtUpperRightCornerOfMBR(XY pos) {
  if(pos.x < theBox.maximum.x-1) return false; 
  if(pos.x > theBox.maximum.x+1) return false; 
  if(pos.y < theBox.maximum.y-1) return false; 
  if(pos.y > theBox.maximum.y+1) return false;
  return true;
}

boolean MouseAtLowerRightCornerOfMBR(XY pos) {
  if(pos.x < theBox.maximum.x-1) return false; 
  if(pos.x > theBox.maximum.x+1) return false; 
  if(pos.y < theBox.minimum.y-1) return false; 
  if(pos.y > theBox.minimum.y+1) return false;
  return true;
}

boolean MouseAtLowerLeftCornerOfMBR(XY pos) {
  if(pos.x < theBox.minimum.x-1) return false; 
  if(pos.x > theBox.minimum.x+1) return false; 
  if(pos.y < theBox.minimum.y-1) return false; 
  if(pos.y > theBox.minimum.y+1) return false;
  return true;
}

boolean MouseAtUpperLeftCornerOfMBR(XY pos) {
  if(pos.x < theBox.minimum.x-1) return false; 
  if(pos.x > theBox.minimum.x+1) return false; 
  if(pos.y < theBox.maximum.y-1) return false; 
  if(pos.y > theBox.maximum.y+1) return false;
  return true;
}

// the following are tested after those above, so corners have priority

boolean MouseAtTopEdgeOfMBR(XY pos){
  if(pos.x < theBox.minimum.x-1) return false; 
  if(pos.x > theBox.maximum.x+1) return false; 
  if(pos.y < theBox.maximum.y-1) return false; 
  if(pos.y > theBox.maximum.y+1) return false;
  return true;
}

boolean MouseAtBottomEdgeOfMBR(XY pos){
  if(pos.x < theBox.minimum.x) return false; 
  if(pos.x > theBox.maximum.x) return false; 
  if(pos.y < theBox.minimum.y-1) return false; 
  if(pos.y > theBox.minimum.y+1) return false;
  return true;
}

boolean MouseAtLeftEdgeOfMBR(XY pos){
  if(pos.x > theBox.minimum.x+1) return false; 
  if(pos.x < theBox.minimum.x-1) return false; 
  if(pos.y > theBox.maximum.y) return false; 
  if(pos.y < theBox.minimum.y) return false;
  return true;
}

boolean MouseAtRightEdgeOfMBR(XY pos){
  if(pos.x > theBox.maximum.x+1) return false; 
  if(pos.x < theBox.maximum.x-1) return false; 
  if(pos.y > theBox.maximum.y) return false; 
  if(pos.y < theBox.minimum.y) return false;
  return true;
}


void mouseReleased() {
      mouseState = 0;
}

XY mouseWhenPressed;
Box theMBRwhenMousePressed;
XY SW_whenMousePressed;
XY NE_whenMousePressed;
XY NW_whenMousePressed;
XY SE_whenMousePressed;
int mouseState = 0; //
    // 0: nothing; 
    // 2: upper right corner
    // 3: lower right corner
    // 4: lower left corner
    // 5: upper left corner
    // To be implemented when time
    // 11: top edge
    // 12: bottom edge
    // 13: left edge
    // 14: right edge

void mousePressed() {
   if(lockedForUpdate) return;
   mouseWhenPressed = mousePositionInternalCoordicates();
   theMBRwhenMousePressed = theBox;
   SW_whenMousePressed = theBox.minimum;
   NE_whenMousePressed = theBox.maximum;
   NW_whenMousePressed = new XY(theBox.minimum.x, theBox.maximum.y);
   SE_whenMousePressed = new XY(theBox.maximum.x, theBox.minimum.y);
   if(MouseAtUpperRightCornerOfMBR(mouseWhenPressed)) mouseState=2;
   else if(MouseAtLowerRightCornerOfMBR(mouseWhenPressed)) mouseState=3;
   else if(MouseAtLowerLeftCornerOfMBR(mouseWhenPressed)) mouseState=4;
   else if(MouseAtUpperLeftCornerOfMBR(mouseWhenPressed)) mouseState=5;
   else if(MouseAtTopEdgeOfMBR(mouseWhenPressed)) mouseState=11;
   else if(MouseAtBottomEdgeOfMBR(mouseWhenPressed)) mouseState=12;
   else if(MouseAtLeftEdgeOfMBR(mouseWhenPressed)) mouseState=13;
   else if(MouseAtRightEdgeOfMBR(mouseWhenPressed)) mouseState=14;
   else if(MouseInsideTheMBR(mouseWhenPressed)) mouseState = 1;
   else mouseState = 0;
}


void mouseDragged() {
  if(lockedForUpdate) return;
  XY mousedMovedVector = minus( mousePositionInternalCoordicates(), mouseWhenPressed);
  if(mouseState==2) { // stretch/shrink box
    XY newNE = plus(NE_whenMousePressed,mousedMovedVector);
    if(newNE.x>=NW_whenMousePressed.x && newNE.y>=SE_whenMousePressed.y)
      theBox = new Box( SW_whenMousePressed, /// SW??????
                        newNE);
  }
  else if(mouseState==3) { // stretch/shrink box
    XY newSE = plus(SE_whenMousePressed,mousedMovedVector);
    if(newSE.x>=SW_whenMousePressed.x && newSE.y<=NE_whenMousePressed.y) {
      XY newNE = new XY(newSE.x, NE_whenMousePressed.y);
      XY newSW = new XY(SW_whenMousePressed.x, newSE.y);
      theBox = new Box( newSW, newNE);
    }
  }
  else if(mouseState==4) { // lower left corner: stretch/shrink box
    XY newSW = plus(SW_whenMousePressed,mousedMovedVector);
    newSW.makeNoneNegative();
    if(newSW.x<=NE_whenMousePressed.x && newSW.y<=NE_whenMousePressed.y) {
      theBox = new Box( newSW, NE_whenMousePressed);
    }
  }
  else if(mouseState==5) { // upper left corner: stretch/shrink box
    XY newNW = plus(NW_whenMousePressed,mousedMovedVector);
    newNW.makeNoneNegative();
    if(newNW.x<=NE_whenMousePressed.x && newNW.y>=SW_whenMousePressed.y) {
      XY newNE = new XY( NE_whenMousePressed.x  , newNW.y); 
      XY newSW = new XY( newNW.x, SE_whenMousePressed.y);
      theBox = new Box( newSW, newNE);
    }
  }
  else if (mouseState==11) { // top edge
    XY newNE = plus(NE_whenMousePressed, new XY(0,mousedMovedVector.y));
    if(newNE.y>=SE_whenMousePressed.y)
      theBox = new Box( SW_whenMousePressed, newNE);
  }
  else if (mouseState==12) { // bottom edge
    XY newSW = plus(SW_whenMousePressed, new XY(0,mousedMovedVector.y));
    newSW.makeNoneNegative();
    if(newSW.y<=NW_whenMousePressed.y)
      theBox = new Box( newSW, NE_whenMousePressed);
  }
  else if (mouseState==13) { // left edge
    XY newSW = plus(SW_whenMousePressed, new XY(mousedMovedVector.x,0));
    newSW.makeNoneNegative();
    if(newSW.x<=NE_whenMousePressed.x)
      theBox = new Box( newSW, NE_whenMousePressed);
  }
  else if (mouseState==14) { // right edge
    XY newNE = plus(NE_whenMousePressed, new XY(mousedMovedVector.x,0));
    //newNE.makeNoneNegative();
    if(newNE.x>=SW_whenMousePressed.x)
      theBox = new Box( SW_whenMousePressed, newNE);
  }
  else if(mouseState==1) { // move box
    theBox = new Box( plus(theMBRwhenMousePressed.minimum,mousedMovedVector),
                      plus(theMBRwhenMousePressed.maximum,mousedMovedVector));
    }
  if(mouseState!=0) updateScreen = true;
}
