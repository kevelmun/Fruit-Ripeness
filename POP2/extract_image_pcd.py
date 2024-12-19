
import numpy as np

def point_cloud_to_image(pcd, custom_scale_factor=1):
    """
    Esta función toma una nube de puntos de tipo open3d.geometry.PointCloud
    y la proyecta a una imagen en 2D. La proyección se realiza sobre el plano XY,
    escalando y trasladando las coordenadas para acomodar todos los puntos en la imagen.

    Parámetros:
    -----------
    pcd : open3d.geometry.PointCloud
        La nube de puntos de entrada, con o sin colores.
    custom_scale_factor : float
        Factor de escala de la proyeccion.

    Retorna:
    --------
    img : numpy.ndarray
        Imagen en formato RGB (uint8) con la nube proyectada.
    """
    points = np.asarray(pcd.points)  # (N,3)
    colors = np.asarray(pcd.colors)  # (N,3) en [0,1] si existen

    if points.size == 0:
        raise ValueError("La nube de puntos está vacía.")

    # Si la nube no tiene colores, asignar blanco por defecto
    if colors.size == 0:
        colors = np.ones((len(points), 3), dtype=np.float32)

    colors_255 = (colors * 255).astype(np.uint8)

    # Determinar rangos y escalas
    x_vals = points[:,0]
    y_vals = points[:,1]

    x_min, x_max = x_vals.min() - 5, x_vals.max() + 5
    y_min, y_max = y_vals.min() - 5, y_vals.max() + 5

    x_range = (x_max - x_min) 
    y_range = (y_max - y_min) 

    if x_range == 0:
        x_range = 1e-6
    if y_range == 0:
        y_range = 1e-6

    # Escala para que la nube quepa y tenga tamaño mínimo aceptable
    min_dimension = 200
    mayor_rango = max(x_range, y_range)
    scale_factor = 1.0

    if mayor_rango < 1:
        scale_factor = min_dimension / mayor_rango
    else:
        scale_factor = custom_scale_factor

    img_width = int(np.ceil(x_range * scale_factor))
    img_height = int(np.ceil(y_range * scale_factor))

    if img_width < 1:
        img_width = 1
    if img_height < 1:
        img_height = 1

    x_pixels = (x_vals - x_min) * scale_factor
    y_pixels = (y_vals - y_min) * scale_factor

    x_pixels = x_pixels.astype(int)
    y_pixels = y_pixels.astype(int)

    # Invertir eje Y para que la imagen tenga origen en la esquina superior izquierda
    y_pixels = img_height - 1 - y_pixels

    # Crear imagen negra (RGB)
    img = np.zeros((img_height, img_width, 3), dtype=np.uint8)

    # Dibujar la nube en la imagen
    for (xp, yp, c) in zip(x_pixels, y_pixels, colors_255):
        if 0 <= xp < img_width and 0 <= yp < img_height:
            img[yp, xp] = c

    return img




# # Re-mapear los colores modificados a la nube
# imagen_modificada = cv2.imread(modified_img_path)
# if imagen_modificada is None:
#     raise ValueError("No se pudo cargar 'imagen_modificada.png'")

# imagen_modificada_rgb = cv2.cvtColor(imagen_modificada, cv2.COLOR_BGR2RGB)

# new_colors = []
# for (xp, yp) in zip(x_pixels, y_pixels):
#     if 0 <= xp < imagen_modificada_rgb.shape[1] and 0 <= yp < imagen_modificada_rgb.shape[0]:
#         r,g,b = imagen_modificada_rgb[yp, xp]
#         new_colors.append((r/255.0, g/255.0, b/255.0))
#     else:
#         new_colors.append((0.0,0.0,0.0))

# new_colors_arr = np.array(new_colors, dtype=np.float64)

# if len(new_colors_arr) != len(pcd.points):
#     raise ValueError("La cantidad de colores no coincide con la cantidad de puntos.")

# pcd.colors = o3d.utility.Vector3dVector(new_colors_arr)

