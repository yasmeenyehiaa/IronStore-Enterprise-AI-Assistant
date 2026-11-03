import csv
import json

from dotenv import load_dotenv
from openai import OpenAI

from chat import stream_answer

load_dotenv()
client = OpenAI()

JUDGE_MODEL = "gpt-4o"  # stronger than the chat model, so it isn't grading its own work

JUDGE_PROMPT = """You are grading an AI assistant's answer about company documents.

Question: {question}
Should the assistant answer this question from the documents? {should_answer}
Reference facts from the documents: {reference}
Assistant's answer: {answer}

Grade the answer and reply with JSON only:
- "correct": true if the answer contains the key facts from the reference and no wrong facts (the answer is sometimes more detailed than the reference, this should be allowed).
  If should_answer is false, set "correct" to true only when the assistant says it doesn't know.
- "abstained": true if the assistant said it could not find the answer.
- "cited": true if the answer names a document title or page.
- "reason": one short sentence explaining the grade.

Example reply: {{"correct": true, "abstained": false, "cited": true, "reason": "Matches the reference steps."}}"""


def judge(item, answer):
    prompt = JUDGE_PROMPT.format(
        question=item["question"],
        should_answer=item["should_answer"],
        reference=item["reference"] or "(none: the assistant should refuse)",
        answer=answer,
    )
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(resp.choices[0].message.content)


def eval():
    with open("eval_set.json", encoding="utf-8") as f:
        items = json.load(f)

    rows = []
    for i, item in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item['question']}")
        answer = "".join(stream_answer(item["question"]))  # run the real assistant
        grade = judge(item, answer)
        rows.append({
            "question": item["question"],
            "should_answer": item["should_answer"],
            "correct": grade["correct"],
            "abstained": grade["abstained"],
            "cited": grade["cited"],
            "reason": grade["reason"],
            "answer": answer,
        })
        print(f"    correct={grade['correct']}  {grade['reason']}")

    with open("eval_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    passed = sum(r["correct"] for r in rows)
    cited = [r for r in rows if r["should_answer"] and not r["abstained"]]
    print("\n--- Summary ---")
    print(f"Passed: {passed}/{total} ({passed / total:.0%})")
    if cited:
        print(f"Answers with a citation: {sum(r['cited'] for r in cited)}/{len(cited)}")
    print("Full results saved to eval_results.csv")


if __name__ == "__main__":
    eval()