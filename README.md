# grpc_test_task

Соберите контейнер:
```commandline
docker build -t grpc_full_app .
```
Запустите контейнер:
```commandline
docker run -p 50051:50051 -p 5432:5432 grpc_full_app
```
Можете зайти в контейнер для проверки правильности директорий:
```commandline
sudo docker run -it grpc_full_app /bin/bash
```

Удалите все образы, не связанные с контейнерами:
```commandline
sudo docker system prune -a
```