"""Generate the game's local Russian voice lines with Silero v4."""

import json
import wave
from pathlib import Path

from silero import silero_tts


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "audio" / "voices"
SAMPLE_RATE = 48000

VOICE_BY_KEY = {
    "ceo": "xenia",
    "accounting": "baya",
    "support": "kseniya",
    "sales": "xenia",
    "teamlead_be": "aidar",
    "teamlead_fe": "eugene",
    "teamlead_qa": "aidar",
    "docs": "eugene",
    "customer": "aidar",
    "legacy": "eugene",
}

RESULTS = {
    "give_resource": ("teamlead_be", "Ресурс отдан BE. FE уже смотрит неодобрительно."),
    "deny_resource": ("teamlead_be", "BE получил отказ и записал это в блокнот."),
    "intervene": ("teamlead_be", "РП взял задачу себе. Тимлид сделал вид, что не обиделся."),
    "manual_qa": ("teamlead_qa", "Ручная проверка нашла баг. Это хороший знак."),
    "pressure_qa": ("teamlead_qa", "QA пообещал ускориться. Очень угрожающе."),
    "trust_qa": ("teamlead_qa", "РП поверил зелёному отчёту."),
    "ceo_buy": ("ceo", "CEO подписала закупку. Бумажка победила."),
    "ceo_wait": ("ceo", "CEO попросила прийти завтра. Классика."),
    "ceo_escalate": ("ceo", "CEO взяла юридическое давление на себя."),
    "ceo_sell_buggy": ("ceo", "CEO объявила продукт готовым и отправила его продавать, несмотря на баги."),
    "give_fe_time": ("teamlead_fe", "FE получил время и перестал смотреть на BE."),
    "check_fe_api": ("teamlead_fe", "API проверен. Нашлась одна маленькая катастрофа."),
    "trust_fe": ("teamlead_fe", "РП поверил фронтенду на слово."),
    "give_docs_time": ("docs", "Документация получила время и открыла файл."),
    "ask_docs_draft": ("docs", "Черновик найден. В нём больше вопросов, чем страниц."),
    "trust_docs": ("docs", "Документация отправлена как есть."),
    "customer_escalate": ("customer", "CEO подключилась к разговору с юристом."),
    "customer_crutch": ("customer", "Костыль приклеен. Держится на честном слове."),
    "customer_explain": ("customer", "Заказчику объяснили порядок. Он записал номер юриста."),
    "support_paper": ("support", "Бумажка выдана. Поддержка зашевелилась."),
    "support_star": ("support", "Звёздный сотрудник решил вопрос за пять минут."),
    "support_escalate": ("support", "Заявка поднялась на самый верх папки."),
    "sales_task": ("sales", "Мобильное приложение записано отдельной задачей."),
    "sales_cancel": ("sales", "Продажи обещали больше ничего не обещать."),
    "sales_bluff": ("sales", "Все сделали вид, что мобильное приложение было в плане."),
    "accounting_sign": ("accounting", "Акт подписан. Печать разочарована."),
    "accounting_pay": ("accounting", "Штраф оплачен. Бухгалтерия улыбается."),
    "accounting_wait": ("accounting", "Отсрочка согласована до следующего звонка."),
}


def save_wav(path: Path, audio) -> None:
    samples = audio.detach().cpu().clamp(-1, 1).mul(32767).short().numpy().tobytes()
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(samples)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    model, _ = silero_tts(language="ru", speaker="v4_ru")
    with (ROOT / "data" / "dialogs.json").open(encoding="utf-8") as stream:
        dialogs = json.load(stream)

    for key, dialog in dialogs.items():
        speaker = VOICE_BY_KEY[key]
        audio = model.apply_tts(text=dialog["text"], speaker=speaker, sample_rate=SAMPLE_RATE)
        save_wav(OUT / f"dialog_{key}.wav", audio)
        print(f"dialog_{key}: {speaker}")

    for action, (key, message) in RESULTS.items():
        speaker = VOICE_BY_KEY[key]
        audio = model.apply_tts(text=message, speaker=speaker, sample_rate=SAMPLE_RATE)
        save_wav(OUT / f"result_{action}.wav", audio)
        print(f"result_{action}: {speaker}")


if __name__ == "__main__":
    main()
