FROM ubuntu:18.04
RUN apt-get update && apt-get install tesseract-ocr-tha -y python 3 #python-setuptools python3-pip && apt-get clean &&  apt-get autoremove

ADD . /var/www/OCR

WORKDIR /var/www/OCR

COPY requirements.txt ./
COPY . .
RUN pip3  install --no-cache-dir -r requirements.txt

VOLUME ["/data"]

EXPOSE 80 80

CMD [ "python3", "main.py"]
RUN apt-get install tesseract-ocr

ENV TESSDATA_PREFIX="/usr/local/share/tessdata"
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/OCR/app/static
