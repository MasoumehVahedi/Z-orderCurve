XY Zreversed(long n) {
  // think of n as a bit vector, same for x and y
  // the x and y are numbers created by x taking even bits for the X
  // and odd bits for the y
  // NB: faster versions made with bitshifts exist
  int x=0, y=0, twopow = 1;
  while(n!=0) {
    if(n%2==1) y+= twopow;
    n /= 2;
    if(n%2==1) x+= twopow;
    n /= 2;
    twopow*=2;    
  }  
  int xx = x; x=y;y=xx;
  return new XY(x,y);
}

public static int zInt(XY xy) {return zInt(xy.x, xy.y);}

// The following code is folklore on the internet
// - original souce not known; certainly not by us!

public static int zInt(int x, int y) {
        x = (x | (x << 16)) & 0x0000FFFF;
        x = (x | (x << 8)) & 0x00FF00FF;
        x = (x | (x << 4)) & 0x0F0F0F0F;
        x = (x | (x << 2)) & 0x33333333;
        x = (x | (x << 1)) & 0x55555555;

        y = (y | (y << 16)) & 0x0000FFFF;
        y = (y | (y << 8)) & 0x00FF00FF;
        y = (y | (y << 4)) & 0x0F0F0F0F;
        y = (y | (y << 2)) & 0x33333333;
        y = (y | (y << 1)) & 0x55555555;

        return x | (y << 1);
    }


   public static long zLong(XY xy) {return zLong(xy.x, xy.y);}

   public static long zLong(int x, int y) {
        // x and y may use all bits
      
        long xx = (long)x;
        long yy = (long)y;
        
        xx = (xx | (xx << 16)) & 0x0000FFFF0000FFFFL;
        xx = (xx | (xx << 8)) & 0x00FF00FF00FF00FFL;
        xx = (xx | (xx << 4)) & 0x0F0F0F0F0F0F0F0FL;
        xx = (xx | (xx << 2)) & 0x3333333333333333L;
        xx = (xx | (xx << 1)) & 0x5555555555555555L;

        yy = (yy | (yy << 16)) & 0x0000FFFF0000FFFFL;
        yy = (yy | (yy << 8)) & 0x00FF00FF00FF00FFL;
        yy = (yy | (yy << 4)) & 0x0F0F0F0F0F0F0F0FL;
        yy = (yy | (yy << 2)) & 0x3333333333333333L;
        yy = (yy | (yy << 1)) & 0x5555555555555555L;

        return xx | (yy << 1);
    }
