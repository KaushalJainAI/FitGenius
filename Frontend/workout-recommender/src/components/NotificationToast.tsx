import { useEffect, useState } from 'react';

export function NotificationToast() {
  const [message, setMessage] = useState<{ title: string; body: string } | null>(null);

  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<{ title: string; body: string }>).detail;
      setMessage(detail);
      window.setTimeout(() => setMessage(null), 5000);
    };

    window.addEventListener('fitgenius-notification', handler);
    return () => window.removeEventListener('fitgenius-notification', handler);
  }, []);

  if (!message) return null;

  return (
    <div className="fixed bottom-5 right-5 z-[200] max-w-sm rounded-lg border border-border bg-card p-4 text-foreground shadow-elegant">
      <p className="font-semibold">{message.title}</p>
      <p className="mt-1 text-sm text-muted-foreground">{message.body}</p>
    </div>
  );
}
