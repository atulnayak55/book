import { MainLayout } from "./layouts/MainLayout";
import { ListingsPage } from "./pages/ListingsPage";
import "./App.css";
import "./pages/ListingsPage.css";

function App() {
  return (
    <MainLayout>
      <ListingsPage />
    </MainLayout>
  );
}

export default App
