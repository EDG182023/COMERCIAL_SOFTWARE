import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { Button, Select, DatePicker } from 'antd';
import { saveAs } from 'file-saver';

const Container = styled.div`
  padding: 20px;
  background-color: #f0f0f0;
  border-radius: 8px;
`;

const Title = styled.h2`
  color: #333;
  margin-bottom: 20px;
`;

const Reportes = () => {
  const [clientes, setClientes] = useState([]);
  const [items, setItems] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [clienteId, setClienteId] = useState('');
  const [itemId, setItemId] = useState('');
  const [categoriaId, setCategoriaId] = useState('');
  const [unidadId, setUnidadId] = useState('');
  const [fechaDesde, setFechaDesde] = useState(null);
  const [fechaHasta, setFechaHasta] = useState(null);
  const [especifico, setEspecifico] = useState(false);

  useEffect(() => {
    fetchClientes();
    fetchItems();
    fetchCategorias();
    fetchUnidades();
  }, []);

  // API para obtener clientes
  const fetchClientes = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/clientes'); // API para obtener clientes
      setClientes(response.data);
    } catch (error) {
      console.error("Error fetching clientes:", error);
    }
  };

  // API para obtener items
  const fetchItems = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/items'); // API para obtener items
      setItems(response.data);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  // API para obtener categorías
  const fetchCategorias = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/categorias'); // API para obtener categorías
      setCategorias(response.data);
    } catch (error) {
      console.error("Error fetching categorias:", error);
    }
  };

  // API para obtener unidades
  const fetchUnidades = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/unidades'); // API para obtener unidades
      setUnidades(response.data);
    } catch (error) {
      console.error("Error fetching unidades:", error);
    }
  };

  // Generar reporte en PDF usando la API
  const generarReportePDF = async () => {
    try {
      const response = await axios.post('http://esadc01:5000/api/reportes/pdf', {
        fecha_desde: fechaDesde ? fechaDesde.format('YYYY-MM-DD') : null,
        fecha_hasta: fechaHasta ? fechaHasta.format('YYYY-MM-DD') : null,
        cliente_id: clienteId,
        item_id: itemId,
        categoria_id: categoriaId,
        unidad_id: unidadId,
        especifico,
      }, { responseType: 'blob' });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      saveAs(blob, 'reporte_tarifario.pdf');
    } catch (error) {
      console.error("Error generating PDF report:", error);
    }
  };

  // Generar reporte en Excel usando la API
  const generarReporteExcel = async () => {
    try {
      const response = await axios.post('http://esadc01:5000/api/reportes/excel', {
        fecha_desde: fechaDesde ? fechaDesde.format('YYYY-MM-DD') : null,
        fecha_hasta: fechaHasta ? fechaHasta.format('YYYY-MM-DD') : null,
        cliente_id: clienteId,
        item_id: itemId,
        categoria_id: categoriaId,
        unidad_id: unidadId,
        especifico,
      }, { responseType: 'blob' });

      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      saveAs(blob, 'reporte_tarifario.xlsx');
    } catch (error) {
      console.error("Error generating Excel report:", error);
    }
  };

  return (
    <Container>
      <Title>Generar Reportes de Tarifas</Title>
      <Select placeholder="Seleccionar Cliente" onChange={setClienteId}>
        {clientes.map(cliente => (
          <Select.Option key={cliente.id} value={cliente.id}>{cliente.nombre}</Select.Option>
        ))}
      </Select>
      <Select placeholder="Seleccionar Item" onChange={setItemId}>
        {items.map(item => (
          <Select.Option key={item.id} value={item.id}>{item.nombre}</Select.Option>
        ))}
      </Select>
      <Select placeholder="Seleccionar Categoría" onChange={setCategoriaId}>
        {categorias.map(categoria => (
          <Select.Option key={categoria.id} value={categoria.id}>{categoria.nombre}</Select.Option>
        ))}
      </Select>
      <Select placeholder="Seleccionar Unidad" onChange={setUnidadId}>
        {unidades.map(unidad => (
          <Select.Option key={unidad.id} value={unidad.id}>{unidad.nombre}</Select.Option>
        ))}
      </Select>
      <DatePicker onChange={(date) => setFechaDesde(date)} placeholder="Fecha Desde" />
      <DatePicker onChange={(date) => setFechaHasta(date)} placeholder="Fecha Hasta" />
      <Button onClick={generarReportePDF}>Generar PDF</Button>
      <Button onClick={generarReporteExcel}>Generar Excel</Button>
    </Container>
  );
};

export default Reportes;
