FROM python:3.7

COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY . /

WORKDIR /flaskapp

# expose the app port
EXPOSE 6543

RUN pip install gunicorn

# run the app server in production with gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:6543", "--workers", "1", "app:app"]

# alternatively use flask server for production or dev_mode
ENTRYPOINT [ "python" ]

CMD [ "app.py"  ]
