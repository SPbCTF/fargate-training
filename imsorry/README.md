# Сервис imsorry

Собрать:
```
docker build -t imsorry_image .
```

Поднять:
```
docker run -p 4567:4567 -it --name imsorry_service imsorry_image rackup -o 0.0.0.0 -p 4567
```