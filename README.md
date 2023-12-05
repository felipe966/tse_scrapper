# tse_scrapper

# Aplicación de Verificación de Identificaciones en Costa Rica

Es una aplicación de Python que te permite verificar el tipo de identificación de personas en Costa Rica y, para las personas físicas, consulta en el Tribunal Supremo de Elecciones (TSE) de Costa Rica para verificar si están fallecidas, recuperando información como fecha de defunción, nombre completo y fecha de nacimiento. Esta aplicación es útil para validar la información de identificación y obtener información vital de personas costarricenses.

# Funciones y Características

Verificación de Tipo de Identificación: utiliza expresiones regulares para identificar el tipo de identificación en función del formato. Admite los siguientes tipos de identificación:

- Persona física
- Persona física - Costarricense Naturalizado
- Persona física - Partida Especial
- Persona Jurídica
- DIMEX (Documento de Identificación Migratorio para Extranjeros)
- DIDI (Documento de Identificación Digital Interinstitucional)

Consulta en el TSE de Costa Rica: Para las personas físicas con identificación válida, consulta automáticamente en el sitio web del TSE de Costa Rica para verificar si están fallecidas. La aplicación recopila la siguiente información si está disponible:

- Nombre completo
- Fecha de nacimiento
- Fecha de defunción (si corresponde)

### Incluye una opción para realizar verificaciones en paralelo utilizando múltiples hilos (threads). Esto mejora la velocidad de procesamiento, especialmente cuando se tienen grandes cantidades de identificaciones para verificar.

### Resultados Exportables: Los resultados de la verificación se almacenan en un archivo CSV que contiene las siguientes columnas:

- Identificación verificada
- Tipo de identificación
- Nombre completo (si disponible)
- Fecha de nacimiento (si disponible)
- Fecha de defunción (si está fallecido)
- Resultado de la verificación (FALLECIDO, No se encontró información en la base de datos, Cédula inválida, Sin fecha de defunción (se asume que está con vida))

# Requisitos
Antes de ejecutar , asegúrate de tener los siguientes requisitos instalados:

- Python (versión 3.x)
- Selenium
- Pandas
- Google Chrome (para la ejecución del WebDriver de Selenium)

Puedes instalar las bibliotecas de Python utilizando pip:
``` pip install requirements.txt```

Descargar ChromeDriver y movero a la carpeta del tse_scrapper

ChromeDriver: https://chromedriver.chromium.org/downloads

Asegúrate de tener un archivo CSV con una columna llamada "cedula" que contenga las identificaciones que deseas verificar.

Ejecuta el script Python proporcionando el nombre del archivo CSV y el número de hilos (threads) que deseas utilizar para la verificación:

``` python script.py nombre_archivo.csv num_threads```

Por ejemplo:

``` python script.py identificaciones.csv 4```

La aplicación dividirá el archivo CSV en partes y ejecutará la verificación en paralelo utilizando el número de hilos especificado. Mostrará los resultados en la consola y generará un archivo CSV llamado "resultado_nombre_archivo.csv" con los resultados de la verificación.

# Contribuciones
¡Las contribuciones son bienvenidas! Si tienes alguna mejora o corrección, no dudes en crear una solicitud de extracción (pull request) o informar sobre problemas (issues).
