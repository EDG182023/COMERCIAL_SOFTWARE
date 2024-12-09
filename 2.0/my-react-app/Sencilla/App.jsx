import React from 'react';
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom';
import Login from './Login';
import TarifasPorVencer from './TarifasPorVencer';
import Tarifas from './Tarifas';
import ActualizacionTarifas from './ActualizacionTarifas';
import ValoroXkilo from './VldPorkilo';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/tarifas-por-vencer">Tarifas por Vencer</Link></li>
            <li><Link to="/tarifas">Tarifas</Link></li>
            <li><Link to="/actualizar-tarifas">Actualizar Tarifas</Link></li>
            <li><Link to="/valor-x-kilo">Valor por kilo</Link></li>
          </ul>
        </nav>

        <Switch>
          <Route path="/login" component={Login} />
          <Route path="/tarifas-por-vencer" component={TarifasPorVencer} />
          <Route path="/tarifas" component={Tarifas} />
          <Route path="/actualizar-tarifas" component={ActualizacionTarifas} />
          <Route path="/valor-x-kilo" component={ValoroXkilo} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;