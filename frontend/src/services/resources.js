import api from "./api";

export const authService = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
};

export const profileService = {
  get: () => api.get("/profile"),
  update: (data) => api.put("/profile", data),
};

export const skillsService = {
  list: () => api.get("/skills"),
  get: (id) => api.get(`/skills/${id}`),
  myGaps: () => api.get("/skills/gap-analysis/me"),
  mySkills: () => api.get("/profile/skills"),
  updateMySkills: (skills) => api.put("/profile/skills", { skills }),
};

export const goalService = {
  create: (text) => api.post("/goals", { text }),
  list: () => api.get("/goals"),
};

export const recommendationService = {
  generate: () => api.post("/recommendations/generate"),
  list: () => api.get("/recommendations"),
  feedback: (id, feedback) => api.post(`/recommendations/${id}/feedback`, { feedback }),
};

export const learningPathService = {
  generate: () => api.post("/learning-path/generate"),
  get: () => api.get("/learning-path"),
  updateItem: (itemId, data) => api.put(`/learning-path/items/${itemId}`, data),
};

export const progressService = {
  list: () => api.get("/progress"),
  create: (data) => api.post("/progress", data),
  update: (id, data) => api.put(`/progress/${id}`, data),
};

export const chatService = {
  send: (message, sessionId) => api.post("/chat", { message, session_id: sessionId }),
  history: () => api.get("/chat/history"),
};

export const assessmentService = {
  list: () => api.get("/assessments"),
  submit: (id, answers) => api.post(`/assessments/${id}/submit`, { answers }),
};
