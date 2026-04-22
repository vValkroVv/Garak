# Инструкция 1 — установка Garak и базовая верификация

## Цель стадии

На выходе у тебя должен быть серверный стенд, где:
1. установлен Garak в отдельном venv;
2. есть доступ к OpenAI API через `OPENAI_API_KEY`;
3. выполняется self-test Garak;
4. выполняется короткий smoke-run против OpenAI напрямую;
5. в каталоге `runs/` появляются артефакты отчета: JSONL report, HTML report и hitlog. Garak официально пишет именно эти типы артефактов по умолчанию. ([pypi.org](https://pypi.org/project/garak/))

## Что важно понимать до начала

Garak — это CLI-инструмент, на PyPI сейчас latest release `0.14.1`, он требует Python `>=3.10`. В официальных docs Garak рекомендует либо установку через `pip`, либо установку из исходников в отдельное окружение. Для быстрого серверного стенда достаточно `pip install -U garak`. ([pypi.org](https://pypi.org/project/garak/))

Полный дефолтный прогон Garak может быть очень тяжелым: docs прямо предупреждают, что стандартный run может доходить до 80,000+ inference requests. Поэтому на стадии установки не делай full scan — только self-test и короткий targeted smoke-run. ([reference.garak.ai](https://reference.garak.ai/en/latest/faster.html))

И еще одно правило из user guide: запускай Garak только по системам, которые тебе разрешено тестировать. Для лабораторного стенда ниже это соблюдено, потому что ты тестируешь свои локальные сервисы на своем сервере. ([docs.garak.ai](https://docs.garak.ai/garak/llm-scanning-basics/your-first-scan))

## Шаг 1. Подготовь рабочие каталоги

```bash
mkdir -p ~/garak-lab/{services,configs,runs,logs,review}
mkdir -p ~/venvs
```

**Критерий завершения:** каталоги созданы, `ls ~/garak-lab` показывает `services`, `configs`, `runs`, `logs`, `review`.

## Шаг 2. Создай отдельное Python-окружение

```bash
python3 --version
python3 -m venv ~/venvs/garak-lab
source ~/venvs/garak-lab/bin/activate
python -m pip install --upgrade pip
```

**Критерий завершения:** после `python3 --version` версия Python не ниже `3.10`, а `which python` указывает на `~/venvs/garak-lab/bin/python`. Требование Python 3.10+ зафиксировано и в PyPI, и в user guide. ([pypi.org](https://pypi.org/project/garak/))

## Шаг 3. Установи Garak и библиотеки для демо-сервисов

```bash
python -m pip install -U garak fastapi "uvicorn[standard]" openai
```

**Критерий завершения:** команда заканчивается без ошибок, `pip` не сообщает о broken dependency resolution, а пакет `garak` доступен для импорта и запуска. Для демо-сервисов дальше понадобятся только `fastapi`, `uvicorn` и `openai`. OpenAI SDK дальше будет использовать Responses API. ([pypi.org](https://pypi.org/project/garak/))

## Шаг 4. Настрой OpenAI API ключ и модель

Официальный quickstart OpenAI рекомендует сначала создать API key и экспортировать его как переменную окружения; help-center отдельно рекомендует использовать именно `OPENAI_API_KEY` как стандартное имя переменной. ([developers.openai.com](https://developers.openai.com/api/docs/quickstart))

```bash
export OPENAI_API_KEY='PASTE_YOUR_KEY_HERE'
export OPENAI_MODEL='gpt-5.2'
```

Если у тебя в аккаунте доступна другая модель, просто замени `gpt-5.2` на нее. Для этого runbook важно только то, чтобы модель реально была доступна твоему ключу.

**Критерий завершения:** `echo ${OPENAI_API_KEY:+set}` печатает `set`, а `echo $OPENAI_MODEL` печатает имя выбранной модели.

## Шаг 5. Проверь, что Garak CLI живой

```bash
python -m garak --version
python -m garak --help
python -m garak --list_generators > ~/garak-lab/review/garak-generators.txt
python -m garak --list_detectors > ~/garak-lab/review/garak-detectors.txt
python -m garak --list_probes -v > ~/garak-lab/review/garak-probes.txt
```

Актуальная CLI reference документирует флаги `--target_type`, `--target_name`, `--probes`, `--detectors`, `--extended_detectors`, `--generator_option_file`, `--taxonomy`, `--parallel_attempts`, `--parallel_requests`, `--report_prefix` и `--config`. Это и есть тот набор, который тебе понадобится дальше. ([reference.garak.ai](https://reference.garak.ai/en/latest/cliref.html))

**Критерий завершения:** команда `--version` выводит версию Garak, `--help` отрабатывает, а в `~/garak-lab/review/` появились три текстовых файла со списками generators/detectors/probes.

## Шаг 6. Прогони self-test Garak

В user guide есть специальный базовый self-test: `test.Blank` generator + `test.Test` probe. Именно его и запускай первым. Обрати внимание: на этой старой example-странице еще используется историческое `--model_type`; это нормально и полезно именно как self-test example. При реальных запусках ниже мы уже будем использовать современный `--target_type`. ([docs.garak.ai](https://docs.garak.ai/garak/examples/basic-test))

```bash
python -m garak \
  --model_type test.Blank \
  --probes test.Test \
  --report_prefix ~/garak-lab/runs/00-selftest
```

**Критерий завершения:** run заканчивается без traceback, а в `~/garak-lab/runs/` появляются артефакты self-test: report JSONL, HTML и hitlog. Garak официально пишет эти три типа результатов по умолчанию. ([reference.garak.ai](https://reference.garak.ai/en/stable/reporting.html))

## Шаг 7. Прогони короткий smoke-test против OpenAI напрямую

У Garak есть отдельный `openai` generator; документация по нему говорит, что он использует OpenAI-compatible API и ожидает `OPENAI_API_KEY` в окружении. Для стадии установки нужен не “опасный” и не длинный прогон, а просто проверка, что Garak способен сходить во внешний API и сформировать отчет. ([reference.garak.ai](https://reference.garak.ai/en/stable/garak.generators.openai.html))

```bash
python -m garak \
  --target_type openai \
  --target_name "$OPENAI_MODEL" \
  --probes ansiescape.AnsiEscaped \
  --generations 1 \
  --report_prefix ~/garak-lab/runs/01-openai-smoke
```

Я здесь специально беру один probe и `--generations 1`, чтобы не раздувать время и стоимость. Это именно технический smoke-run, а не полноценный security assessment. Garak docs отдельно советуют на ранней стадии держать run узким и targeted, а не запускать все подряд. ([reference.garak.ai](https://reference.garak.ai/en/latest/faster.html))

**Критерий завершения:** run завершается без ошибки авторизации или model lookup error, а в `runs/` появляется еще один комплект отчетов.

## Финальный критерий успеха для Инструкции 1

Стадия считается завершенной, если выполнены все пункты:

- venv активируется, Python не ниже 3.10;
- `python -m garak --version` и `--help` работают;
- сохранены inventory-файлы `garak-generators.txt`, `garak-detectors.txt`, `garak-probes.txt`;
- self-test `test.Blank + test.Test` отработал;
- короткий OpenAI smoke-run отработал;
- в `~/garak-lab/runs/` есть как минимум два набора артефактов Garak: JSONL report, HTML report, hitlog. ([pypi.org](https://pypi.org/project/garak/))
