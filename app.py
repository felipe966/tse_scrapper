import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re
import sys


def inspect_csv(csv_file):
    # Create a WebDriver instance (no need to specify executable_path)
    driver = webdriver.Chrome()

    # Load the CSV file

    df = pd.read_csv(csv_file)

    # Ensure the 'Fecha defuncion' column has a string data type
    df['Fecha defuncion'] = df['Fecha defuncion'].astype(str)
    df['resultado'] = df['resultado'].astype(str)
    df['Fecha Nacimiento'] = df['resultado'].astype(str)
    df['Nombre completo'] = df['resultado'].astype(str)
    df['Tipo identificacion'] = df['resultado'].astype(str)

    try:
        for index, row in df.iterrows():
            print(index)
            id_str=str(row['cedula'])
            # Navigate to the website
            driver.get("https://servicioselectorales.tse.go.cr/chc/consulta_cedula.aspx")
            # Find the input field for the ID number and enter the ID from the CSV
            id_input = driver.find_element(By.ID, "txtcedula")
            id_input.clear()  # Clear any existing input
            id_input.send_keys(id_str)  # Use the 'cedula' column from the CSV

            tipo_id=inspect_id(id_str)
            df.at[index, 'Tipo identificacion'] = tipo_id

            id_str_tipo=id_str+' - '+tipo_id

            # Click the "Consultar" button
            consultar_button = driver.find_element(By.ID, "btnConsultaCedula")
            consultar_button.click()

            time.sleep(2)
            
            # Check if the element with ID "lbldefuncion1" exists on the page
            try:
                lbl_nombre_completo = driver.find_element(By.ID, "lblnombrecompleto")
                df.at[index, 'Nombre completo'] = lbl_nombre_completo.text
                id_str_tipo+=' - '+lbl_nombre_completo.text
                lbl_fecha_nacimiento = driver.find_element(By.ID, "lblfechaNacimiento")
                df.at[index, 'Fecha Nacimiento'] = lbl_fecha_nacimiento.text
                id_str_tipo+=' - '+lbl_fecha_nacimiento.text
                lbl_defuncion_element = driver.find_element(By.ID, "lbldefuncion1")
                lbl_defuncion2_element = driver.find_element(By.ID, "lbldefuncion2")
                if lbl_defuncion_element.text.strip():  # Check if the element has non-empty text
                    df.at[index, 'resultado'] = "FALLECIDO"
                    df.at[index, 'Fecha defuncion'] = lbl_defuncion2_element.text
                    print(f"{id_str_tipo} - Fallecido en "+lbl_defuncion2_element.text)
                
            except NoSuchElementException:
                try:
                    lblMensaje2 = driver.find_element(By.ID, "lblmensaje1")
                    if lblMensaje2.text ==  "No se encontró información en la base de datos registral civil que coincida con los datos aportados.":
                        df.at[index, 'resultado'] = "No se encontró información en la base de datos"
                        print(f"{id_str_tipo} - No se encontró información en la base de datos")
                except NoSuchElementException:
                    try:
                        lblmensajes = driver.find_element(By.ID, "lblmensajes")
                        if lblmensajes.text ==  "Por favor ingrese una cédula válida":
                            df.at[index, 'resultado'] = "Cédula invalida"
                            print(f"{id_str_tipo} - Cédula invalida")
                    except NoSuchElementException:
                        df.at[index, 'resultado'] = "Sin fecha defuncion"
                        print(f"{id_str_tipo} - Sin fecha de defuncion")

            # Wait for n seconds before proceeding to the next query
            time.sleep(1)

    except Exception as e:
        print("An error occurred:", str(e))

    finally:
        # Close the browser window
        driver.quit()

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)

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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py nombre_archivo.csv")
    else:
        archivo_csv = sys.argv[1]
        inspect_csv(archivo_csv)


