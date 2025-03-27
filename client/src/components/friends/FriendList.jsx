import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const FriendList = () => {
    const { user } = useAuth();
    const [friends, setFriends] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchFriends = async () => {
            setLoading(true);
            try {
                const response = await axios.get('/api/users/friends');
                setFriends(response.data);
            } catch (error) {
                setError(error.response?.data?.error || 'Failed to fetch friends.');
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchFriends();
        }
    }, [user]);

    if (loading) {
        return <p>Loading friends...</p>;
    }

    if (error) {
        return <p style={{ color: 'red' }}>Error: {error}</p>;
    }

    if (friends.length === 0) {
        return <p>You have no friends yet.</p>;
    }

    return (
        <ul>
            {friends.map(friend => (
                <li key={friend.id}>
                    {friend.username} ({friend.email})
                </li>
            ))}
        </ul>
    );
};

export default FriendList;