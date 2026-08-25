# Social DNSBL sem WhatsApp e Google Ads

Este script baixa a lista social do projeto StevenBlack, remove as exceções abaixo, elimina duplicatas, ordena os domínios e gera `social-waps.txt` no formato hosts aceito pelo pfBlockerNG.

Exceções removidas da lista de bloqueio:

- `whatsapp.com` e todos os subdomínios
- `whatsapp.net` e todos os subdomínios
- `wa.me` e todos os subdomínios
- `googleadservices.com` e todos os subdomínios
- `ads.google.com`
- `adservice.google.com`

## Gerar a lista

Requer Python 3.9 ou mais recente e não usa pacotes externos.

```bash
python gerar_social_waps.py
```

O arquivo `social-waps.txt` será criado na mesma pasta do script. Para escolher outro destino:

```bash
python gerar_social_waps.py --output caminho/social-waps.txt
```

## Publicar no GitHub

1. Crie um repositório ou copie `gerar_social_waps.py`, este `README.md` e o `social-waps.txt` gerado para um repositório existente.
2. Execute o script sempre que quiser atualizar a lista e envie o novo `social-waps.txt` ao GitHub.
3. Troque `SEU_USUARIO` e `SEU_REPOSITORIO` na URL abaixo. Se usar outra branch, troque também `main`.

```text
https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/social-waps.txt
```

## Usar no pfSense/pfBlockerNG

Em **Firewall > pfBlockerNG > DNSBL > DNSBL Groups**, adicione a URL RAW acima como uma fonte. Use o formato **Auto** ou **Hosts**, salve e execute **Update/Reload**.

Depois, confirme em **Reports > Alerts > DNSBL** que os domínios necessários não estão sendo bloqueados. O filtro trata somente nomes de domínio; eventuais bloqueios por IP, ASN, firewall ou outra lista precisam ser revisados separadamente.

## Observação

Liberar esses domínios evita que esta lista específica os bloqueie. Isso não garante que todos os recursos do WhatsApp ou do Google Ads funcionarão se outras listas DNSBL também bloquearem dependências relacionadas.
