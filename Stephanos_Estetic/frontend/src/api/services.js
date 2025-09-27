import { api } from './client'

export const ServicesAPI = {
  list: () => api.get('/services/'),
}
