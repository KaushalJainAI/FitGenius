import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Bot, FileText, Globe2, History, Loader2, Plus, UserRound, X, Sparkles, SendHorizontal } from "lucide-react";
import { api } from "../lib/api";
import type { ChatConversation as ApiConversation, ChatMessage as ApiMessage, HelpChatResponse } from "../lib/api";
import { cn } from "../lib/utils";

type Source = HelpChatResponse["sources"][number];
type ToolCall = HelpChatResponse["tool_calls"][number];

type UiMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Source[];
  toolCalls?: ToolCall[];
};

const initialMessage: UiMessage = {
  id: "welcome-local",
  role: "assistant",
  content: "Hi, I am your FitGenius help assistant. Ask me about your workout plan, diet, recovery, goals, or an uploaded note, and I will answer using your profile and trusted fitness guidance.",
};

export default function HelpChat({ embedded = false }: { embedded?: boolean }) {
  const [conversations, setConversations] = useState<ApiConversation[]>([]);
  const [activeId, setActiveId] = useState("");
  const [messages, setMessages] = useState<UiMessage[]>([initialMessage]);
  const [message, setMessage] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [expandedSourcesId, setExpandedSourcesId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    setIsLoadingConversations(true);
    try {
      const list = await api.chatConversations();
      if (list.length) {
        setConversations(list);
        await loadConversation(list[0].id);
      } else {
        await startNewConversation();
      }
    } finally {
      setIsLoadingConversations(false);
    }
  }

  async function loadConversation(id: string) {
    const conversation = await api.chatConversation(id);
    setActiveId(conversation.id);
    setMessages(toUiMessages(conversation.messages ?? []));
    setConversations((current) => {
      const others = current.filter((item) => item.id !== conversation.id);
      return [conversation, ...others].sort((a, b) => b.updated_at.localeCompare(a.updated_at));
    });
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isSending || !activeId) return;

    const optimisticUser: UiMessage = { id: `pending-${crypto.randomUUID()}`, role: "user", content: trimmed };
    setMessages((current) => [...current, optimisticUser]);
    setMessage("");
    setIsSending(true);

    try {
      const response = await api.sendChatMessage(activeId, { message: trimmed, document_text: documentText });
      if (response.conversation) {
        setConversations((current) => {
          const others = current.filter((item) => item.id !== response.conversation?.id);
          return [response.conversation!, ...others].sort((a, b) => b.updated_at.localeCompare(a.updated_at));
        });
      }
      await loadConversation(activeId);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "The AI endpoint failed.";
      setMessages((current) => [...current, { id: `error-${crypto.randomUUID()}`, role: "assistant", content: detail }]);
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

  async function startNewConversation() {
    const next = await api.createChatConversation({ title: "New Chat" });
    setConversations((current) => [next, ...current.filter((item) => item.id !== next.id)]);
    setActiveId(next.id);
    setMessages([initialMessage]);
    setSidebarOpen(false);
  }

  return (
    <div className={cn(
      "animate-page-enter flex min-w-0 overflow-hidden bg-card",
      embedded ? "h-full min-h-0" : "h-[calc(100vh-12rem)] min-h-[620px] rounded-xl border border-border shadow-lg"
    )}>
      {!embedded && sidebarOpen && (
        <aside className="w-64 shrink-0 border-r border-border bg-muted/20 flex flex-col transition-all">
          <div className="p-3 border-b border-border/40">
            <button
              type="button"
              onClick={startNewConversation}
              className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm"
            >
              <Plus className="h-4 w-4" />
              New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {isLoadingConversations && (
              <div className="p-4 text-center text-xs text-muted-foreground">
                Loading chats...
              </div>
            )}
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                onClick={() => setActiveId(conversation.id)}
                className={cn(
                  "relative w-full text-left p-3 rounded-lg hover:bg-muted transition-colors",
                  activeId === conversation.id && "bg-muted font-medium"
                )}
              >
                <div className="truncate text-sm">{conversation.title}</div>
              </button>
            ))}
          </div>
        </aside>
      )}

      <section className="min-w-0 flex-1 flex flex-col bg-card overflow-hidden relative">
        {!embedded && <div className="flex items-center justify-between p-4 border-b border-border/40 shrink-0 bg-card">
          <div className="flex items-center gap-4">
            <button 
              type="button" 
              onClick={() => setSidebarOpen(!sidebarOpen)} 
              className={cn("p-2 -ml-2 rounded-lg transition-colors", sidebarOpen ? "bg-muted text-foreground" : "hover:bg-muted text-muted-foreground")}
              title="Toggle History"
            >
              <History className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h2 className="text-base font-bold tracking-tight">AI Assistant</h2>
            </div>
          </div>
        </div>}

        <div className={cn("flex-1 overflow-y-auto space-y-5 bg-card", embedded ? "px-4 py-3" : "p-4 md:p-6")}>
          {messages.map((item) => (
            <div key={item.id} className={`flex gap-3 ${item.role === "user" ? "justify-end" : "justify-start"}`}>
              {item.role === "assistant" && <Avatar icon={<Bot className="h-5 w-5" />} />}
              <div className={cn("min-w-0 flex flex-col gap-1", embedded ? "max-w-[88%]" : "max-w-[85%] md:max-w-[75%]")}>
                {item.role === "user" && <div className="text-xs text-muted-foreground flex justify-end px-1">You</div>}
                <div className={`px-5 py-3.5 text-sm leading-relaxed shadow-sm ${item.role === "user" ? "whitespace-pre-wrap bg-primary text-primary-foreground rounded-2xl rounded-tr-sm" : "bg-muted/40 text-foreground rounded-2xl rounded-tl-sm border border-border/50"}`}>
                  {item.role === "assistant" ? <FormattedAssistantMessage content={item.content} /> : item.content}
                </div>
                {item.role === "assistant" && (item.sources?.length ?? 0) > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    <MetaButton active={expandedSourcesId === item.id} onClick={() => setExpandedSourcesId(expandedSourcesId === item.id ? null : item.id)} icon={<Globe2 className="h-3.5 w-3.5" />} label={`${item.sources?.length ?? 0} Sources`} />
                  </div>
                )}
                {item.role === "assistant" && expandedSourcesId === item.id && (
                  <div className="mt-2 space-y-2">
                    {(item.sources ?? []).map((source, index) => (
                      <div key={`${source.label}-${index}`} className="rounded-xl border border-border bg-background p-3 text-xs shadow-sm">
                        <div className="font-semibold text-foreground">{source.label}</div>
                        <div className="mt-1 text-muted-foreground">{[source.organization, source.subtopic, source.population, source.condition].filter(Boolean).join(" - ")}</div>
                        <p className="mt-2 line-clamp-3 text-muted-foreground">{source.text}</p>
                        {source.url && <a className="mt-2 block truncate text-primary hover:underline font-medium" href={source.url} target="_blank" rel="noreferrer">{source.url}</a>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {item.role === "user" && <Avatar icon={<UserRound className="h-5 w-5" />} user />}
            </div>
          ))}
          {isSending && (
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              Thinking...
            </div>
          )}
        </div>

        <div className={cn("shrink-0 border-t border-border/50 bg-card", embedded ? "p-3" : "p-4")}>
          <form onSubmit={handleSubmit} className="rounded-2xl border border-border bg-background p-3 shadow-sm transition-all focus-within:border-primary/40 focus-within:ring-2 focus-within:ring-primary/10">
            <div className="flex items-center gap-2">
              <input ref={fileInputRef} type="file" accept=".txt,.md,.csv,.json" className="hidden" onChange={(event) => handleFile(event.target.files?.[0])} />
              <button type="button" onClick={() => fileInputRef.current?.click()} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border/50 bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground transition-all" title="Attach file">
                <Plus className="h-4 w-4" />
              </button>
              
              <div className="flex-1 flex flex-col justify-center min-w-0">
                {documentName && (
                  <div className="flex items-center gap-1.5 px-2 py-0.5 text-xs text-primary font-medium">
                    <FileText className="h-3 w-3" />
                    <span className="truncate">{documentName}</span>
                    <button type="button" onClick={clearDocument} className="hover:text-destructive ml-1">
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                )}
                <input
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  className="w-full bg-transparent px-2 py-2 text-sm outline-none placeholder:text-muted-foreground"
                  placeholder={documentName ? "Ask about this file..." : "Ask about your workout, diet, recovery, or goals..."}
                />
              </div>
              <button type="submit" disabled={isSending || !message.trim()} className="inline-flex h-10 shrink-0 items-center gap-2 rounded-full bg-primary px-4 font-bold text-primary-foreground shadow-sm transition-all hover:bg-primary/90 hover:shadow disabled:cursor-not-allowed disabled:opacity-50">
                <SendHorizontal className="h-4 w-4" />
                <span className="hidden sm:inline">HELP</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
  );
}

function toUiMessages(messages: ApiMessage[]): UiMessage[] {
  if (!messages.length) return [initialMessage];
  return messages.map((message) => ({
    id: String(message.id),
    role: message.role,
    content: message.content,
    sources: message.sources ?? [],
    toolCalls: message.tool_calls ?? [],
  }));
}

function Avatar({ icon, user = false }: { icon: React.ReactNode; user?: boolean }) {
  return (
    <div className={cn("mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full", user ? "bg-accent/20 text-accent-foreground" : "bg-primary/10 text-primary")}>
      {icon}
    </div>
  );
}

function FormattedAssistantMessage({ content }: { content: string }) {
  const normalized = content
    .replace(/【[^】]+】/g, "")
    .replace(/\[(\d+)\]\([^)]*\)/g, "")
    .trim();
  const blocks = normalized.split(/\n{2,}/).filter(Boolean);

  return (
    <div className="space-y-3">
      {blocks.map((block, blockIndex) => {
        const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
        const bulletLines = lines.filter((line) => /^[-*]\s+/.test(line));

        if (bulletLines.length === lines.length) {
          return (
            <ul key={`block-${blockIndex}`} className="space-y-2 pl-4">
              {lines.map((line, lineIndex) => (
                <li key={`bullet-${blockIndex}-${lineIndex}`} className="list-disc pl-1">
                  {formatInline(line.replace(/^[-*]\s+/, ""))}
                </li>
              ))}
            </ul>
          );
        }

        if (lines.length > 1 && bulletLines.length > 0) {
          const intro = lines.filter((line) => !/^[-*]\s+/.test(line));
          return (
            <div key={`block-${blockIndex}`} className="space-y-2">
              {intro.map((line, lineIndex) => (
                <p key={`intro-${blockIndex}-${lineIndex}`}>{formatInline(line)}</p>
              ))}
              <ul className="space-y-2 pl-4">
                {bulletLines.map((line, lineIndex) => (
                  <li key={`mixed-bullet-${blockIndex}-${lineIndex}`} className="list-disc pl-1">
                    {formatInline(line.replace(/^[-*]\s+/, ""))}
                  </li>
                ))}
              </ul>
            </div>
          );
        }

        return (
          <p key={`block-${blockIndex}`} className="whitespace-pre-line">
            {formatInline(lines.join("\n"))}
          </p>
        );
      })}
    </div>
  );
}

function formatInline(text: string): ReactNode[] {
  const cleanText = text.replace(/\s{2,}/g, " ").trim();
  const parts = cleanText.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={`${part}-${index}`} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
    }
    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

function MetaButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button onClick={onClick} className={cn("flex items-center gap-2 px-3 py-1.5 rounded-full transition-all border group", active ? "bg-primary/10 border-primary/30 text-primary shadow-sm" : "bg-muted/30 border-border/40 text-muted-foreground hover:bg-muted/50")}>
      {icon}
      <span className="text-[11px] font-bold tracking-wide">{label}</span>
    </button>
  );
}
