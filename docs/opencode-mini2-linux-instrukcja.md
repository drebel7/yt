# Instrukcja dla instancji OpenCode na mini2 (Linux): uporządkowanie providera LM Studio

Dokument do przekazania agentowi OpenCode działającemu na Linuksie **na hoście mini2**.
Zakres: wyłącznie sekcje `provider`, `model` i `small_model` w `~/.config/opencode/opencode.jsonc`.
Nie dotyczy MCP ani konfiguracji innych maszyn.

Ważna różnica środowiskowa: tam LM Studio stoi na tym samym hoście, więc `baseURL`
to `http://127.0.0.1:1234/v1` — **nie** `http://mini2:1234/v1` i nie adres LAN.
W dokumentacji poniżej wszędzie używane jest `127.0.0.1`.

---

## Cel

1. Jedna, spójna definicja providera LM Studio (bez duplikatów i martwych bloków).
2. Lista modeli zgodna 1:1 z tym, co serwer faktycznie wystawia (`/v1/models`).
3. Poprawne `capabilities` dla każdego modelu — ustalone na podstawie dokumentacji
   twórców, metadanych LM Studio i testów empirycznych, nie zgadywane.
4. Ustawione globalne `model` oraz `small_model`.

## Zasady twarde

1. **Kopia zapasowa przed edycją**:
   `cp ~/.config/opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc.bak-$(date +%Y%m%d%H%M)`
   — ścieżkę backupu podaj w raporcie.
2. **Nie wymyślaj pól, których nie ma w schemacie** `https://opencode.ai/config.json`
   (`$defs.ProviderConfig`, `$defs.Config.Model.Capabilities`, `$defs.Config.Model.Reasoning`).
   Konkretnie:
   - **nie istnieje** „domyślny model providera” — są tylko globalne `model` i `small_model`,
   - `capabilities` to **obiekt** `{ tools, input, output, temperature, reasoning }`,
     **nie** tablica stringów w stylu `["text_generation","tool_use"]`,
   - `reasoning` to obiekt: `{ "supported": false }` albo
     `{ "supported": true, "toggle": bool, "effort": [...], "budget": {min,max} }`.
3. **Usuwaj tylko duplikaty i martwe wpisy.** Modele embeddingów pomiń w configu
   (nie służą do czatu), ale nie usuwaj ich z serwera.
4. **Brak deklaracji jest lepszy niż fałszywe `true`.** Czego nie potrafisz
   zweryfikować, tego nie deklaruj i wyjaśnij to w raporcie.
5. Zachowaj styl pliku: wcięcia i komentarze `//` (to JSONC — komentarze są dozwolone).

---

## Krok 1 — inwentaryzacja konfiguracji

Wypisz: klucze `provider`, dla każdego `options.baseURL` i listę modeli.

**Sprawdź, czy klucz `provider` nie występuje dwukrotnie.** W JSON duplikat klucza
cicho wygrywa ostatnim wystąpieniem — pierwszy blok staje się martwy i nie widać tego
w UI. Jeśli duplikat jest, scal oba bloki w jeden (wszystkie providery jako rodzeństwo).

## Krok 2 — co serwer naprawdę wystawia

```bash
curl -s http://127.0.0.1:1234/v1/models | jq -r '.data[].id' | sort
curl -s http://127.0.0.1:1234/api/v0/models \
  | jq -r '.data[] | [.id, .type, .state, ((.capabilities // []) | join(","))] | @tsv' | sort
```

Interpretacja drugiego endpointu (LM Studio native API):

- `type`: `llm` = tekst, `vlm` = tekst + obraz, `embeddings` = pomiń w configu;
- `capabilities`: obecność `tool_use` = szablon czatu obsługuje narzędzia;
- `state`: `not-loaded` oznacza JIT-load przy pierwszym żądaniu (35B: ~35 s, to nie błąd).

Gdy serwer nie odpowiada: `ss -ltnp | grep 1234` i sprawdź, czy LM Studio ma włączony
serwer Local API.

## Krok 3 — jeden provider

```jsonc
"provider": {
  "mini2-LMStudio": {
    "name": "mini2-LMStudio",
    "npm": "@ai-sdk/openai-compatible",
    "options": {
      "baseURL": "http://127.0.0.1:1234/v1",
      "timeout": 3600000,        // 60 min
      "chunkTimeout": 3000000,   // 50 min
      "setCacheKey": true
    },
    "models": { }
  }
}
```

Jeśli istniało kilka providerów wskazujących na ten sam serwer: scal `options`
(zachowaj timeouty), a modele trzymaj tylko raz.

## Krok 4 — synchronizacja listy modeli

- Klucz w `models` to **ID wysyłane do API** — musi być identyczne z `id` z `/v1/models`
  (wielkość liter i myślniki też). Przykład realnej pomyłki:
  `nvidia/nemotron-3-annotated-omni` zamiast `nvidia/nemotron-3-nano-omni`
  → „model not found”.
- `"name"` to tylko etykieta w UI; trzymaj `"name": "<to samo co ID>"` dla spójności.
- Stan docelowy: każdy model z `/v1/models` poza embeddingami jest w configu i odwrotnie
  (0 różnic w obie strony).

## Krok 5 — `capabilities` z weryfikacją

| Pole | Jak ustalić |
|---|---|
| `input` | `type` z `/api/v0/models`: `llm` → `["text"]`, `vlm` → `["text","image"]`. `audio`/`video` dodawaj tylko, gdy twórca deklaruje to explicite **i** ścieżka OpenAI-compatible to realnie przenosi |
| `tools` | tylko po potwierdzeniu: karta modelu twórcy **albo** test empiryczny **albo** `tool_use` w `/api/v0/models`. Rozbieżność → rozstrzyga test empiryczny |
| `reasoning` | karta twórcy; `supported: true` gdy odpowiedź zwraca `reasoning_content` lub thinking jest domyślny/odwracalny (`enable_thinking`) |
| `effort` | tylko gdy twórca dokumentuje poziomy (np. `["low","medium","high"]`) |

### Test empiryczny tool-callingu

```bash
cat > /tmp/tool-probe.js <<'EOF'
const model = process.argv[2];
const ac = new AbortController();
setTimeout(() => ac.abort(), 240000);
const r = await fetch("http://127.0.0.1:1234/v1/chat/completions", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  signal: ac.signal,
  body: JSON.stringify({
    model,
    max_tokens: 700,
    temperature: 0,
    messages: [{ role: "user", content: "What is the weather in Paris right now? Use the provided tool." }],
    tools: [{
      type: "function",
      function: {
        name: "get_weather",
        description: "Get current weather for a city",
        parameters: { type: "object", properties: { city: { type: "string" } }, required: ["city"] },
      },
    }],
  }),
});
const j = await r.json();
const m = j.choices?.[0]?.message ?? {};
console.log(model,
  "| tool_calls:", JSON.stringify(m.tool_calls ?? null),
  "| reasoning:", m.reasoning_content ? "yes" : "no",
  "| err:", j.error ? JSON.stringify(j.error) : "-");
EOF
node /tmp/tool-probe.js "<model-id>"
```

Reguły decyzji:

- `tool_calls` z `{"city":"Paris"}` → `tools: true`;
- brak `tool_calls` i odpowiedź tekstowa → `tools: false` **tylko** gdy twórca też mówi
  „not supported”; inaczej pomiń klucz;
- `400 Failed to load model` → model jest niedziałający (patrz Pułapki). Nie deklaruj
  capabilities, zgłoś sprawę użytkownikowi.

Dla fine-tunów społecznościowych (abliterated, uncensored, dystylacje CoT) karta autora
bywa jedynym źródłem — jeśli autor nic nie deklaruje, rozstrzygaj testem.

## Krok 6 — `model` i `small_model`

Tylko globalnie, na końcu pliku:

```jsonc
"model": "mini2-LMStudio/<model-do-czatu>",
"small_model": "mini2-LMStudio/<lekki-model-do-tytułów>"
```

Przy wyborze `small_model` zmierz czasy realnie (tytuły sesji generują się często):
kilka sekund, dobra polszczyzna i angielski. Model rozumujący z długim CoT nie jest
dobrym wyborem, jeśli jest szybsza alternatywa.

## Krok 7 — walidacja przed raportem

1. Parser JSONC **świadomy stringów** — naiwne `sed 's,//.*,,'` psuje URL-e `http://…`
   i daje fałszywy alarm. Użyj skryptu niżej.
2. Brak duplikatów kluczy na każdym poziomie zagnieżdżenia.
3. Tylko dozwolone klucze w `capabilities` i poprawne `reasoning`.
4. 0 rozjazdów ID względem `/v1/models`.
5. `model` i `small_model` wskazują na istniejący provider i istniejący klucz modelu.

```bash
cat > /tmp/validate-config.js <<'EOF'
const fs = require("fs");
const file = process.argv[2];

function strip(src) {
  let out = "", inStr = false, esc = false, inLine = false, inBlock = false;
  for (let i = 0; i < src.length; i++) {
    const c = src[i], n = src[i + 1];
    if (inLine) { if (c === "\n") { inLine = false; out += c; } continue; }
    if (inBlock) { if (c === "*" && n === "/") { inBlock = false; i++; } continue; }
    if (inStr) {
      out += c;
      if (esc) esc = false; else if (c === "\\") esc = true; else if (c === '"') inStr = false;
      continue;
    }
    if (c === '"') { inStr = true; out += c; continue; }
    if (c === "/" && n === "/") { inLine = true; i++; continue; }
    if (c === "/" && n === "*") { inBlock = true; i++; continue; }
    out += c;
  }
  return out;
}

const CAP_KEYS = ["tools", "input", "output", "temperature", "reasoning"];
const REASON_KEYS = ["supported", "toggle", "effort", "budget"];
const out = strip(fs.readFileSync(file, "utf8"));

// duplikaty kluczy
const stack = [], seen = [new Set()], dups = [];
const re = /"((?:[^"\\]|\\.)*)"\s*:|[{}\[\]]/g;
let m;
while ((m = re.exec(out))) {
  const t = m[0];
  if (t === "{") { stack.push("o"); seen.push(new Set()); }
  else if (t === "[") { stack.push("a"); seen.push(new Set()); }
  else if (t === "}" || t === "]") { stack.pop(); seen.pop(); }
  else { const k = m[1], top = seen[seen.length - 1]; if (top.has(k)) dups.push(k); top.add(k); }
}
if (dups.length) { console.log("DUPLIKATY KEYS: " + dups.join(", ")); process.exit(1); }

const cfg = JSON.parse(out);
const errors = [];
for (const [pid, p] of Object.entries(cfg.provider || {})) {
  for (const [mid, mv] of Object.entries(p.models || {})) {
    const caps = mv.capabilities;
    if (!caps) { errors.push(`${mid}: brak capabilities`); continue; }
    for (const k of Object.keys(caps)) if (!CAP_KEYS.includes(k)) errors.push(`${mid}: zły klucz capabilities.${k}`);
    if (caps.reasoning) {
      for (const k of Object.keys(caps.reasoning)) if (!REASON_KEYS.includes(k)) errors.push(`${mid}: zły klucz reasoning.${k}`);
      if (typeof caps.reasoning.supported !== "boolean") errors.push(`${mid}: reasoning.supported nie jest boolean`);
      if (caps.reasoning.supported === false && Object.keys(caps.reasoning).length > 1)
        errors.push(`${mid}: supported=false z dodatkowymi kluczami`);
    }
  }
}

(async () => {
  const live = (await (await fetch("http://127.0.0.1:1234/v1/models")).json()).data.map((d) => d.id).sort();
  for (const [pid, p] of Object.entries(cfg.provider || {})) {
    const ids = Object.keys(p.models || {});
    const missingOnServer = ids.filter((i) => !live.includes(i));
    const missingInConfig = live.filter((i) => !ids.includes(i) && !i.startsWith("text-embedding"));
    console.log(`[${pid}] baseURL=${p.options?.baseURL} modeli=${ids.length}`);
    console.log("  brak na serwerze: " + (missingOnServer.join(", ") || "brak"));
    console.log("  brak w configu:   " + (missingInConfig.join(", ") || "brak"));
  }
  for (const key of ["model", "small_model"]) {
    if (!cfg[key]) { console.log(`${key}: nie ustawiony`); continue; }
    const [prov, ...rest] = cfg[key].split("/");
    const mid = rest.join("/");
    console.log(`${key}: ${cfg[key]} -> provider=${!!cfg.provider?.[prov]} model=${!!cfg.provider?.[prov]?.models?.[mid]}`);
  }
  console.log(errors.length ? "BLEDY:\n" + errors.join("\n") : "capabilities: struktura OK");
})();
EOF
node /tmp/validate-config.js ~/.config/opencode/opencode.jsonc
```

## Krok 8 — raport

Podaj: listę zmian, dla każdego modelu `tools: true/false` **oraz podstawę decyzji**
(karta twórcy / test empiryczny / metadane LM Studio), co zostało bez deklaracji i dlaczego,
wyniki walidacji, ścieżkę backupu. Na końcu: zmiany działają **po restarcie OpenCode**.

---

## Pułapki (wszystkie wystąpiły realnie)

1. **Duplikat klucza `provider`** — drugi blok wygrywa, pierwszy provider jest martwy.
2. **Nieaktualne ID modeli** po przemianowaniu w LM Studio
   (`…-v2` → `…-v2-abliterated` / `…-v2-mtp`, `Ornith-1.5-35B-A3B-GGUF` → `ornith-1.5-35b-a3b`).
3. **`capabilities` jako tablica stringów** — niezgodne ze schematem, prawdopodobnie
   ignorowane; poprawnie `{ "tools": true }`.
4. **`tool_call` vs `capabilities.tools`** — dwa różne pola w schemacie; wybierz jedno,
   konsekwentnie `capabilities`.
5. **Model widoczny w `/v1/models` ≠ model działający.** Eksperymentalna architektura
   (np. `qwen4exp`) potrafi zwrócić `400 Failed to load model` nawet na „Say hi.”.
   Taki wpis zgłoś, nie „naprawiaj” mu capabilities.
6. **`type: llm` przy modelu multimodalnym u twórcy** — brak `mmproj` w tym quancie;
   deklaruj to, co realnie działa.
7. **Długie pierwsze żądanie** = JIT-load modelu, nie błąd.
8. Nie kopiuj ścieżek Windows ani bloków MCP z innej maszyny — zakres to tylko
   `provider`, `model`, `small_model`.

---

## Dodatek A — stan referencyjny z maszyny źródłowej

U źródła: 19 modeli czatu w configu, 20 na serwerze (`text-embedding-nomic-embed-text-v1.5`
pominięty celowo). Wszystkie `tools: true` poza dwoma: `deepseek-coder-v2-lite-instruct`
i `survival-uncensored-gemma-270m-v2-i1` (`false` — zgodnie z twórcami i metadanymi).
`qwen4` bez deklaracji `tools` (nie da się załadować). `input` wg `llm`/`vlm`.

| Model | tools | input | reasoning |
|---|---|---|---|
| `deepseek-coder-v2-lite-instruct` | false | text | false |
| `gemma-4-e4b-uncensored-hauhaucs-aggressive` | true | text, image | true + toggle |
| `google/gemma-4-26b-a4b` | true | text, image | true + toggle |
| `google/gemma-4-31b` | true | text, image | true + toggle |
| `google/gemma-4-e2b` | true | text, image | true + toggle |
| `nvidia/nemotron-3-nano-omni` | true | text, image, audio, video | true + toggle |
| `openai/gpt-oss-20b` | true | text | true + effort (low/medium/high) |
| `ornith-1.5-35b-a3b` | true | text, image | true + toggle |
| `qwen/qwen3.5-9b` | true | text, image, video | true + toggle |
| `qwen/qwen3.6-35b-a3b` | true | text, image, video | true + toggle |
| `qwen/qwen3.8-27b` | true | text, image | true + toggle |
| `qwen3.5-9b-claude-4.6-opus-reasoning-distilled` | true | text | true |
| `qwen3.6-27b-mtp` | true | text, image | true + toggle |
| `qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive` | true | text, image | true + toggle |
| `qwen4` | — (nie da się załadować) | text, image | — |
| `qwopus3.6-27b-v2-abliterated` | true | text, image | true |
| `qwopus3.6-27b-v2-mtp` | true | text, image | true |
| `supergemma4-26b-uncensored-v2` | true | text | true + toggle |
| `survival-uncensored-gemma-270m-v2-i1` | false | text | false |

**To punkt odniesienia, nie do bezmyślnego kopiowania** — u siebie zweryfikuj ponownie,
serwer może mieć inne lub nowsze modele.

## Dodatek B — źródła weryfikacji

- Gemma 4: <https://ai.google.dev/gemma/docs/core/model_card_4> (multimodal, natywne
  function calling, thinking; audio tylko E2B/E4B/12B)
- Qwen3.5: <https://huggingface.co/Qwen/Qwen3.5-9B> (multimodal, tool use, thinking)
- Qwen3.6: <https://huggingface.co/Qwen/Qwen3.6-27B>
- gpt-oss-20b: <https://developers.openai.com/api/docs/models/gpt-oss-20b>
  (text-only, function calling, reasoning effort)
- Nemotron 3 Nano Omni: <https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning/modelcard>
- Ornith 1.5: <https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B>
- Qwopus 3.6: <https://huggingface.co/Jackrong/Qwopus3.6-27B-v2>
- DeepSeek-Coder-V2-Lite: <https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct>
  (function calling: not supported)
- Schemat konfiguracji: <https://opencode.ai/config.json>
