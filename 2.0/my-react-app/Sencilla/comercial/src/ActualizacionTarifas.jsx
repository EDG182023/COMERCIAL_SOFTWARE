import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';

const Container = styled.div`
  padding: 20px;
  background-color: #f0f0f0;
  border-radius: 8px;
`;

const Title = styled.h2`
  color: #333;
  margin-bottom: 20px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const Select = styled.select`
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  color: #000;
`;

const Input = styled.input`
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
`;

const Button = styled.button`
  padding: 10px 15px;
  background-color: #4cd137;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background-color: #44bd32;
  }
`;

const ResultMessage = styled.div`
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
  background-color: ${props => (props.$success ? '#4cd137' : '#e74c3c')};
  color: white;
`;

const Checkbox = styled.input`
  margin-right: 10px;
`;

const Label = styled.label`
  display: flex;
  align-items: center;
  margin-bottom: 10px;
`;

const DateInput = styled.input`
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-bottom: 10px;
`;

function ActualizacionMasivaTarifas() {
  const [clientes, setClientes] = useState([]);
  const [items, setItems] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [criterio, setCriterio] = useState('cliente');
  const [seleccionId, setSeleccionId] = useState('');
  const [clienteId, setClienteId] = useState('');
  const [incluirCliente, setIncluirCliente] = useState(false);
  const [porcentaje, setPorcentaje] = useState('');
  const [resultMessage, setResultMessage] = useState('');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [usuario, setUsuario] = useState(''); // Asume que tienes el usuario actual

  useEffect(() => {
    fetchClientes();
    fetchItems();
    fetchUnidades();
  }, []);

  const fetchClientes = async () => {
    try {
      const response = await axios.get('http://192.168.1.10:5000/api/clientes');
      setClientes(response.data);
    } catch (error) {
      console.error('Error al obtener clientes:', error);
    }
  };

  const fetchItems = async () => {
    try {
      const response = await axios.get('http://192.168.1.10:5000/api/items');
      setItems(response.data);
    } catch (error) {
      console.error('Error al obtener items:', error);
    }
  };

  const fetchUnidades = async () => {
    try {
      const response = await axios.get('http://192.168.1.10:5000/api/unidades');
      setUnidades(response.data);
    } catch (error) {
      console.error('Error al obtener unidades:', error);
    }
  };

 
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!seleccionId) {
      setResultMessage('Error: Debe seleccionar un elemento.');
      return;
    }

    if (incluirCliente && !clienteId) {
      setResultMessage('Error: Debe seleccionar un cliente si se incluye.');
      return;
    }

    if (!porcentaje) {
      setResultMessage('Error: El porcentaje no puede estar vacío.');
      return;
    }

    try {
      const actualizacionMasiva = {
        criterio,
        seleccionId,
        incluirCliente,
        clienteId,
        fechaInicio,
        fechaFin,
        porcentaje: parseFloat(porcentaje),
        usuario,
      };

      console.log('Datos de actualización masiva:', actualizacionMasiva);

      const response = await axios.post('http://192.168.1.10:5000/api/actualizacion_masiva_tarifas', actualizacionMasiva);

      console.log('Respuesta del servidor:', response.data);
      setResultMessage(`Éxito: ${response.data.message}`);


    } catch (error) {
      console.error('Error detallado:', error.response?.data);
      setResultMessage(`Error: ${error.response?.data?.error || 'Ocurrió un error al actualizar las tarifas'}`);
    }
  };

  return (
    <Container>
      <Title>Actualización Masiva de Tarifas</Title>
      <Form onSubmit={handleSubmit}>
        <Select value={criterio} onChange={(e) => setCriterio(e.target.value)}>
          <option value="cliente">Por Cliente</option>
          <option value="item">Por Item</option>
          <option value="unidad">Por Unidad</option>
          <option value="categoria">Por Categoría de Item</option>
        </Select>

        <Select value={seleccionId} onChange={(e) => setSeleccionId(e.target.value)}>
          <option value="">Seleccione {criterio}</option>
          {criterio === 'cliente' && clientes.map(cliente => (
            <option key={cliente.id} value={cliente.id}>{cliente.nombre}</option>
          ))}
          {criterio === 'item' && items.map(item => (
            <option key={item.id} value={item.id}>{item.nombre}</option>
          ))}
          {criterio === 'unidad' && unidades.map(unidad => (
            <option key={unidad.id} value={unidad.id}>{unidad.nombre}</option>
          ))}
          {criterio === 'categoria' && items.map(item => (
            <option key={item.id} value={item.id}>{item.categoria}</option>
          ))}
        </Select>

        <Label>
          <Checkbox
            type="checkbox"
            checked={incluirCliente}
            onChange={(e) => setIncluirCliente(e.target.checked)}
          />
          Incluir cliente específico
        </Label>

        {incluirCliente && (
          <Select value={clienteId} onChange={(e) => setClienteId(e.target.value)}>
            <option value="">Seleccione un cliente</option>
            {clientes.map(cliente => (
              <option key={cliente.id} value={cliente.id}>{cliente.nombre}</option>
            ))}
          </Select>
        )}

        <Input
          type="number"
          value={porcentaje}
          onChange={(e) => setPorcentaje(e.target.value)}
          placeholder="Porcentaje"
        />

        <DateInput
          type="date"
          value={fechaInicio}
          onChange={(e) => setFechaInicio(e.target.value)}
        />
        <DateInput
          type="date"
          value={fechaFin}
          onChange={(e) => setFechaFin(e.target.value)}
        />

        <Button type="submit">Actualizar Tarifas</Button>
        
      </Form>

      {resultMessage && (
        <ResultMessage $success={!resultMessage.startsWith('Error')}>
          {resultMessage}
        </ResultMessage>
      )}
    </Container>
  );
}

export default ActualizacionMasivaTarifas;
