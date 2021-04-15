FROM python:3.7.1
RUN groupadd web_server_group && \
    useradd -m -g web_server_group -s /bin/bash web_server && \
    apt-get update -y && \
    apt-get install python3-dev -y && \
    mkdir -p /home/web_server
ENV PYTHONPATH "${PYTHONPATH}:/home/web_server"
COPY . /home/web_server/
RUN chown -R web_server:web_server_group /home/web_server && \
    pip install -r /home/web_server/requirements.txt
WORKDIR /home/web_server
USER web_server
EXPOSE 8080
CMD python app.py
