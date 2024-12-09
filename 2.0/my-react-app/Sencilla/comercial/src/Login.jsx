import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from './AuthContext';

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
`;

const LoginForm = styled.form`
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 10px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
`;

const Input = styled.input`
  width: 100%;
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: none;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
`;

const Button = styled.button`
  width: 100%;
  padding: 0.5rem;
  margin-top: 1rem;
  border: none;
  border-radius: 5px;
  background: #00a8ff;
  color: #fff;
  cursor: pointer;
  transition: background 0.3s ease;

  &:hover {
    background: #0097e6;
  }
`;

const Logo = styled.svg`
  width: 200px;
  height: auto;
  margin-top: 2rem;
  color: #00a8ff;
`;

function Login() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (login(credentials.username, credentials.password)) {
      navigate('/dashboard');
    } else {
      alert('Credenciales inválidas');
    }
  };

  return (
    <LoginContainer>
      <LoginForm onSubmit={handleLogin}>
        <Input
          type="text"
          placeholder="Usuario"
          value={credentials.username}
          onChange={(e) => setCredentials({...credentials, username: e.target.value})}
        />
        <Input
          type="password"
          placeholder="Contraseña"
          value={credentials.password}
          onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        />
        <Button type="submit">Iniciar sesión</Button>
      </LoginForm>
      <Logo viewBox="0 0 300 300">
        <path d="M40.47 58.18h34.17c6.63-7.56 14.17-14.13 22.39-19.63 24.72-15.89 55.61-22.67 86.95-16.58 19.12 3.72 36.17 11.83 50.34 23.01.12.09.25.16.38.23l-.02.02c.17.12.33.21.5.31l.04.05c4.74 2.82 5.05-.14 5.05-.14l-.02-.01c.09-.74-.35-1.68-.7-2.3-.3-.65-1.23-1.99-3.97-4.71-16.54-16.89-38.1-29.39-63.01-35.05-.62-.14-1.23-.26-1.85-.4-.72-.15-1.44-.32-2.17-.47l-.18-.03A130.28 130.28 0 00148.28.1C104.3-1.67 62.98 18.72 38.17 53.83c-1.3 1.84.03 4.35 2.3 4.35zm206.58 144.38h-34.14c-.02 0-.04.01-.04.01a115.51 115.51 0 01-7.09 7.4c-26.52 24.18-64.18 36-102.5 28.54-19.12-3.72-36.17-11.83-50.34-23.01-.12-.09-.26-.16-.38-.24l.02-.01c-.17-.12-.34-.21-.5-.31l-.04-.05c-4.74-2.82-5.05.14-5.05.14l.02.01c-.09.74.35 1.68.7 2.3.3.66 1.23 2 3.97 4.71 12.16 12.42 27.04 22.46 43.97 29.17 13.74 5.6 28.44 8.81 43.6 9.42 1.78.07 3.55.11 5.31.11 41.99 0 80.99-20.14 104.8-53.84 1.29-1.84-.04-4.35-2.31-4.35zm-102.84-37.5c-6.35 0-13.78-1.41-16.26-8.16-.5-1.3-.86-2.79-1.07-4.44-.21-1.66-1.55-2.94-3.2-2.94H96.02c-1.87 0-3.37 1.62-3.22 3.51 2.54 32.58 36.35 36.83 48.47 36.83 24.62 0 51.1-9.42 51.1-38.62 0-20.57-15.48-27.95-31.13-32.34-15.64-4.4-31.44-6.12-32.06-14.13 0-6.28 7.59-7.54 12.23-7.54 3.41 0 7.28.79 10.07 2.82 2.77 1.87 4.62 4.68 4.04 8.87-.01.04.02.08.06.08h28.67c1.92 0 3.42-1.7 3.22-3.63-2.62-24.51-22.99-32.94-45.9-32.94-22.77 0-44.6 11.15-44.6 37.05 0 22.61 19.98 27.47 37.47 32.5 19.05 5.5 23.85 7.07 23.85 12.88.02 8.32-8.5 10.2-14.08 10.2zm155.14 17.76L260.77 75.39a.433.433 0 00-.41-.29H227.7c-.2 0-.38.12-.44.31L188.24 182.8c-.77 2.13.78 4.39 3.02 4.39h29.29c.19 0 .36-.12.41-.31l4.76-15.37c.06-.2.25-.33.45-.33h34.48c.19 0 .36.13.42.31l4.46 15.36c.06.2.24.34.46.34h30.36c2.21.01 3.77-2.24 3-4.37zm-49.48-35.65h-12.23c-2.17 0-3.72-2.14-3.07-4.24l9.37-30.3h.31l8.72 30.36c.59 2.09-.96 4.18-3.1 4.18zM89.04 183.94v-22.2c0-1.8-1.38-3.26-3.07-3.26H35.61c-1.7 0-3.08-1.46-3.08-3.26v-7.45c0-1.8 1.38-3.26 3.08-3.26h43.7c1.7 0 3.07-1.46 3.07-3.26v-20.16c0-1.8-1.38-3.26-3.07-3.26h-43.7c-1.7 0-3.08-1.46-3.08-3.26v-7.45c0-1.8 1.38-3.26 3.08-3.26h48.73c1.7 0 3.08-1.46 3.08-3.26V78.4c0-1.8-1.38-3.26-3.08-3.26H3.07C1.37 75.14 0 76.6 0 78.4v105.57c0 1.8 1.38 3.26 3.07 3.26h82.89c1.71-.03 3.08-1.49 3.08-3.29z" fill="currentColor" />
      </Logo>
    </LoginContainer>
  );
}

export default Login;