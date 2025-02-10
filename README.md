# Analizador Sintáctico

## Descripción

Este proyecto es un analizador léxico y sintáctico que procesa el código fuente ingresado por el usuario. El analizador realiza un análisis léxico para identificar y clasificar los tokens, actualiza una tabla de símbolos, y verifica las reglas sintácticas del lenguaje definido. Los datos procesados se guardan en archivos de texto para su posterior análisis.

## Funcionalidades

### Analizador Léxico

1. **Tabla RW (Reserved Words)**
   - Contiene las palabras reservadas del lenguaje, como tipos de datos (`int`, `double`, `char`, `bool`).
   - Cada palabra reservada está asociada con su tipo de dato correspondiente.

2. **Tabla de Símbolos**
   - Se actualiza dinámicamente conforme se procesan los tokens.
   - Almacena identificadores, literales y otros elementos relevantes encontrados en el código.

3. **Base de Datos**
   - Los datos ingresados y procesados se guardan en archivos de texto (`.txt`).
   - Estos archivos actúan como una base de datos simple para almacenar y recuperar información durante el análisis.

### Analizador Sintáctico

1. **Tabla de Reglas Semánticas**
   - Define las reglas sintácticas y semánticas que deben cumplir las instrucciones del lenguaje.
   - Si una instrucción no cumple con estas reglas, se marca como un error sintáctico.

2. **Validación de Instrucciones**
   - El analizador verifica si las instrucciones del código cumplen con las reglas definidas en la tabla de reglas semánticas.
   - Los errores sintácticos se notifican al usuario para que puedan corregirse.

3. **Alimentación de la Base de Datos**
   - Los datos válidos y procesados se almacenan en los archivos de texto, asegurando la persistencia de la información.

## Uso

1. **Ingreso de Código:**
   - Los usuarios pueden ingresar su código en la caja de texto proporcionada por la interfaz.

2. **Análisis Léxico y Sintáctico:**
   - El analizador procesa el código ingresado, identificando tokens, validando las reglas sintácticas y almacenando los datos en la base de datos.

3. **Visualización de Resultados:**
   - Los resultados del análisis, incluyendo los errores sintácticos y los datos almacenados, se presentan al usuario.

## Estructura de Archivos

- `TablaSimbolos.txt`: Almacena la tabla de símbolos generada durante el análisis léxico.
- `resultado_sintactico.txt`: Contiene los datos ingresados y procesados, actuando como una base de datos.

