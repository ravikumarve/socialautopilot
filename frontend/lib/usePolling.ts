'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface UsePollingResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Custom hook that polls a fetch function at a specified interval.
 *
 * - Shows loading state only on the initial fetch (not on subsequent polls).
 * - Captures errors gracefully without crashing the UI.
 * - Returns a `refetch` function for manual refresh (e.g. after a mutation).
 * - Cleans up the interval on unmount.
 * - Uses a mounted ref to prevent state updates on unmounted components.
 */
function usePolling<T>(
  fetchFn: () => Promise<T>,
  intervalMs: number = 5000
): UsePollingResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const mountedRef = useRef<boolean>(true);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const fetchFnRef = useRef(fetchFn);

  // Keep the fetchFn ref current so the interval always calls the latest closure
  useEffect(() => {
    fetchFnRef.current = fetchFn;
  }, [fetchFn]);

  const executeFetch = useCallback(async (isInitialFetch: boolean) => {
    if (isInitialFetch) {
      setLoading(true);
    }
    setError(null);

    try {
      const result = await fetchFnRef.current();
      if (mountedRef.current) {
        setData(result);
        setError(null);
      }
    } catch (err) {
      if (mountedRef.current) {
        const message =
          err instanceof Error ? err.message : 'An unexpected error occurred';
        setError(message);
        console.error('usePolling fetch error:', err);
      }
    } finally {
      if (mountedRef.current && isInitialFetch) {
        setLoading(false);
      }
    }
  }, []);

  // Manual refetch — always shows loading briefly to give user feedback
  const refetch = useCallback(() => {
    executeFetch(true);
  }, [executeFetch]);

  // Initial fetch + interval setup
  useEffect(() => {
    mountedRef.current = true;

    // First fetch (initial load)
    executeFetch(true);

    // Set up polling interval (subsequent fetches are NOT initial)
    intervalRef.current = setInterval(() => {
      executeFetch(false);
    }, intervalMs);

    return () => {
      mountedRef.current = false;
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [intervalMs, executeFetch]);

  return { data, loading, error, refetch };
}

export default usePolling;
