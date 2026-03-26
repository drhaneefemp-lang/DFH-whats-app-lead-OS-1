import "@/App.css";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { ChatCircleDots, Lightning } from "@phosphor-icons/react";
import InboxPage from "./pages/InboxPage";
import AutomationPage from "./pages/AutomationPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <div className="flex h-screen">
          {/* Side Navigation */}
          <nav className="w-16 bg-gray-900 flex flex-col items-center py-4 gap-2">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `w-12 h-12 flex items-center justify-center rounded-sm transition-colors ${
                  isActive ? 'bg-green-500 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
              title="Inbox"
              data-testid="nav-inbox"
            >
              <ChatCircleDots size={24} weight="fill" />
            </NavLink>
            
            <NavLink
              to="/automation"
              className={({ isActive }) =>
                `w-12 h-12 flex items-center justify-center rounded-sm transition-colors ${
                  isActive ? 'bg-green-500 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`
              }
              title="Automation"
              data-testid="nav-automation"
            >
              <Lightning size={24} weight="fill" />
            </NavLink>
          </nav>

          {/* Main Content */}
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<InboxPage />} />
              <Route path="/automation" element={<AutomationPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
