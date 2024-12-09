import React, { useState, useEffect } from 'react';
import { Table, Button, DatePicker, message, Modal, Form, Input, Select } from 'antd';
import axios from 'axios';
import ExcelJS from 'exceljs';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/lab/Autocomplete';
import dayjs from 'dayjs'; // Asegúrate de que sea dayjs o moment según lo que uses

const { Option } = Select;

const Tarifas = () => {
  const [tarifas, setTarifas] = useState([]);
  const [filteredTarifas, setFilteredTarifas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [items, setItems] = useState([]);
  const [searchParams, setSearchParams] = useState({
    cliente: null,
    unidad_id: null,
    item_id: null,
    fecha_vigencia_inicio: null,
    fecha_vigencia_final: null,
  });

  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [currentTarifa, setCurrentTarifa] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    const fetchData = async () => {
      try {
        await Promise.all([fetchClientes(), fetchUnidades(), fetchItems()]);
      } catch (error) {
        message.error('Error al cargar los datos iniciales.');
      }
    };
    fetchData();
  }, []);

  const fetchClientes = async () => {
    const response = await axios.get('http://esadc01:5000/api/clientes');
    setClientes(response.data);
  };

  const fetchUnidades = async () => {
    const response = await axios.get('http://esadc01:5000/api/unidades');
    setUnidades(response.data);
  };

  const fetchItems = async () => {
    const response = await axios.get('http://esadc01:5000/api/items');
    setItems(response.data);
  };

  const handleSearch = async () => {
    const { cliente, unidad_id, item_id, fecha_vigencia_inicio, fecha_vigencia_final } = searchParams;

    let url = 'http://esadc01:5000/api/tarifario';
    const params = [];

    if (cliente) params.push(`cliente=${cliente}`);
    if (unidad_id) params.push(`unidad=${unidad_id}`);
    if (item_id) params.push(`item=${item_id}`);
    if (fecha_vigencia_inicio) params.push(`fechaInicio=${fecha_vigencia_inicio.toISOString().split('T')[0]}`);
    if (fecha_vigencia_final) params.push(`fechaFin=${fecha_vigencia_final.toISOString().split('T')[0]}`);

    if (params.length > 0) {
      url += '?' + params.join('&');
    }

    try {
      const response = await axios.get(url);
      setFilteredTarifas(response.data);
    } catch (error) {
      message.error('Error al obtener las tarifas. Revisa la consola para más detalles.');
      console.error('Error al obtener las tarifas:', error);
    }
  };

  const handleDescargarExcel = async () => {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Tarifas');

    worksheet.columns = [
      { header: 'Cliente', key: 'cliente', width: 30 },
      { header: 'Categoria', key: 'categoria', width: 15 },
      { header: 'Unidad', key: 'unidad', width: 15 },
      { header: 'Item', key: 'item', width: 25 },
      { header: 'Incremento', key: 'incremento', width: 10 },
      { header: 'Precio', key: 'precio', width: 10 },
      { header: 'Mínimo', key: 'minimo', width: 10 },
      { header: 'Fecha Inicio', key: 'fechainicio', width: 15 },
      { header: 'Fecha Final', key: 'fechafinal', width: 15 },
    ];

    filteredTarifas.forEach((tarifa) => {
      worksheet.addRow({
        cliente: tarifa.cliente,
        categoria: tarifa.categoria,
        unidad: tarifa.unidad,
        item: tarifa.item,
        incremento: `${tarifa.incremento}%`,
        precio: `$${tarifa.precio.toLocaleString('es-AR', { minimumFractionDigits: 2 })}`,
        minimo: tarifa.minimo,
        fechainicio: tarifa.fecha_vigencia_inicio,
        fechafinal: tarifa.fecha_vigencia_final,
      });
    });

    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = 'tarifas.xlsx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleAddTarifa = () => {
    setIsEditMode(false);
    setCurrentTarifa(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEditTarifa = (tarifa) => {
    setIsEditMode(true);
    setCurrentTarifa(tarifa);
    form.setFieldsValue({
      cliente_id: tarifa.cliente_id,
      unidad_id: tarifa.unidad_id,
      item_id: tarifa.item_id,
      precio: tarifa.precio,
      incremento: tarifa.incremento,
      minimo: tarifa.minimo,
      fecha_vigencia_inicio: tarifa.fecha_vigencia_inicio ? dayjs(tarifa.fecha_vigencia_inicio) : null,
      fecha_vigencia_final: tarifa.fecha_vigencia_final ? dayjs(tarifa.fecha_vigencia_final) : null,
    });
    setIsModalVisible(true);
  };

  const handleDeleteTarifa = async (id) => {
    try {
      await axios.delete(`http://esadc01:5000/api/tarifario/${id}`);
      message.success('Tarifa eliminada exitosamente');
      handleSearch(); // Refresh the list after deletion
    } catch (error) {
      message.error('Error al eliminar la tarifa. Revisa la consola para más detalles.');
      console.error('Error al eliminar la tarifa:', error);
    }
  };

  const handleModalOk = async () => {
    const values = await form.validateFields();
    // Asegúrate de que las fechas sean instancias de moment y conviértelas a ISO
    values.fecha_vigencia_inicio = values.fecha_vigencia_inicio ? values.fecha_vigencia_inicio.toISOString() : null;
    values.fecha_vigencia_final = values.fecha_vigencia_final ? values.fecha_vigencia_final.toISOString() : null;
    if (isEditMode) {
      await axios.put(`http://esadc01:5000/api/tarifario/${currentTarifa.id}`, values);
      message.success('Tarifa actualizada exitosamente');
    } else {
      await axios.post('http://esadc01:5000/api/tarifario', values);
      message.success('Tarifa agregada exitosamente');
    }
    setIsModalVisible(false);
    handleSearch(); // Refresh the list after adding or editing
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
  };

  const columns = [
    { title: 'Cliente', dataIndex: 'cliente', key: 'cliente' },
    { title: 'Categoria', dataIndex: 'categoria', key: 'categoria' },
    { title: 'Unidad', dataIndex: 'unidad', key: 'unidad' },
    { title: 'Item', dataIndex: 'item', key: 'item' },
    { title: 'Incremento', dataIndex: 'incremento', key: 'incremento', render: (text) => `${text}%` },
    { title: 'Precio', dataIndex: 'precio', key: 'precio', render: (text) => `$${text.toLocaleString('es-AR', { minimumFractionDigits: 2 })}` },
    { title: 'Mínimo', dataIndex: 'minimo', key: 'minimo' },
    { title: 'Fecha Inicio', dataIndex: 'fecha_vigencia_inicio', key: 'fechainicio' },
    { title: 'Fecha Final', dataIndex: 'fecha_vigencia_final', key: 'fechafinal' },
    {
      title: 'Acciones',
      key: 'acciones',
      render: (text, record) => (
        <>
          <Button onClick={() => handleEditTarifa(record)}>Editar</Button>
          <Button onClick={() => handleDeleteTarifa(record.id)} style={{ marginLeft: 8 }} danger>
            Eliminar
          </Button>
        </>
      ),
    },
  ];

  return (
    <div>
      <h1>Tarifas Vigente</h1>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={handleAddTarifa} style={{ marginBottom: 16 }}>
          Agregar Tarifas
        </Button>
        <Select
          placeholder="Cliente"
          style={{ width: 200, marginRight: 8 }}
          value={searchParams.cliente}
          onChange={(value ) => setSearchParams({ ...searchParams, cliente: value })}
        >
          {clientes.map((cliente) => (
            <Option key={cliente.id} value={cliente.id}>
              {cliente.nombre}
            </Option>
          ))}
        </Select>
        <Select
          placeholder="Unidad"
          style={{ width: 200, marginRight: 8 }}
          value={searchParams.unidad}
          onChange={(value) => setSearchParams({ ...searchParams, unidad: value })}
        >
          {unidades.map((unidad) => (
            <Option key={unidad.id} value={unidad.id}>
              {unidad.nombre}
            </Option>
          ))}
        </Select>
        <Select
          placeholder="Item"
          style={{ width: 200, marginRight: 8 }}
          value={searchParams.item}
          onChange={(value) => setSearchParams({ ...searchParams, item: value })}
        >
          {items.map((item) => (
            <Option key={item.id} value={item.id}>
              {item.nombre}
            </Option>
          ))}
        </Select>
        <DatePicker
          placeholder="Fecha Inicio"
          style={{ width: 200, marginRight: 8 }}
          onChange={(date) => setSearchParams({ ...searchParams, fecha_vigencia_inicio: date ? date : null })}
        />
        <DatePicker
          placeholder="Fecha Final"
          style={{ width: 200, marginRight: 8 }}
          onChange={(date) => setSearchParams({ ...searchParams, fecha_vigencia_final: date ? date : null })}
        />
        <Button type="primary" onClick={handleSearch}>
          Buscar
        </Button>
      </div>

      <Table dataSource={filteredTarifas} columns={columns} rowKey="id" />
      
      <Button type="default" onClick={handleDescargarExcel} style={{ marginTop: 16 }}>
        Descargar Excel
      </Button>

      <Modal
        title={isEditMode ? "Editar Tarifa" : "Agregar Tarifa"}
        visible={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="cliente_id" label="Cliente" rules={[{ required: true, message: 'Por favor selecciona un cliente' }]}>
            <Autocomplete
              options={clientes}
              getOptionLabel={(option) => option.nombre}
              renderInput={(params) => <TextField {...params} label="Cliente" variant="outlined" />}
              onChange={(event, newValue) => {
                form.setFieldsValue({ cliente_id: newValue ? newValue.id : null });
              }}
            />
          </Form.Item>
          <Form.Item name="unidad_id" label="Unidad" rules={[{ required: true, message: 'Por favor selecciona una unidad' }]}>
            <Autocomplete
              options={unidades}
              getOptionLabel={(option) => option.nombre}
              renderInput={(params) => <TextField {...params} label="Unidad" variant="outlined" />}
              onChange={(event, newValue) => {
                form.setFieldsValue({ unidad_id: newValue ? newValue.id : null });
              }}
            />
          </Form.Item>
          <Form.Item name="item_id" label="Item" rules={[{ required: true, message: 'Por favor selecciona un item' }]}>
            <Autocomplete
              options={items}
              getOptionLabel={(option) => option.nombre}
              renderInput={(params) => <TextField {...params} label="Item" variant="outlined" />}
              onChange={(event, newValue) => {
                form.setFieldsValue({ item_id: newValue ? newValue.id : null });
              }}
            />
          </Form.Item>
          <Form.Item name="precio" label="Precio" rules={[{ required: true, message: 'Por favor ingresa un precio' }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="incremento" label="Incremento" rules={[{ required: true, message: 'Por favor ingresa un incremento' }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="minimo" label="Mínimo" rules={[{ required: true, message: 'Por favor ingresa un mínimo' }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="fecha_vigencia_inicio" label="Fecha de Vigencia Inicio" rules={[{ required: true, message: 'Por favor selecciona una fecha de inicio' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="fecha_vigencia_final" label="Fecha de Vigencia Final">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Tarifas;