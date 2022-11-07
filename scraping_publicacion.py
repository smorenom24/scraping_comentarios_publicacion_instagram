"""web scrpaing solo con selenium
+
Un montón de configs para chrome y evitar detecciones de bots"""

#Para guardar cookies
import pickle
#Instalación automática de webdriver
from lib2to3.pgen2 import driver
import os
from webdriver_manager.chrome import ChromeDriverManager
#Drivers de selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

#Para modificar opciones de webdriver de chrome
from selenium.webdriver.chrome.options import Options
#Para buscar elementos con sellenium:
from selenium.webdriver.common.by import By
from credenciales import *
#Para manejar el tiempo de espera
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import pickle

def iniciar_chrome():
    """Inicia chrome con los parámetros indicados. Devuelve el driver."""  

    #Instalamos la versión del chromedirve correspondiente. Nos devuelve la ruta completa del ejecutable.
    ruta = ChromeDriverManager(path='./chromedriver').install()
    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    options.add_argument(f"user-agent={user_agent}")
    #dimensiones de chrome:
    options.add_argument("--window-size=970,1080")
    #options.add_argument("--headless") #Para que no se abra ventana
    options.add_argument("--start-maximized")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors") #Hasta aquí son autodescriptivos
    options.add_argument("--no-sandbox") 
    options.add_argument("--log-level=3") #Para que chromedriver no muestre nada en la terminal
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run") #evita las ejecuciones de eventos que pasan la 1era vez que inicia chrome
    options.add_argument("--no-proxy-server")
    options.add_argument("--disable-blink-features=AutomationControlled") #Importante!!! evita que sellenium sea detectado como bot

    #Parámetros a omitir en el inicio de chromedriver
    exp_opt = [
        'enable-automation',
        'ignore-certificate-errors',
        'enable-logging' #Para salida más limpia x terminal
    ]
    options.add_experimental_option("excludeSwitches",exp_opt)

    #Parámetros que definen preferencias en CHROMEDRIVER
    prefs = {
        'profile.default_content_setting_values.notifications' : 2, # 0 = preguntar, 1 = aceptar, 2 = no aceptar
        'intl.accept_languages' : ["es-ES", "es"],
        "credentials_enable_service" : False #Para no preguntar si guardamos contraseñas. 
    }
    options.add_experimental_option("prefs", prefs)

    #instanciamos el servicio de chromedriver
    s = Service(ruta)
    #webdriver de selenium con chrome
    driver = webdriver.Chrome(service=s,options=options)
    driver.set_window_position(0,0)
    return driver

def login_instagram():
    """Función que realiza un logeo en IG según el archivo credenciales.py inicilmente.
    Guarda cookies para hacer un loguin más rápido las siguientes veces"""
    #Comprobamos si hay cookies
    if os.path.isfile("instagram.cookies"):
        print("Hay cookies. Usamos este login.")
        cookies = pickle.load(open("instagram.cookies", 'rb'))
        driver.get("https://instagram.com/robots.txt")
        #recorremos el obj cookies y las añadimos al driver
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get("https://www.instagram.com")
        try:
            elemento = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "article[role = 'presentation']")))
            print('   Login desde 0 ok.')
            return "OK"
        except TimeoutException:
            print('    Error: feed de noticias no se ha cargado')
            return "Error"
    
    print("No hay cookies. Login desde 0")
    driver.get("https://instagram.com/")
    ##############Scraping de username and password###################
    try:
        username_input = wait.until(ec.visibility_of_element_located((By.NAME, "username")))
    except TimeoutException:
        print('    Error: Elemento "username" no disponible')
        return "Error"
    username_input.send_keys(USER_IG)
    try:
        password_input = wait.until(ec.visibility_of_element_located((By.NAME, "password")))
    except TimeoutException:
        print('    Error: Elemento "password" no disponible')
        return "Error"
    password_input.send_keys(PASS_IG)
    boton_submit = wait.until(ec.element_to_be_clickable((By.XPATH, "//div[text()='Iniciar sesión']")))
    boton_submit.click()
    try:
        guardar_info = wait.until(ec.element_to_be_clickable((By.XPATH, "//button[text()='Ahora no']")))
        guardar_info.click()
    except:
        pass    
    ##############Scraping de username and password###################
    
    try:
        elemento = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "article[role = 'presentation']")))
        print('   Login desde 0 ok.')
        #Guardamos cookies
        cookies = driver.get_cookies()
        pickle.dump(cookies, open("instagram.cookies", "wb"))
        return "OK"    
    except TimeoutException:
        print('    Error: feed de noticias no se ha cargado')
        return "Error"
    
def extraccion_comentarios_ig(link):
    """Función que extrae comentarios de una publicación ingresada. Retorna lista con cada elemento que incluye
    username de persona que hizo comentario + su comentario.
    ***Por ahora no considera extracción de respuestas."""
    driver.get(link)
    
    while True:
        #El ciclo identifica todos los botones que cargan más comentarios hasta que no se puedan cargar más.
        try:
            more_comments = wait.until(ec.element_to_be_clickable((By.XPATH, "//*[local-name()='svg' and @aria-label='Cargar más comentarios']")))
            comentarios = driver.find_elements(By.XPATH,"//div/div/div/div[1]/div/div/div/div[1]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/ul")
            more_comments.click()
        except TimeoutException:
            print("Ya aparecieron todos los comentarios.")
            break
    cantidad_comentarios = len(comentarios)
    print("Sacamos: " + str(cantidad_comentarios) + " comentarios.")
    lista_user_comentario = []
    for comentario in comentarios:
        lista_comentario = comentario.text.encode().split(b'\n')
        #Condición para ver qué comentarios tenían respuestas a él.
        if lista_comentario[-1].decode("utf-8")[0:14] == "Ver respuestas":
            user = lista_comentario[0].decode("utf-8")
            mensaje_decodificado = lista_comentario[-1].decode("utf-8")
            cantidad_respuestas_inicio = mensaje_decodificado.find("(") + 1
            cantidad_respuestas_final = mensaje_decodificado.find(")")
            cantidad_respuestas = mensaje_decodificado[cantidad_respuestas_inicio:cantidad_respuestas_final]
            print(f"El comentario de {user} tenía {cantidad_respuestas} respuestas")
        #Se guarda el username + comentario en una lista y se agrega a la lista final.    
        lista_user_comentario.append([lista_comentario[0].decode('utf-8'),lista_comentario[1].decode('utf-8')])
    return lista_user_comentario

def write_csv_from_list_with_comment(output_name_file, total_list):
    """Función que escribe en csv. Recibe un string output_name_file que debe incluir la extensión csv.
    También recibe la lista de usernames+comentario."""
    import csv
    with open(output_name_file,"w",encoding = "utf-8") as f:
        writer = csv.writer(f)
        for line in total_list:
            writer.writerow(line)
        print("CSV generado y rellenado.")

if __name__ == '__main__':
    driver = iniciar_chrome()
    #Para tiempos de espera 10seg como máximo en que aparezca el elemento a scrapear:
    wait = WebDriverWait(driver,10)
    res = login_instagram()
    #Por ahora hardcodeado el link. Podemos pedir por consola este link
    link_publicacion = "https://www.instagram.com/p/Cj1Lq62uLaa/?hl=es"
    lista_comentarios = extraccion_comentarios_ig(link_publicacion)
    write_csv_from_list_with_comment("comentario_publicacion_cnn.csv", lista_comentarios)
    print("Extraccion completada :D")