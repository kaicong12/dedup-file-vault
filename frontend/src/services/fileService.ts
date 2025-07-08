import axios from "axios";
import { File as FileType } from "../types/file";
import { PaginatedResponse, GetFilesParams } from "../types/api";
import { API_URL } from "./constant";

export const fileService = {
  async uploadFile(file: File): Promise<FileType> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(`${API_URL}/files/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async getFiles(
    params?: GetFilesParams
  ): Promise<PaginatedResponse<FileType>> {
    const queryParams = new URLSearchParams();

    if (params?.search) queryParams.append("search", params.search);
    if (params?.sortBy) queryParams.append("sortBy", params.sortBy);
    if (params?.page) queryParams.append("page", String(params.page));
    if (params?.page_size)
      queryParams.append("page_size", String(params.page_size));
    if (params?.fileType) queryParams.append("fileType", params.fileType);

    const url = `${API_URL}/files/${
      queryParams.toString() ? `?${queryParams.toString()}` : ""
    }`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("Failed to fetch files");
    }

    return response.json();
  },

  async deleteFile(id: string): Promise<void> {
    await axios.delete(`${API_URL}/files/${id}/`);
  },

  async batchDeleteFiles(fileIds: string[]): Promise<void> {
    try {
      await axios.post(`${API_URL}/files/batch_delete/`, {
        file_ids: fileIds,
      });
    } catch (error) {
      console.error("Batch delete error:", error);
      throw new Error("Failed to delete files");
    }
  },

  async downloadFile(fileUrl: string, filename: string): Promise<void> {
    try {
      const response = await axios.get(fileUrl, {
        responseType: "blob",
      });

      // Create a blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download error:", error);
      throw new Error("Failed to download file");
    }
  },
};
