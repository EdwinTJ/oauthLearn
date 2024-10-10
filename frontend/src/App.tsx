import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import YouTubeAuth from "./components/YouTubeAuth";
import SummaryAIPage from "./components/SummaryAIPage";
import ErrorPage from "./components/ErrorPage";
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<YouTubeAuth />} />
        <Route path="/summary/:videoId" element={<SummaryAIPage />} />
        <Route path="/error" element={<ErrorPage />} />
      </Routes>
    </Router>
  );
}

export default App;
