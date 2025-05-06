
ArrayList<Box>  splitBoxIntoMax4(Box theMBR) {
  Box boxNE, boxSE, boxSW, boxNW;
  int splitX = optimalSplitOneAxis(theMBR.minimum.x, theMBR.maximum.x);
  int splitY = optimalSplitOneAxis(theMBR.minimum.y, theMBR.maximum.y);
  XY splitPoint = new XY(splitX,splitY);
  // 4 split boxes
  boxNE = new Box( splitPoint, theMBR.maximum);
  boxSE = new Box( new XY(splitX,theMBR.minimum.y), new XY(theMBR.maximum.x, splitY-1));
  boxSW = new Box(theMBR.minimum, new XY(splitX-1, splitY-1));
  boxNW = new Box( new XY(theMBR.minimum.x, splitY), new XY(splitX-1, theMBR.maximum.y));
  ArrayList<Box> result = new ArrayList<Box>(4);
  // result boxes must be in the order boxNE, boxSE, boxSW, boxNW;
  result.add(boxNE); result.add(boxSE); result.add(boxSW); result.add(boxNW); 
  return result;
}

int optimalSplitOneAxis(int min, int max) {
  int XOR = min ^ max; // ^ means XOR (!)
  int mostSignfBit = (31 - Integer.numberOfLeadingZeros(XOR));
  return (max >> mostSignfBit) << mostSignfBit;
}
