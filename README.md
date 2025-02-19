# Fruit-Ripeness

Este repositorio tiene como objetivo crear una base de datos de imágenes extraídas de nubes de puntos 3D en formato `.ply`. El código está diseñado para trabajar específicamente con nubes generadas por el escáner 3D POP2, aunque la metodología empleada debería ser aplicable a cualquier nube de puntos 3D.

El flujo del código se centra en leer y procesar nubes de puntos, recortar un porcentaje específico de la nube, extraer la información de color de cada punto y luego generar imágenes proyectadas con una matriz de píxeles que se rellena para completar los espacios vacíos. Además, se generan máscaras de las imágenes que representan áreas específicas.

## Nuevos Enfoques para la Extracción de Imágenes

Se ha incorporado un nuevo método que permite capturar imágenes desde múltiples vistas alrededor del objeto. Este enfoque se basa en capturar fotogramas del visualizador de Open3D, aplicando rotaciones en los tres ejes (pitch, yaw y roll). Para ello se han añadido dos archivos nuevos:

- **`capture3d.py`**: Contiene funciones que, a partir de una nube de puntos o malla, generan múltiples imágenes al rotar el objeto. Se capturan las vistas mediante el visualizador de Open3D en modo oculto, guardando cada imagen con información de los ángulos de rotación.
- **`main2.py`**: Script principal que invoca las funciones de `capture3d.py`. Recorre las nubes de puntos en un directorio específico y genera las imágenes correspondientes en otro directorio.

## Descripción del Código

1. **Carga de Nube de Puntos:**
   El código utiliza la librería Open3D para leer las nubes de puntos en formato `.ply`.

2. **Recorte de Nube:**
   El recorte de la nube de puntos se controla mediante el parámetro `cut_percentage`. Este parámetro determina el porcentaje de la nube que se utilizará para la extracción de la imagen. El valor predeterminado es 60%, lo que significa que se utiliza el 60% de la región frontal de la nube de puntos.
   
   - **`cut_percentage = 0`**: Se utiliza la nube completa, sin recorte (puede provocar solapamientos en las proyecciones).
   - **`cut_percentage = 60`**: Usa el 60% de la parte frontal de la nube.
   - **`cut_percentage = -60`**: Toma el 60% de la parte posterior de la nube.

3. **Extracción de Información de Color:**
   La información de color se mapea en una matriz bidimensional, cuyas dimensiones se calculan a partir de los valores mínimos y máximos de las coordenadas **x** y **y** de la nube, permitiendo escalar y ajustar la imagen al tamaño deseado.

4. **Escala:**
   La imagen resultante se escala utilizando un factor que garantiza que la nube de puntos tenga un tamaño mínimo aceptable en la imagen generada. El cálculo se realiza mediante:

   ```python
   x_vals = points[:,0]
   y_vals = points[:,1]

   x_min, x_max = x_vals.min() - 5, x_vals.max() + 5
   y_min, y_max = y_vals.min() - 5, y_vals.max() + 5

   x_range = x_max - x_min
   y_range = y_max - y_min

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
   ```

5. **Generación de Imágenes y Máscaras:**
   Se generan dos imágenes principales:
   - **Imagen proyectada:** Representa la nube de puntos en 2D.
   - **Máscara:** Resalta los puntos relevantes (por ejemplo, con color blanco).

6. **Relleno de Píxeles Vacíos:**
   Tras la proyección, se aplican métodos para rellenar los píxeles vacíos. Se ofrecen dos alternativas:
   - **Método 1:** Relleno básico en la imagen y la máscara.
   - **Método 2:** Relleno alternativo que preserva los bordes para obtener mejores resultados visuales.

## Ejecución del Código

### Uso del Enfoque Tradicional

El archivo principal `main.py` implementa el método tradicional de proyección de la nube de puntos. Para ejecutarlo, utiliza:

```bash
python main.py
```

Este script procesa una o varias nubes de puntos y genera las imágenes en el directorio de salida configurado.

### Uso del Nuevo Enfoque de Captura Múltiple

El nuevo enfoque se ejecuta mediante `main2.py`, el cual utiliza las funciones de `capture3d.py` para capturar imágenes desde múltiples vistas. Para ejecutarlo, simplemente corre:

```bash
python main2.py
```

Este script recorre las nubes de puntos en el directorio `./data/POP2/{categoria}/pcd/` (por ejemplo, `mango`) y guarda las imágenes resultantes en `./data/POP2/{categoria}/color/`.

## Requisitos

El código requiere las siguientes librerías:

- `open3d`
- `opencv-python` (cv2)
- `glob`

Instálalas ejecutando:

```bash
pip install open3d opencv-python
```

## Estructura del Repositorio

```
Fruit-Ripeness/
├── main.py              # Enfoque tradicional de extracción de imágenes
├── main2.py             # Nuevo enfoque para captura de múltiples vistas
├── POP2/
│   ├── extract_image_pcd.py  # Función point_cloud_to_image para proyectar la nube 3D a 2D
│   ├── util.py               # Funciones auxiliares (recorte, cambio de color, etc.)
│   └── capture3d.py          # Funciones para capturar múltiples vistas de la nube de puntos
└── data/
    ├── POP2/
    └── mango/
```

### Descripción de Archivos

- **`main.py`**: Script principal que utiliza el método tradicional para procesar nubes de puntos.
- **`main2.py`**: Script que implementa el nuevo método de captura de imágenes desde múltiples vistas, aprovechando las funciones de `capture3d.py`.
- **`POP2/extract_image_pcd.py`**: Contiene la función `point_cloud_to_image`, que convierte la nube de puntos en una imagen 2D.
- **`POP2/util.py`**: Incluye funciones auxiliares, como `filter_pcd_percentage` para recortar la nube y `change_image_color` para modificar la imagen generada.
- **`POP2/capture3d.py`**: Implementa `capture_views_for_pcd` y `process_input_folder`, que permiten capturar imágenes de la nube desde múltiples ángulos aplicando rotaciones en los ejes pitch, yaw y roll.

## Notas

- El parámetro `cut_percentage` permite seleccionar la región deseada de la nube: **0** para la nube completa, valores positivos para la parte frontal y negativos para la parte posterior.
- Ajustar el `custom_scale_factor` puede requerir incrementar el número de iteraciones en el relleno de píxeles para obtener mejores resultados visuales.
- Se recomienda una dimensión mínima de 200 para las imágenes generadas (con `custom_scale_factor` == 1), aunque puedes modificar este valor según tus necesidades.
- Verifica que los directorios de entrada y salida existan o que el script tenga permisos para crearlos, especialmente al utilizar el nuevo enfoque en `main2.py`.
