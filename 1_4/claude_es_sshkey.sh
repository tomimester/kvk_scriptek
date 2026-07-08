#Claude Code Setup
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
claude --version
claude

########
########
#OPCIONÁLIS: erősebb security itt:
# https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server
# PARANCSOK, DE NE KÖVESD VAKON!!!
######
#LOCAL
ssh-keygen #kulcsgenerálás, CSAK HA NINCS!!
ssh-copy-id deploy@[IPcím]
ssh deploy@[szerverIPcím]

############
#SERVER AS DEPLOY
sudo mcedit /etc/ssh/sshd_config

### a fájlba ezeket állítsd be
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
### SAVE & EXIT

sudo systemctl restart ssh
