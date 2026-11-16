import React, { useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Bot,
  X,
  Send,
  Paperclip,
  Trash2,
  FileText,
  Sparkles,
  Maximize2,
  Minimize2,
  Loader2,
} from 'lucide-react';
import {
  streamChat,
  uploadRagDocument,
  getRagDocuments,
  getChatHistory,
  formatApiError,
} from '../api/api';
import { useAuth } from '../context/AuthContext';
import { usePrediction } from '../context/PredictionContext';

const WELCOME_MSG = {
  role: 'assistant',
  content:
    "Hi! I'm your **Carbon AI Advisor**.\n\n" +
    'Ask me about:\n' +
    '- Your latest **prediction** or **sector trends**\n' +
    '- **What-if scenarios** (powered by XGBoost)\n' +
    '- **Model accuracy & SHAP drivers**\n' +
    '- **Uploaded ESG / policy documents** (click 📎)',
};

const DatasetChatbot = () => {
  const { user, token } = useAuth();
  const { currentPrediction } = usePrediction();

  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState([WELCOME_MSG]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [docs, setDocs] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const sessionId = useMemo(() => {
    if (user?.id) return `carbon-user-${user.id}`;
    let guestId = localStorage.getItem('carbon_guest_session');
    if (!guestId) {
      guestId = `carbon-guest-${Date.now()}`;
      localStorage.setItem('carbon_guest_session', guestId);
    }
    return guestId;
  }, [user]);

  useEffect(() => {
    if (!isOpen) return;
    getChatHistory(sessionId, token)
      .then((data) => {
        const saved = (data?.messages || []).map((m) => ({
          role: m.role === 'model' ? 'assistant' : 'user',
          content: m.text,
        }));
        setMessages(saved.length > 0 ? saved : [WELCOME_MSG]);
      })
      .catch(() => {});

    getRagDocuments(token)
      .then((data) => setDocs(data?.documents || []))
      .catch(() => {});
  }, [isOpen, sessionId, token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, statusText]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    setIsUploading(true);
    try {
      const res = await uploadRagDocument(file, token);
      setDocs((prev) => Array.from(new Set([...prev, res.filename])));
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Indexed **${res.filename}** (${res.chunks_indexed} chunks). You can now ask questions about it!`,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Upload failed: ${formatApiError(err)}` },
      ]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async () => {
    const userMessage = input.trim();
    if (!userMessage || isLoading) return;

    setInput('');
    setIsLoading(true);
    setStatusText('');

    setMessages((prev) => [
      ...prev,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: '' },
    ]);

    try {
      await streamChat({
        sessionId,
        message: userMessage,
        currentPrediction,
        token,
        onStatus: (s) => setStatusText(s),
        onToken: (tok) => {
          setStatusText('');
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            updated[updated.length - 1] = {
              ...last,
              content: (last?.content || '') + tok,
            };
            return updated;
          });
        },
        onError: (errMsg) => {
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: 'assistant',
              content: `Error: ${errMsg}`,
            };
            return updated;
          });
        },
        onDone: () => setStatusText(''),
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: `Error: ${formatApiError(err, 'Unable to reach Carbon AI Advisor.')}`,
        };
        return updated;
      });
    } finally {
      setIsLoading(false);
      setStatusText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-5 py-3.5 rounded-full bg-neon-green text-deep-blue font-bold shadow-[0_0_25px_rgba(57,255,20,0.4)] hover:bg-green-400 transition-all hover:scale-105"
      >
        <Bot className="w-5 h-5" />
        <span>Carbon AI Advisor</span>
      </button>
    );
  }

  return (
    <div
      className={`fixed bottom-5 right-5 z-50 flex flex-col rounded-2xl bg-[#0b1121]/95 backdrop-blur-xl border border-white/15 shadow-[0_20px_60px_rgba(0,0,0,0.6)] transition-all ${
        isExpanded
          ? 'w-[92vw] sm:w-[640px] h-[80vh]'
          : 'w-[92vw] sm:w-[410px] h-[560px]'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/5 rounded-t-2xl">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-neon-green/15 border border-neon-green/40 flex items-center justify-center text-neon-green">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white leading-tight">
              Carbon AI Advisor
            </h3>
            <span className="text-[11px] text-neon-green flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              {currentPrediction
                ? 'Linked to active prediction'
                : 'Analytics · RAG · What-If'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setMessages([WELCOME_MSG])}
            title="Clear view"
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setIsExpanded((v) => !v)}
            title={isExpanded ? 'Minimize' : 'Expand'}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10"
          >
            {isExpanded ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            title="Close"
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Active Prediction + Indexed Docs strip */}
      {(currentPrediction || docs.length > 0) && (
        <div className="px-4 py-2 border-b border-white/10 bg-black/30 flex flex-wrap items-center gap-2 text-xs">
          {currentPrediction?.predicted_co2 !== undefined && (
            <span className="px-2 py-0.5 rounded-full bg-neon-green/15 text-neon-green border border-neon-green/30 font-medium">
              Active: {Number(currentPrediction.predicted_co2).toFixed(2)} tCO₂e
              {currentPrediction.sector ? ` (${currentPrediction.sector})` : ''}
            </span>
          )}
          {docs.map((doc) => (
            <span
              key={doc}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30"
            >
              <FileText className="w-3 h-3" />
              {doc}
            </span>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-neon-green text-deep-blue font-medium rounded-br-sm'
                  : 'bg-white/10 text-gray-100 border border-white/10 rounded-bl-sm prose prose-invert prose-sm max-w-none'
              }`}
            >
              {msg.role === 'assistant' ? (
                <ReactMarkdown>{msg.content || '...'}</ReactMarkdown>
              ) : (
                <span className="whitespace-pre-wrap">{msg.content}</span>
              )}
            </div>
          </div>
        ))}

        {statusText && (
          <div className="flex items-center gap-2 text-xs text-neon-green/90 pl-1">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>{statusText}</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-white/10 bg-white/5 rounded-b-2xl flex items-end gap-2">
        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept=".pdf,.txt,.csv,.md"
          onChange={handleFileUpload}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          title="Upload document (PDF, TXT, CSV, MD) for RAG"
          className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-gray-300 hover:text-neon-green transition-colors disabled:opacity-50"
        >
          {isUploading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Paperclip className="w-4 h-4" />
          )}
        </button>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about predictions, sectors, SHAP, or docs..."
          disabled={isLoading}
          rows={1}
          className="flex-1 resize-none bg-black/40 border border-white/15 rounded-xl px-3 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:border-neon-green"
        />

        <button
          type="button"
          onClick={handleSendMessage}
          disabled={isLoading || !input.trim()}
          className="p-2.5 rounded-xl bg-neon-green text-deep-blue hover:bg-green-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default DatasetChatbot;