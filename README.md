# Fruit-Ripeness

Este repositorio tiene como objetivo crear una base de datos de imágenes extraídas de nubes de puntos 3D en formato `.ply`. El código está diseñado para trabajar específicamente con nubes generadas por el escáner 3D POP2, aunque la metodología empleada debería ser aplicable a cualquier nube de puntos 3D.

El flujo del código se centra en leer y procesar nubes de puntos, recortar un porcentaje específico de la nube, extraer la información de color de cada punto y luego generar imágenes proyectadas con una matriz de píxeles que se rellena para completar los espacios vacíos. Además, se generan máscaras de las imágenes que representan áreas específicas.

## Descripción del Código

1. **Carga de Nube de Puntos:**
   El código utiliza la librería Open3D para leer las nubes de puntos en formato `.ply`.

2. **Recorte de Nube:**
   El recorte de la nube de puntos se controla mediante el parámetro `cut_percentage`. Este parámetro determina el porcentaje de la nube que se utilizará para la extracción de la imagen. El valor predeterminado es 60%, lo que significa que se utiliza el 60% de la región frontal de la nube de puntos.

   - Un valor de **`cut_percentage = 0`** utilizará la nube completa, sin ningún recorte. Esto puede provocar la sobreescritura de píxeles debido al solapamiento de los valores en las coordenadas **x** y **y**.
   - Un valor de **`cut_percentage = 60`** usará el 60% de la parte frontal de la nube de puntos para la extracción de la imagen.
   - Un valor de **`cut_percentage = -60`** tomará el 60% de la parte posterior de la nube de puntos, lo que también ajusta la región de la nube de donde se extraerán los puntos.

3. **Extracción de Información de Color:**
   La información de color de la nube de puntos se mapea dentro de una matriz de ceros, con dimensiones **x** y **y**, que se calculan usando los valores máximos y mínimos de las coordenadas **x** y **y** de la nube. Estas dimensiones se utilizan para escalar la imagen y ajustarla al tamaño deseado.

4. **Escala:**
   La imagen resultante es escalada utilizando un factor de escala para asegurar que la nube de puntos tenga el tamaño adecuado en la imagen generada. El cálculo se realiza con la siguiente fórmula:

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

5. **Generación de Imágenes:**
   El código genera dos imágenes principales:
   - Una **imagen proyectada** que muestra la nube de puntos como una representación 2D.
   - Una **máscara** que representa la misma información pero con un color diferente (por ejemplo, blanco) para marcar los puntos relevantes.

6. **Relleno de Píxeles Vacíos:**
   Después de proyectar las imágenes, se utilizan dos métodos para rellenar los píxeles vacíos en la imagen. Esto se realiza en las siguientes iteraciones:
   - **Método 1:** Relleno básico de píxeles en la imagen de color y en la máscara.
   - **Método 2:** Se puede usar un método alternativo que preserva los bordes.

## Ejecución del Código

El archivo principal `main.py` contiene la lógica para procesar las nubes de puntos. Para ejecutar el código, simplemente ejecuta el archivo `main.py` desde la línea de comandos, pasando las rutas de las nubes de puntos y los directorios de salida.

Claro, aquí está la corrección:

### Ejemplo de Ejecución

En el archivo `main.py` se tienen dos escenarios:

1. **Procesar una sola nube de puntos**:  
   Este es el escenario por defecto. Para ejecutarlo, simplemente corre el siguiente comando:

   ```bash
   python main.py
   ```

   Este script tomará una nube de puntos (`1209_02_pc.ply` en el ejemplo) y generará las imágenes de salida en el directorio `data/POP2/mango/`.

2. **Procesar múltiples nubes de puntos**:  
   Si deseas procesar varias nubes de puntos, descomenta la sección correspondiente en el código (por defecto está comentada) y luego ejecuta el siguiente comando:

   ```bash
   python main.py
   ```

   Este script recorrerá todas las nubes de puntos en el directorio `data/POP2/`, generando las imágenes de salida en el directorio especificado.

## Requisitos

Este código requiere las siguientes librerías para su ejecución:

- `open3d`
- `cv2` (OpenCV)
- `glob`

Puedes instalarlas mediante:

```bash
pip install open3d opencv-python
```

## Estructura del Repositorio

```
Fruit-Ripeness/
├── main.py
├── POP2/
│   ├── extract_image_pcd.py
│   └── util.py
└── data/
    ├── POP2/
    └── mango/
```

### Descripción de Archivos

- `main.py`: Script principal que carga y procesa las nubes de puntos.
- `POP2/extract_image_pcd.py`: Contiene la función `point_cloud_to_image` que proyecta la nube de puntos a una imagen 2D.
- `POP2/util.py`: Funciones auxiliares, como `filter_pcd_percentage` para recortar la nube de puntos y `change_image_color` para modificar la imagen generada.

## Notas

- El valor de `cut_percentage` se puede ajustar para seleccionar la región deseada de la nube de puntos. Un valor de **0** usa toda la nube, mientras que valores positivos o negativos recortan la nube para usar solo la parte frontal o posterior, respectivamente.
- Si usas un `custom_scale_factor` grande, es posible que debas aumentar el número de iteraciones en el relleno de píxeles para obtener mejores resultados visuales.
- Se recomienda usar una dimensión mínima de 200 (`custom_scale_factor` == 1) para las imágenes generadas, pero puedes ajustar este valor en función de tus necesidades.