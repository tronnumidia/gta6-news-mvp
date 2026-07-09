# WK Games News - GTA 6 & Mundo Geek

Site automatizado com notícias sobre **GTA 6** e o mundo gamer.

## Como funciona

1. **GitHub Actions** roda 2x ao dia (06h e 18h)
2. O script Python (`scripts/scraper.py`) busca:
   - RSS feeds de sites de games (IGN, Gamespot, etc.)
   - Vídeos do YouTube sobre GTA 6 (via API)
3. Gera `data/news.json` com todas as notícias
4. Commita automaticamente → GitHub Pages atualiza

## Para ativar no seu GitHub

1. Crie um repositório no GitHub com este conteúdo
2. Vá em **Settings → Pages** → selecione `main` / `root`
3. (Opcional) Adicione um **secret** `YT_API_KEY` com sua chave da YouTube Data API v3
4. Pronto! O site já começa a se atualizar automaticamente

## Tecnologias

- GitHub Pages (hospedagem gratuita)
- Python + Requests (scraping)
- GitHub Actions (automação diária)
- YouTube Data API (vídeos)

---

Feito com ❤️ para a comunidade gamer.