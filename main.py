import glob
import open3d as o3d
from POP2.extract_image_pcd import point_cloud_to_image
from POP2.util import *
import os



def main(pcd_path, output_path, n=0, cut_percentage=60, scale_factor=5, fillrgb_iterations=1, fillmask_iterations=1):
    
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    
    # 1. Cargar nube de puntos
    pcd = o3d.io.read_point_cloud(pcd_path)

    # Filtrado por porcentaje
    pcd = filter_pcd_percentage(pcd, cut_percentage)

    o3d.visualization.draw_geometries([pcd])

    # 2. Imagen proyectada
    img = point_cloud_to_image(pcd, scale_factor)
 
    projected_img_path = f"./tmp/projected_image.png"
    cv2.imwrite(projected_img_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f"Imagen proyectada guardada como '{projected_img_path}' con resolucion {img.shape}.")

    if not os.path.exists(projected_img_path):
        raise ValueError("No se pudo guardar la imagen proyectada.")

    # 3. Modificar la imagen: cambiar píxeles no negros e.g rojo=(BGR=(0,0,255))
    
    imagen = change_image_color(projected_img_path, (255,255,255))

    modified_img_path = f"./tmp/imagen_modificada.png"
    cv2.imwrite(modified_img_path, imagen)
    print(f"Imagen modificada guardada como '{modified_img_path}'.")

    if not os.path.exists(modified_img_path):
        raise ValueError("No se pudo guardar la imagen modificada.")


    # Relleno de pixeles metodo 1
    imagen_rellenada  = fill_missing_pixels(projected_img_path, iteraciones=fillrgb_iterations)
    cv2.imwrite(f"{output_path}color/imagen_rellenada_{n}.png", imagen_rellenada)

    imagen_rellenada_mascara  = fill_missing_pixels(modified_img_path, iteraciones=fillmask_iterations)
    cv2.imwrite(f"{output_path}mask/mask_{n}.png", imagen_rellenada_mascara)


    # Relleno de pixeles metodo 2. (Experimental, da buenos resultados cuando no se utiliza un factor de escala muy grande > 10)
    # imagen_rellenada  = fill_missing_pixels_preserve_borders(projected_img_path, iteraciones=fillrgb_iterations)
    # cv2.imwrite(f"{output_path}color/imagen_rellenada_{n}.png", imagen_rellenada)

    # imagen_rellenada_mascara  = fill_missing_pixels_preserve_borders(modified_img_path, iteraciones=fillmask_iterations)
    # cv2.imwrite(f"{output_path}mask/mask_{n}.png", imagen_rellenada_mascara)


if __name__ == "__main__":
    # PROCESO PARA UNA SOLA NUBE
    pcd_path = "data/POP2/mango/pcd/1209_02_pc.ply"
    output_path = "data/POP2/mango/"
    main(pcd_path, output_path,cut_percentage=50, scale_factor=10)

    # # PROCESO PARA VARIAS NUBES
    # output_path = "data/POP2/mango/"
    # pcds = glob.glob('data/POP2/*.ply')
    # for id_, pcd_path in enumerate(pcds, start=1):
    #     main(pcd_path, output_path, n=id_)

