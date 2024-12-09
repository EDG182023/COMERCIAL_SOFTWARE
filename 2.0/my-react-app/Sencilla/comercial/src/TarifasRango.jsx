import React, { useState, useEffect } from 'react';
import { Table, Select, Button, Space, message, Modal, Form, Input, DatePicker } from 'antd';
import axios from 'axios';
import moment from 'moment';
import "bootstrap/dist/css/bootstrap.min.css";

const { Option } = Select;

const TarifasRango = () => {
  const [TarifasRango, setTarifasRango] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [items, setItems] = useState([]);
  const [filteredTarifasRango, setFilteredTarifasRango] = useState([]);
  const [TarifasRangoeleccionada, setTarifasRangoeleccionada] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isAddModalVisible, setIsAddModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [addForm] = Form.useForm();

  useEffect(() => {
    fetchTarifasRango();
    fetchClientes();
    fetchUnidades();
    fetchItems();
  }, []);

  const fetchTarifasRango = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/tarifarioRango');
      setTarifasRango(response.data);
      setFilteredTarifasRango(response.data);
    } catch (error) {
      console.error('Error al obtener las TarifasRango:', error);
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

  const fetchUnidades = async () => {
    try {
      const response = await axios.get('http://esadc01:5000/api/unidades');
      setUnidades(response.data);
    } catch (error) {
      console.error('Error al obtener las unidades:', error);
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
    setTarifasRangoeleccionada(record);
    const valuesWithDates = {
      ...record,
      fecha_vigencia_inicio: moment(record.fecha_vigencia_inicio),
      fecha_vigencia_final: moment(record.fecha_vigencia_final),
    };
    form.setFieldsValue(valuesWithDates);
    setIsModalVisible(true);
  };

  const handleEliminarTarifa = async (id) => {
    try {
      await axios.delete(`http://esadc01:5000/api/tarifarioRango/${id}`);
      message.success('Tarifa eliminada exitosamente');
      fetchTarifasRango();
    } catch (error) {
      console.error('Error al eliminar la tarifa:', error);
      message.error('Error al eliminar la tarifa. Revisa la consola para más detalles.');
    }
  };

  const handleGuardarTarifa = async () => {
    try {
      const values = await form.validateFields();
      const tarifa = {
        cliente_id: values.cliente_id,
        unidad_id: values.unidad_id,
        item_id: values.item_id,
        precio: values.precio,
        minimo: values.minimo,
        incremento: values.incremento,
        fecha_vigencia_inicio: values.fecha_vigencia_inicio.format('YYYY-MM-DD'),
        fecha_vigencia_final: values.fecha_vigencia_final.format('YYYY-MM-DD'),
      };

      await axios.put(`http://esadc01:5000/api/tarifarioRango/${TarifasRangoeleccionada.id}`, tarifa);
      message.success('Tarifa editada exitosamente');
      setIsModalVisible(false);
      setTarifasRangoeleccionada(null);
      fetchTarifasRango();
    } catch (error) {
      console.error('Error al editar la tarifa:', error);
      message.error('Error al editar la tarifa. Revisa la consola para más detalles.');
    }
  };

  const handleAgregarTarifa = async () => {
    try {
      const values = await addForm.validateFields();
      const tarifa = {
        cliente_id: values.cliente_id,
        unidad_id: values.unidad_id,
        item_id: values.item_id,
        precio: values.precio,
        minimo: values.minimo,
        incremento: values.incremento,
        fecha_vigencia_inicio: values.fecha_vigencia_inicio.format('YYYY-MM-DD'),
        fecha_vigencia_final: values.fecha_vigencia_final.format('YYYY-MM-DD'),
      };

      await axios.post('http://esadc01:5000/api/tarifarioRango', tarifa);
      message.success('Tarifa agregada exitosamente');
      setIsAddModalVisible(false);
      fetchTarifasRango();
    } catch (error) {
      console.error('Error al agregar la tarifa:', error);
      message.error('Error al agregar la tarifa. Revisa la consola para más detalles.');
    }
  };

  const columns = [
    { title: 'Cliente', dataIndex: 'cliente', key: 'cliente' },
    { title: 'Categoría', dataIndex: 'categoria', key: 'categoria' },
    { title: 'Unidad', dataIndex: 'unidad', key: 'unidad_id' },
    {
      title: 'Item',
      dataIndex: 'item',
      key: 'item_id',
      render: (item_id) => {
        const item = items.find((i) => i.id === item_id);
        return item ? item.nombre : item_id;
      },
    },
    {
      title: 'Incremento',
      dataIndex: 'incremento',
      key: 'incremento',
      render: (incremento) => `${incremento}%`
    },
    {
      title: 'Precio',
      dataIndex: 'precio',
      key: 'precio',
      render: (precio) => `$${precio.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    },
    { title: 'Mínimo', dataIndex: 'minimo', key: 'minimo' },
    { title: 'Fecha Inicio', dataIndex: 'fecha_vigencia_inicio', key: 'fechainicio' },
    { title: 'Fecha Final', dataIndex: 'fecha_vigencia_final', key: 'fechafinal' },
    {
      title: 'Acciones',
      dataIndex: 'acciones',
      key: 'acciones',
      render: (_, record) => (
        <Space size="middle">
          <Button type="primary" onClick={() => handleEditarTarifa(record)}>
            Editar
          </Button>
          <Button type="danger" onClick={() => handleEliminarTarifa(record.id)}>
            Eliminar
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <>
      <div className="container mt-3">
        <h2>Gestión de TarifasRango</h2>
        <Button type="primary" onClick={() => setIsAddModalVisible(true)}>
          Agregar Tarifa
        </Button>
        <Table dataSource={filteredTarifasRango} columns={columns} rowKey="id" />
      </div>

      {/* Modal para editar tarifa */}
      <Modal
        title="Editar Tarifa"
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsModalVisible(false)}>
            Cancelar
          </Button>,
          <Button key="submit" type="primary" onClick={handleGuardarTarifa}>
            Guardar
          </Button>,
        ]}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="cliente_id" label="Cliente" rules={[{ required: true }]}>
            <Select placeholder="Seleccione un cliente">
              {clientes.map((cliente) => (
                <Option key={cliente.id} value={cliente.id}>{cliente.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="unidad_id" label="Unidad" rules={[{ required: true }]}>
            <Select placeholder="Seleccione una unidad">
              {unidades.map((unidad) => (
                <Option key={unidad.id} value={unidad.id}>{unidad.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="item_id" label="Item" rules={[{ required: true }]}>
            <Select placeholder="Seleccione un item">
              {items.map((item) => (
                <Option key={item.id} value={item.id}>{item.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="precio" label="Precio" rules={[{ required: true }]}>
            <Input type="number" placeholder="Ingrese el precio" />
          </Form.Item>
          <Form.Item name="minimo" label="Mínimo" rules={[{ required: true }]}>
            <Input type="number" placeholder="Ingrese el mínimo" />
          </Form.Item>
          <Form.Item name="incremento" label="Incremento" rules={[{ required: true }]}>
            <Input type="number" placeholder="Ingrese el incremento" />
          </Form.Item>
          <Form.Item name="fecha_vigencia_inicio" label="Fecha de Inicio" rules={[{ required: true }]}>
            <DatePicker format="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="fecha_vigencia_final" label="Fecha de Finalización" rules={[{ required: true }]}>
            <DatePicker format="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal para agregar tarifa */}
      <Modal
        title="Agregar Tarifa"
        visible={isAddModalVisible}
        onCancel={() => setIsAddModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsAddModalVisible(false)}>
            Cancelar
          </Button>,
          <Button key="submit" type="primary" onClick={handleAgregarTarifa}>
            Agregar
          </Button>,
        ]}
      >
        <Form form={addForm} layout="vertical">
          <Form.Item name="cliente_id" label="Cliente" rules={[{ required: true }]}>
            <Select placeholder="Seleccione un cliente">
              {clientes.map((cliente) => (
                <Option key={cliente.id} value={cliente.id}>{cliente.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="unidad_id" label="Unidad" rules={[{ required: true }]}>
            <Select placeholder="Seleccione una unidad">
              {unidades.map((unidad) => (
                <Option key={unidad.id} value={unidad.id}>{unidad.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="item_id" label="Item" rules={[{ required: true }]}>
            <Select placeholder="Seleccione un item">
              {items.map((item) => (
                <Option key={item.id} value={item.id}>{item.nombre}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="precio" label="Precio" rules={[{ required: true }]}>
            <Input type="number" placeholder="Ingrese el precio" />
          </Form.Item>
          <Form.Item name="minimo" label="Mínimo" rules={[{ required: true }]}>
            <Input type="number" placeholder="Ingrese el mínimo" />
          </Form.Item>
          <Form.Item name="incremento" label="Incremento" rules={[{ required: true }]}>
            <Input type="number" placeholder="Ingrese el incremento" />
          </Form.Item>
          <Form.Item name="fecha_vigencia_inicio" label="Fecha de Inicio" rules={[{ required: true }]}>
            <DatePicker format="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="fecha_vigencia_final" label="Fecha de Finalización" rules={[{ required: true }]}>
            <DatePicker format="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default TarifasRango;
