const API_BASE = "http://127.0.0.1:8000/api/";

const api = {
  getDocuments: async () => {
    const res = await fetch(`${API_BASE}documents/`);
    if (!res.ok) throw new Error("Failed to fetch documents");
    return res.json();
  },
  uploadDocument: async (formData) => {
    const res = await fetch(`${API_BASE}documents/upload/`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to upload document");
    return res.json();
  },
  deleteDocument: async (id) => {
    const res = await fetch(`${API_BASE}documents/${id}/`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete document");
  },
  getChatSessions: async () => {
    const res = await fetch(`${API_BASE}chat/sessions/`);
    if (!res.ok) throw new Error("Failed to fetch chat sessions");
    return res.json();
  },
  getChatMessages: async (sessionId) => {
    const res = await fetch(`${API_BASE}chat/sessions/${sessionId}/messages/`);
    if (!res.ok) throw new Error("Failed to fetch chat messages");
    return res.json();
  },
  chat: async (message) => {
    const res = await fetch(`${API_BASE}chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message }),
    });
    if (!res.ok) throw new Error("Failed to send chat message");
    return res.json();
  },
  healthCheck: async () => {
    const res = await fetch(`${API_BASE}health/`);
    if (!res.ok) throw new Error("Failed to check health");
    return res.json();
  },
};

export default api;
