import axios from 'axios';
import API_BASE_URL from '../config/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/tarot`,
  headers: {
    'Content-Type': 'application/json',
  },
});

const tarotApi = {
  getCards() {
    return apiClient.get('/cards/');
  },
  getCard(id) {
    return apiClient.get(`/cards/${id}/`);
  },
  getSpreads() {
    return apiClient.get('/spreads/');
  },
  getDaily(date) {
    return apiClient.get('/daily/', { params: date ? { date } : {} });
  },
  divine(question, cards, spreadType, mode = 'ritual') {
    return apiClient.post('/divine/', {
      question,
      cards,
      spread_type: spreadType,
      mode,
    });
  },
};

export default tarotApi;
