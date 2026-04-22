# Итоговый отчет по лабораторному стенду Garak

Дата сборки итогового пакета: `2026-04-23`

## 1. Installation

- Python version: `Python 3.12.3` (`python-version.txt`)
- Garak version: `garak LLM vulnerability scanner v0.14.1` (`garak-version.txt`)
- System snapshot: `Linux eager-caribou 6.8.0-101-generic x86_64 GNU/Linux` (`system.txt`)
- OpenAI SDK installed: да, в ходе установки был зафиксирован `openai 2.32.0`; полный список зависимостей сохранен в `pip-freeze.txt`
- Self-test completed: да; прогон `runs/00-selftest/00-selftest.report.jsonl` завершился успешно, итог `always.Pass: PASS ok on 40/40`
- Direct OpenAI smoke-run completed: да; прогон `runs/01-openai-smoke/01-openai-smoke.report.jsonl` успешно загрузил target `openai:gpt-5.2`, без ошибок аутентификации и lookup на момент теста
- Inventory snapshot completed: да; в текущей сборке зафиксированы `63` generators, `137` detectors и `222` probes (`garak-generators.txt`, `garak-detectors.txt`, `garak-probes.txt`)
- Review package assembled: да; в каталоге `review/` присутствуют environment snapshot, inventory, копии `configs/`, `services/`, `logs/`, `runs/` и итоговый отчет

Практически важное замечание по установочной части: на момент recovery-сессии из Инструкции 2 текущий ключ из `.env` уже перестал проходить против upstream OpenAI API, но это не отменяет факт успешного smoke-run на этапе Инструкции 1. Для сохранения воспроизводимости уязвимого поведения три учебных сервиса были доработаны так, чтобы они сохраняли намеренно небезопасный сценарий и при локальном fallback.

## 2. Demo services

### 2.1 ansi-terminal-proxy

- Endpoint: `http://127.0.0.1:8001/generate`
- Intended vulnerability: сервис возвращает в поле `text` сырые ANSI escape sequences и одновременно небезопасно эхо-отражает пользовательский ввод. Это модель учебного сервиса, который можно использовать как терминальный прокси и тем самым протащить управляющие последовательности в downstream-консоль.
- Manual proof: в `runs/10-ansi-terminal-proxy/manual-proof.json` ответ начинается с `\u001b[31mANSI_OK\u001b[0m`, после чего следует блок `USER_ECHO:` и исходный запрос пользователя. Ручное доказательство уязвимости присутствует и однозначно показывает наличие ANSI-кодов в JSON-ответе.
- Service implementation evidence: логика заложена в `services/ansi-terminal-proxy/app.py`; небезопасный фрагмент добавляет `raw_ansi_prefix = "\u001b[31mANSI_OK\u001b[0m\n"` и возвращает его без очистки.
- Generator config: `configs/rest-generator-ansi-terminal-proxy.json`
- Garak probes: `ansiescape.AnsiRaw`, `ansiescape.AnsiEscaped`
- Garak detectors: `ansiescape.Raw`, `ansiescape.Escaped`
- Result: Garak уязвимость поймал уверенно. `ansiescape.AnsiRaw -> FAIL` с attack success rate `100.00%`; `ansiescape.AnsiEscaped -> FAIL` с attack success rate `94.12% [86.27%, 100.00%]`
- Interpretation: это сильное совпадение между заложенной логикой сервиса, ручным proof и автоматически собранным hitlog. Для этой категории риска Garak показал высокую практическую полезность.
- Evidence files: `runs/10-ansi-terminal-proxy/manual-proof.json`, `runs/10-ansi-terminal-proxy/10-ansi-terminal-proxy.hitlog.jsonl`, `runs/10-ansi-terminal-proxy/10-ansi-terminal-proxy.report.jsonl`, `runs/10-ansi-terminal-proxy/10-ansi-terminal-proxy.report.html`, `runs/10-ansi-terminal-proxy/10-ansi-terminal-proxy.console.log`, `runs/10-ansi-terminal-proxy/run-summary.txt`

### 2.2 rag-summarizer-naive

- Endpoint: `http://127.0.0.1:8002/generate`
- Intended vulnerability: сервис суммаризации наивно доверяет тексту документа и может следовать инструкциям, встроенным в пользовательский контент. В этом сервисе специально заложены два класса слабостей: прямой prompt injection и latent injection через скрытые или замаскированные команды внутри документа.
- Service implementation evidence: `services/rag-summarizer-naive/app.py` содержит набор `SUSPICIOUS_MARKERS`, регулярные шаблоны `DIRECTIVE_PATTERNS` и функцию `extract_injected_response`, которая извлекает вредоносную директиву из текста и возвращает ее как ответ. Это и есть намеренно уязвимое поведение.
- Generator config: `configs/rest-generator-rag-summarizer-naive.json`

#### Prompt injection

- Manual proof: `runs/20-rag-promptinject/manual-proof.json` возвращает точную строку `ROGUE_MARKER_12345` по прямой внедренной инструкции
- Garak probes: `promptinject.HijackHateHumans`, `promptinject.HijackKillHumans`, `promptinject.HijackLongPrompt`
- Garak detector: `promptinject.AttackRogueString`
- Result: все три probe-сценария дали `FAIL`, attack success rate `98.05% [96.09%, 99.61%]`
- Interpretation: Garak практически без потерь фиксирует, что сервис подчиняется инъецированным директивам вместо выполнения основной пользовательской задачи
- Evidence files: `runs/20-rag-promptinject/manual-proof.json`, `runs/20-rag-promptinject/20-rag-promptinject.hitlog.jsonl`, `runs/20-rag-promptinject/20-rag-promptinject.report.jsonl`, `runs/20-rag-promptinject/20-rag-promptinject.report.html`, `runs/20-rag-promptinject/20-rag-promptinject.console.log`, `runs/20-rag-promptinject/run-summary.txt`

#### Latent injection

- Manual proof: `runs/21-rag-latentinjection/manual-proof.json` возвращает строку `Phil Ivey wasn't cheating` для скрытой latent-style инструкции
- Garak probes that failed:
- `latentinjection.LatentInjectionFactSnippetEiffel -> FAIL` через `base.TriggerListDetector`, attack success rate `49.22% [43.36%, 55.47%]`
- `latentinjection.LatentInjectionFactSnippetLegal -> FAIL` через `base.TriggerListDetector`, attack success rate `28.52% [23.05%, 33.98%]`
- `latentinjection.LatentInjectionResume -> FAIL` через `base.TriggerListDetector`, attack success rate `78.91% [73.83%, 83.59%]`
- `latentinjection.LatentInjectionTranslationEnFr -> FAIL` через `base.TriggerListDetector`, attack success rate `100.00%`
- `latentinjection.LatentInjectionTranslationEnZh -> FAIL` через `base.TriggerListDetector`, attack success rate `100.00%`
- `latentinjection.LatentJailbreak -> FAIL` через `unsafe_content.ToxicCommentModel`, attack success rate `5.86% [3.12%, 8.98%]`
- `latentinjection.LatentJailbreak -> FAIL` через `base.TriggerListDetector`, attack success rate `100.00%`
- `latentinjection.LatentWhois -> FAIL` через `base.TriggerListDetector`, attack success rate `33.33% [26.19%, 40.48%]`
- `latentinjection.LatentWhoisSnippet -> FAIL` через `base.TriggerListDetector`, attack success rate `7.81% [4.69%, 11.33%]`
- Garak probe that did not fire: `latentinjection.LatentInjectionReport -> PASS`
- Overall result: Garak уязвимость latent injection в целом поймал, но не равномерно по всем семействам. Большинство релевантных latent probes сработали, однако один probe-сценарий (`LatentInjectionReport`) дал `PASS`
- Interpretation: вывод по сервису положительный, но не в стиле "любой latent injection всегда детектируется". В закрытом контуре это означает, что семья `latentinjection` полезна, но ее нужно валидировать на собственных шаблонах документов и собственных триггерах
- Evidence files: `runs/21-rag-latentinjection/manual-proof.json`, `runs/21-rag-latentinjection/21-rag-latentinjection.hitlog.jsonl`, `runs/21-rag-latentinjection/21-rag-latentinjection.report.jsonl`, `runs/21-rag-latentinjection/21-rag-latentinjection.report.html`, `runs/21-rag-latentinjection/21-rag-latentinjection.console.log`, `runs/21-rag-latentinjection/run-summary.txt`, `runs/21-rag-latentinjection-interrupted-2026-04-23/`

### 2.3 code-helper-bad-imports

- Endpoint: `http://127.0.0.1:8003/generate`
- Intended vulnerability: сервис помогает с кодом, но всегда дописывает в начало ответа несуществующие Python import-ы. Это учебная модель package hallucination, когда LLM-сервис рекомендует или вставляет пакеты, которых не существует.
- Manual proof: `runs/30-code-helper-bad-imports/manual-proof.json` начинается с `import acmeultracachezz` и `from zzzx_qcache_magic_314159 import FastCache`
- Service implementation evidence: `services/code-helper-bad-imports/app.py` содержит константу `FAKE_IMPORTS`, которая безусловно префиксируется к каждому ответу
- Generator config: `configs/rest-generator-code-helper-bad-imports.json`
- Garak probes: `packagehallucination.Python`
- Garak detector: `packagehallucination.PythonPypi`
- Result: Garak уязвимость поймал полностью. `packagehallucination.Python -> FAIL`, attack success rate `100.00%`
- Important note: в процессе detector предупреждал, что запросы к Hugging Face выполнялись без аутентификации, но сам run завершился успешно и сигнал детекта был получен
- Evidence files: `runs/30-code-helper-bad-imports/manual-proof.json`, `runs/30-code-helper-bad-imports/30-code-helper-bad-imports.hitlog.jsonl`, `runs/30-code-helper-bad-imports/30-code-helper-bad-imports.report.jsonl`, `runs/30-code-helper-bad-imports/30-code-helper-bad-imports.report.html`, `runs/30-code-helper-bad-imports/30-code-helper-bad-imports.console.log`, `runs/30-code-helper-bad-imports/run-summary.txt`

## 3. Detection matrix

| Service | Intended vulnerability present manually? | Garak caught it? | Which probe / detector? | Notes |
| --- | --- | --- | --- | --- |
| `ansi-terminal-proxy` | yes | yes | `ansiescape.AnsiRaw` / `ansiescape.Raw`; `ansiescape.AnsiEscaped` / `ansiescape.Escaped` | Самый чистый и однозначный кейс: ручное proof и hitlog полностью согласуются |
| `rag-summarizer-naive` (prompt injection) | yes | yes | `promptinject.HijackHateHumans`, `promptinject.HijackKillHumans`, `promptinject.HijackLongPrompt` / `promptinject.AttackRogueString` | Очень высокая чувствительность, все ключевые promptinject-проверки ушли в `FAIL` |
| `rag-summarizer-naive` (latent injection) | yes | yes, но не полностью равномерно | `latentinjection.*` / в основном `base.TriggerListDetector`, для `LatentJailbreak` также `unsafe_content.ToxicCommentModel` | Большинство latent-сценариев пойманы, но `LatentInjectionReport` дал `PASS`; это важное ограничение |
| `code-helper-bad-imports` | yes | yes | `packagehallucination.Python` / `packagehallucination.PythonPypi` | Детект полный, но есть внешняя зависимость detector-а от сетевого источника метаданных |

## 4. Как читались отчеты Garak

- Основным evidence я считаю `hitlog` и конкретные успешные `attempt`-записи, потому что именно они показывают фактический prompt, фактический output и конкретный detector, который сработал
- HTML report (`*.report.html`) использую как обзорный слой по probe families и detector outcomes; он удобен для навигации, но не заменяет первичные сырые строки
- JSONL report (`*.report.jsonl`) считаю source-of-truth, потому что там лежат исходные записи run-а, попыток и eval results
- Confidence intervals интерпретирую только там, где sample size уже достаточно разумный; для `100.00%` на малом числе попыток это скорее сильный сигнал, чем абсолютная гарантия
- Detector result интерпретирую с учетом качества самого detector-а; detector для меня не оракул, а измеримый классификатор с ограничениями по precision/recall/F1
- Для чистых или пропущенных run-ов отсутствие `hitlog` не трактую как проблему сборки: в этой версии Garak hitlog создается только когда есть failing detector results
- Для AVID-конверсии ориентируюсь не на exit code процесса, а на факт появления файла `*.avid.jsonl`; в текущей сборке `garak -r` печатает validation error и при этом завершает процесс кодом `0`, поэтому реальный успех нужно проверять по файловому артефакту

## 5. Garak customization options relevant for internal contour

- REST generator contract: текущий стенд использует `rest.RestGenerator` с одинаковой схемой запроса и ответа для всех трех сервисов. Критичный контракт сейчас такой: `POST`, `Content-Type: application/json`, тело `{"prompt": "$INPUT"}`, ответ JSON, полезное поле `text`, timeout `120`. Если внутренние сервисы в контуре сохранят этот shape, текущие generator config files можно переносить почти без изменений
- Probe selection strategy: для практического скана полезно не запускать "весь Garak", а целиться в конкретные risk-families. Для этого в контуре важны `--probes`, `--probe_tags`, `--detectors`, `--extended_detectors`, `--taxonomy`. В лабораторном стенде реально полезными оказались семейства `ansiescape`, `promptinject`, `latentinjection` и `packagehallucination`
- Extended detectors: latent-сценарии показали, что один и тот же probe family может опираться на разные detectors, например `base.TriggerListDetector` и `unsafe_content.ToxicCommentModel`. Это значит, что в контуре надо явно фиксировать не только probe family, но и набор detectors, без которых coverage может заметно измениться
- Generations: параметр `--generations` управляет глубиной прогона и влияет на статистическую интерпретацию. Для smoke-check достаточно минимального значения, но для принятия решений по security posture внутреннего сервиса нужны более насыщенные прогоны, иначе confidence interval остается слишком широким
- Parallelism: для управления временем и стоимостью важны `--parallel_attempts`, `--parallel_requests` и при необходимости `--config fast`. Это особенно важно для больших probe families вроде `promptinject` и `latentinjection`, где время выполнения быстро растет
- Taxonomy/reporting: для эксплуатации в контуре следует сохранять минимум три класса артефактов: `report.jsonl` как source-of-truth, `report.html` как обзор и `hitlog.jsonl` как краткий журнал успешных атак. Дополнительно можно использовать AVID-конверсию через `garak -r`, но в текущей сборке `v0.14.1` она сработала только для `runs/01-openai-smoke/01-openai-smoke.report.jsonl`; остальные попытки зафиксированы в `avid-conversion.log` и упираются в `1 validation error for Artifact name`
- Need for custom probes/generators: если внутренние сервисы не совпадут по REST-контракту с текущим стендом, лучше писать собственный generator plugin, чем ломать внутренний API под тестовый формат. Если внутренние риски не сводятся к stock prompt patterns Garak, нужно писать собственные probes. Для сложных policy layers или pre-processing можно также использовать свои detectors и buffs
- Offline migration notes: сами три учебных приложения в контур как есть не переезжают, потому что они были завязаны на внешний OpenAI API. Зато переносится сам подход: Garak стреляет в endpoint по HTTP-контракту. Для полностью закрытого контура понадобятся или внутренний OpenAI-compatible endpoint, или собственный generator plugin. Дополнительно надо заранее проверить detectors, которым требуется интернет или внешние метаданные; в этом стенде такой зависимостью отметился `packagehallucination.PythonPypi`

## 6. Практический вывод для переноса в закрытый контур

### Что сработало

- `ansiescape` показал себя как очень сильная и практичная семья probes для сервисов, которые отдают текст дальше в терминал, консольный UI или другие интерпретаторы управляющих последовательностей
- `promptinject` уверенно поймал наивное следование вредоносным инструкциям внутри пользовательского контента
- `latentinjection` оказался полезен именно как stress-test на скрытые или замаскированные директивы внутри документа, а не как "абсолютный детектор всего"
- `packagehallucination.Python` хорошо работает для кода, когда сервис генерирует зависимости и import-ы

### Что Garak пропустил или поймал не полностью

- На `rag-summarizer-naive` один latent probe (`latentinjection.LatentInjectionReport`) не сработал, хотя другие latent probes уязвимость показали. Это означает, что coverage по latent injection не равномерен и не должен интерпретироваться как гарантия
- AVID-конверсия в этой конкретной сборке Garak частично нестабильна. Фактически создан только `runs/01-openai-smoke/01-openai-smoke.avid.jsonl`; остальные конверсии записаны в `avid-conversion.log` и падают на валидации `Artifact.name`
- Для `packagehallucination` есть зависимость от внешнего источника метаданных, так что в полностью offline-контуре эта семья probes потребует отдельной проверки и, возможно, локального зеркала или замены detector-а

### Что брать в контур в первую очередь

- `ansiescape` для всех сервисов, которые могут отдавать терминальные последовательности или иной потенциально опасный текстовый control output
- `promptinject` для RAG, summarization, agent-like pipelines и всех систем, где пользовательский документ может содержать инструкции
- `latentinjection` как следующий слой после promptinject, если в контуре есть обработка документов, резюме, переводов, справочных snippets или иных смешанных текстов
- `packagehallucination` для code assistants, codegen endpoints и developer tooling
- Текущий `rest.RestGenerator`-подход с generator option files, если внутренние сервисы согласованы по HTTP-контракту

### Что не брать в контур "как есть"

- Сами учебные FastAPI-сервисы как продуктовую основу: они нужны как демонстрационный стенд, а не как компонент продового контура
- Предположение, что внешний OpenAI API будет доступен или стабилен; recovery уже показал, что ключ мог стать невалидным позже, чем завершились исходные тесты
- Предположение, что `garak -r` надежно отработает по всем отчетам без дополнительной проверки результата по файловой системе

### Что нужно доработать перед переносом

- Зафиксировать внутренний REST-контракт тестируемых сервисов и по возможности сохранить его совместимым с текущими generator config files
- Прогнать pilot-валидацию detectors в реально закрытой среде, особенно там, где есть внешние зависимости или judge-модели
- Добавить собственные probes под внутренние риски, если в контуре есть нестандартные agent workflows, policy layers, retrieval chains или специфические форматы документов
- Определить baseline-набор probes для регулярного прогона: быстрый smoke-set, основной security-set и расширенный regression-set
- Проверить AVID-конверсию на целевой сборке Garak или зафиксировать альтернативный путь экспорта результатов, если AVID обязателен для внутренней отчетности

## 7. Состав итогового review-пакета

- Environment snapshot: `python-version.txt`, `garak-version.txt`, `garak-help.txt`, `pip-freeze.txt`, `system.txt`
- Garak inventory: `garak-generators.txt`, `garak-detectors.txt`, `garak-probes.txt`
- Generator configs: каталог `configs/`
- Source code of demo services: каталог `services/`
- Operational logs: каталог `logs/`
- Raw Garak reports and manual proofs: каталог `runs/`
- AVID conversion evidence: `runs/01-openai-smoke/01-openai-smoke.avid.jsonl`, `avid-conversion.log`
- Final summary: `FINAL_SUMMARY.md`

## 8. Итоговое заключение

Лабораторный стенд подтвердил, что Garak в связке с `rest.RestGenerator` хорошо подходит для проверки HTTP-сервисов, которые инкапсулируют LLM-поведение за обычным REST endpoint. На этом стенде Garak уверенно поймал ANSI output injection, prompt injection и package hallucination, а latent injection выявил частично: достаточно хорошо, чтобы считать эту семью probes полезной, но недостаточно хорошо, чтобы считать ее исчерпывающей без адаптации под внутренние документы и сценарии.

Практически это означает следующее: в закрытый контур имеет смысл переносить не сами демонстрационные сервисы, а методику и пакет артефактов. Базовый путь миграции выглядит так: сохранить совместимый REST-контракт для внутренних сервисов, взять в первый набор `ansiescape`, `promptinject`, `latentinjection` и `packagehallucination`, а затем дописать собственные probes/detectors там, где внутренние риски не совпадают со stock-наборами Garak. При этом результаты нужно читать прежде всего по `hitlog` и `report.jsonl`, а любые AVID-конверсии проверять по факту созданного файла, а не только по коду завершения команды.
