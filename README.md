# Laboratorio de Producto de Datos 2021


Estructura de información

```
└──FLASK_ON_DOCKER (este directorio)
    ├── src
    |    ├──main
    |    |    ├──api (Contiene los endpoints, RequestParser y métodos)
    |    |    ├──models (Módelo de tablas en SQLAlchemy)
    |    |    ├──__init__.py
    |    |    ├──configs.py
    |    |    └──exceptions.py
    |    ├──migrations
    |    ├──entrypoint.sh 
    |    ├──manage.py
    |    └──setup.py      
    ├── .env (Variables de entorno)
    ├── docker-compose.yml
    └── Dockerfile
```

### Prerequisito: Tener Docker instalado en tu computador.
 
 
## Pasos usando Docker

```
docker-compose -f docker-compose.yml build --no-cache

docker-compose up
```

## Pregunta 2.1
El endpoint ```/predict``` se encuentra en ```src/main/api/clasifier_pd/endpoints/``` en la route ```@imagentry_ns.route("/predict", endpoint="predict_image")```

## Pregunta 2.2
Presente en el archivo ```consultas_api.ipynb```

## Pregunta 2.3
El endpoint ```/countObject``` se encuentra en ```src/main/api/clasifier_pd/endpoints/``` en la route ```@imagentry_ns.route("/countObject", endpoint="count_objects")```

## Pregunta 2.4
Presente en el archivo ```consultas_api.ipynb```
 
## Pregunta 3.1
Un ejemplo de aplicación de negocio actual seria un contador de personas dentro de un recinto con espacios cerrados, enfocado en las restricciones de aforo impuestas por el Ministerio de Salud.

Vale la pena destacar que más allá de un contador de personas, debemos enfocarnos en un contador de rostros o de cualquier otra parte única y facilmente identificable por medio de una camara. Consideremos que el proceso de identificación de una persona a cuerpo completo tendría la dificultad del ángulo de captura de la imagen y por otra parte la sobreposición de personas haria más dificil la captura a cuerpo completo.

 Los usuarios serian administradores de recintos comerciales, tiendas, establecimientos culturales, de entretenimiento o educacionales. Las aplicaciones se podrían dar a dos niveles:


- Contadores en puntos de control: Enfocado al conteo de personas en recintos de corta estadia, donde la ubicación estratégica de las camaras en puntos de entrada y salida, permite estimar el flujo temporal de personas en un recinto. Esta información cruzada con datos de la superficie del recinto en m2, permitiria determinar si el aforo esta siendo cumplido a cabalidad.

- Contadores de espacios cerrados: Enfocado al conteo de personas en recintos donde se realicen actividades habituales, como actividades de estudio, laborales o culturales, donde el conteo de personas en salones, cowork, anfiteatros o comedores permitiria calcular el número de personas que frecuentan un lugar y asi controlar de forma óptima el flujo activo de personas en el lugar.


El valor de esta aplicación busca por un lado controlar de mejor manera la entrada y salida de personas en un lugar, de ahi en base a información histórica es posible generar estimadores que permitan conocer el tiempo estimado de entrada a un recinto (semejante al tiempo de espera en el Metro de Santiago) lo que reduciría la incertidumbre del usuario o cliente del recinto. Por otro lado, busca evitar sumarios sanitarios o infracciones por parte del Ministerio de Salud, que pueden llegar hasta los 50 millones de pesos.


