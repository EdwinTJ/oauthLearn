export const clearStoredTokens = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("userData");
};

// Call this function when you detect that re-authentication is needed
// For example, you could call it when you receive a 403 error
export const handleInsufficientPermissions = () => {
  clearStoredTokens();
  // Redirect to login page or show a message asking the user to log in again
  window.location.href = "/login";
};
