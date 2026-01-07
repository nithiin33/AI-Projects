import { useState } from "react";
import "./ChatWidget.css";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([
    { role: "bot", text: "Hi! Ask me anything about your policy or claims." },
  ]);
  const [text, setText] = useState("");

  async function send() {
    const msg = text.trim();
    if (!msg) return;

    setMsgs((m) => [...m, { role: "user", text: msg }]);
    setText("");

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });

    const data = await res.json();
    setMsgs((m) => [...m, { role: "bot", text: data.answer }]);
  }

  return (
    <>
      <button className="chat-fab" onClick={() => setOpen(!open)}>
        {open ? "×" : "Chat"}
      </button>

      {open && (
        <div className="chat-modal">
          <div className="chat-header">Insurance Help</div>

          <div className="chat-body">
            {msgs.map((m, i) => (
              <div key={i} className={`bubble ${m.role}`}>
                {m.text}
              </div>
            ))}
          </div>

          <div className="chat-input">
            <input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type your question..."
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button onClick={send}>Send</button>
          </div>
        </div>
      )}
    </>
  );
}