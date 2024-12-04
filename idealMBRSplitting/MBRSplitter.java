import java.io.*;
import java.util.ArrayList;

public class MBRSplitter {

    public static void main(String[] args) {
        if(args.length < 2) {
            System.out.println("Usage: java MBRSplitter <input_file> <output_file>");
            System.exit(1);
        }

        String inputFile = args[0];
        String outputFile = args[1];

        ArrayList<Box> mbrs = readMBRsFromCSV(inputFile);
        ArrayList<Box> splitMBRs = new ArrayList<>();

        MBRSplitter splitter = new MBRSplitter();

        for (Box mbr : mbrs) {
            ArrayList<Box> splitBoxes = splitter.splitBox(mbr);
            splitMBRs.addAll(splitBoxes);
        }

        writeBoxesToCSV(splitMBRs, outputFile);

    }


    public static ArrayList<Box> readMBRsFromCSV(String filename) {
        ArrayList<Box> mbrs = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                long min_x = Long.parseLong(values[0]);
                long min_y = Long.parseLong(values[1]);
                long max_x = Long.parseLong(values[2]);
                long max_y = Long.parseLong(values[3]);
                XY min = new XY(min_x, min_y);
                XY max = new XY(max_x, max_y);
                Box box = new Box(min, max);
                mbrs.add(box);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return mbrs;
    }

    public static void writeBoxesToCSV(ArrayList<Box> boxes, String filename) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(filename))) {
            for (Box box : boxes) {
                String line = String.format("%d,%d,%d,%d",
                        box.min.x, box.min.y, box.max.x, box.max.y);
                bw.write(line);
                bw.newLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    ArrayList<Box> splitBox(Box box) {
        ArrayList<Box> container = new ArrayList<Box>(200) ;
        splitBoxRecursive(box, container);
        return container;
    }

    void splitBoxRecursive(Box box, ArrayList<Box> container) {
        // Find a largest Z-ideal box inside Box
        long h = box.max.y - box.min.y; // Number of points in y-direction
        long w = box.max.x - box.min.x; // Number of points in x-direction
        if (h < 0 || w < 0) return;
        long pow = largestPow2LessEq(Math.min(h + 1, w + 1)); // Expected side of ideal square
        long multiplierX = smallestMultiplierToMakeGreaterEq(pow, box.min.x);
        long zIdealBoxMinX = multiplierX * pow;
        long multiplierY = smallestMultiplierToMakeGreaterEq(pow, box.min.y);
        long zIdealBoxMinY = multiplierY * pow;
        // Unless the big new box can be inside box, we need to use smaller size
        if (zIdealBoxMinX + pow > box.max.x + 1 || zIdealBoxMinY + pow > box.max.y + 1) {
            pow = pow / 2;
            // Recalculate minx, miny
            multiplierX = smallestMultiplierToMakeGreaterEq(pow, box.min.x);
            zIdealBoxMinX = multiplierX * pow;
            multiplierY = smallestMultiplierToMakeGreaterEq(pow, box.min.y);
            zIdealBoxMinY = multiplierY * pow;
        }
        XY zIdealBoxMin = new XY(zIdealBoxMinX, zIdealBoxMinY);
        long zIdealBoxMaxX;
        if (multiplierX % 2 == 0 && zIdealBoxMinX + 2 * pow - 1 <= box.max.x) {
            // If room for an extended
            zIdealBoxMaxX = zIdealBoxMinX + Math.max(0, 2 * pow - 1);
        } else {
            zIdealBoxMaxX = zIdealBoxMinX + Math.max(0, pow - 1);
        }
        long zIdealBoxMaxY = zIdealBoxMinY + Math.max(0, pow - 1);
        XY zIdealBoxMax = new XY(zIdealBoxMaxX, zIdealBoxMaxY);
        Box largestIdeal = new Box(zIdealBoxMin, zIdealBoxMax);
        container.add(largestIdeal);
        // Recursive calls for the rest of the box
        if (box.min.x <= zIdealBoxMinX - 1) {
            Box west = new Box(box.min, new XY(zIdealBoxMinX - 1, box.max.y));
            splitBoxRecursive(west, container);
        }

        if (zIdealBoxMaxX + 1 <= box.max.x) {
            Box east = new Box(new XY(zIdealBoxMaxX + 1, box.min.y), box.max);
            splitBoxRecursive(east, container);
        }

        if (zIdealBoxMaxY + 1 <= box.max.y) {
            Box north = new Box(new XY(zIdealBoxMinX, zIdealBoxMaxY + 1),
                    new XY(zIdealBoxMaxX, box.max.y));
            splitBoxRecursive(north, container);
        }

        if (box.min.y <= zIdealBoxMinY - 1) {
            Box south = new Box(new XY(zIdealBoxMinX, box.min.y),
                    new XY(zIdealBoxMaxX, zIdealBoxMinY - 1));
            splitBoxRecursive(south, container);
        }
    }


    // The largestPow2LessEq method
    long largestPow2LessEq(long n) {
        if (n == 0) return 0;
        long p = 1;
        while (2 * p <= n) p = p * 2;
        return p;
    }

    long smallestMultiplierToMakeGreaterEq(long factor, long x) {
        if (factor == 0) return 1;
        return (x + factor - 1) / factor;
    }

    // The XY class
    static class XY {
        long x;
        long y;

        XY(long xx, long yy) {
            x = xx;
            y = yy;
        }

        @Override
        public String toString() {
            return "<" + x + "," + y + ">";
        }
    }

    // The Box class
    static class Box {
        XY min, max;

        Box(XY mi, XY ma) {
            min = mi;
            max = ma;
        }

        @Override
        public String toString() {
            return "<" + min + ";" + max + ">";
        }
    }

    // The sick method (not used in this code, but included for completeness)
    boolean sick(Box b) {
        return b.min.x > b.max.x || b.min.y > b.max.y;
    }



}







