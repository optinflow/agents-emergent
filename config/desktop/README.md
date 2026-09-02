# Desktop Config Templates

Non-secret desktop preferences and templates. Safe to commit - nothing here
is a secret.

Add files like `.bashrc.template`, `xfce4-panel.xml`, or default launcher
shortcuts here, then wire them into `infrastructure/Dockerfile.desktop`
(e.g. `COPY config/desktop/skel/. /root/skel/`) if you want them provisioned
automatically on first boot.
