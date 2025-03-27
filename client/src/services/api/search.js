import apiClient from './axios';

// Matches GET /api/users/search?q=<query>
export const searchUsers = async (query) => {
    if (!query || query.length < 3) {
        return Promise.resolve([]); // Or reject, as before
    }
    // Axios handles query parameters easily with the 'params' option
    const response = await apiClient.get('/users/search', {
        params: { q: query }
    });
    return response.data;
};