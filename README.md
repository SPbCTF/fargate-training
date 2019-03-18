# Тренировка SPbCTF 17 марта 2019 от команды fargate

## Сервисы

| Сервис         | Язык                  | Дополнительно                |
| -------------- | --------------------- | ---------------------------- |
| kv8            | C                     | нет исходников на тренировке |
| imsorry        | ruby                  |                              |
| haveibeenpwned | python                | mongodb                      |
| pokupaika      | typescript/javascript | redis                        |
| chukcha        | C                     |                              |
| cryptostorm    | python                |                              |

## Как юзать

- Запуск сервиса (первый раз) — `docker-compose up -d`
- Перезапуск сервиса после патча для скриптовых сервисов (imsorry, haveibeenpwned, cryptostorm) — `docker-compose restart`
- Перезапуск сервиса после патча для остальных сервисов - `docker-compose up --build -d`
- Если вам снесли всё в контейнере или как-то по-другому покорраптили — `docker-compose up --force -d` (пересоздаёт контейнер)

**Не рекомендуется использовать комманду `docker`, делайте всё через `docker-compose`**


## Деплой

- `./combine.sh` комбинирует все сервисы в папку `deploy` для копирования в `/home` вулнбокса
- `./deploy_to_vulnbox.sh` копирует все сервисы из папки `deploy` на вулнбокс и запускает их
- `./run_all.sh` просто запускает все сервисы из `/home`