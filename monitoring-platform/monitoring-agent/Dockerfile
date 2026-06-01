FROM rockylinux:9

RUN dnf install -y \
    procps-ng \
    net-tools \
    chrony \
    hostname \
    && dnf clean all

WORKDIR /app

COPY check_status.sh .

RUN chmod +x check_status.sh

CMD ["./check_status.sh"]
