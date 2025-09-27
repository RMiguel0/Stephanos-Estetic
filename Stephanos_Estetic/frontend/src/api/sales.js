import { api } from './client'

export const SalesAPI = {
  list: () => api.get('/sales/'),
}
