"""Tool Using Agent Pro: Tkinter desktop interface."""
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path

from tools import (
    list_topics, search_knowledge, get_topic_details,
    add_knowledge_entry, load_knowledge, get_knowledge_stats
)

APP_DIR = Path(__file__).parent


class AgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tool Using Agent | Knowledge Desk")
        self.root.geometry("1120x760")
        self.root.minsize(920, 620)
        self.root.configure(bg="#0b1220")
        self.history = []
        self._configure_style()
        self._build_ui()
        self.refresh_topics()
        self._welcome_message()
        self.update_stats()

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(10, 8))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 9))

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#111c31", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="✦  TOOL USING AGENT", bg="#111c31", fg="#f1f5f9",
                 font=("Segoe UI Semibold", 19)).pack(anchor="w", padx=22, pady=(15, 0))
        tk.Label(header, text="Knowledge retrieval • Tool routing • Evidence-grounded answers",
                 bg="#111c31", fg="#9fb0ca", font=("Segoe UI", 10)).pack(anchor="w", padx=24)

        body = tk.Frame(self.root, bg="#0b1220")
        body.pack(fill="both", expand=True, padx=14, pady=14)

        sidebar = tk.Frame(body, bg="#111c31", width=260)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="WORKSPACE", bg="#111c31", fg="#7dd3fc",
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=16, pady=(17, 8))
        ttk.Button(sidebar, text="＋  New conversation", command=self.clear_chat).pack(fill="x", padx=12, pady=3)
        ttk.Button(sidebar, text="↻  Refresh knowledge", command=self.refresh_all).pack(fill="x", padx=12, pady=3)
        ttk.Button(sidebar, text="⇩  Export conversation", command=self.export_history).pack(fill="x", padx=12, pady=3)

        tk.Label(sidebar, text="KNOWLEDGE TOPICS", bg="#111c31", fg="#7dd3fc",
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=16, pady=(22, 8))
        topic_frame = tk.Frame(sidebar, bg="#111c31")
        topic_frame.pack(fill="both", expand=True, padx=12)
        self.topic_list = tk.Listbox(topic_frame, bg="#17243b", fg="#e2e8f0",
                                     selectbackground="#2563eb", selectforeground="white",
                                     borderwidth=0, highlightthickness=0,
                                     font=("Segoe UI", 10), activestyle="none")
        self.topic_list.pack(fill="both", expand=True)
        self.topic_list.bind("<Double-Button-1>", self.ask_selected_topic)

        self.stats_label = tk.Label(sidebar, text="", justify="left", bg="#111c31",
                                    fg="#9fb0ca", font=("Segoe UI", 9))
        self.stats_label.pack(anchor="w", padx=16, pady=14)

        content = tk.Frame(body, bg="#0b1220")
        content.pack(side="left", fill="both", expand=True)

        controls = tk.Frame(content, bg="#0b1220")
        controls.pack(fill="x", pady=(0, 10))
        tk.Label(controls, text="Response mode", bg="#0b1220", fg="#cbd5e1",
                 font=("Segoe UI Semibold", 10)).pack(side="left")
        self.mode = tk.StringVar(value="Auto route")
        self.mode_combo = ttk.Combobox(controls, textvariable=self.mode, state="readonly",
                                       values=["Auto route", "Search knowledge", "Topic details", "List topics"],
                                       width=19)
        self.mode_combo.pack(side="left", padx=10)
        ttk.Button(controls, text="＋ Add knowledge", command=self.open_add_dialog).pack(side="right")

        chat_card = tk.Frame(content, bg="#111c31", highlightbackground="#24344f", highlightthickness=1)
        chat_card.pack(fill="both", expand=True)
        tk.Label(chat_card, text="AGENT CONVERSATION", bg="#111c31", fg="#7dd3fc",
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=15, pady=(13, 4))

        self.chat = tk.Text(chat_card, wrap="word", bg="#0f192b", fg="#e5edf8",
                            insertbackground="white", relief="flat", borderwidth=0,
                            padx=15, pady=12, font=("Segoe UI", 10), state="disabled")
        self.chat.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.chat.tag_configure("user", foreground="#7dd3fc", font=("Segoe UI Semibold", 10))
        self.chat.tag_configure("agent", foreground="#86efac", font=("Segoe UI Semibold", 10))
        self.chat.tag_configure("meta", foreground="#94a3b8", font=("Consolas", 9))
        self.chat.tag_configure("body", foreground="#e5edf8", spacing1=2, spacing3=7)
        self.chat.tag_configure("error", foreground="#fca5a5")

        quick = tk.Frame(content, bg="#0b1220")
        quick.pack(fill="x", pady=(10, 7))
        tk.Label(quick, text="Try:", bg="#0b1220", fg="#94a3b8",
                 font=("Segoe UI", 9)).pack(side="left", padx=(2, 8))
        for label, prompt in [
            ("What is Python?", "What is Python?"),
            ("CSS parser", "What does a CSS parser do?"),
            ("Hallucination prevention", "Explain hallucination prevention"),
            ("List topics", "list topics")
        ]:
            ttk.Button(quick, text=label, command=lambda p=prompt: self.use_prompt(p)).pack(side="left", padx=3)

        composer = tk.Frame(content, bg="#111c31", padx=10, pady=10)
        composer.pack(fill="x")
        self.question = tk.Text(composer, height=3, wrap="word", bg="#17243b", fg="#f8fafc",
                                insertbackground="white", relief="flat", padx=10, pady=8,
                                font=("Segoe UI", 10))
        self.question.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.question.bind("<Control-Return>", self._send_shortcut)
        ttk.Button(composer, text="Send  ➤", style="Accent.TButton",
                   command=self.send_question).pack(side="right", anchor="s")

        tk.Label(content, text="Enter sends nothing automatically • Ctrl+Enter submits • Answers use local knowledge.json",
                 bg="#0b1220", fg="#64748b", font=("Segoe UI", 8)).pack(anchor="w", pady=(7, 0))

    def _welcome_message(self):
        self._append("AGENT", "Welcome to Knowledge Desk. Ask a question, choose a response mode, or double-click a topic on the left.", "agent")
        self._append("SYSTEM", "This demo uses local keyword retrieval. It is not connected to an external LLM.", "meta")

    def _append(self, speaker, text, tag="body"):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{speaker}\n", "user" if speaker == "YOU" else ("agent" if speaker == "AGENT" else "meta"))
        self.chat.insert("end", text + "\n\n", tag)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _send_shortcut(self, _event):
        self.send_question()
        return "break"

    def use_prompt(self, prompt):
        self.question.delete("1.0", "end")
        self.question.insert("1.0", prompt)
        self.send_question()

    def ask_selected_topic(self, _event=None):
        selection = self.topic_list.curselection()
        if selection:
            topic = self.topic_list.get(selection[0])
            self.use_prompt(f"Tell me about {topic}")

    def send_question(self):
        question = self.question.get("1.0", "end").strip()
        if not question:
            messagebox.showinfo("Question needed", "Type a question first.")
            return
        self.question.delete("1.0", "end")
        self._append("YOU", question, "body")

        selected_mode = self.mode.get()
        if selected_mode == "List topics":
            result = list_topics()
            tool = "list_topics"
            answer = "Available topics: " + ", ".join(result["topics"]) if result["found"] else "The knowledge base has no topics yet."
            evidence = []
        elif selected_mode == "Search knowledge":
            result = search_knowledge(question)
            tool = "search_knowledge"
            answer, evidence = self._format_result(result)
        elif selected_mode == "Topic details":
            result = get_topic_details(question)
            tool = "get_topic_details"
            answer, evidence = self._format_result(result)
        else:
            tool = self._route(question)
            if tool == "list_topics":
                result = list_topics()
                answer = "Available topics: " + ", ".join(result["topics"]) if result["found"] else "The knowledge base has no topics yet."
                evidence = []
            elif tool == "search_knowledge":
                result = search_knowledge(question)
                answer, evidence = self._format_result(result)
            else:
                result = get_topic_details(question)
                answer, evidence = self._format_result(result)

        self._append("TOOL ROUTER", f"Selected tool: {tool}", "meta")
        self._append("AGENT", answer, "error" if not result.get("found") and tool != "list_topics" else "body")
        if evidence:
            evidence_text = "\n".join(
                f"• {e.get('topic', 'Untitled')} | matched source entry\n  {e.get('answer', '')}"
                for e in evidence
            )
            self._append("EVIDENCE", evidence_text, "meta")

        self.history.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "question": question,
            "mode": selected_mode,
            "tool": tool,
            "answer": answer,
            "evidence": evidence
        })
        self.update_stats()

    def _route(self, question):
        q = question.lower().strip()
        if q == "topics" or any(x in q for x in ("list topics", "available topics", "what topics")):
            return "list_topics"
        if any(x in q for x in ("search", "find", "look for", "keyword")):
            return "search_knowledge"
        return "get_topic_details"

    def _format_result(self, result):
        if not result.get("found"):
            return ("I couldn't find enough information in the local knowledge base. "
                    "Try another wording or add a trusted entry using “Add knowledge.”", [])
        evidence = result.get("entries", [])
        answer = "\n\n".join(f"{entry['topic']}: {entry['answer']}" for entry in evidence)
        return answer, evidence

    def refresh_topics(self):
        self.topic_list.delete(0, "end")
        for topic in list_topics().get("topics", []):
            self.topic_list.insert("end", topic)

    def update_stats(self):
        stats = get_knowledge_stats()
        self.stats_label.config(
            text=f"LOCAL KNOWLEDGE BASE\n{stats['entries']} entries  •  {stats['topics']} topics\n"
                 f"{stats['keywords']} keywords indexed\n\nSession: {len(self.history)} questions"
        )

    def refresh_all(self):
        self.refresh_topics()
        self.update_stats()
        self._append("SYSTEM", "Knowledge source refreshed from knowledge.json.", "meta")

    def clear_chat(self):
        self.history.clear()
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self._welcome_message()
        self.update_stats()

    def export_history(self):
        if not self.history:
            messagebox.showinfo("Nothing to export", "Ask at least one question before exporting.")
            return
        path = filedialog.asksaveasfilename(
            title="Export conversation",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="agent_conversation.json"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Export complete", f"Conversation saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

    def open_add_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add trusted knowledge")
        dialog.geometry("520x470")
        dialog.configure(bg="#111c31")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Add a knowledge entry", bg="#111c31", fg="#f1f5f9",
                 font=("Segoe UI Semibold", 16)).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(dialog, text="Entries are saved to knowledge.json and used in future searches.",
                 bg="#111c31", fg="#9fb0ca", wraplength=470, justify="left").pack(anchor="w", padx=18, pady=(0, 12))

        fields = {}
        for key, label, height in [
            ("topic", "Topic", 1),
            ("question", "Example question", 1),
            ("answer", "Trusted answer", 4),
            ("keywords", "Keywords (comma-separated)", 2)
        ]:
            tk.Label(dialog, text=label, bg="#111c31", fg="#cbd5e1").pack(anchor="w", padx=18)
            widget = tk.Text(dialog, height=height, wrap="word", bg="#17243b", fg="#f8fafc",
                             insertbackground="white", relief="flat", padx=8, pady=6)
            widget.pack(fill="x", padx=18, pady=(3, 9))
            fields[key] = widget

        def save():
            entry = {
                "topic": fields["topic"].get("1.0", "end").strip(),
                "question": fields["question"].get("1.0", "end").strip(),
                "answer": fields["answer"].get("1.0", "end").strip(),
                "keywords": [x.strip() for x in fields["keywords"].get("1.0", "end").split(",") if x.strip()]
            }
            if not entry["topic"] or not entry["answer"]:
                messagebox.showwarning("Missing fields", "Topic and trusted answer are required.", parent=dialog)
                return
            try:
                add_knowledge_entry(entry)
                self.refresh_topics()
                self.update_stats()
                self._append("SYSTEM", f"Added knowledge entry: {entry['topic']}", "meta")
                messagebox.showinfo("Saved", "Knowledge entry saved successfully.", parent=dialog)
                dialog.destroy()
            except (OSError, ValueError) as exc:
                messagebox.showerror("Could not save", str(exc), parent=dialog)

        ttk.Button(dialog, text="Save knowledge entry", command=save).pack(anchor="e", padx=18, pady=12)


def main():
    root = tk.Tk()
    AgentApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
