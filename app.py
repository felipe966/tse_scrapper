import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re
import sys
import concurrent.futures

def inspect_id(identificacion):
    # Expresiones regulares para verificar los formatos
    formato_persona_fisica = r'^[1-7]\d{8}$'
    formato_costarricense_naturalizado = r'^8\d{8}$'
    formato_partida_especial = r'^9\d{8}$'
    formato_persona_juridica = r'^3\d{9}$'
    formato_dimex = r'^1\d{11}$'
    formato_didi = r'^5\d{11}$'

    # Verificar el tipo de identificación
    if re.match(formato_persona_fisica, identificacion):
        return "Persona física"
    elif re.match(formato_costarricense_naturalizado, identificacion):
        return "Persona física - Costarricense Naturalización"
    elif re.match(formato_partida_especial, identificacion):
        return "Persona física - Partida Especial"
    elif re.match(formato_persona_juridica, identificacion):
        return "Persona Jurídica"
    elif re.match(formato_dimex, identificacion):
        return "DIMEX"
    elif re.match(formato_didi, identificacion):
        return "DIDI"
    else:
        return "Tipo de identificación desconocido"

def inspect_csv_partial(df):
    driver = webdriver.Chrome()
    
    # Load the CSV file


    # Ensure the 'Fecha defuncion' column has a string data type
    df['Fecha defuncion'] = df['Fecha defuncion'].astype(str)
    df['resultado'] = df['resultado'].astype(str)
    df['Fecha Nacimiento'] = df['resultado'].astype(str)
    df['Nombre completo'] = df['resultado'].astype(str)
    df['Tipo identificacion'] = df['resultado'].astype(str)

    try:
        for index, row in df.iterrows():
            # id_str=''
            # id_str_tipo=''
            # df.at[index, 'resultado'] = 'nan'
            # df.at[index, 'Fecha defuncion'] = 'nan'
            # df.at[index, 'Tipo identificacion'] = 'nan'
            # df.at[index, 'Nombre completo'] = 'nan'
            # df.at[index, 'Fecha Nacimiento'] = 'nan'

            id_str = str(row['cedula'])
            #print(index, ': ', id_str)
            tipo_id = inspect_id(id_str)
            df.at[index, 'Tipo identificacion'] = tipo_id
            id_str_tipo = str(index)+': '+id_str + ' - ' + tipo_id

            if tipo_id not in ['Persona física', 'Persona física - Costarricense Naturalización', 'Persona física - Partida Especial']:
                continue

            driver.get("https://servicioselectorales.tse.go.cr/chc/consulta_cedula.aspx")
            id_input = driver.find_element(By.ID, "txtcedula")
            id_input.clear()
            id_input.send_keys(id_str)

            consultar_button = driver.find_element(By.ID, "btnConsultaCedula")
            consultar_button.click()

            time.sleep(2)

            try:
                lbl_nombre_completo = driver.find_element(By.ID, "lblnombrecompleto")
                df.at[index, 'Nombre completo'] = lbl_nombre_completo.text
                id_str_tipo += ' - ' + lbl_nombre_completo.text
                lbl_fecha_nacimiento = driver.find_element(By.ID, "lblfechaNacimiento")
                df.at[index, 'Fecha Nacimiento'] = lbl_fecha_nacimiento.text
                id_str_tipo += ' - ' + lbl_fecha_nacimiento.text
                lbl_defuncion_element = driver.find_element(By.ID, "lbldefuncion1")
                lbl_defuncion2_element = driver.find_element(By.ID, "lbldefuncion2")
                if lbl_defuncion_element.text.strip():
                    df.at[index, 'resultado'] = "FALLECIDO"
                    df.at[index, 'Fecha defuncion'] = lbl_defuncion2_element.text
                    print(f"{id_str_tipo} - Fallecido en " + lbl_defuncion2_element.text)

            except NoSuchElementException:
                try:
                    lblMensaje2 = driver.find_element(By.ID, "lblmensaje1")
                    if lblMensaje2.text == "No se encontró información en la base de datos registral civil que coincida con los datos aportados.":
                        df.at[index, 'resultado'] = "No se encontró información en la base de datos"
                        print(f"{id_str_tipo} - No se encontró información en la base de datos")
                except NoSuchElementException:
                    try:
                        lblmensajes = driver.find_element(By.ID, "lblmensajes")
                        if lblmensajes.text == "Por favor ingrese una cédula válida":
                            df.at[index, 'resultado'] = "Cédula invalida"
                            print(f"{id_str_tipo} - Cédula invalida")
                    except NoSuchElementException:
                        df.at[index, 'resultado'] = "Sin fecha defuncion"
                        print(f"{id_str_tipo} - Sin fecha de defuncion")

            time.sleep(1)
    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        driver.quit()

    return df

def inspect_csv_multi_threaded(csv_file, num_threads):
    df = pd.read_csv(csv_file)
    total_rows = len(df)

    # Divide the DataFrame into parts to be processed by each thread
    chunk_size = total_rows // num_threads
    futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size if i < num_threads - 1 else total_rows
            df_part = df.iloc[start:end].copy()  # Create a copy of the DataFrame part
            futures.append(executor.submit(inspect_csv_partial, df_part))

    # Wait for all threads to finish
    for future in concurrent.futures.as_completed(futures):
        if future.exception() is not None:
            print("Error in thread:", future.exception())

    # Concatenate the results from all threads
    result_df = pd.concat([future.result() for future in futures], ignore_index=True)

    # Write the result DataFrame to a CSV file
    result_df.to_csv('resultado_' + csv_file, index=False)

def inspect_csv_multi_subprocess(csv_file, num_processes):
    df = pd.read_csv(csv_file)
    total_rows = len(df)

    # Divide el DataFrame en partes iguales para cada subprocess
    chunk_size = total_rows // num_processes
    futures = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        for i in range(num_processes):
            start = i * chunk_size
            end = start + chunk_size if i < num_processes - 1 else total_rows
            futures.append(executor.submit(inspect_csv_partial, csv_file, start, end))

    # Espera a que todos los subprocesses finalicen
    for future in concurrent.futures.as_completed(futures):
        if future.exception() is not None:
            print("Error in subprocess:", future.exception())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script.py nombre_archivo.csv num_threads")
    else:
        archivo_csv = sys.argv[1]
        num_threads = int(sys.argv[2])

        # Record the start time
        start_time = time.time()

        inspect_csv_multi_threaded(archivo_csv, num_threads)

        # Record the end time
        end_time = time.time()

        # Calculate and print the total time taken
        total_time = end_time - start_time
        print(f"Total time taken: {total_time} seconds")

