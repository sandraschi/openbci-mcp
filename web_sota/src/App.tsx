import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { Apps } from "@/pages/apps";
import { Chat } from "@/pages/chat";
import { Dashboard } from "@/pages/dashboard";
import { Help } from "@/pages/help";
import { Logs } from "@/pages/logs";
import { Settings } from "@/pages/settings";
import { Skill } from "@/pages/skill";
import { Status } from "@/pages/status";
import { Tools } from "@/pages/tools";
import { Triggers } from "@/pages/triggers";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/triggers" element={<Triggers />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/apps" element={<Apps />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/status" element={<Status />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/skill" element={<Skill />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
