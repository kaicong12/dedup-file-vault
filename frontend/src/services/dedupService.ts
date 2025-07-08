import axios from "axios";
import { API_URL } from "./constant";

export const dedupService = {
  getLatestDedup: async () => {
    const response = await axios.get(`${API_URL}/dedup/latest`);
    return response.data;
  },
};
