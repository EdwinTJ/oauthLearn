import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { fetchVideos, loginWithGoogle, logout } from "../api";

const YouTubeAuth = () => {
  const [userData, setUserData] = useState(null);
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const name = params.get("name");
    const email = params.get("email");
    const channel_id = params.get("channel_id");
    const access_token = params.get("access_token");

    if (name && email && channel_id && access_token) {
      const userDataObj = { name, email, channel_id };
      setUserData(userDataObj);
      localStorage.setItem("userData", JSON.stringify(userDataObj));
      localStorage.setItem("accessToken", access_token);

      // Clear URL parameters
      navigate("/", { replace: true });

      // Fetch videos after authentication
      fetchUserVideos();
    } else {
      const storedUserData = localStorage.getItem("userData");
      if (storedUserData) {
        setUserData(JSON.parse(storedUserData));
        fetchUserVideos();
      }
    }
  }, [location, navigate]);

  const fetchUserVideos = async () => {
    try {
      const fetchedVideos = await fetchVideos();
      setVideos(fetchedVideos);
    } catch (error) {
      setError("Failed to fetch videos. Please log in again.");
      handleLogout();
    }
  };

  const handleLogin = () => {
    loginWithGoogle();
  };

  const handleLogout = async () => {
    try {
      await logout();
      setUserData(null);
      setVideos([]);
      navigate("/");
    } catch (error) {
      setError("Failed to log out. Please try again.");
    }
  };

  return (
    <div>
      <h1>YouTube Authentication</h1>
      {!userData ? (
        <button onClick={handleLogin}>Login with Google</button>
      ) : (
        <div>
          <h2>Welcome, {userData.name}</h2>
          <p>Email: {userData.email}</p>
          <p>Channel ID: {userData.channel_id}</p>
          <h3>Your Videos:</h3>
          <ul>
            {videos.map((video) => (
              <li key={video.id.videoId}>
                <a
                  href={`https://www.youtube.com/watch?v=${video.id.videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {video.snippet.title}
                </a>
              </li>
            ))}
          </ul>
          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default YouTubeAuth;
