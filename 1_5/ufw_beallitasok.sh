# DEPLOY USER CSINÁLJA!
# Be van kapcsolva?
sudo ufw status verbose

# Alap szabályok: minden bejövő forgalom tiltva, minden kimenő forgalom engedélyezve
sudo ufw default deny incoming
sudo ufw default allow outgoing

# FONTOS! SSH-t engedélyezd — ezt MINDENKÉPP az (5) enable/bekapcsolás ELŐTT csináld, különben kizárod magad a szerverről
sudo ufw limit OpenSSH
# a "limit" ("allow" helyett) korlátozza az ismétlődő kapcsolódási próbálkozásokat
# ugyanarról az IP-ről, így alapszintű brute-force védelmet ad a 22-es porton (max 6 kapcsolódás 30 mp-n belül)

# 4. HTTP requeste-ek engedélyezése web portok megnyitásával
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 5. Bekapcsolás
sudo ufw enable

# 6. Ellenőrzés
sudo ufw status verbose
