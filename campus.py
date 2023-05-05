import requests

def is_campus_up():

    response_threshold = 3
    timeout = 5
    url = "https://campus.exactas.uba.ar"

    try:
        response = requests.get(url, timeout=timeout)
        response_time = response.elapsed.total_seconds()
        response.raise_for_status() 
        
        msg = ""
        if response_time > response_threshold:
            msg = "El campus pareciera estar andando medio lenteja :/"
        else:
            msg = "El campus pareciera estar andando :)"      
    
    except requests.exceptions.Timeout:
        msg = "Tardó bocha y no recibí respuesta. Debe estar caído o andando lento :("
    except requests.exceptions.ConnectionError:
        msg = "Hubo un error de conexión, debe estar caído. Espero no sea época de parciales..."
    except requests.exceptions.HTTPError:
        msg = f"Recibí una respuesta del campus con error. {response.status_code}: {response.reason}"
    except:
        msg = "Hubo un error y no tengo idea de qué fue. Rezale a Shannon."

    return msg
