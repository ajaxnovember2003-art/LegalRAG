import requests


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "llama3.2:3b"


# ============================================================
# GENERATE LEGAL ANSWER
# ============================================================

def generate_answer(context, query):

    prompt = f"""
You are a legal information extraction assistant for the
Bharatiya Nyaya Sanhita (BNS), 2023.

Your task is to answer the user's question ONLY using the
RETRIEVED LEGAL CONTEXT.

============================================================
USER QUESTION
============================================================

{query}

============================================================
RETRIEVED LEGAL CONTEXT
============================================================

{context}

============================================================
STRICT EXTRACTION RULES
============================================================

1. First identify which section directly answers the question.

2. For the identified section, carefully scan the ENTIRE section
   before generating the answer.

3. Give the section number and offence name.

4. Extract EVERY punishment condition explicitly stated in that
   section.

5. Pay particular attention to subsection numbers such as:
   (1), (2), (3), etc.

6. Pay particular attention to legal qualifiers including:
   - "second or subsequent conviction"
   - "first time"
   - "provided that"
   - "where"
   - "if"
   - "when"
   - "shall be punished"
   - "may extend to"
   - "shall not be less than"
   - "with fine"
   - "with both"
   - "community service"

7. DO NOT stop after finding the first punishment.

8. If the section contains a general punishment AND a special
   conditional punishment, include BOTH.

9. If the section contains a different punishment for a second
   or subsequent conviction, include it separately.

10. If the section contains a proviso that changes the punishment
    under certain conditions, include that proviso separately.

11. Do NOT use punishment information from another section merely
    because that section mentions the same offence.

12. Do NOT combine punishments from Sections 303, 304, 307, 314,
    317, or any other section unless the user's question explicitly
    asks about those sections.

13. Do NOT use IPC provisions.

14. Do NOT use outside legal knowledge.

15. Do NOT infer a punishment that is not explicitly present in
    the retrieved context.

16. Preserve all important conditions such as:
    - first conviction
    - subsequent conviction
    - property value
    - minimum imprisonment
    - maximum imprisonment
    - fine
    - community service
    - return/restoration of property

17. Ignore examples and illustrations unless they are necessary
    to understand a punishment condition.

============================================================
ANSWER FORMAT
============================================================

Section XXX — Offence Name

Punishment:
- General punishment: ...
- Second/subsequent conviction: ...
- Special conditional punishment/proviso: ...

If a category does not apply, do not include it.

============================================================
FINAL CHECK BEFORE ANSWERING
============================================================

Before producing the answer, verify:

[ ] Correct section identified
[ ] Entire relevant section examined
[ ] Every punishment subsection examined
[ ] Provisos examined
[ ] First-conviction condition examined
[ ] Subsequent-conviction condition examined
[ ] Fine included where applicable
[ ] Community service included where applicable
[ ] No unrelated section used

If the retrieved context genuinely does not contain enough
information to answer the question, respond exactly:

The retrieved legal context does not contain enough information
to answer this question.

ANSWER:
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            ""
        ).strip()

        if not answer:
            return "The LLM returned an empty response."

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "The LLM request timed out. "
            "Please try again."
        )

    except requests.exceptions.RequestException as e:

        return f"LLM request failed: {e}"

    except Exception as e:

        return f"Unexpected LLM error: {e}"