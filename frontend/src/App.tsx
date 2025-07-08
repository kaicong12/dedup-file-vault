import { useState, useEffect } from "react";
import { FileUpload } from "./components/FileUpload";
import { FileList } from "./components/FileList";
import { DuplicatesModal } from "./components/DuplicatesModal";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { dedupService } from "./services/dedupService";
import { fileService } from "./services/fileService";

const POLLING_INTERVAL = 1000; // 1 second

function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPolling, setIsPolling] = useState(false);

  const handleUploadSuccess = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const queryClient = useQueryClient();

  // Fetch deduplication data using React Query
  const { data: dedupData, isLoading } = useQuery({
    queryKey: ["dedupData"],
    queryFn: dedupService.getLatestDedup,
    refetchInterval: isPolling ? POLLING_INTERVAL : false,
  });

  useEffect(() => {
    if (
      dedupData &&
      (dedupData.status === "completed" || dedupData.status === "failed")
    ) {
      setIsPolling(false); // Stop polling when the job is completed or failed
    }
  }, [dedupData]);

  // Mutation to handle batch delete
  const batchDeleteMutation = useMutation({
    mutationFn: fileService.batchDeleteFiles,
    onSuccess: () => {
      // Refetch deduplication data after batch delete
      setIsPolling(true);
      queryClient.invalidateQueries({ queryKey: ["dedupData"] });
      queryClient.invalidateQueries({ queryKey: ["files"] });
    },
  });

  const handleBatchDelete = async (fileIds: string[]) => {
    try {
      await batchDeleteMutation.mutateAsync(fileIds);
    } catch (error) {
      console.error("Failed to delete files:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Abnormal Security - File Hub
          </h1>
          <p className="mt-1 text-sm text-gray-500">File management system</p>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="space-y-6">
            <div className="bg-white shadow sm:rounded-lg">
              <FileUpload
                onUploadSuccess={handleUploadSuccess}
                setIsPolling={setIsPolling}
              />
            </div>
            <div className="bg-white shadow sm:rounded-lg">
              <FileList key={refreshKey} setIsPolling={setIsPolling} />
            </div>
            <div className="bg-white shadow sm:rounded-lg p-4">
              <button
                onClick={() => setIsModalOpen(true)}
                disabled={
                  isLoading || !dedupData || !dedupData.duplicates.length
                }
                className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                  isLoading || !dedupData || !dedupData.duplicates.length
                    ? "bg-gray-300 cursor-not-allowed"
                    : "bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                }`}
              >
                {isLoading
                  ? "Checking for duplicate files..."
                  : dedupData?.duplicates?.length
                  ? "View Duplicate Files"
                  : "No duplicates found"}
              </button>
            </div>
          </div>
        </div>
      </main>

      <DuplicatesModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        dedupData={dedupData}
        onBatchDelete={handleBatchDelete}
      />

      <footer className="bg-white shadow mt-8">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2024 File Hub. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
