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


## Pregunta 3.2

En un caso hipotético de implementación de este módelo de ML, podremos vernos enfrentados a las siguientes dificultades:

- Calidad de datos: Se puede dar el caso que la calidad de las cámaras no sea la adecuada, esto puede generar fallas en la identificación de personas en imagenes "pixeladas" donde el bajo contraste de colores dificultaria la identificación de un rostro. Una solución viable estaria vinculada al módelo de negocios, donde se deberia licitar el servicio de reconocimiento de personas junto con las cámaras.

- Decadencia del módelo: A medida que el tiempo pase, la efectividad del módelo irá en bajada como consecuencia de los datos de la vida real, ante estos casos, una solución factible es el re-entramiento del módelo a medida que pasa el tiempo, en este ejemplo, se podrian ajustar funciones tales que identifiquen cuando el indice de valores ingresados es congruente con algún módulo (el último indice es divisible por X) y en esos casos activar un reentrenamiento del módelo.

- Localidad: La demografía es un factor importante en la identificación de personas, dado que en base a las distintas zonas de un país, puede variar el atuendo o vestimenta de las personas, de ahí que sea sumamente importante considerar el amplio ábanico de casos posibles en el proceso de entrenamiento del módelo, sumado a esto, debemos considerar las estaciones del año y el clima que varia junto con ello.

- Seguridad y privacidad: Debemos considerar todos los cuidados a nivel de ingenería de software que debe tener nuestro programa en un contexto de producción, evitando usar procesos de encriptado deprecados o llaves rotativas. Sumado a esto, debemos considerar una interfaz de ususario final que se limite a la entrega de indicadores de gestión más que al acceso de información sensible, como lo puede ser el registro de imagenes de rostros. Para ello debemos entregar capacitación a cada uno de los usuarios de este contador de personas, usar doble autenticación y llevar un registro (por medio del Logging) de todas aquellas consultas que sean realizadas.