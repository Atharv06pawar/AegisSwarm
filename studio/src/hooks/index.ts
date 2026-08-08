import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

// 1. Dashboard Hook
export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const response = await apiClient.get("/dashboard");
      return response.data;
    },
  });
}

// 2. Plugins Hook
export function usePlugins() {
  const queryClient = useQueryClient();

  const pluginsQuery = useQuery({
    queryKey: ["plugins"],
    queryFn: async () => {
      const response = await apiClient.get("/plugins");
      return response.data;
    },
  });

  const discoverMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/plugins/discover");
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plugins"] });
    },
  });

  return {
    ...pluginsQuery,
    discover: discoverMutation.mutate,
    isDiscovering: discoverMutation.isPending,
  };
}

// 3. Corpus Hook
export function useCorpus() {
  return useQuery({
    queryKey: ["corpus"],
    queryFn: async () => {
      const response = await apiClient.get("/corpus/datasets");
      return response.data;
    },
  });
}

// 4. Coverage Hook
export function useCoverage() {
  return useQuery({
    queryKey: ["coverage"],
    queryFn: async () => {
      const response = await apiClient.get("/corpus/coverage");
      return response.data;
    },
  });
}

// 5. Reports Hook
export function useReports() {
  const queryClient = useQueryClient();

  const reportsQuery = useQuery({
    queryKey: ["reports"],
    queryFn: async () => {
      const response = await apiClient.get("/reports");
      return response.data;
    },
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/reports/generate");
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });

  return {
    ...reportsQuery,
    generateReports: generateMutation.mutate,
    isGenerating: generateMutation.isPending,
  };
}

// 6. Search Hook
export function useSearch(initialQuery?: any) {
  return useMutation({
    mutationFn: async (searchPayload: any) => {
      const response = await apiClient.post("/search", searchPayload);
      return response.data;
    },
  });
}

// 7. Ingestion Jobs Hook
export function useJobs() {
  const queryClient = useQueryClient();

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: async () => {
      const response = await apiClient.get("/jobs");
      return response.data;
    },
    refetchInterval: 3000,
  });

  const submitIngestMutation = useMutation({
    mutationFn: async (payload: { datasets: string[]; dry_run?: boolean; batch_size?: number }) => {
      const response = await apiClient.post("/ingest", payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  return {
    ...jobsQuery,
    submitIngest: submitIngestMutation.mutateAsync,
    isSubmitting: submitIngestMutation.isPending,
  };
}
