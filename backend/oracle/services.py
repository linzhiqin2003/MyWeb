"""Oracle prompt building, parsing, and DeepSeek consultation."""

from __future__ import annotations

import hashlib
import os
import re
from datetime import date
from typing import Any, Dict, Sequence

from cards.meanings import CARD_MEANINGS, meaning_for
from common.deepseek_models import CHAT_MODEL, get_client, non_thinking_kwargs

VALID_TONES = {"hopeful", "cautionary", "transformative", "conflicted", "serene"}
VALID_VERDICTS = {"yes", "lean_yes", "unclear", "lean_no", "no"}

POLARITY_SCORE = {"yes": 1.0, "maybe": 0.0, "no": -1.0}


def _card_line(card: Dict[str, Any], index: int) -> str:
    name = card.get("name") or "Unknown"
    extra = CARD_MEANINGS.get(name, {})
    name_cn = card.get("name_cn") or extra.get("name_cn") or name
    reversed_ = bool(card.get("reversed") or card.get("is_reversed"))
    position = card.get("position") or f"Position {index + 1}"
    position_cn = card.get("position_cn") or ""
    pos = f"{position_cn} / {position}" if position_cn else position
    orientation = "逆位 REVERSED" if reversed_ else "正位 UPRIGHT"
    keywords = card.get("keywords") or extra.get("keywords") or []
    kw = "、".join(keywords[:6])
    meaning = card.get("meaning") or meaning_for(name, reversed_)
    return (
        f"{index + 1}. [{pos}] {name_cn}（{name}）· {orientation}\n"
        f"   关键词: {kw or '—'}\n"
        f"   牌意: {meaning}"
    )


def build_prompt(
    question: str,
    cards: Sequence[Dict[str, Any]],
    spread_type: str = "reading",
    spread_name_cn: str = "",
    mode: str = "ritual",
) -> str:
    card_block = "\n".join(_card_line(c, i) for i, c in enumerate(cards))
    spread_label = spread_name_cn or spread_type

    if mode == "yesno":
        return f"""求问者的是非问题：「{question}」

抽出的牌：
{card_block}

请给出倾向性的是/否解读（不是算命保证，是牌面倾向），严格按下面格式输出：

---INTERPRETATION---
一段神秘而具体的英文解读（80-140 words），把牌的正逆位织进「为什么是这个倾向」。
---SUMMARY---
用中文 2-3 句说明：倾向是什么、关键阻力/助力、当下最该注意的一点。
---ADVICE---
一句可执行的中文建议。
---TONE---
hopeful | cautionary | transformative | conflicted | serene  （只写一个词）
---VERDICT---
yes | lean_yes | unclear | lean_no | no  （只写一个词）
"""

    if mode == "daily":
        return f"""求问者想要今日神谕。日期语境：「{question}」

今日之牌：
{card_block}

请给出今日指引，严格按下面格式输出：

---INTERPRETATION---
一段英文神谕（80-140 words），像黎明时分的低语，点出今天的能量与陷阱。
---SUMMARY---
用中文 2-3 句：今天的主旋律、需要小心的地方、可以把能量用在何处。
---ADVICE---
一句可执行的中文今日建议。
---TONE---
hopeful | cautionary | transformative | conflicted | serene
"""

    return f"""求问者问：「{question}」

牌阵：{spread_label}
抽出的牌：
{card_block}

请把所有牌织成一个完整叙事（不要逐张列标题清单），并给出可执行的建议。严格按下面格式输出：

---INTERPRETATION---
一段流畅的英文神秘解读（120-180 words），把每张牌的位置与正逆位自然织进故事，不要用 Card 1 / Card 2 这种标题。
---SUMMARY---
用通俗中文 3 句左右：当前局势、应该怎么做、可能的走向。
---ADVICE---
2 句中文行动建议，具体、可做，不要空话。
---TONE---
hopeful | cautionary | transformative | conflicted | serene
"""


def parse_oracle_text(ai_text: str, mode: str = "ritual") -> Dict[str, str]:
    text = (ai_text or "").strip()
    sections = {
        "interpretation": "",
        "summary": "",
        "advice": "",
        "tone": "",
        "verdict": "",
    }

    markers = [
        ("INTERPRETATION", "interpretation"),
        ("SUMMARY", "summary"),
        ("ADVICE", "advice"),
        ("TONE", "tone"),
        ("VERDICT", "verdict"),
    ]

    if "---" in text:
        parts = re.split(r"---([A-Z]+)---", text)
        # parts: [preamble, NAME, body, NAME, body, ...]
        mapping = {name: key for name, key in markers}
        i = 1
        while i + 1 < len(parts):
            name = parts[i].strip().upper()
            body = parts[i + 1].strip()
            if name in mapping:
                sections[mapping[name]] = body
            i += 2
        if not sections["interpretation"] and parts[0].strip():
            sections["interpretation"] = parts[0].strip()
    else:
        sections["interpretation"] = text

    tone = sections["tone"].split()[0].lower() if sections["tone"] else ""
    sections["tone"] = tone if tone in VALID_TONES else ""

    verdict = sections["verdict"].split()[0].lower() if sections["verdict"] else ""
    sections["verdict"] = verdict if verdict in VALID_VERDICTS else ""

    if not sections["summary"]:
        sections["summary"] = "牌阵揭示了你当前所面临的情况，建议保持觉察，相信自己的选择。"
    if not sections["advice"]:
        sections["advice"] = "先停一下，看清自己真正想要的，再迈下一步。"
    if not sections["interpretation"]:
        sections["interpretation"] = "The mists part slowly. Listen again."

    if mode == "yesno" and not sections["verdict"]:
        sections["verdict"] = "unclear"

    return sections


def fallback_reading(mode: str = "ritual") -> Dict[str, str]:
    if mode == "yesno":
        return {
            "interpretation": "The card leans, but will not shout. Sit with the tilt until it becomes a direction.",
            "summary": "目前倾向并不绝对。先看清自己真正在问什么，再决定要不要推进。",
            "advice": "把问题改写成「我准备好承担哪种结果了吗」，再问一次自己。",
            "tone": "conflicted",
            "verdict": "unclear",
        }
    if mode == "daily":
        return {
            "interpretation": "Today asks for a quieter kind of courage — not a leap, but a true step.",
            "summary": "今天适合把注意力收回身体和一件具体的事上。不必追求高潮，完成比完美重要。",
            "advice": "选一件小事做到底，让今天有一个清晰的句号。",
            "tone": "serene",
            "verdict": "",
        }
    return {
        "interpretation": "The mists part to reveal your path. The cards speak of transformation and new beginnings. Trust the shape of the journey, not only its speed.",
        "summary": "目前正处于转变期。保持开放，同时给自己一个可执行的下一步。前方会逐渐明朗。",
        "advice": "写下你真正害怕失去的东西，然后只为那一件采取一个小行动。",
        "tone": "transformative",
        "verdict": "",
    }


def consult_oracle(prompt: str, mode: str = "ritual") -> Dict[str, str]:
    api_key = os.environ.get("DEEPSEEK_API_KEY") or ""
    client = get_client(api_key)
    if not client:
        return fallback_reading(mode)

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a skilled, grounded Tarot reader. Mystical but specific. "
                        "Never claim certainty about medical, legal, or financial outcomes. "
                        "Follow the exact section markers requested."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            **non_thinking_kwargs(),
        )
        ai_text = response.choices[0].message.content or ""
        return parse_oracle_text(ai_text, mode=mode)
    except Exception:
        return fallback_reading(mode)


def polarity_verdict(cards: Sequence[Dict[str, Any]]) -> str:
    """Heuristic yes/no tilt from card polarities and reversals."""
    if not cards:
        return "unclear"
    total = 0.0
    for card in cards:
        name = card.get("name") or ""
        extra = CARD_MEANINGS.get(name, {})
        score = POLARITY_SCORE.get(extra.get("yes_no", "maybe"), 0.0)
        if card.get("reversed") or card.get("is_reversed"):
            score *= -0.7
        total += score
    avg = total / len(cards)
    if avg >= 0.55:
        return "yes"
    if avg >= 0.2:
        return "lean_yes"
    if avg <= -0.55:
        return "no"
    if avg <= -0.2:
        return "lean_no"
    return "unclear"


def pick_daily_index(day: date, n: int, salt: str = "") -> int:
    if n <= 0:
        return 0
    raw = f"{day.isoformat()}|{salt}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return int(digest, 16) % n


def pick_daily_reversed(day: date, chance: float = 0.28) -> bool:
    raw = f"{day.isoformat()}|reversed".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return bucket < chance
