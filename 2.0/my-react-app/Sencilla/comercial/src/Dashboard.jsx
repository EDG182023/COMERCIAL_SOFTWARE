import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from './AuthContext';
import Tarifas from './Tarifas';
import ActualizacionTarifas from './ActualizacionTarifas';
import TarifasPorVencer from './TarifasPorVencer';
import axios from 'axios';
import TarifasHistoricas from './TarifasHistoricas';
import Reportes from './Reportes';
import Valorxkilo from './VldPorkilo';
import TarifasRango from './TarifasRango';

const DashboardContainer = styled.div`
  display: flex;
  min-height: 100vh;
`;

const Sidebar = styled.nav`
  width: 250px;
  background: #1e272e;
  padding: 2rem 1rem;
`;

const MainContent = styled.main`
  flex-grow: 1;
  padding: 2rem;
  background: #f1f2f6;
`;

const NavItem = styled.div`
  padding: 0.5rem 1rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  color: ${props => props.active ? '#00a8ff' : '#fff'};
  background: ${props => props.active ? 'rgba(0, 168, 255, 0.1)' : 'transparent'};
  border-radius: 5px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(0, 168, 255, 0.1);
  }
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  color: #2f3640;
`;

const LogoutButton = styled.button`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  background: #ff4757;
  color: #fff;
  cursor: pointer;
  transition: background 0.3s ease;

  &:hover {
    background: #ff6b81;
  }
`;

function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('tarifas');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Función auxiliar para verificar permisos
  const tienePermiso = (modulo) => user?.permisos.includes(modulo);

  return (
    <DashboardContainer>
      <Sidebar>
        {tienePermiso('tarifas') && (
          <NavItem active={activeTab === 'tarifas'} onClick={() => setActiveTab('tarifas')}>
            Tarifas
          </NavItem>
        )}
        {tienePermiso('tarifasPorRango') && (
          <NavItem active={activeTab === 'tarifasPorRango'} onClick={() => setActiveTab('tarifasPorRango')}>
            Tarifas por Rango
          </NavItem>
        )}
        {tienePermiso('tarifasPorVencer') && (
          <NavItem active={activeTab === 'tarifasPorVencer'} onClick={() => setActiveTab('tarifasPorVencer')}>
            Tarifas por Vencer
          </NavItem>
        )}
        {tienePermiso('actualizacionTarifas') && (
          <NavItem active={activeTab === 'actualizacionTarifas'} onClick={() => setActiveTab('actualizacionTarifas')}>
            Actualización de Tarifas
          </NavItem>
        )}
        {tienePermiso('tarifasHistoricas') && (
          <NavItem active={activeTab === 'tarifasHistoricas'} onClick={() => setActiveTab('tarifasHistoricas')}>
            Tarifas Históricas
          </NavItem>
        )}
        {tienePermiso('reportes') && (
          <NavItem active={activeTab === 'reportes'} onClick={() => setActiveTab('reportes')}>
            Reportes
          </NavItem>
        )}
        {tienePermiso('valor-x-kilo') && (
          <NavItem active={activeTab === 'valor-x-kilo'} onClick={() => setActiveTab('valor-x-kilo')}>
            Valor x Kilo
          </NavItem>
        )}
        
      </Sidebar>
      <MainContent>
        <Header>
          <Title>Bienvenido, {user?.username}</Title>
          <LogoutButton onClick={handleLogout}>Cerrar sesión</LogoutButton>
        </Header>
        {activeTab === 'tarifas' && tienePermiso('tarifas') && <Tarifas />}
        {activeTab === 'tarifasPorVencer' && tienePermiso('tarifasPorVencer') && <TarifasPorVencer />}
        {activeTab === 'actualizacionTarifas' && tienePermiso('actualizacionTarifas') && <ActualizacionTarifas />}
        {activeTab === 'tarifasHistoricas' && tienePermiso('tarifasHistoricas') && <TarifasHistoricas />}
        {activeTab === 'reportes' && tienePermiso('reportes') && <Reportes />}
        {activeTab === 'valor-x-kilo' && tienePermiso('valor-x-kilo') && <Valorxkilo />}
        {activeTab === 'tarifasPorRango' && tienePermiso('tarfasPorRango') && <TarifasRango />}
      </MainContent>
    </DashboardContainer>
  );
}


export default Dashboard;