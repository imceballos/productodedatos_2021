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
