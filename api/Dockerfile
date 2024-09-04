FROM python:3.12.4-alpine

WORKDIR /app/


COPY ./requirements.txt /app/requirements.txt


RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python -m pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
 apk --purge del .build-deps

COPY ./app /app/

CMD ["fastapi", "run", "main.py", "--port", "8000"]