"use client";

import { ToastHost } from "@/components/shared/Toast";
import { QUERY_CLIENT_META, defaultOptions } from "@/lib/queryClient";
import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import React, { useState } from "react";

/**
 * สร้าง client ต่อครั้งเมื่อ mount เพื่อกัน state จาก request เก่ารั่วเมื่อ SSR (แนะนำจาก TanStack)
 * v5 ไม่รองรับ queries.defaultOptions.onError — เลื่อนเข้าหา QueryCache/MutationCache
 */
function makeBrowserQueryClient(): QueryClient {
  return new QueryClient({
    queryCache: new QueryCache({
      onError: (error, query) => {
        if (query.meta?.[QUERY_CLIENT_META.SKIP_GLOBAL_ERROR_TOAST]) return;
        defaultOptions.onError(error);
      },
    }),
    mutationCache: new MutationCache({
      onError: (error, _vars, _ctx, mutation) => {
        if (mutation.meta?.[QUERY_CLIENT_META.SKIP_GLOBAL_ERROR_TOAST]) return;
        defaultOptions.onError(error);
      },
    }),
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        retry: 1,
      },
    },
  });
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => makeBrowserQueryClient());
  return (
    <QueryClientProvider client={client}>
      {children}
      <ToastHost />
    </QueryClientProvider>
  );
}
