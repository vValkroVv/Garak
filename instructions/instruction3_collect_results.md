# Инструкция 3 — сбор результата и подготовка общей картины для использования “в контуре”

## Цель стадии

На выходе у тебя должен быть один собранный пакет материалов, из которого видно:
1. как Garak устанавливался и верифицировался;
2. какие три учебных сервиса были спроектированы;
3. какие именно уязвимости были в них заложены;
4. какие probes/detectors применялись;
5. что Garak поймал, а что нет;
6. как Garak кастомизируется;
7. как этот стенд переносится в закрытый контур.  
Это важно, потому что Garak по умолчанию пишет подробный JSONL report, HTML summary и hitlog, а дальше умеет еще преобразовывать отчеты в AVID-совместимый формат. ([reference.garak.ai](https://reference.garak.ai/en/stable/reporting.html))

## Шаг 1. Зафиксируй окружение и версию инструмента

```bash
python --version > ~/garak-lab/review/python-version.txt
python -m garak --version > ~/garak-lab/review/garak-version.txt
python -m garak --help > ~/garak-lab/review/garak-help.txt
python -m pip freeze > ~/garak-lab/review/pip-freeze.txt
uname -a > ~/garak-lab/review/system.txt
```

Это нужно для воспроизводимости. Особенно важно зафиксировать версию Garak, потому что его probes и scoring со временем меняются, а current CLI docs уже собираются из более свежей ветки, чем latest stable release на PyPI. ([pypi.org](https://pypi.org/project/garak/))

**Критерий завершения:** в `review/` лежат пять текстовых файлов с версией Python, версией Garak, help, pip freeze и системной информацией.

## Шаг 2. Сохрани inventory того, что умеет Garak в твоей сборке

```bash
python -m garak --list_generators > ~/garak-lab/review/garak-generators.txt
python -m garak --list_detectors > ~/garak-lab/review/garak-detectors.txt
python -m garak --list_probes -v > ~/garak-lab/review/garak-probes.txt
```

Это даст тебе “снимок возможностей” текущего Garak: какие generators, detectors и probes реально доступны в твоем окружении. Для внутреннего контура это важно как baseline before/after, особенно если потом будешь ставить другой wheel, другой build или форк. ([reference.garak.ai](https://reference.garak.ai/en/latest/usage.html?utm_source=chatgpt.com))

**Критерий завершения:** три inventory-файла присутствуют в `review/`.

## Шаг 3. Скопируй в review все исходники и конфиги стенда

```bash
cp -R ~/garak-lab/configs ~/garak-lab/review/
cp -R ~/garak-lab/services ~/garak-lab/review/
cp -R ~/garak-lab/logs ~/garak-lab/review/
mkdir -p ~/garak-lab/review/runs
cp ~/garak-lab/runs/* ~/garak-lab/review/runs/ 2>/dev/null || true
```

Здесь идея простая: в итоговом пакете должны лежать не только отчеты Garak, но и **точный код** трех сервисов, плюс generator config, которым ты реально стрелял в endpoint’ы. Для будущего использования в контуре это важнее любого текстового summary. `rest.RestGenerator` зависит именно от URI, шаблона запроса, headers и поля ответа, поэтому сам generator config — это ключевой артефакт. ([reference.garak.ai](https://reference.garak.ai/en/latest/garak.generators.rest.html))

**Критерий завершения:** в `review/` есть каталоги `configs/`, `services/`, `logs/`, `runs/`.

## Шаг 4. Преобразуй сырые отчеты в более удобные артефакты

Garak docs говорят, что по умолчанию у тебя уже есть JSONL report, HTML report и hitlog. Этого достаточно как source-of-truth. Дополнительно Garak умеет превращать report JSONL в AVID-совместимый формат через `python -m garak -r <path_to_file>`. ([reference.garak.ai](https://reference.garak.ai/en/stable/reporting.html))

```bash
for f in ~/garak-lab/review/runs/*.report.jsonl; do
  python -m garak -r "$f"
done
```

Если потом захочешь более “редакторскую” выжимку, у Garak есть отдельные анализаторы, включая `garak.analyze.qual_review`, который генерирует qualitative Markdown review и выделяет сильно падающие probes. Это уже advanced-слой, но знать о нем полезно. ([reference.garak.ai](https://reference.garak.ai/en/latest/analyze.html))

**Критерий завершения:** рядом с report JSONL появляются AVID-артефакты.

## Шаг 5. Собери один итоговый Markdown-отчет

Создай файл `~/garak-lab/review/FINAL_SUMMARY.md` и заполни его по шаблону ниже.

```markdown
# Garak lab summary

## 1. Installation
- Python version:
- Garak version:
- OpenAI SDK installed:
- Self-test completed:
- Direct OpenAI smoke-run completed:

## 2. Demo services
### 2.1 ansi-terminal-proxy
- Endpoint:
- Intended vulnerability:
- Manual proof:
- Garak probes:
- Result:
- Evidence files:

### 2.2 rag-summarizer-naive
- Endpoint:
- Intended vulnerability:
- Manual proof:
- Garak probes:
- Result:
- Evidence files:

### 2.3 code-helper-bad-imports
- Endpoint:
- Intended vulnerability:
- Manual proof:
- Garak probes:
- Result:
- Evidence files:

## 3. Detection matrix
| Service | Manual vulnerability present? | Garak caught it? | Which probe/detector? | Notes |

## 4. Garak customization options relevant for internal contour
- REST generator contract:
- Probe selection strategy:
- Extended detectors:
- Generations:
- Parallelism:
- Taxonomy/reporting:
- Need for custom probes/generators:
- Offline migration notes:

## 5. Conclusion
- What worked:
- What Garak missed:
- What to change before moving into contour:
```

**Критерий завершения:** `FINAL_SUMMARY.md` заполнен по всем трем сервисам, и по каждому сервису явно указано “manual vulnerability present” и “Garak caught?”.

## Шаг 6. Отдельно зафиксируй, как ты интерпретировал отчеты

Это важный блок, потому что Garak reports — не просто PASS/FAIL-строки. Официальные docs говорят:
- JSONL report хранит entry rows, включая попытки и eval results;
- HTML report раскладывает результаты по modules/taxonomy → probes → detectors;
- hitlog содержит только успешные атаки;
- в eval entries могут быть confidence intervals;
- в HTML/console могут быть абсолютные и относительные оценки, включая z-scores. ([reference.garak.ai](https://reference.garak.ai/en/stable/reporting.html))

Отдельно задокументируй в `FINAL_SUMMARY.md` вот такие правила чтения:

- “основным evidence считаю hitlog и конкретные успешные attempts”;
- “HTML использую для overview по probe/detector”;
- “JSONL считаю source-of-truth”;
- “confidence intervals смотрю там, где sample size уже разумный”;
- “detector result интерпретирую с учетом качества detector’а”.

Последний пункт нужен потому, что docs по Detector Quality Metrics прямо говорят, что detectors оцениваются по labeled datasets и имеют precision / recall / F1; то есть detector — не магический oracle, а измеримый классификатор с ограничениями. ([reference.garak.ai](https://reference.garak.ai/en/latest/detector_metrics.html))

**Критерий завершения:** в итоговом summary есть короткий раздел “Как читались отчеты Garak”.

## Шаг 7. Зафиксируй, какие рычаги кастомизации Garak для тебя реально важны

По docs у Garak есть несколько слоев кастомизации:
- CLI-параметры;
- YAML/JSON config files;
- generator option files;
- собственные plugins — generators, probes, detectors, buffs, harnesses, evaluators.  
Buffs умеют модифицировать prompt перед отправкой; plugin system официально расширяемый, и docs отдельно показывают guide по написанию собственного generator и собственного probe. ([reference.garak.ai](https://reference.garak.ai/en/latest/configurable.html))

Для твоего будущего контура я бы зафиксировал в summary именно эти практические рычаги:

1. **Сужение скана:** `--probes`, `--probe_tags`, `--detectors`, `--extended_detectors`, `--taxonomy`. Это помогает не гонять “весь Garak”, а держать scan под конкретную систему и риск-класс. ([reference.garak.ai](https://reference.garak.ai/en/latest/cliref.html))  
2. **Управление временем/стоимостью:** `--generations`, `--parallel_attempts`, `--parallel_requests`, `--config fast`. Это критично, потому что full/default run может быть очень тяжелым. ([reference.garak.ai](https://reference.garak.ai/en/latest/cliref.html))  
3. **Подключение внутренних сервисов:** `rest.RestGenerator` + generator option file. Если внутренний сервис сохранит контракт запроса/ответа, можно почти без изменений перенести текущий стенд в контур. Если контракт другой — меняешь шаблон JSON или пишешь собственный generator plugin. ([reference.garak.ai](https://reference.garak.ai/en/latest/garak.generators.rest.html))  
4. **LLM-as-judge слой:** если потом захочешь judge-based detectors, docs отдельно говорят, что judge model должен быть OpenAI-compatible внутри Garak. ([reference.garak.ai](https://reference.garak.ai/en/latest/garak.detectors.judge.html))  
5. **Собственные probes под внутренние риски:** если в контуре есть нестандартный агентный workflow или свой специфический policy layer, его удобнее покрыть кастомным probe, а не надеяться только на stock probes. ([reference.garak.ai](https://reference.garak.ai/en/latest/extending.probe.html))

**Критерий завершения:** в `FINAL_SUMMARY.md` есть раздел “Garak customization options relevant for internal contour”, и в нем перечислены конкретные флаги/механизмы, а не общие слова.

## Шаг 8. Сформулируй вывод для переноса в контур

Три учебных сервиса здесь завязаны на внешний OpenAI API, значит сами они **не** переезжают в закрытый контур как есть. Но сам подход переносится почти напрямую: Garak работает с локальными или удаленными endpoints, а `rest.RestGenerator` зависит от формы HTTP-контракта, а не от того, какой именно LLM стоит за сервисом. Из этого следует практическая схема миграции: в контуре ты сохраняешь тот же внешний REST-контракт для тестируемых внутренних сервисов, а Garak-конфиг и набор probes оставляешь максимально неизменными. Если внутренний сервис не ложится на существующий REST-shape, тогда уже пишешь собственный generator plugin. ([reference.garak.ai](https://reference.garak.ai/en/latest/garak.generators.rest.html))

В итоговом выводе зафиксируй три вещи:

- какие probe families оказались полезными на лабораторном стенде;
- какие из них стоит брать в контур в первую очередь;
- что придется заменить или дописать при отсутствии интернета.

**Критерий завершения:** в конце `FINAL_SUMMARY.md` есть практический список “что берем в контур / что не берем / что надо доработать”.

---

## Финальный критерий успеха для Инструкции 3

Стадия считается завершенной, если у тебя есть единый каталог `~/garak-lab/review/`, внутри которого находятся:

- environment snapshot;
- inventory Garak capabilities;
- код трех сервисов;
- generator config;
- сырые Garak reports и hitlogs;
- AVID-конверсии;
- итоговый `FINAL_SUMMARY.md` с матрицей:
  - заложенная уязвимость,
  - ручное доказательство,
  - probe family,
  - поймал ли Garak,
  - какие артефакты это доказывают. ([reference.garak.ai](https://reference.garak.ai/en/latest/report.html))

Следующий логичный шаг — выполнять эти три инструкции по очереди и не переходить к следующей стадии, пока не выполнен ее критерий завершения.
