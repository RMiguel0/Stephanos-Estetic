import { api } from './client'

export const DonationsAPI = {
  list: () => api.get('/donations/'),
}
