FROM python:3.10.9 as base

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt update && apt -qy install python3-dev gcc musl-dev

FROM base as dev

RUN useradd -rms /bin/bash commery_admin && chmod 777 /opt /run

WORKDIR /commery_project

RUN mkdir /commery_project/static && mkdir /commery_project/media && chown -R commery_admin:commery_admin /commery_project && chmod 755 /commery_project

COPY --chown=commery_admin:commery_admin . .

RUN pip install -r requirements.txt

USER commery_admin

CMD ["python3 manage.py runserver 0.0.0.0:8000"]

FROM base as prod

RUN useradd -rms /bin/bash commery_admin && chmod 777 /opt /run

WORKDIR /commery_project

RUN mkdir /commery_project/staticfiles && mkdir /commery_project/media && chown -R commery_admin:commery_admin /commery_project && chmod 755 /commery_project

COPY --chown=commery_admin:commery_admin . .

RUN pip install -r requirements.txt

USER commery_admin

CMD ["gunicorn", "-b", "0.0.0.0:8000", "config.wsgi:application"]