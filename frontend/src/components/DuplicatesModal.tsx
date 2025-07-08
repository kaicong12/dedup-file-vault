import React, { useState } from "react";

interface DuplicatesModalProps {
  isOpen: boolean;
  onClose: () => void;
  dedupData: any;
  onBatchDelete: (fileIds: string[]) => Promise<void>;
}

export const DuplicatesModal: React.FC<DuplicatesModalProps> = ({
  isOpen,
  onClose,
  dedupData,
  onBatchDelete,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleSelectFile = (fileId: string) => {
    setSelectedFiles((prev) =>
      prev.includes(fileId)
        ? prev.filter((id) => id !== fileId)
        : [...prev, fileId]
    );
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onBatchDelete(selectedFiles);
      setSelectedFiles([]);
      onClose();
    } catch (error) {
      console.error("Failed to delete files:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (!isOpen || !dedupData) return null;

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-3/4 max-h-[80%] overflow-y-auto">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Duplicate Files</h2>
        </div>
        <div className="p-4">
          {dedupData.duplicates.map((group: any, index: number) => (
            <div key={index} className="mb-6">
              <h3 className="font-medium text-gray-700">Original File</h3>
              <div className="p-2 border rounded mb-2">
                <p>{group.original_file.name}</p>
                <p className="text-sm text-gray-500">
                  {group.original_file.file_type}
                </p>
              </div>
              <h4 className="font-medium text-gray-700">Duplicates</h4>
              {group.duplicate_files.map((file: any) => (
                <div
                  key={file.id}
                  className="flex items-center p-2 border rounded mb-2"
                >
                  <input
                    type="checkbox"
                    checked={selectedFiles.includes(file.id)}
                    onChange={() => handleSelectFile(file.id)}
                    className="mr-2"
                  />
                  <div>
                    <p>{file.name}</p>
                    <p className="text-sm text-gray-500">{file.file_type}</p>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
        <div className="p-4 border-t flex justify-end space-x-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            Close
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting || selectedFiles.length === 0}
            className={`px-4 py-2 rounded text-white ${
              isDeleting || selectedFiles.length === 0
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-red-600 hover:bg-red-700"
            }`}
          >
            {isDeleting ? "Deleting..." : "Delete Selected"}
          </button>
        </div>
      </div>
    </div>
  );
};
