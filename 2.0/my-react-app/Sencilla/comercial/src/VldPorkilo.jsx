import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { Table, Button, Select, Space, Modal, Form, Input, DatePicker, message } from 'antd';
import moment from 'moment';
import * as XLSX from 'xlsx';

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

const ReportesValoresPrep = () => {
  const [reportes, setReportes] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchReportes();
    fetchClientes();
  }, []);

  const fetchReportes = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/reportes/valores_prep');
      setReportes(response.data);
    } catch (error) {
      console.error('Error al obtener reportes:', error);
      message.error('Error al cargar los datos.');
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

  const handleAgregarReporte = async (values) => {
    try {
      await axios.post('http://esadc01:5000/api/reportes/valores_prep', {
        cliente_id: values.cliente_id,
        fecha_inicio: values.fecha_inicio.format('YYYYMMDD'),
        fecha_final: values.fecha_final.format('YYYYMMDD'),
        valor: values.valor,
      });
      message.success('Reporte agregado exitosamente');
      setIsModalVisible(false);
      fetchReportes();
    } catch (error) {
      console.error('Error al agregar el reporte:', error);
      message.error('Error al agregar el reporte. Revisa la consola para más detalles.');
    }
  };

  const handleExportarExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(reportes);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Reportes');
    XLSX.writeFile(workbook, 'reportes.xlsx');
  };

  const columns = [
    {
      title: 'ID Cliente',
      dataIndex: 'nombre',
      key: 'cliente_id',
    },
    {
      title: 'Fecha Inicio',
      dataIndex: 'fecha_inicio',
      key: 'fecha_inicio',
      render: (text) => moment(text).format('YYYY-MM-DD'),
    },
    {
      title: 'Fecha Final',
      dataIndex: 'fecha_final',
      key: 'fecha_final',
      render: (text) => moment(text).format('YYYY-MM-DD'),
    },
    {
      title: 'Valor',
      dataIndex: 'Valor_kilo_prep',
      key: 'valor',
    },
  ];

  return (
    <Container>
      <Title>Reportes de Valores Prep</Title>
      <Button type="primary" onClick={() => setIsModalVisible(true)}>Agregar Reporte</Button>
      <Button type="default" onClick={handleExportarExcel} style={{ marginLeft: '10px' }}>Exportar a Excel</Button>
      <Table dataSource={reportes} columns={columns} rowKey="cliente_id" style={{ marginTop: '20px' }} />
      <Modal
        title="Agregar Reporte"
        visible={isModalVisible}
        onOk={() => form.submit()}
        onCancel={() => setIsModalVisible(false)}
      >
        <Form form={form} layout="vertical" onFinish={handleAgregarReporte}>
          <Form.Item label="Cliente" name="cliente_id" rules={[{ required: true, message: 'Selecciona un cliente' }]}>
            <Select placeholder="Selecciona un cliente">
              {clientes.map((cliente) => (
                <Option value={cliente.id}>{cliente.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="Fecha Inicio" name="fecha_inicio" rules={[{ required: true, message: 'Selecciona una fecha de inicio' }]}>
            <DatePicker format="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item label="Fecha Final" name="fecha_final" rules={[{ required: true, message: 'Selecciona una fecha de final' }]}>
            <DatePicker format="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item label="Valor" name="valor" rules={[{ required: true, message: 'Ingresa un valor' }]}>
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </Container>
  );
};

export default ReportesValoresPrep;