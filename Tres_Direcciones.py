import re

contador_temporales = 1
contador_etiquetas = 1

def nuevo_temporal():
    global contador_temporales
    temporal = f"t{contador_temporales}"
    contador_temporales += 1
    return temporal

def nueva_etiqueta():
    global contador_etiquetas
    etiqueta = f"L{contador_etiquetas}"
    contador_etiquetas += 1
    return etiqueta
    

def generar_codigo_tres_direcciones(expresion):
    global contador_temporales
    resultado = []
    if_pattern = re.compile(r'if\s*\((.*?)\)\s*{(.*?)}', re.DOTALL)
    else_if_pattern = re.compile(r'elseif\s*\((.*?)\)\s*{(.*?)}', re.DOTALL)
    else_pattern = re.compile(r'else\s*{(.*?)}', re.DOTALL)
    while_pattern = re.compile(r'while\s*\((.*?)\)\s*{(.*?)}', re.DOTALL)
    dowhile_pattern = re.compile(r'do\s*{(.*?)}\s*while\s*\((.*?)\)', re.DOTALL)
    assign_pattern = re.compile(r'(\w+)\s*=\s*(.+)')

    tokens = expresion.replace("{", " { ").replace("}", " } ").split()

    if if_pattern.search(expresion) and else_if_pattern.search(expresion) and else_pattern.search(expresion):
        return manejar_if_elseif_else(expresion, resultado)
    elif if_pattern.search(expresion) and else_pattern.search(expresion):
        return manejar_if_else(expresion, resultado)
    elif if_pattern.search(expresion):
        return manejar_if(tokens, resultado)
    elif while_pattern.search(expresion):
        return manejar_while(expresion, resultado)
    elif dowhile_pattern.search(expresion):
        return manejar_dowhile(expresion, resultado)
    elif assign_pattern.match(expresion):
        variable, expr = assign_pattern.match(expresion).groups()
        return generar_codigo_asignacion(variable, expr)

    return "Error: Expresión mal formada."

def generar_codigo_asignacion(variable, expresion):
    resultado = []
    pila_operandos = []
    pila_operadores = []
    
    tokens = expresion.split()
    
    for token in tokens:
        if token.isalnum(): 
            pila_operandos.append(token)
        elif token in "+-*/":
            while (pila_operadores and
                   pila_operadores[-1] != '(' and
                   precedencia(pila_operadores[-1]) >= precedencia(token)):
                aplicar_operador(pila_operandos, pila_operadores, resultado)
            pila_operadores.append(token)
        elif token == '(':
            pila_operadores.append(token)
        elif token == ')':
            while pila_operadores and pila_operadores[-1] != '(':
                aplicar_operador(pila_operandos, pila_operadores, resultado)
            pila_operadores.pop()  
        else:
            return f"Error: Token no reconocido '{token}'"

    while pila_operadores:
        aplicar_operador(pila_operandos, pila_operadores, resultado)

    if len(pila_operandos) != 1:
        return "Error: Expresión mal formada."

    temporal_final = pila_operandos.pop()
    resultado.append(f"{variable} = {temporal_final}")  
    return "\n".join(resultado)
    
def generar_codigo_condicional(condicion, resultado):
    global contador_temporales
    pila_operandos = []
    pila_operadores = []
    tokens = condicion.split()

    if 'and' in tokens or 'or' in tokens or 'not' in tokens:
        return None


    
    for token in tokens:
        if token.isalnum() or re.match(r'[a-zA-Z_]\w*', token): 
            pila_operandos.append(token)
        elif token in "+-*/": 
            while (pila_operadores and
                   pila_operadores[-1] != '(' and
                   precedencia(pila_operadores[-1]) >= precedencia(token)):
                aplicar_operador(pila_operandos, pila_operadores, resultado)
            pila_operadores.append(token)
        elif token in "><=": 
            while pila_operadores and pila_operadores[-1] != '(':
                aplicar_operador(pila_operandos, pila_operadores, resultado)
            pila_operadores.append(token)
        elif token == '(':
            pila_operadores.append(token)
        elif token == ')':
            while pila_operadores and pila_operadores[-1] != '(':
                aplicar_operador(pila_operandos, pila_operadores, resultado)
            pila_operadores.pop() 
        else:
            return f"Error: Token no reconocido '{token}'"

    while pila_operadores:
        aplicar_operador(pila_operandos, pila_operadores, resultado)
        

    if len(pila_operandos) != 1:
        return "Error: Expresión mal formada en la condición."
        
    try:
        contador_temporales -= 1
        if resultado is not None:
            parte_despues_del_igual = resultado[-1].split('=')[1].strip()
        resultado.pop()
    except:
        parte_despues_del_igual = "Error"
    return parte_despues_del_igual

def operadores_logicos(condicion, resultado):
    
    result_operadores = extraer_condiciones(condicion)
    etiquetas_verdaderas = ""
    etiquetas_falsas = ""
    longitud = len(result_operadores)

    texto = condicion.lstrip()
    palabras = texto.split()
    comienza_not = False
    if len(palabras) > 0 and palabras[0] == "not":
        comienza_not = True
    iteracion = 0
    print(comienza_not)
    for condicion1, operador1 in result_operadores:

        if comienza_not and iteracion == 0 and operador1 == None:

            condicion_procesada = generar_codigo_condicional(condicion1, resultado)
            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            
            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero} --LV: {etiqueta_final}  ####")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final} --LF: {etiqueta_verdadero}  #$#$")
            etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
            resultado.append(f"{etiqueta_verdadero}:")

            etiquetas_verdaderas = f"{etiqueta_verdadero}"
            etiquetas_falsas = f"{etiqueta_final}"
            
        elif operador1 == "and" and iteracion == 0:

            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion1, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            
            if comienza_not:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero} --LV: {etiqueta_final}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final} --LF: {etiqueta_verdadero}  #$#$")
                etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
                resultado.append(f"{etiqueta_verdadero}:")
            else:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  #$#$")
                resultado.append(f"{etiqueta_verdadero}:")

            etiquetas_falsas += f"{etiqueta_final}"

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)
            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}")

            etiquetas_verdaderas += f"{etiqueta_verdadero}"
            etiquetas_falsas += f", {etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]

            if longitud <= 2:
                resultado.append(f"{etiquetas_verdaderas}:")
        
        elif operador1 == "and not" and iteracion == 0:

            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion1, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()

            if comienza_not:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero} --LV: {etiqueta_final}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final} --LF: {etiqueta_verdadero}  #$#$")
                etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
                resultado.append(f"{etiqueta_verdadero}:")
            else:

                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  #$#$")
                resultado.append(f"{etiqueta_verdadero}:")

            etiquetas_falsas += f"{etiqueta_final}"

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)
            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  --LV: {etiqueta_final}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  --LF: {etiqueta_verdadero}")

            etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
            etiquetas_verdaderas += f"{etiqueta_verdadero}"
            etiquetas_falsas += f", {etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]

            if longitud <= 2:
                resultado.append(f"{etiquetas_verdaderas}:")

        elif operador1 == "or" and iteracion == 0:

            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion1, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()

            if comienza_not:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero} --LV: {etiqueta_final}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final} --LF: {etiqueta_verdadero}  #$#$")
                etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
                resultado.append(f"{etiqueta_final}:")
            else:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  #$#$")
                resultado.append(f"{etiqueta_final}:")


            etiquetas_verdaderas += f"{etiqueta_verdadero}"

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)
            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}")

            etiquetas_verdaderas += f", {etiqueta_verdadero}"
            etiquetas_falsas += f"{etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]
            
            if longitud <= 2:
                resultado.append(f"{etiquetas_verdaderas}:") 

        elif operador1 == "or not" and iteracion == 0:

            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion1, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            if comienza_not:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero} --LV: {etiqueta_final}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final} --LF: {etiqueta_verdadero}  #$#$")
                etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
                resultado.append(f"{etiqueta_final}:")
            else:
                resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  ####")
                resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  #$#$")
                resultado.append(f"{etiqueta_final}:")


            etiquetas_verdaderas += f"{etiqueta_verdadero}"

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)
            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  --LV: {etiqueta_final}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  --LF: {etiqueta_verdadero}")

            etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
            etiquetas_verdaderas += f", {etiqueta_verdadero}"
            etiquetas_falsas += f"{etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]
            
            if longitud <= 2:
                resultado.append(f"{etiquetas_verdaderas}:") 
            
        
        elif operador1 == "and" and  iteracion <= longitud - 1 :

            resultado.append(f"{etiquetas_verdaderas}:")  

            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()

            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}")

            etiquetas_verdaderas = f"{etiqueta_verdadero}"
            etiquetas_falsas += f", {etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]

            resultado.append(f"{etiquetas_verdaderas}:") 
        elif operador1 == "and not" and  iteracion <= longitud - 1 :

            resultado.append(f"{etiquetas_verdaderas}:")  

            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()

            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}")

            etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
            etiquetas_verdaderas = f"{etiqueta_verdadero}"
            etiquetas_falsas += f", {etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]

            resultado.append(f"{etiquetas_verdaderas}:") 

        elif operador1 == "or" and  iteracion <= longitud - 1 :
            
            resultado.append(f"{etiquetas_falsas}:")  
            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()

            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}")
            etiquetas_verdaderas += f", {etiqueta_verdadero}"
            etiquetas_falsas = f"{etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]

            resultado.append(f"{etiquetas_verdaderas}:")
        elif operador1 == "or not" and  iteracion <= longitud - 1 :
            
            resultado.append(f"{etiquetas_falsas}:")  
            condicion2, operador2 = result_operadores[iteracion+1]
            condicion_procesada = generar_codigo_condicional(condicion2, resultado)

            etiqueta_verdadero = nueva_etiqueta()
            etiqueta_final = nueva_etiqueta()

            resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}  --LV: {etiqueta_final}")
            resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}  --LF: {etiqueta_verdadero}")

            etiqueta_verdadero, etiqueta_final = etiqueta_final, etiqueta_verdadero
            etiquetas_verdaderas += f", {etiqueta_verdadero}"
            etiquetas_falsas = f"{etiqueta_final}"

            resultado = [lineas.replace("####", f'--LV: {etiquetas_verdaderas}    ####') for lineas in resultado]
            resultado = [lineas.replace("#$#$", f'--LF: {etiquetas_falsas}    #$#$') for lineas in resultado]

            resultado.append(f"{etiquetas_verdaderas}:") 
        
        iteracion += 1

    resultado = [lineas.replace("####", f'') for lineas in resultado]
    resultado = [lineas.replace("#$#$", f'') for lineas in resultado]
    
    
    return etiquetas_verdaderas, etiquetas_falsas, resultado


def extraer_condiciones(expresion):
    operadores = re.findall(r'\b(?:and not|or not|and|or)\b', expresion)
    
    condiciones = re.split(r'\b(?:and not|or not|and|or)\b', expresion)
    
    condiciones = [condicion.strip() for condicion in condiciones]
    
    if condiciones[0].startswith('not '):
        condiciones[0] = condiciones[0][4:]
    
    resultado = []

    for i, condicion in enumerate(condiciones):
        if i < len(operadores):
            resultado.append((condicion, operadores[i]))
        else:
            resultado.append((condicion, None))
    
    return resultado

def manejar_if(tokens, resultado):
    match = re.search(r'if\s*\((.*?)\)', ' '.join(tokens))
    if not match:
        raise ValueError("Condición if no válida.")
    
    condicion = match.group(1).strip()
    condicion_procesada = generar_codigo_condicional(condicion, resultado)
    if condicion_procesada is not None:
        etiqueta_verdadero = nueva_etiqueta()
        etiqueta_final = nueva_etiqueta()

        resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
        resultado.append(f"Goto {etiqueta_final}                --LF: {etiqueta_final}")
        resultado.append(f"{etiqueta_verdadero}:") 
    else:
        etiqueta_verdadero, etiqueta_final, resultado = operadores_logicos(condicion, resultado)
    

    bloque_if_match = re.search(r'\{\s*(.*?)\s*\}', ' '.join(tokens), re.DOTALL)
    if bloque_if_match:
        bloque_if = bloque_if_match.group(1).strip()
        if "<sentencias1>" in bloque_if or "[sentencias1]" in bloque_if or "<sentencias 1>" in bloque_if or "[sentencias 1]" in bloque_if:
            resultado.append(bloque_if) 
        else:
            for sentencia in bloque_if.split(";"):
                sentencia = sentencia.strip()
                if sentencia:
                    codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                    resultado.append(codigo_bloque)
    resultado.append(f"{etiqueta_final}:")


    return "\n".join(resultado)


def manejar_if_else(expresion, resultado):
    match = re.search(r'if\s*\((.*?)\)\s*{(.*?)}\s*else\s*{(.*?)}', expresion, re.DOTALL)
    
    if not match:
        raise ValueError("La expresión no es válida para un if-else.")
    
    condicion = match.group(1).strip()
    bloque_if = match.group(2).strip()
    bloque_else = match.group(3).strip()

    condicion_procesada = generar_codigo_condicional(condicion, resultado)
    if condicion_procesada is not None:
        etiqueta_verdadero = nueva_etiqueta()
        etiqueta_falso = nueva_etiqueta()
        resultado.append(f"if {condicion_procesada} goto {etiqueta_verdadero}       --LV: {etiqueta_verdadero}")
        resultado.append(f"Goto {etiqueta_falso}                --LF: {etiqueta_falso}")
        resultado.append(f"{etiqueta_verdadero}:")

    else:
        etiqueta_verdadero, etiqueta_falso, resultado = operadores_logicos(condicion, resultado)

    if "[sentencias1]" in bloque_if or "<sentencias1>" in bloque_if or \
       "[sentencias 1]" in bloque_if or "<sentencias 1>" in bloque_if:
        resultado.append(bloque_if) 
    else:
        for sentencia in bloque_if.split(";"):
            sentencia = sentencia.strip()
            if sentencia:
                codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                resultado.append(codigo_bloque)

    etiqueta_salida = nueva_etiqueta()
    resultado.append(f"Goto {etiqueta_salida}           --LS: {etiqueta_salida}")
    resultado.append(f"{etiqueta_falso}:")

    if "[sentencias2]" in bloque_else or "<sentencias2>" in bloque_else or \
       "[sentencias 2]" in bloque_else or "<sentencias 2>" in bloque_else:
        resultado.append(bloque_else)  
    else:
        for sentencia in bloque_else.split(";"):
            sentencia = sentencia.strip()
            if sentencia:
                codigo_bloque_else = generar_codigo_tres_direcciones(sentencia)
                resultado.append(codigo_bloque_else)

    resultado.append(f"{etiqueta_salida}:")
    return "\n".join(resultado)

def manejar_if_elseif_else(expresion, resultado):
    etiqueta_salida = []
    etiqueta_else = ""

    condicion_if = re.search(r'if\s*\((.*?)\)', expresion).group(1).strip()  
    condicion_if_procesada = generar_codigo_condicional(condicion_if, resultado)
    if condicion_if_procesada is not None:
        etiqueta_if_verdadero = nueva_etiqueta()  
        etiqueta_else = nueva_etiqueta() 
        resultado.append(f"if {condicion_if_procesada} goto {etiqueta_if_verdadero}       --LV: {etiqueta_if_verdadero}")
        resultado.append(f"Goto {etiqueta_else}                --LF: {etiqueta_else}") 
        resultado.append(f"{etiqueta_if_verdadero}:")
    else:
        etiqueta_verdadero, etiqueta_falso, resultado = operadores_logicos(condicion_if, resultado)
        etiqueta_else = etiqueta_falso


    bloque_if_match = re.search(r'\{\s*(.*?)\s*\}', ''.join(expresion), re.DOTALL)
    if bloque_if_match:
        bloque_if = bloque_if_match.group(1).strip()
        if "<sentencias1>" in bloque_if or "[sentencias1]" in bloque_if or "<sentencias 1>" in bloque_if or "[sentencias 1]" in bloque_if:
            resultado.append(bloque_if)  
        else:
            for sentencia in bloque_if.split(";"):
                sentencia = sentencia.strip()
                if sentencia:
                    codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                    resultado.append(codigo_bloque)
                    pass


        etiqueta_salida_1 = nueva_etiqueta() 
        resultado.append(f"Goto {etiqueta_salida_1}         --LS: {etiqueta_salida_1}")
        etiqueta_salida.append(etiqueta_salida_1)

    bloque_sentencia = 2  
    for match in re.finditer(r'elseif\s*\((.*?)\)\s*{(.*?)}', expresion, re.DOTALL):
        condicion_elseif = match.group(1).strip()

        condicion_elseif_procesada = generar_codigo_condicional(condicion_elseif, resultado)
        
        resultado.append(f"{etiqueta_else}:") 
        if condicion_elseif_procesada is not None:
            etiqueta_elseif_verdadero = nueva_etiqueta() 
            etiqueta_else_siguiente = nueva_etiqueta()  
            resultado.append(f"if {condicion_elseif_procesada} goto {etiqueta_elseif_verdadero}       --LV: {etiqueta_elseif_verdadero}")
            resultado.append(f"Goto {etiqueta_else_siguiente}                --LF: {etiqueta_else_siguiente}")
            resultado.append(f"{etiqueta_elseif_verdadero}:")
        else:
            etiqueta_verdadero, etiqueta_falso, resultado = operadores_logicos(condicion_elseif, resultado)
            etiqueta_else = etiqueta_falso


        if match:
            bloque_if = match.group(2).strip()
            if f"<sentencias{bloque_sentencia}>" in bloque_if or f"[sentencias{bloque_sentencia}]" in bloque_if or f"<sentencias {bloque_sentencia}>" in bloque_if or f"[sentencias {bloque_sentencia}]" in bloque_if:
                resultado.append(bloque_if)  
            else:
                for sentencia in bloque_if.split(";"):
                    sentencia = sentencia.strip()
                    if sentencia:
                        codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                        resultado.append(codigo_bloque)
                        pass


        etiqueta_salida_nueva = nueva_etiqueta() 
        resultado.append(f"Goto {etiqueta_salida_nueva}         --LS: {', '.join(etiqueta_salida + [etiqueta_salida_nueva])}")

        etiqueta_salida.append(etiqueta_salida_nueva)
        if condicion_elseif_procesada is not None:
            etiqueta_else = etiqueta_else_siguiente
        bloque_sentencia += 1

    resultado.append(f"{etiqueta_else}:")

    bloques_if = re.findall(r'\{\s*(.*?)\s*\}', ''.join(expresion), re.DOTALL)
    ultima_coincidencia = bloques_if[-1] if bloques_if else None
    if ultima_coincidencia:
        bloque_if = ultima_coincidencia.strip()
        if f"<sentencias{bloque_sentencia}>" in bloque_if or f"[sentencias{bloque_sentencia}]" in bloque_if or f"<sentencias {bloque_sentencia}>" in bloque_if or f"[sentencias {bloque_sentencia}]" in bloque_if:
            resultado.append(bloque_if) 
        else:
            for sentencia in bloque_if.split(";"):
                sentencia = sentencia.strip()
                if sentencia:
                    codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                    resultado.append(codigo_bloque)
                    pass

    
    resultado.append(f"{', '.join(etiqueta_salida)}:")
    return "\n".join(resultado)

def manejar_while(expresion, resultado):
    etiqueta_recurrencia = "LR"

    
    resultado.append(f"{etiqueta_recurrencia}:")
    match = re.search(r'while\s*\((.*?)\)', expresion).group(1).strip()  
    if not match:
        raise ValueError("Condición if no válida.")
    
    condicion = match
    condicion_procesada = generar_codigo_condicional(condicion, resultado)
    if condicion_procesada is not None:
        
        etiqueta_inicio = nueva_etiqueta()
        etiqueta_salida = nueva_etiqueta()
        resultado.append(f"if {condicion_procesada} goto {etiqueta_inicio}       --LV: {etiqueta_inicio}")
        resultado.append(f"Goto {etiqueta_salida}                --LF: {etiqueta_salida}") 
        resultado.append(f"{etiqueta_inicio}:")
    else:
        etiqueta_verdadero, etiqueta_salida, resultado = operadores_logicos(condicion, resultado)
    bloque_if_match = re.search(r'\{\s*(.*?)\s*\}', ''.join(expresion), re.DOTALL)
    if bloque_if_match:
        bloque_if = bloque_if_match.group(1).strip()
        if "<sentencias1>" in bloque_if or "[sentencias1]" in bloque_if or "<sentencias 1>" in bloque_if or "[sentencias 1]" in bloque_if:
            resultado.append(bloque_if)  
        else:
            for sentencia in bloque_if.split(";"):
                sentencia = sentencia.strip()
                if sentencia:
                    codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                    resultado.append(codigo_bloque)
                    pass

    etiqueta_recurrencia = nueva_etiqueta()
    resultado.append(f"goto {etiqueta_recurrencia}")
    resultado.append(f"{etiqueta_salida}:")
    resultado = [lineas.replace('LR:', f'{etiqueta_recurrencia}:') for lineas in resultado]
    return "\n".join(resultado)


def manejar_dowhile(expresion, resultado):
    etiqueta_recurrencia = "LR"
    resultado.append(f"{etiqueta_recurrencia}:")


    bloque_do = re.search(r'do\s*{(.*?)}\s*while\s*\((.*?)\)', expresion, re.DOTALL)
    if bloque_do:
        bloque_if = bloque_do.group(1).strip()
        if "<sentencias1>" in bloque_if or "[sentencias1]" in bloque_if or "<sentencias 1>" in bloque_if or "[sentencias 1]" in bloque_if:
            resultado.append(bloque_if)  
        else:
            for sentencia in bloque_if.split(";"):
                sentencia = sentencia.strip()
                if sentencia:
                    codigo_bloque = generar_codigo_tres_direcciones(sentencia)
                    resultado.append(codigo_bloque)
                    pass

    condicion = bloque_do.group(2).strip()
    condicion_procesada = generar_codigo_condicional(condicion, resultado)
    if condicion_procesada is not None:
        
        etiqueta_recurrencia = nueva_etiqueta()  
        etiqueta_salida = nueva_etiqueta() 
        resultado.append(f"if {condicion_procesada} goto {etiqueta_recurrencia}       --LV: {etiqueta_recurrencia}")
        resultado.append(f"goto {etiqueta_salida}                --LF: {etiqueta_salida}")
    else:
        etiqueta_verdadero, etiqueta_salida, resultado = operadores_logicos(condicion, resultado)
        etiqueta_recurrencia = etiqueta_verdadero
    resultado = [lineas.replace('LR:', f'{etiqueta_recurrencia}:') for lineas in resultado]
    resultado.append(f"{etiqueta_salida}:") 

    return "\n".join(resultado)


def precedencia(operador):
    if operador in "+-":
        return 1
    elif operador in "*/":
        return 2
    else:
        return 0

def aplicar_operador(pila_operandos, pila_operadores, resultado):
    operador = pila_operadores.pop()
    operando2 = pila_operandos.pop()
    operando1 = pila_operandos.pop()
    
    temporal = nuevo_temporal()
    resultado.append(f"{temporal} = {operando1} {operador} {operando2}")
    pila_operandos.append(temporal)
    return temporal

def codigo_3_direcciones(entrada_texto):
    global contador_etiquetas
    global contador_temporales
    contador_temporales = 1
    contador_etiquetas = 1
    resultado_codigo = generar_codigo_tres_direcciones(entrada_texto)
    return resultado_codigo

def limpiar_codigo_3_direcciones():
    global contador_temporales, contador_etiquetas
    contador_temporales = 1
    contador_etiquetas = 1
