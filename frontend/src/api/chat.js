import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const chatApi = {
  sendMessage: (payload) => request(endpoints.chat.chat, { method: "POST", body: payload }),
  listSessions: () => request(endpoints.chat.sessions),
  getSession: (id) => request(endpoints.chat.session(id)),
  deleteSession: (id) => request(endpoints.chat.session(id), { method: "DELETE" }),
};
