import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import YouTubeAuth from "./components/YouTubeAuth";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<YouTubeAuth />} />
      </Routes>
    </Router>
  );
}

export default App;
