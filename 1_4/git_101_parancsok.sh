### INSTALLÁCIÓ
# DigitalOcean-ös Ubuntu 24.04-re már alapból fel van téve, nem kell installálni
# Ha máshol vagy, akkor ezekkel a parancsokkal tudod megtenni:

sudo apt update
sudo apt install git

# Ha nem tudod, hogy van-e telepítve git VAGY telepítetted, de tudni akarod, hogy sikerült-e, futtasd ezt a parancsot:
git --version
# Ha kiírja a git-ed verziószámát, akkor jó vagy. (Ha nem, lásd az első két lépést.)

### GIT START ###
# SZERVER BEÁLLÍTÁSOK (egyszer kell megcsinálni)
git config --global user.name "TE NEVED"
git config --global user.email "te@emailcimed.com" #ha van github-od, akkor lehetőség szerint a github-os email címedet add meg
git config --global init.defaultBranch main

### ELSŐ LÉPÉS
# adott mappából git repot csinál (értsd: "elindítjuk" a git verziókövetést)
git init

# változás nélkül kiírja, hogy milyen fájlok vannak követve, frissítve, stb.
git status

# fájl verziókövetésének indítása
git add <file>

# változás "mentése" -- "commit"-olása
git commit -m "valami értelmes komment"

### VISSZAÁLLÍTÁS
# minden korábbi állapot listázása
git log --oneline 
#példa kimenet:
#a1b2c3d fix telegram delivery
#e4f5g6h add csv parser
#9z8y7x6 initial commit

# visszaállítás az adott állapotra:
git revert [állapotkód]

#pl. git revert e4f5g6h

### VESZÉLYZÓNA
# TELJES GIT KÖVETÉS MEGSZÜNTETÉSE AZ ADOTT MAPPÁBAN
# SZINTE SOHA SEM CSINÁLJUK!!!
rm -rf .git
