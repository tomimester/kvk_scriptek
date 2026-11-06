# NAGY BETŰS RÉSZEKET CSERÉLD!
# 1. Új SSH kulcs generálása ehhez a szerverhez
ssh-keygen -t ed25519 -f ~/.ssh/KULCS_NEVE -N "" -C "KULCS_MEGJEGYZES"

# 2. A publikus kulcs kiírása – ezt kell hozzáadni a GitHubon (repo → Settings → Deploy keys)
cat ~/.ssh/KULCS_NEVE.pub

# 3. A GitHub-kapcsolat tesztelése
ssh -T -i ~/.ssh/KULCS_NEVE -o IdentitiesOnly=yes git@github.com

# 4. Beállítjuk, hogy ez a repo mindig ezt a kulcsot használja
git -C /eleresi/ut/a/projekthez config core.sshCommand "ssh -i ~/.ssh/KULCS_NEVE -o IdentitiesOnly=yes"

# 5. A helyi repo összekötése a GitHub repóval
git -C /eleresi/ut/a/projekthez remote add origin git@github.com:GITHUB_FELHASZNALONEV/REPO_NEVE.git

# 6. A kód feltöltése
git -C /eleresi/ut/a/projekthez push -u origin main
