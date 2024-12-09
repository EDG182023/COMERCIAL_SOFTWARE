import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

// Función simple para simular un token
const generateToken = (username) => {
  return btoa(JSON.stringify({ username, exp: Date.now() + 3600000 })); // Expira en 1 hora
};

// Lista de permisos simulada según el usuario
const getUserPermissions = (username) => {
  if (username === 'Diego') {
    return ['tarifas', 'tarifasPorVencer','actualizacionTarifas', 'tarifasHistoricas', 'tarifasPorRango' ]; // permisos de Diego
  } else if (username === 'admin') {
    return ['tarifas', 'tarifasPorVencer', 'actualizacionTarifas', 'tarifasHistoricas', 'reportes', 'valor-x-kilo', 'tarifasPorRango']; // permisos de admin
  }
  return [];
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (username, password) => {
    // Simulación de autenticación
    if ((username === 'Diego' && password === 'Comercial.2024') || (username === 'admin' && password === 'admin')) {
      const token = generateToken(username);
      const permisos = getUserPermissions(username);
      localStorage.setItem('token', token);
      setUser({ username, permisos }); // Añadimos permisos al usuario
      return true;
    }
    return false;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
