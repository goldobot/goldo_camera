import numpy as np
import pyvista as pv
from scipy.spatial import Delaunay
import cv2

# ================================
# 1. YOUR DATA (unchanged)
# ================================
P_exp = [
    [(   14,   775,   100,  +400), #
     (   97,   817,   100,  +300), #
     ( 1123,   829,   100,  -300), #
     ( 1206,   785,   100,  -400)],#

    [(   31,   646,   200,  +400), #
     (  116,   664,   200,  +300), #
     (  232,   688,   200,  +200), #
     (  985,   693,   200,  -200), #
     ( 1106,   676,   200,  -300), #
     ( 1168,   651,   200,  -400)],#

    [(   67,   519,   300,  +400), #
     (  154,   516,   300,  +300), #
     (  266,   522,   300,  +200), #
     (  422,   523,   300,  +100), #
     (  608,   529,   300,     0), #
     (  797,   531,   300,  -100), #
     (  952,   528,   300,  -200), #
     ( 1070,   527,   300,  -300), #
     ( 1155,   525,   300,  -400)],#

    [(  112,   407,   400,  +400), #
     (  198,   394,   400,  +300), #
     (  308,   386,   400,  +200), #
     (  450,   378,   400,  +100), #
     (  609,   377,   400,     0), #
     (  773,   383,   400,  -100), #
     (  915,   392,   400,  -200), #
     ( 1025,   403,   400,  -300), #
     ( 1112,   412,   400,  -400)],#

    [(  115,   316,   500,  +400), #
     (  243,   297,   500,  +300), #
     (  348,   285,   500,  +200), #
     (  474,   274,   500,  +100), #
     (  613,   272,   500,     0), #
     (  750,   277,   500,  -100), #
     (  878,   290,   500,  -200), #
     (  981,   304,   500,  -300), #
     ( 1067,   321,   500,  -400)],#

    [(  282,   227,   600,  +300), #
     (  380,   212,   600,  +200), #
     (  492,   201,   600,  +100), #
     (  613,   198,   600,     0), #
     (  735,   203,   600,  -100), #
     (  847,   215,   600,  -200), #
     (  943,   230,   600,  -300)],#

    [(  317,   170,   700,  +300), #
     (  408,   155,   700,  +200), #
     (  508,   140,   700,  +100), #
     (  614,   142,   700,     0), #
     (  720,   147,   700,  -100), #
     (  820,   158,   700,  -200), #
     (  908,   173,   700,  -300)],#

]

# ================================
# 2. FLATTEN DATA
# ================================
points = []
values = []

for row in P_exp:
    for (x, y, xr, yr) in row:
        points.append([x, y])
        values.append([xr, yr])

points = np.array(points)
values = np.array(values)

# ================================
# 3. DELAUNAY TRIANGULATION
# ================================
tri = Delaunay(points)

# ================================
# 4. BARYCENTRIC INTERPOLATION
# ================================
def map_pixel_to_real(x, y):
    simplex = tri.find_simplex([[x, y]])
    if simplex < 0:
        return None  # outside

    simplex = simplex[0]
    vertices = tri.simplices[simplex]

    T = tri.transform[simplex]
    bary = np.dot(T[:2], [x, y] - T[2])
    bary = np.append(bary, 1 - bary.sum())

    xr = np.dot(bary, values[vertices, 0])
    yr = np.dot(bary, values[vertices, 1])

    return xr, yr

# ================================
# 5. DEBUG: SHOW TRIANGULATION
# ================================
def show_triangulation_old():
    # Create PyVista mesh from triangles
    faces = []
    for tri_indices in tri.simplices:
        faces.append([3, tri_indices[0], tri_indices[1], tri_indices[2]])

    faces = np.hstack(faces)

    points_3d = np.hstack([points, np.zeros((points.shape[0], 1))])
    mesh = pv.PolyData(points_3d, faces)

    plotter = pv.Plotter()
    plotter.add_mesh(mesh, show_edges=True, color="lightblue")
    plotter.add_points(points_3d, color="red", point_size=10, render_points_as_spheres=True)
    plotter.add_axes()
    plotter.show()

def show_triangulation_bad():
    points_3d = np.hstack([points, np.zeros((points.shape[0], 1))])

    faces = []
    cell_values = []

    for tri_indices in tri.simplices:
        faces.append([3, tri_indices[0], tri_indices[1], tri_indices[2]])

        # --- distortion computation ---
        p = points[tri_indices]   # pixel coords
        r = values[tri_indices]   # real coords

        # pixel triangle area
        area_p = abs(np.linalg.det([
            [p[1][0]-p[0][0], p[1][1]-p[0][1]],
            [p[2][0]-p[0][0], p[2][1]-p[0][1]]
        ]))

        # real triangle area
        area_r = abs(np.linalg.det([
            [r[1][0]-r[0][0], r[1][1]-r[0][1]],
            [r[2][0]-r[0][0], r[2][1]-r[0][1]]
        ]))

        distortion = area_r / (area_p + 1e-6)
        cell_values.append(distortion)

    faces = np.hstack(faces)

    mesh = pv.PolyData(points_3d, faces)

    # attach distortion per triangle (cell data)
    mesh.cell_data["distortion"] = np.array(cell_values)

    plotter = pv.Plotter()
    plotter.add_mesh(mesh, show_edges=True, scalars="distortion", cmap="viridis")
    plotter.add_points(points_3d, color="red", point_size=10, render_points_as_spheres=True)
    plotter.add_axes()
    plotter.show()

def show_triangulation():
    points_3d = np.hstack([points, np.zeros((points.shape[0], 1))])

    faces = []
    for tri_indices in tri.simplices:
        faces.append([3, tri_indices[0], tri_indices[1], tri_indices[2]])

    faces = np.hstack(faces)

    mesh = pv.PolyData(points_3d, faces)

    plotter = pv.Plotter()
    plotter.add_mesh(mesh, show_edges=True, color="lightblue")
    plotter.add_points(points_3d, color="red", point_size=10)
    plotter.show()

# ================================
# 6. DEBUG: SHOW WARPED GRID
# ================================
def show_warped_grid(W=200, H=150, scale=6):
    X = np.zeros((H, W))
    Y = np.zeros((H, W))
    Z = np.zeros((H, W))

    for i in range(W):
        for j in range(H):
            px = i * scale
            py = j * scale

            res = map_pixel_to_real(px, py)
            if res is None:
                continue

            xr, yr = res
            X[j, i] = xr
            Y[j, i] = yr

    grid = pv.StructuredGrid(X, Y, Z)

    plotter = pv.Plotter()
    plotter.add_mesh(grid, show_edges=True)
    plotter.add_axes()
    plotter.show()

def quick_opencv_overlay():
    img = cv2.imread("lab_1.png")

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            res = map_pixel_to_real(x, y)
    
            if res is None:
                print(f"Pixel ({x},{y}) → outside triangulation")
            else:
                xr, yr = res
                print(f"Pixel ({x},{y}) → Real ({xr:.1f}, {yr:.1f})")
    
                # draw feedback on image
                cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
                cv2.putText(img, f"{int(xr)},{int(yr)}",
                            (x+10, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0,255,0), 1)

    for tri_indices in tri.simplices:
        pts = points[tri_indices].astype(int)
        cv2.line(img, tuple(pts[0]), tuple(pts[1]), (0,255,0), 1)
        cv2.line(img, tuple(pts[1]), tuple(pts[2]), (0,255,0), 1)
        cv2.line(img, tuple(pts[2]), tuple(pts[0]), (0,255,0), 1)

    #cv2.imshow("triangulation", img)
    #cv2.waitKey(0)

    cv2.namedWindow("DELAUNAY")
    cv2.setMouseCallback("DELAUNAY", on_mouse)

    while True:
        cv2.imshow("DELAUNAY", img)
        key = cv2.waitKey(10)
        if key == 27:  # ESC to quit
            break

    cv2.destroyAllWindows()


# ================================
# MAIN
# ================================
if __name__ == "__main__":
    #show_triangulation()
    #show_warped_grid()
    quick_opencv_overlay()
