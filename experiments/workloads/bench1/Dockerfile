FROM python:3.6-slim

# Create the user that will run the app
RUN adduser --disabled-password --gecos '' api-user

ENV FLASK_APP=app.py

# Install requirements
ADD src/requirements.txt /opt/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /opt/requirements.txt

# to enable ps command
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --no-install-recommends -y procps \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

ADD src /opt/src/

WORKDIR /opt/src
RUN chmod +x /opt/src/*.sh
RUN chown -R api-user:api-user ./

USER api-user

EXPOSE 5000

ENTRYPOINT [ "/opt/src/entrypoint.sh" ]

CMD ["python", "index.py"]

