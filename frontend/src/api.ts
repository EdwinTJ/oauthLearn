import axios from "axios";

const API_URL = "http://localhost:8000";

export const loginWithGoogle = async () => {
  try {
    window.location.href = `${API_URL}/auth/login`;
  } catch (error) {
    console.error("Error logging in:", error);
    throw error;
  }
};

export const refreshToken = async () => {
  try {
    const oldToken = localStorage.getItem("accessToken");
    const response = await axios.post(
      `${API_URL}/api/refresh_token`,
      {},
      {
        headers: { Authorization: `Bearer ${oldToken}` },
      }
    );
    const newToken = response.data.access_token;
    localStorage.setItem("accessToken", newToken);
    return newToken;
  } catch (error) {
    console.error("Error refreshing token:", error);
    throw error;
  }
};

export const fetchVideos = async () => {
  try {
    const token = localStorage.getItem("accessToken");
    const response = await axios.get(`${API_URL}/api/videos`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data.videos;
  } catch (error) {
    if (error.response && error.response.status === 401) {
      // Token might have expired, attempt to refresh
      try {
        await refreshToken();
        // Retry the request with the new token
        return await fetchVideos();
      } catch (refreshError) {
        console.error("Error refreshing token:", refreshError);
        throw refreshError;
      }
    }
    console.error("Error fetching videos:", error);
    throw error;
  }
};

export const logout = async () => {
  try {
    const token = localStorage.getItem("accessToken");
    await axios.get(`${API_URL}/logout`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    localStorage.removeItem("accessToken");
    localStorage.removeItem("userData");
  } catch (error) {
    console.error("Error logging out:", error);
    throw error;
  }
};
