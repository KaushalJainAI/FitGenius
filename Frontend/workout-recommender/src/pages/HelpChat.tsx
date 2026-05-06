import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { Bot, FileText, Loader2, Send, UserRound, X } from "lucide-react";
import { api } from "../lib/api";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function HelpChat({ embedded = false }: { embedded?: boolean }) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hi, I can answer using your profile, latest check-in, and an attached document.",
    },
  ]);
  const [message, setMessage] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [isSending, setIsSending] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isSending) return;

    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setMessage("");
    setIsSending(true);

    try {
      const response = await api.helpChat({ message: trimmed, document_text: documentText });
      setMessages((current) => [...current, { role: "assistant", content: response.answer }]);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "The AI endpoint failed.";
      setMessages((current) => [...current, { role: "assistant", content: detail }]);
    } finally {
      setIsSending(false);
    }
  }

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setDocumentName(file.name);
    setDocumentText(await file.text());
  }

  function clearDocument() {
    setDocumentName("");
    setDocumentText("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div className={`${embedded ? "h-full min-h-0" : "h-[calc(100vh-12rem)] min-h-[620px]"} animate-page-enter grid grid-rows-[auto_1fr_auto] gap-4`}>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Help Chat</h2>
          <p className="text-sm text-muted-foreground mt-1">Ask about your plan, recovery, diet, or the attached document.</p>
        </div>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.csv,.json"
            className="hidden"
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-border bg-card px-4 text-sm font-medium hover:bg-muted transition-colors"
          >
            <FileText className="h-4 w-4" />
            Attach
          </button>
          {documentName && (
            <button
              type="button"
              onClick={clearDocument}
              className="inline-flex h-10 max-w-[220px] items-center gap-2 rounded-lg bg-secondary/10 px-3 text-sm text-secondary hover:bg-secondary/15 transition-colors"
              title={documentName}
            >
              <span className="truncate">{documentName}</span>
              <X className="h-4 w-4 flex-shrink-0" />
            </button>
          )}
        </div>
      </div>

      <div className="overflow-y-auto rounded-lg border border-border bg-card p-4 shadow-sm">
        <div className="space-y-4">
          {messages.map((item, index) => (
            <div key={`${item.role}-${index}`} className={`flex gap-3 ${item.role === "user" ? "justify-end" : "justify-start"}`}>
              {item.role === "assistant" && (
                <div className="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Bot className="h-5 w-5" />
                </div>
              )}
              <div
                className={`max-w-[min(760px,80%)] whitespace-pre-wrap rounded-lg px-4 py-3 text-sm leading-6 ${
                  item.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                {item.content}
              </div>
              {item.role === "user" && (
                <div className="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-accent/20 text-accent-foreground">
                  <UserRound className="h-5 w-5" />
                </div>
              )}
            </div>
          ))}
          {isSending && (
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Thinking with your profile context
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3 rounded-lg border border-border bg-card p-3 shadow-sm">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          className="min-h-12 flex-1 resize-none rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          placeholder="Ask FitGenius..."
          rows={2}
        />
        <button
          type="submit"
          disabled={isSending || !message.trim()}
          className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
          title="Send"
        >
          {isSending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
        </button>
      </form>
    </div>
  );
}
