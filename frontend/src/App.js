import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import InboxPage from "./pages/InboxPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<InboxPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
