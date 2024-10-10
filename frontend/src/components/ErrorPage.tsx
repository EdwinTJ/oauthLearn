// Create a new ErrorPage component
import { useLocation } from "react-router-dom";

const ErrorPage = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const error = searchParams.get("error");
  const message = searchParams.get("message");

  return (
    <div>
      <h1>Authentication Error</h1>
      <p>Error type: {error}</p>
      <p>Error message: {message}</p>
      <a href="/">Try again</a>
    </div>
  );
};

export default ErrorPage;
