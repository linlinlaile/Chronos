import java.util.ArrayList;
import java.util.List;

public class ExactRectanglePacking {

    static class Rectangle {
        int width, height;

        Rectangle(int width, int height) {
            this.width = width;
            this.height = height;
        }

        int area() {
            return width * height;
        }

        @Override
        public String toString() {
            return width + "x" + height;
        }
    }

    static class Placement {
        int x, y;
        Rectangle rectangle;

        Placement(int x, int y, Rectangle rectangle) {
            this.x = x;
            this.y = y;
            this.rectangle = rectangle;
        }

        @Override
        public String toString() {
            return "矩形 (" + rectangle + ") 放置在 (" + x + ", " + y + ")";
        }
    }

    static class Result {
        List<Placement> placements;
        int filledArea;
        int overlappingArea;
        int outOfBoundsArea;

        Result(List<Placement> placements, int filledArea, int overlappingArea, int outOfBoundsArea) {
            this.placements = placements;
            this.filledArea = filledArea;
            this.overlappingArea = overlappingArea;
            this.outOfBoundsArea = outOfBoundsArea;
        }
    }

    // 检查是否可以放置长方形
    private static boolean canPlace(int x, int y, Rectangle rect, int[][] grid, int containerWidth, int containerHeight) {
        if (x + rect.width > containerWidth || y + rect.height > containerHeight) {
            return false; // 超出边界
        }
        for (int i = x; i < x + rect.width; i++) {
            for (int j = y; j < y + rect.height; j++) {
                if (grid[i][j] == 1) {
                    return false; // 重叠
                }
            }
        }
        return true;
    }

    // 放置长方形
    private static boolean placeRectangle(Rectangle rect, int[][] grid, int containerWidth, int containerHeight, List<Placement> placements) {
        for (int x = 0; x <= containerWidth - rect.width; x++) {
            for (int y = 0; y <= containerHeight - rect.height; y++) {
                if (canPlace(x, y, rect, grid, containerWidth, containerHeight)) {
                    // 放置长方形
                    for (int i = x; i < x + rect.width; i++) {
                        for (int j = y; j < y + rect.height; j++) {
                            grid[i][j] = 1;
                        }
                    }
                    placements.add(new Placement(x, y, rect));
                    return true;
                }
            }
        }
        return false;
    }

    // 尝试放置所有长方形
    private static Result tryPlaceSubset(List<Rectangle> subset, int containerWidth, int containerHeight) {
        int[][] grid = new int[containerWidth][containerHeight];
        List<Placement> placements = new ArrayList<>();
        int filledArea = 0;

        for (Rectangle rect : subset) {
            if (!placeRectangle(rect, grid, containerWidth, containerHeight, placements)) {
                return null; // 无法放置
            }
            filledArea += rect.area();
        }

        return new Result(placements, filledArea, 0, 0);
    }

    // 查找符合条件的子集
    private static List<Rectangle> findValidSubset(List<Rectangle> rectangles, int targetArea, int containerWidth, int containerHeight) {
        int n = rectangles.size();
        // 遍历所有可能的子集
        for (int mask = 1; mask < (1 << n); mask++) {
            List<Rectangle> subset = new ArrayList<>();
            int totalArea = 0;
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) {
                    subset.add(rectangles.get(i));
                    totalArea += rectangles.get(i).area();
                }
            }
            if (totalArea == targetArea) {
                // 尝试放置子集
                Result result = tryPlaceSubset(subset, containerWidth, containerHeight);
                if (result != null) {
                    return subset; // 找到符合条件的子集
                }
            }
        }
        return null; // 未找到符合条件的子集
    }

    public static void main(String[] args) {
        int containerWidth = 5;
        int containerHeight = 5;
        int targetArea = containerWidth * containerHeight;

        List<Rectangle> rectangles = new ArrayList<>();
        rectangles.add(new Rectangle(2, 3));
        rectangles.add(new Rectangle(1, 4));
        rectangles.add(new Rectangle(3, 2));
        rectangles.add(new Rectangle(2, 2));
        rectangles.add(new Rectangle(1, 4));
        rectangles.add(new Rectangle(5, 4));

        // 查找符合条件的子集
        List<Rectangle> subset = findValidSubset(rectangles, targetArea, containerWidth, containerHeight);
        if (subset == null) {
            System.out.println("无法找到完全填充的子集");
            return;
        }

        // 放置选中的子集
        Result result = tryPlaceSubset(subset, containerWidth, containerHeight);

        System.out.println("选中的长方形子集:");
        for (Rectangle rect : subset) {
            System.out.println("矩形 (" + rect + ")");
        }

        System.out.println("Placement方案:");
        for (Placement placement : result.placements) {
            System.out.println(placement);
        }

        System.out.println("填充面积: " + result.filledArea);
        System.out.println("重叠面积: " + result.overlappingArea);
        System.out.println("超出面积: " + result.outOfBoundsArea);
    }
}