import numpy as np
import matplotlib.pyplot as plt

WIDTH, HEIGHT = 500, 500

def edge_function(v0, v1, p):
    return (p[0] - v0[0]) * (v1[1] - v0[1]) - (p[1] - v0[1]) * (v1[0] - v0[0])

def rasterize_triangle(img, z_buffer, v0, v1, v2, color, use_zbuffer=True):
    min_x = int(max(0, min(v0[0], v1[0], v2[0])))
    max_x = int(min(WIDTH - 1, max(v0[0], v1[0], v2[0])))
    min_y = int(max(0, min(v0[1], v1[1], v2[1])))
    max_y = int(min(HEIGHT - 1, max(v0[1], v1[1], v2[1])))

    area = edge_function(v0, v1, v2)
    if area == 0: return

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            p = np.array([x, y])
            
            w0 = edge_function(v1, v2, p) / area
            w1 = edge_function(v2, v0, p) / area
            w2 = edge_function(v0, v1, p) / area

            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                z = w0 * v0[2] + w1 * v1[2] + w2 * v2[2]

                if use_zbuffer:
                    if z < z_buffer[y, x]:
                        z_buffer[y, x] = z
                        img[y, x] = color
                else:
                    img[y, x] = color

def run_experiment():
    t1_v0, t1_v1, t1_v2 = np.array([100, 100, 10]), np.array([400, 100, 10]), np.array([250, 400, 10])
    color1 = [1.0, 0.0, 0.0]
    t2_v0, t2_v1, t2_v2 = np.array([200, 50, 20]), np.array([500, 200, 20]), np.array([150, 350, 20])
    color2 = [0.0, 0.0, 1.0]

    img_no_z = np.zeros((HEIGHT, WIDTH, 3))
    rasterize_triangle(img_no_z, None, t1_v0, t1_v1, t1_v2, color1, use_zbuffer=False)
    rasterize_triangle(img_no_z, None, t2_v0, t2_v1, t2_v2, color2, use_zbuffer=False)

    img_z = np.zeros((HEIGHT, WIDTH, 3))
    z_buffer = np.full((HEIGHT, WIDTH), np.inf)
    rasterize_triangle(img_z, z_buffer, t1_v0, t1_v1, t1_v2, color1, use_zbuffer=True)
    rasterize_triangle(img_z, z_buffer, t2_v0, t2_v1, t2_v2, color2, use_zbuffer=True)

    z_visual = np.copy(z_buffer)
    valid_z = z_visual[z_visual != np.inf]
    if len(valid_z) > 0:
        min_z, max_z = np.min(valid_z), np.max(valid_z)
        z_visual[z_visual != np.inf] = (z_visual[z_visual != np.inf] - min_z) / (max_z - min_z + 1e-5)
    z_visual[z_visual == np.inf] = 1.0

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(img_no_z, origin='lower')
    axs[0].set_title('Sin Z-Buffer (Error de oclusión)')
    
    axs[1].imshow(img_z, origin='lower')
    axs[1].set_title('Con Z-Buffer (Oclusión correcta)')
    
    axs[2].imshow(z_visual, cmap='gray', origin='lower')
    axs[2].set_title('Mapa de Profundidad (Z-Buffer)')

    plt.savefig('../media/python_zbuffer_results.png')
    plt.show()

if __name__ == "__main__":
    run_experiment()