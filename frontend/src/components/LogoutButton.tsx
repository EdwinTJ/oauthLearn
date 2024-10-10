const LogoutButton = () => {
  const handleLogout = async () => {
    try {
      // Call the logout endpoint
      await fetch("http://localhost:8000/logout", {
        method: "GET",
        credentials: "include", // Include credentials for the session
      });

      // Redirect or update state after logout if needed
      window.location.href = "/"; // Redirect to home or login page
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return <button onClick={handleLogout}>Logout</button>;
};

export default LogoutButton;
