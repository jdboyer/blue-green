FROM fedora:latest
RUN dnf install -y gcc make nginx valkey unzip && dnf clean all
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh
EXPOSE 80
CMD ["/bin/sh", "-c", "bash"]