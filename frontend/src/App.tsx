import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/MainLayout';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<div>Home</div>} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
