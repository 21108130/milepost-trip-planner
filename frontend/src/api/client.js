import axios from 'axios';

// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const API_BASE_URL = 'https://mairajaved.pythonanywhere.com/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

/**
 * Extracts a human-readable error message from an Axios error,
 * matching the {"error": {"message", "detail"}} shape returned by the API.
 */
export function extractErrorMessage(error) {
  const data = error?.response?.data;

  if (data?.error) {
    const { message, detail } = data.error;

    if (typeof detail === 'string') return detail;

    if (detail && typeof detail === 'object') {
      const firstKey = Object.keys(detail)[0];
      const firstVal = detail[firstKey];

      if (Array.isArray(firstVal)) {
        return `${firstKey}: ${firstVal[0]}`;
      }
    }

    return message || 'Something went wrong.';
  }

  if (error?.message === 'Network Error') {
    return 'Could not reach the server. Please check your connection and try again.';
  }

  return error?.message || 'An unexpected error occurred.';
}
