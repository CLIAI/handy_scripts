FROM archlinux:base-devel

# Install git and go
RUN pacman -Syu --noconfirm git go

# Create a non-root user
RUN useradd -m -G wheel builder && \
    echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switch to the non-root user
USER builder
WORKDIR /home/builder

# Copy the PKGBUILD file and build the package
COPY PKGBUILD .
RUN makepkg -s --noconfirm
RUN ls -lha *.pkg.*

# Echo success
CMD ["echo", "SUCCESS"]
