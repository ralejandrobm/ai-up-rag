FROM odoo:18.0

USER root

WORKDIR /app

RUN apt-get update && apt-get install -y \
    locales \
    python3-pip \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./setup/requirements.txt /app/base-requirements.txt
RUN pip install \
    --no-cache-dir \
    --ignore-installed \
    --break-system-packages \
    -r /app/base-requirements.txt

# install torch to use with cpu (without cuda)
RUN pip install\
    --break-system-packages\
    --no-cache-dir \
    --ignore-installed \
    torch --index-url https://download.pytorch.org/whl/cpu

EXPOSE 8069 8072

CMD ["odoo"]
