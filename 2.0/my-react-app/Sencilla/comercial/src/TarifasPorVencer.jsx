import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { Table, Button, Select, Space, Modal, Form, Input, DatePicker, message } from 'antd';
import moment from 'moment';

const { Option } = Select;

const Container = styled.div`
  margin: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h2`
  color: #343a40;
  margin-bottom: 20px;
`;

const TarifasConActualizacion = () => {
  const [clientesVencidos, setClientesVencidos] = useState([]);
  const [tarifas, setTarifas] = useState([]);
  const [filteredTarifas, setFilteredTarifas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [items, setItems] = useState([]);
  const [tarifaSeleccionada, setTarifaSeleccionada] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [porcentaje, setPorcentaje] = useState(0); // Nuevo estado para el porcentaje

  useEffect(() => {
    fetchTarifasPorVencer();
    fetchTarifas();
    fetchClientes();
    fetchItems();
  }, []);

  const fetchTarifasPorVencer = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/tarifas-vencidas');
      console.log('Datos de tarifas vencidas:', response.data);
      setClientesVencidos(response.data);
    } catch (error) {
      console.error('Error al obtener tarifas vencidas:', error);
      message.error('Error al cargar los datos.');
    }
  };

  const fetchTarifas = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/tarifario');
      setTarifas(response.data);
      setFilteredTarifas(response.data);
    } catch (error) {
      console.error('Error al obtener las tarifas:', error);
    }
  };

  const fetchClientes = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/clientes');
      setClientes(response.data);
    } catch (error) {
      console.error('Error al obtener los clientes:', error);
    }
  };

  const fetchItems = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/items');
      setItems(response.data);
    } catch (error) {
      console.error('Error al obtener los items:', error);
    }
  };

  const handleEditarTarifa = (record) => {
    setTarifaSeleccionada(record);
    const valuesWithDates = {
      ...record,
      fecha_vigencia_inicio: moment(record.fecha_vigencia_inicio),
      fecha_vigencia_final: moment(record.fecha_vigencia_final),
    };
    form.setFieldsValue(valuesWithDates);
    setIsModalVisible(true);
  };

  const handleGuardarTarifa = async () => {
    try {
      const values = await form.validateFields();
      const tarifa = {
        ...values,
        fecha_vigencia_inicio: values.fecha_vigencia_inicio.format('YYYY-MM-DD'),
        fecha_vigencia_final: values.fecha_vigencia_final.format('YYYY-MM-DD'),
      };

      await axios.put(`http://esadc01:5000/api/tarifario/${tarifaSeleccionada.id}`, tarifa);
      message.success('Tarifa editada exitosamente');
      setIsModalVisible(false);
      setTarifaSeleccionada(null);
      fetchTarifas();
    } catch (error) {
      console.error('Error al editar la tarifa:', error);
      message.error('Error al editar la tarifa. Revisa la consola para más detalles.');
    }
  };

  const handleClearFilters = () => {
    setFilteredTarifas(tarifas);
  };

  // Nueva función para manejar la actualización masiva
  const handleActualizacionMasiva = async () => {
    try {
      const actualizacionMasiva = {
        criterio: 'cliente', // Define el criterio según tu lógica seleccionId: tarifaSeleccionada.id, // O el ID que necesites
        incluirCliente: false, // O false, según tu lógica
        clienteId: '', // O el ID del cliente si es necesario
        fechaInicio: moment().format('YYYY-MM-DD'), // Fecha actual o la que necesites
        fechaFin: moment().add(1, 'month').format('YYYY-MM-DD'), // Un mes después o la que necesites
        porcentaje: parseFloat(porcentaje),
        usuario: '', // Cambia esto por el usuario actual
        seleccionId:  tarifaSeleccionada.id, // O el ID que necesites

      };

      console.log('Datos de actualización masiva:', actualizacionMasiva);

      const response = await axios.post('http://esadc01:5000/api/actualizacion_masiva_tarifas', actualizacionMasiva);

      console.log('Respuesta del servidor:', response.data);
      message.success(`Éxito: ${response.data.message}`);
    } catch (error) {
      console.error('Error detallado:', error.response?.data);
      message.error(`Error: ${error.response?.data?.error || 'Ocurrió un error al actualizar las tarifas'}`);
    }
  };

  const columns = [
    {
      title: 'ID Cliente',
      dataIndex: 'id', // Asegúrate de que el dataIndex sea correcto
      key: 'id',
    },
    {
      title: 'Nombre del Cliente',
      dataIndex: 'nombre', // Asegúrate de que el dataIndex sea correcto
      key: 'nombre',
    },
    {
      title: 'Acciones',
      key: 'acciones',
      render: (_, record) => (
        <Space size="middle">
          <Button type="primary" onClick={() => handleEditarTarifa(record)}>Actualizar Tarifa</Button>
        </Space>
      ),
    },
  ];

  return (
    <Container>
      <Title>Clientes con Tarifas a Vencer</Title>
      {clientesVencidos.length === 0 ? (
        <p>No hay tarifas vencidas en este momento.</p>
      ) : (
        <Table dataSource={clientesVencidos} columns={columns} rowKey="id" />
      )}
      <Modal
        title="Editar Tarifa"
        visible={isModalVisible}
        onOk={handleActualizacionMasiva}
        onCancel={() => setIsModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="Nombre del Cliente" name="nombre">
            <Select>
              {clientesVencidos.map((cliente) => (
                <Option value={cliente.nombre}>{cliente.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="Fecha Vigencia Inicio" name="fecha_vigencia_inicio">
            <DatePicker />
          </Form.Item>
          <Form.Item label="Fecha Vigencia Final" name="fecha_vigencia_final">
            <DatePicker />
          </Form.Item>
          <Form.Item label="Porcentaje" name="porcentaje">
            <Input type="number" value={porcentaje} onChange={(e) => setPorcentaje(e.target.value)} />
          </Form.Item>
        </Form>
      </Modal>
    </Container>
  );
};

export default TarifasConActualizacion;