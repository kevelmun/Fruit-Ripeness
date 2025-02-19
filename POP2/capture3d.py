import open3d as o3d
import numpy as np
import cv2
import os
import argparse
import copy

def capture_views_for_pcd(pcd, base_name, output_dir,
                          num_yaw=10, num_pitch=5, num_roll=5,
                          pitch_range=30, roll_range=30):
    """
    Captura imágenes de la nube de puntos o malla desde múltiples puntos de vista
    mediante rotaciones en los tres ejes.
    """
    print(f"Capturando vistas para: {base_name}")
    # Crear la carpeta de salida para este archivo
    pcd_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(pcd_output_dir, exist_ok=True)
    
    # Definir los ángulos (en radianes) para cada eje
    yaw_angles = np.radians(np.linspace(0, 360, num=num_yaw, endpoint=False))
    pitch_angles = np.linspace(-np.radians(pitch_range), np.radians(pitch_range), num=num_pitch)
    roll_angles = np.linspace(-np.radians(roll_range), np.radians(roll_range), num=num_roll)
    
    # Inicializar el visualizador de Open3D en modo oculto
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=800, height=600, visible=False)
    
    count = 0
    for pitch in pitch_angles:
        for yaw in yaw_angles:
            for roll in roll_angles:
                # Usamos deepcopy para crear una copia del objeto original
                pcd_copy = copy.deepcopy(pcd)
                # Obtener la matriz de rotación combinando (pitch, yaw, roll)
                R = o3d.geometry.get_rotation_matrix_from_xyz((pitch, yaw, roll))
                pcd_copy.rotate(R, center=pcd_copy.get_center())
                
                # Limpiar la escena y agregar la geometría rotada
                vis.clear_geometries()
                vis.add_geometry(pcd_copy)
                
                vis.poll_events()
                vis.update_renderer()
                # Capturar la imagen actual
                color_image = vis.capture_screen_float_buffer(False)
                
                # Convertir la imagen de Open3D (RGB float [0,1]) a formato OpenCV (BGR uint8)
                color_image_cv = np.array(color_image)
                color_image_cv = cv2.cvtColor((color_image_cv * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
                
                # Guardar la imagen con un nombre que incluya el índice y los ángulos (en grados)
                filename = os.path.join(
                    pcd_output_dir,
                    f"frame_{count:04d}_pitch{np.degrees(pitch):.1f}_yaw{np.degrees(yaw):.1f}_roll{np.degrees(roll):.1f}.png"
                )
                cv2.imwrite(filename, color_image_cv)
                print(f"Guardado: {filename}")
                count += 1

    print(f"Se guardaron {count} imágenes en: {pcd_output_dir}")
    vis.destroy_window()


def process_input_folder(input_folder, output_folder,
                         num_yaw=10, num_pitch=5, num_roll=5,
                         pitch_range=30, roll_range=30):
    """
    Recorre la carpeta de entrada en busca de archivos .ply que terminen en '_pc.ply'
    y para cada uno genera capturas desde múltiples puntos de vista.
    
    Parámetros:
      - input_folder: carpeta donde se encuentran los archivos .ply
      - output_folder: carpeta donde se guardarán las imágenes generadas
      - num_yaw, num_pitch, num_roll, pitch_range, roll_range: parámetros de la función capture_views_for_pcd
    """
    print(f"Procesando la carpeta de entrada: {input_folder}")
    
    # Listar archivos que terminen en _pc.ply (sin buscar en subcarpetas)
    files = [f for f in os.listdir(input_folder) if f.lower().endswith('mesh.ply')]
    if len(files) == 0:
        print("No se encontraron archivos .ply en", input_folder)
        return

    os.makedirs(output_folder, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(input_folder, file)
        base_name = os.path.splitext(file)[0]
        print("Procesando:", file_path)
        # Se utiliza read_triangle_mesh, pero si se trata de una nube de puntos se puede usar read_point_cloud
        pcd = o3d.io.read_triangle_mesh(file_path)
        pcd.compute_vertex_normals()
        if pcd.is_empty():
            print("El objeto está vacío. Se omite:", file_path)
            continue
        capture_views_for_pcd(pcd, base_name, output_folder,
                              num_yaw=num_yaw, num_pitch=num_pitch, num_roll=num_roll,
                              pitch_range=pitch_range, roll_range=roll_range)
