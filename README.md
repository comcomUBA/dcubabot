# dcubabot

La idea de este repositorio es migrar desde el viejo repositorio las funcionalidades que tiene el bot de forma estructurada, prolija y segura. Muy pronto traeremos bardearmarto, tranquilos.

Mientras seguimos la migración todos son libres de colaborar con pull requests.

Para probar el bot en acción en Telegram es necesario crear un archivo `tokenz.py` que asigne a la variable `token` el token del bot con el que se desea hacer las pruebas.

Para instalar las dependencias correr lo siguiente:
```bash
$ pip3 install -r requirements.txt
```

pero te recomendamos que mejor te armes un ambiente virtual (no es necesario hacerlo cada vez):
```bash
$ python3 -m venv venv
$ venv/bin/pip3 install -r requirements.txt
```

para que el bot tenga los comandos hay que instalarlos en la base de datos:
```bash
$ venv/bin/python3 install.py
```
y ahora si es posible correr el bot:
```bash
$ venv/bin/python3 dcubabot.py
```

## notas:
- la librería pony no funciona con python3.11, así que vas a necesitar instalarte python3.10
  tenés muchas alternativas, descargartelo de la web, usar el paquete de tu distro, etc
  Otra es usar **guix** que permite además crearte todo el ambiente y tener una shell contenerizada, para instalarlo podés ver el primer link de [la guia de instalación binaria](https://guix.gnu.org/manual/en/html_node/Binary-Installation.html) que apunta a un script que automatiza el proceso.
  Luego:
  ```bash
  guix shell python3.10.7
  ```
  y luego seguir con la instalación del ambiente virtual. 

también podés correr dicha shell en un container, pero en ese caso tenés que instalar más paquetes:
  ```bash
  guix shell -CN coreutils tzdata python@3.10.7
  ```
  '-C' crea el container y '-N' habilita el uso de la red.
  tené en cuenta que vas a tener que recrear el ambiente virtual en estes caso. 

  
