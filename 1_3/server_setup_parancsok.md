##########################
### x parancs összesen -- ne gépelj el semmit!!
### TELJES MAGYARÁZAT ITT: https://mestertomi.hu/
##########################

######
#LOCAL
#szerverre bejelentkezés
ssh root@[szerverIPcím]

######
#SERVER AS ROOT
#új user hozzáadása
adduser deploy
#sudo jogok megadása
usermod -aG sudo deploy

#kijelentkezés
exit

######
#LOCAL
ssh deploy@[szerverIPcím]

######
#SERVER AS DEPLOY
#megfelelő csomagok és kiegészítők telepítése
sudo apt-get update
sudo apt-get install mc
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-dev
sudo apt install python3-pip

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
