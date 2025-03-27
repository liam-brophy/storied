import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const FriendRequests = () => {
    const { user } = useAuth();
    const [sentRequests, setSentRequests] = useState([]);
    const [receivedRequests, setReceivedRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchFriendRequests = async () => {
            setLoading(true);
            try {
                const response = await axios.get('/api/users/friends/requests');
                setSentRequests(response.data.sent);
                setReceivedRequests(response.data.received);
            } catch (error) {
                setError(error.response?.data?.error || 'Failed to fetch friend requests.');
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchFriendRequests();
        }
    }, [user]);


    // then
    const handleAcceptRequest = async (requestId) => {
        try {
            await axios.post(`/api/users/friends/request/${requestId}/respond`, { status: 'accepted' });
            // Refresh friend requests after accepting
            // fetchFriendRequests();
        } catch (error) {
            console.error("Error accepting friend request:", error);
            setError(error.response?.data?.error || 'Failed to accept friend request.');
        }
    };

    const handleRejectRequest = async (requestId) => {
        try {
            await axios.post(`/api/users/friends/request/${requestId}/respond`, { status: 'rejected' });
            // Refresh friend requests after rejecting
            fetchFriendRequests(); // Re-run fetch
        } catch (error) {
            console.error("Error rejecting friend request:", error);
            setError(error.response?.data?.error || 'Failed to reject friend request.');
        }
    };


    if (loading) {
        return <p>Loading friend requests...</p>;
    }

    if (error) {
        return <p style={{ color: 'red' }}>Error: {error}</p>;
    }

    return (
        <div>
            <h3>Sent Requests</h3>
            {sentRequests.length === 0 ? (
                <p>No sent friend requests.</p>
            ) : (
                <ul>
                    {sentRequests.map(request => (
                        <li key={request.id}>
                            To: {request.friend_username} ({request.friend_id})
                        </li>
                    ))}
                </ul>
            )}

            <h3>Received Requests</h3>
            {receivedRequests.length === 0 ? (
                <p>No received friend requests.</p>
            ) : (
                <ul>
                    {receivedRequests.map(request => (
                        <li key={request.id}>
                            From: {request.sender_username} ({request.sender_id})
                            <button onClick={() => handleAcceptRequest(request.id)}>Accept</button>
                            <button onClick={() => handleRejectRequest(request.id)}>Reject</button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default FriendRequests;