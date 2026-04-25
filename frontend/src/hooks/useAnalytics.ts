import { useCallback } from 'react'

interface AnalyticsEvent {
  event_type: string
  event_data?: Record<string, unknown>
  page_url?: string
  session_id?: string
}

export function useAnalytics() {
  const trackEvent = useCallback(async (event: AnalyticsEvent) => {
    try {
      await fetch('/api/v1/analytics/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          ...event,
          page_url: event.page_url || window.location.pathname,
        }),
      })
    } catch (err) {
      // Silently fail - analytics should not break the app
      console.debug('Analytics track failed', err)
    }
  }, [])

  const trackPageView = useCallback(
    (url?: string) => {
      trackEvent({
        event_type: 'page_view',
        page_url: url || window.location.pathname,
      })
    },
    [trackEvent]
  )

  const trackAnalysisRun = useCallback(
    (analysisType: string, datasetId: string, success: boolean) => {
      trackEvent({
        event_type: 'analysis_run',
        event_data: {
          analysis_type: analysisType,
          dataset_id: datasetId,
          success,
        },
      })
    },
    [trackEvent]
  )

  const trackExport = useCallback(
    (format: string, rowCount: number) => {
      trackEvent({
        event_type: 'export_data',
        event_data: {
          format,
          row_count: rowCount,
        },
      })
    },
    [trackEvent]
  )

  const trackSearch = useCallback(
    (query: string) => {
      trackEvent({
        event_type: 'search_query',
        event_data: { query },
      })
    },
    [trackEvent]
  )

  const trackError = useCallback(
    (message: string, context?: Record<string, unknown>) => {
      trackEvent({
        event_type: 'error_encountered',
        event_data: {
          message,
          ...context,
        },
      })
    },
    [trackEvent]
  )

  return {
    trackEvent,
    trackPageView,
    trackAnalysisRun,
    trackExport,
    trackSearch,
    trackError,
  }
}
