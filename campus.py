import requests

def is_campus_up():

    response_threshold = 3
    timeout = 5
    url = "https://campus.exactas.uba.ar"

    try:
        response = requests.get(url, timeout=timeout)
        response_time = response.elapsed.total_seconds() 
        
        msg = ""
        if  400 <= response.status_code:
            msg = "El campus está caído :("
        elif response_time > response_threshold :
            msg = "El campus pareciera estar andando medio lenteja :/"
        else:
            msg = "El campus pareciera estar andando :)"      
    
    except requests.exceptions.Timeout:
        msg = "Tardó bocha y no recibí respuesta. Debe estar caído o andando lento :(" 

    return msg
