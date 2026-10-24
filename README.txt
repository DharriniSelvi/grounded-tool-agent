TOOL USING AGENT PRO — DESKTOP UI
===================================

WHAT'S INCLUDED
---------------
main.py         Tkinter desktop interface and chat workflow
tools.py        Search, topic retrieval, stats, and add-knowledge tools
knowledge.json  Local trusted knowledge base
README.txt      Setup and usage notes
test_agent.py   Basic automated tests

FEATURES
--------
- Desktop chat interface with dark theme
- Automatic routing or manual response-mode selection
- Local keyword search over a JSON knowledge base
- Evidence entries displayed under answers
- Topic sidebar with double-click-to-ask
- Add new trusted knowledge entries from the UI
- Knowledge statistics
- Export conversation to JSON
- Missing-information fallback
- Automated tests for retrieval and knowledge management

RUN
---
1. Extract the ZIP.
2. Open the folder in VS Code.
3. Run: python main.py

Tkinter is normally included with standard Python on Windows. No pip installs
are required.

TESTS
-----
Run: python -m unittest test_agent.py

LIMITATIONS
-----------
This is a more feature-rich deterministic tool-using agent prototype, not a
live LLM. It uses keyword matching and simple routing. It may miss paraphrases
or retrieve irrelevant entries. The "evidence" shown is the retrieved knowledge
entry, not a guarantee that a claim is universally true. Only add information
you trust to knowledge.json.
