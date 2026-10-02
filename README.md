# Продажи · Streamlit Community Cloud

Самостоятельное приложение: читает data/sales.parquet, без Trino и Docker. Данные — снимок 20 000 синтетических заказов из Iceberg. Фильтры, графики и агрегаты вычисляются в pandas. Выбранные заказы можно скачать в CSV.

## Публикация

1. Создайте GitHub-репозиторий и загрузите содержимое этой папки в его корень: app.py, requirements.txt, data/sales.parquet, .gitignore и README.md. Файл Parquet обязательно должен попасть в репозиторий.
2. Войдите на https://share.streamlit.io через GitHub и нажмите Create app.
3. Выберите репозиторий, ветку и основной файл app.py.
4. В Advanced settings выберите Python 3.12. Secrets не нужны.
5. Нажмите Deploy. После запуска проверьте настройки доступа приложения: оно должно быть публичным.

Если загружаете весь исходный проект с сохранением структуры, основной файл: community_cloud/app.py. requirements.txt лежит рядом с ним.

Документация: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Обновление данных

Из родительской папки с compose.yaml:

```bash
docker compose exec -T streamlit python -c 'import pandas as pd; from db import query; rows, columns = query("SELECT * FROM iceberg.demo.sales ORDER BY order_id"); pd.DataFrame(rows, columns=columns).to_parquet("/tmp/sales-cloud.parquet", index=False, compression="snappy")'
docker cp iceberg-demo-streamlit-1:/tmp/sales-cloud.parquet community_cloud/data/sales.parquet
```

Загрузите обновлённый Parquet в GitHub. Приложение перезапустится с новым снимком. Данные автоматически из Iceberg не обновляются.

Проверено: 20 000 уникальных заказов, сумма выручки совпадает с Iceberg, приложение и фильтры по городу и каналу работают. Размер Parquet — около 194 КиБ.
