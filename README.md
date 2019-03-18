# Тренировка SPbCTF 17 марта 2019 от команды fargate

## Сервисы

| Сервис         | Язык                  | Дополнительно |
| -------------- | --------------------- | ------------- |
| kv8            | C                     |               |
| imsorry        | ruby                  |               |
| haveibeenpwned | python                | mongodb       |
| pokupaika      | typescript/javascript | redis         |
| chukcha        | C                     |               |
| cryptostorm    | python                |               |

## Деплой

* `./combine.sh` комбинирует все сервисы в папку `deploy` для копирования в `/home` вулнбокса
* `./deploy_to_vulnbox.sh` копирует все сервисы из папки `deploy` на вулнбокс и запускает их
* `./run_all.sh` просто запускает все сервисы из `/home`