# 📚 Fantasy-Worlds, Fantlab Metadata Providers for Calibre-Web

**FantasyWorlds**, **Fantlab** — пользовательский метадата-провайдер для Calibre-Web , получающий информацию о книгах с сайта https://fantasy-worlds.org, https://fantlab.ru/



## ⚙️ Установка вручную в Docker 
1.Находим конетейнер
```bash
docker ps
```

2.Входим в контейнер
```bash
docker exec -it ИМЯ_КОНТЕЙНЕРА /bin/sh
```

3.Заходим в папку провайдеров
```bash
cd /app/calibre-web/cps/metadata_provider
```

Fantasy-Worlds
```bash
curl -O https://raw.githubusercontent.com/D4VM/calibre-web-fantasywords-fantlab-metadata-provider/refs/heads/main/fantasyworlds.py
```

Fantlab
```bash
curl -O https://raw.githubusercontent.com/D4VM/calibre-web-fantasywords-fantlab-metadata-provider/refs/heads/main/fantlab.py
```

4.Рестартим Calibre-web либо через админку calibre-web или через сам докер
