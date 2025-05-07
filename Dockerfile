# pull the official docker image
FROM python:3.11-alpine 

# set work directory
WORKDIR /app

# install dependencies
COPY /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#copying from src to dst
COPY . .

CMD ["uvicorn" "app.app:app" "--host 0.0.0.0" ]