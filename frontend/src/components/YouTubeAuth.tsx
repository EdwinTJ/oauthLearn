import React, { useEffect, useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { fetchVideos, loginWithGoogle, logout } from "../api";
import { Button } from "@/components/ui/button";

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
      console.error("Error fetching videos:", error);
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
      console.error("Error logging out:", error);
      setError("Failed to log out. Please try again.");
    }
  };

  const renderVideoItem = (video) => {
    if (!video || !video.title || !video.videoId) {
      console.error("Invalid video object:", video);
      return null;
    }

    return (
      <li key={video.videoId} className="mb-4">
        <a
          href={`https://www.youtube.com/watch?v=${video.videoId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          {video.title}
        </a>
        <img
          src={video.thumbnail}
          alt={video.title}
          className="max-w-[200px] mt-2 mb-2"
        />
        <Link to={`/summary/${video.videoId}`} state={{ title: video.title }}>
          <Button className="bg-green-500 text-white mt-2">SummaryAI</Button>
        </Link>
      </li>
    );
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">YouTube Authentication</h1>
      {!userData ? (
        <Button onClick={handleLogin} className="bg-red-600 text-white">
          Login with Google
        </Button>
      ) : (
        <div>
          <h2 className="text-2xl font-semibold mb-4">
            Welcome, {userData.name}
          </h2>
          <p className="mb-2">Email: {userData.email}</p>
          <p className="mb-4">Channel ID: {userData.channel_id}</p>
          <h3 className="text-xl font-semibold mb-4">Your Videos:</h3>
          {videos && videos.length > 0 ? (
            <ul className="list-none p-0">{videos.map(renderVideoItem)}</ul>
          ) : (
            <p>No videos found.</p>
          )}
          <Button
            onClick={handleLogout}
            className="bg-gray-500 text-white mt-4"
          >
            Logout
          </Button>
        </div>
      )}
      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
};

export default YouTubeAuth;
