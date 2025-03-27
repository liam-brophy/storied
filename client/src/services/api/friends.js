import apiClient from './axios';

// Matches GET /api/users/friends
export const fetchFriends = async () => {
    const response = await apiClient.get('/users/friends');
    return response.data;
};

// Matches GET /api/users/friends/requests
export const fetchFriendRequests = async () => {
    const response = await apiClient.get('/users/friends/requests');
    return response.data;
};

// Matches POST /api/users/friends/request
export const sendFriendRequest = async (friendId) => {
    const response = await apiClient.post('/users/friends/request', { friend_id: friendId });
    return response.data;
};

// Matches POST /api/users/friends/request/<int:request_id>/respond
export const respondToFriendRequest = async (requestId, status) => {
    if (status !== 'accepted' && status !== 'rejected') {
         // Client-side validation remains useful
         return Promise.reject(new Error("Invalid status provided. Must be 'accepted' or 'rejected'."));
    }
    const response = await apiClient.post(`/users/friends/request/${requestId}/respond`, { status });
    return response.data;
};

// Matches DELETE /api/users/friends/<int:friendship_id>
export const removeFriend = async (friendshipId) => {
    const response = await apiClient.delete(`/users/friends/${friendshipId}`);
    return response.data; // Assuming backend sends a confirmation message in JSON
    // If backend sends 204, response.data will be empty. Adjust if necessary.
};