import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import styled, { createGlobalStyle } from 'styled-components';
import { AuthProvider } from './AuthContext';
import Login from './Login';
import Dashboard from './Dashboard';
import TarifasHistoricas from './TarifasHistoricas';
import Reportes from './Reportes';
import ValoroXkilo from './VldPorkilo';
import TarifasRango from './TarifasRango';

const GlobalStyle = createGlobalStyle`
  body {
    margin: 0;
    padding: 0;
    font-family: 'Roboto', sans-serif;
    background: linear-gradient(to right, #000428, #004e92);
    color: #fff;
  }
`;

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

function App() {
  return (
    <AuthProvider>
      <Router>
        <GlobalStyle />
        <AppContainer>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tarifas-historicas" element={<TarifasHistoricas />} />
            <Route path="/reportes" element={<Reportes />} />
            <Route path="/valor-x-kilo" element={<ValoroXkilo />} />
            <Route path="/tarifas-rango" element={<TarifasRango />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </AppContainer>
      </Router>
    </AuthProvider>
  );
}

export default App;