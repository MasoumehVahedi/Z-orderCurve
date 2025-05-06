
int screenMargin = 50; // pixels

int pixPerUnit;

ScreenXY screenOrigo; 

int unitsOnYAxis, unitsOnXAxis;



class XY {
  int x, y;  // in internal units
  XY(int xx, int yy){x=xx;y=yy;}

  void makeNoneNegative() {x = max(0,x);y = max(0,y);}
  
  String toString() {
    return "("+x+","+y+")";
  }  
}

class Box {
  XY minimum, maximum; // internal
  Box(XY p0, XY p1) {
    minimum = p0; maximum = p1;
    minZ = zLong(p0);
    maxZ = zLong(p1);
    zLength = maxZ - minZ +1;
    area = (p1.x-p0.x+1) * (p1.y-p0.y+1);
    isIdeal = zLength==area;
  }
  long minZ, maxZ;
  long zLength;
  long area;
  boolean isIdeal;
  
  String toString() {
    return "(("+minimum.x+","+minimum.y+"),("+maximum.x+","+maximum.y+"))";
  }
  double badness() {
    return zLength / (double)(area) ;
  }
  int width() {return maximum.x - minimum.x +1;}
  int height() {return maximum.y - minimum.y +1;}

}

double totalBadness(Box m, ArrayList<Box> subMs) {
  // it is assumed that subMs is a splitting of m int disjoint MBRs that cover exactly m
  long totalZLength = 0;
  for(int i=0; i<subMs.size(); i++)
    totalZLength += subMs.get(i).zLength;
  return totalZLength / (double) m.area;
}

boolean in(XY p, Box b) {
  if(p.x < b.minimum.x) return false;
  if(p.y < b.minimum.y) return false;
  if(p.x > b.maximum.x) return false;
  if(p.y > b.maximum.y) return false;
  return true;
}

XY minus(XY xy1, XY xy2) {return new XY(xy1.x-xy2.x,xy1.y-xy2.y);}

XY plus(XY xy1, XY xy2) {return new XY(xy1.x+xy2.x,xy1.y+xy2.y);}

XY times(XY xy, int a) {return new XY(xy.x*a,xy.y*a);}

//XY divide(XY xy, int a) {return new XY(round(xy.x/(float)a),round(xy.y/(float)a));}

class ScreenXY{
  float x, y;
  // stub: should convert XY ty screen poiint
  // y axis upwards ....
  ScreenXY(XY xy) {
    x = screenOrigo.x + xy.x*pixPerUnit;
    y = screenOrigo.y - xy.y*pixPerUnit;
  }
  ScreenXY(int xx, int yy){x=xx;y=yy;}
}
