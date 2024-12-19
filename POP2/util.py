import cv2
import numpy as np
from PIL import Image
import open3d as o3d

def change_image_color(path_imagen, color=(255,0,0)):
    # Cargar la imagen como un numpy array (en BGR por defecto)
    image = cv2.imread(path_imagen)

    if image is None:
        raise ValueError(f"No se pudo cargar la imagen desde {path_imagen}")

    # Obtener dimensiones
    alto, ancho, canales = image.shape

    # Suponiendo que consideramos un píxel "distinto de 0" si no es completamente negro
    # Un píxel negro en BGR es (0,0,0)
    for y in range(alto):
        for x in range(ancho):
            b,g,r = image[y,x]
            if not (b==0 and g==0 and r==0):
                # Cambiamos el píxel por el color dado (el color está en RGB, lo convertimos a BGR)
                image[y,x] = (color[2], color[1], color[0])

    # Devolvemos la imagen modificada
    return image



def fill_missing_pixels(imagen_path, iteraciones=5):
    """
    Rellena los píxeles negros en una imagen utilizando el promedio de los píxeles vecinos.

    Parámetros:
    - imagen_path: Ruta de la imagen a procesar.
    - iteraciones: Número de iteraciones para propagar el relleno.

    Retorna:
    - imagen_resultante: Imagen con los píxeles faltantes rellenados.
    """
    # Cargar la imagen
    imagen = cv2.imread(imagen_path, cv2.IMREAD_COLOR)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen desde la ruta: {imagen_path}")
    
    # Crear una máscara de píxeles negros
    # Se considera un píxel negro si todas las componentes B, G, R son 0
    mascara_negra = np.all(imagen == [0, 0, 0], axis=2)

    # Kernel para los vecinos (8 vecinos)
    kernel = np.array([[1,1,1],
                       [1,0,1],
                       [1,1,1]], dtype=np.uint8)

    imagen_filled = imagen.copy()

    for _ in range(iteraciones):
        # Identificar los píxeles que aún son negros
        mascara_negra = np.all(imagen_filled == [0, 0, 0], axis=2)

        if not np.any(mascara_negra):
            break  # No hay más píxeles negros que rellenar

        # Para cada canal, calcular la suma de los vecinos y el conteo de vecinos no negros
        suma_vecinos = np.zeros_like(imagen_filled, dtype=np.float32)
        conteo_vecinos = np.zeros((imagen_filled.shape[0], imagen_filled.shape[1]), dtype=np.float32)

        for c in range(3):  # B, G, R
            # Usar filtrado para sumar los valores de los vecinos
            suma = cv2.filter2D(imagen_filled[:,:,c].astype(np.float32), -1, kernel)
            suma_vecinos[:,:,c] += suma

        # Contar los vecinos que no son negros
        vecinos_no_negros = np.any(imagen_filled != [0,0,0], axis=2).astype(np.float32)
        conteo = cv2.filter2D(vecinos_no_negros, -1, kernel)
        conteo_vecinos = conteo

        # Evitar división por cero
        conteo_vecinos[conteo_vecinos == 0] = 1

        # Calcular el promedio
        promedio = suma_vecinos / conteo_vecinos[:,:,np.newaxis]

        # Redondear y convertir a entero
        promedio = np.round(promedio).astype(np.uint8)

        # Reemplazar solo los píxeles negros
        imagen_filled[mascara_negra] = promedio[mascara_negra]

    return imagen_filled

def fill_missing_pixels_preserve_borders(imagen_path, iteraciones=1, umbral_vecinos=4):
    """
    Rellena los píxeles negros internos en una imagen utilizando el promedio de los píxeles vecinos,
    manteniendo intactos los bordes del objeto.

    Parámetros:
    - imagen_path: Ruta de la imagen a procesar.
    - iteraciones: Número de iteraciones para propagar el relleno.
    - umbral_vecinos: Número mínimo de vecinos no negros requeridos para rellenar un píxel.

    Retorna:
    - imagen_resultante: Imagen con los píxeles faltantes rellenados.
    """
    # Cargar la imagen
    imagen = cv2.imread(imagen_path, cv2.IMREAD_COLOR)
    if imagen is None:
        raise ValueError(f"No se pudo cargar la imagen desde la ruta: {imagen_path}")
    
    # Crear una máscara de píxeles negros
    # Consideramos un píxel negro si todas las componentes B, G, R son 0
    mascara_negra = np.all(imagen == [0, 0, 0], axis=2)
    
    # Kernel para los vecinos (8 vecinos)
    kernel = np.array([[1,1,1],
                       [1,0,1],
                       [1,1,1]], dtype=np.uint8)
    
    # Crear una copia de la imagen para rellenar
    imagen_filled = imagen.copy()
    
    for it in range(iteraciones):
        # Identificar los píxeles que aún son negros
        mascara_negra = np.all(imagen_filled == [0, 0, 0], axis=2)
        
        if not np.any(mascara_negra):
            print(f"No hay más píxeles negros que rellenar en la iteración {it+1}.")
            break  # No hay más píxeles negros que rellenar
        
        # Contar el número de vecinos no negros para cada píxel
        vecinos_no_negros = cv2.filter2D((~mascara_negra).astype(np.uint8), -1, kernel)
        
        # Crear una máscara de píxeles a rellenar basándose en el umbral
        mascara_filling = mascara_negra & (vecinos_no_negros >= umbral_vecinos)
        
        # Si no hay píxeles que cumplir con la condición, finalizar
        if not np.any(mascara_filling):
            print(f"No hay píxeles internos negros que rellenar en la iteración {it+1}.")
            break
        
        # Para cada canal, calcular la suma de los vecinos
        suma_vecinos = np.zeros_like(imagen_filled, dtype=np.float32)
        conteo_vecinos = vecinos_no_negros.astype(np.float32)
        
        for c in range(3):  # B, G, R
            # Usar filtrado para sumar los valores de los vecinos
            suma = cv2.filter2D(imagen_filled[:,:,c].astype(np.float32), -1, kernel)
            suma_vecinos[:,:,c] += suma
        
        # Evitar división por cero
        conteo_vecinos[conteo_vecinos == 0] = 1
        
        # Calcular el promedio
        promedio = suma_vecinos / conteo_vecinos[:,:,np.newaxis]
        
        # Redondear y convertir a entero
        promedio = np.round(promedio).astype(np.uint8)
        
        # Reemplazar solo los píxeles negros internos
        imagen_filled[mascara_filling] = promedio[mascara_filling]
        
        num_rellenados = np.sum(mascara_filling)
        print(f"Iteración {it+1}: Rellenados {num_rellenados} píxeles internos.")
    
    return imagen_filled



def filter_pcd(pcd, z_value):
    """
    Filtra una nube de puntos de Open3D, conservando los puntos z menores o iguales a z_value.

    Parámetros:
    - pcd: open3d.geometry.PointCloud
        Nube de puntos en formato Open3D.
    - z_value: Valor z de profundidad al cual se desea filtrar la nube.

    Retorna:
    - filtered_pcd: open3d.geometry.PointCloud
        Nube de puntos filtrada en formato Open3D
    """
    points = np.asarray(pcd.points) 
    colors = None
    if len(pcd.colors):
        colors = np.asarray(pcd.colors)
    mask = points[:, 2] <= z_value

    filtered_points = points[mask]
    filtered_pcd = o3d.geometry.PointCloud()
    filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)

    if colors is not None:
        filtered_colors = colors[mask]
        filtered_pcd.colors = o3d.utility.Vector3dVector(filtered_colors)
    return filtered_pcd


def filter_pcd_percentage(pcd, percentage=50):
    """
    Filtra una nube de puntos por porcentaje en el eje Z.
    Ejemplo: porcentaje=50 => se toma el percentil 50 (mediana) 
    y se conservan los puntos que estén por encima o igual de ese valor de z.

    Parámetros:
    -----------
    pcd : open3d.geometry.PointCloud
        Nube de puntos de entrada.
    percentage : float
        Porcentaje para el umbral en z (ej. 50 significa el percentil 50, la mediana).

    Retorna:
    --------
    filtered_pcd : open3d.geometry.PointCloud
        Nube de puntos filtrada que conserva los puntos a partir 
        del percentil dado hacia arriba.
    """
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors) if len(pcd.colors) > 0 else None
    
    # Extraemos solo las coordenadas Z
    z_vals = points[:, 2]

    # Calculamos el umbral de z correspondiente al porcentaje solicitado
    # Por ejemplo: porcentaje=50 => np.percentile(z_vals, 50) => mediana de z
    z_threshold = np.percentile(z_vals, abs(percentage))

    
    
    # Creamos máscara conservando solo los points con z >= z_threshold 
    # en caso de ser un porcentaje positivo o z <= z_threshold en caso de
    # ser negativo
    if percentage >= 0:
        mask = (z_vals >= z_threshold)
    else:
        mask = (z_vals <= z_threshold)

    filtered_points = points[mask]
    filtered_pcd = o3d.geometry.PointCloud()
    filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)

    if colors is not None:
        colors_filtrados = colors[mask]
        filtered_pcd.colors = o3d.utility.Vector3dVector(colors_filtrados)

    return filtered_pcd