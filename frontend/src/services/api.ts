import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const problemApi = {
  getHistory: () => api.get('/history'),
  initProblem: (problemId: string) => api.post('/init', { problemId }),
  saveCode: (data: { problemId: string, version: string, difficulty: string, content: string }) => 
    api.post('/save', data),
  runTest: (data: { code: string, problemId: string, difficulty: string }) => 
    api.post('/run', data),
  resumeSession: () => api.get('/resume'),
  getProblemVersion: (difficulty: string, problemId: string, version: string) => 
    api.get(`/problem/${difficulty}/${problemId}/${version}`),
  cleanCode: (data: { code: string, problemId: string, difficulty: string }) => 
    api.post('/clean', data),
};

export default api;
