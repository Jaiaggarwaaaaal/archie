// API client module
import { validateRequest } from './utils.js';

class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async fetchUser(userId) {
    const request = { userId };
    validateRequest(request);
    return fetch(`${this.baseUrl}/users/${userId}`);
  }

  async createPayment(amount, cardToken) {
    return fetch(`${this.baseUrl}/payments`, {
      method: 'POST',
      body: JSON.stringify({ amount, cardToken })
    });
  }
}

export { ApiClient };
