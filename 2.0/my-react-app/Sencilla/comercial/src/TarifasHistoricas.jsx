import React, { useState, useEffect } from 'react';
import { Table, Button, Select, DatePicker, message } from 'antd';
import axios from 'axios';
import ExcelJS from 'exceljs';
import moment from 'moment';

const { Option } = Select;

const Tarifas = () => {
  const [tarifas, setTarifas] = useState([]);
  const [filteredTarifas, setFilteredTarifas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [items, setItems] = useState([]);
  const [searchParams, setSearchParams] = useState({
    cliente_id: null,
    unidad_id: null,
    item_id: null,
    fecha_vigencia_inicio: null,
    fecha_vigencia_final: null,
  });

  useEffect(() => {
    fetchClientes();
    fetchUnidades();
    fetchItems();
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    const response = await axios.get('http://esadc01:5000/api/categorias');
    setCategorias(response.data);
  };
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
    try {
      const response = await axios.get('http://esadc01:5000/api/tarifas_historicas', {
        params: searchParams,
      });
      setTarifas(response.data);
      setFilteredTarifas(response.data);
    } catch (error) {
      console.error('Error al obtener las tarifas:', error);
      message.error('Error al obtener las tarifas. Revisa la consola para más detalles.');
    }
  };

  const handleDescargarExcel = async () => {
    try {
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet('Tarifas');

      worksheet.columns = [
        { header: 'Cliente', key: 'cliente', width: 30 },
        { header: 'Categoría', key: 'categoria', width: 15 },
        { header: 'Item', key: 'item', width: 25 },
        { header: 'Unidad', key: 'unidad', width: 15 },
        { header: 'Mínimo', key: 'minimo', width: 10 },
        { header: 'Incremento', key: 'incremento', width: 10 },
        { header: 'Precio', key: 'precio', width: 10 },
        { header: 'Fecha Inicio', key: 'fechainicio', width: 15 },
        { header: 'Fecha Final', key: 'fechafinal', width: 15 },
      ];

      filteredTarifas.forEach((tarifa) => {
        worksheet.addRow({
          cliente: tarifa.cliente,
          unidad: tarifa.unidad,
          item: tarifa.item,
          incremento: tarifa.incremento,
          precio: `$${tarifa.precio}`,
          minimo: tarifa.minimo,
          fechainicio: tarifa.fechadesde,
          fechafinal: tarifa.fechahasta,
          categoria: tarifa.categoria,
        });
      });

      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      // Descarga
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = 'tarifas.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      message.error('Error al descargar el archivo Excel.');
      console.error('Error al generar Excel:', error);
    }
  };

  const columns = [
    { title: 'Cliente', dataIndex: 'cliente', key: 'cliente',},
    { title: 'Categoría', dataIndex: 'categoria', key: 'categoria'},      
    { title: 'Unidad', dataIndex: 'unidad', key: 'unidad_id'},
    { title: 'Item', dataIndex: 'item', key: 'item_id'},
    { title: 'Incremento', dataIndex: 'incremento', key: 'incremento', render: (incremento) => incremento + '%' },
    { title: 'Precio', dataIndex: 'precio', key: 'precio', render: (precio) => `$${precio.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,},
    { title: 'Mínimo', dataIndex: 'minimo', key: 'minimo' },
    { title: 'Fecha Inicio', dataIndex: 'fechadesde', key: 'fechainicio' },
    { title: 'Fecha Final', dataIndex: 'fechahasta', key: 'fechafinal' },
  ];

  return (
    <div>
      <h1>Tarifas Históricas</h1>

      <div style={{ marginBottom: 16 }}>
        <Select
          placeholder="Cliente"
          style={{ width: 200, marginRight: 8 }}
          value={searchParams.cliente}
          onChange={(value) => setSearchParams({ ...searchParams, cliente: value })}
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
        value={searchParams.fecha_inicio ? moment(searchParams.fecha_inicio) : null}
        onChange={(date) => setSearchParams({ ...searchParams, fecha_inicio: date ? date.toDate() : null })}
        />
        <DatePicker
        placeholder="Fecha Final"
        style={{ width: 200, marginRight: 8 }}
        value={searchParams.fecha_final ? moment(searchParams.fecha_final) : null}
        onChange={(date) => setSearchParams({ ...searchParams, fecha_final: date ? date.toDate() : null })}
        />
        <DatePicker
        placeholder="Fecha Movimiento"
        style={{ width: 200, marginRight: 8 }}
        value={searchParams.fecha_movimiento ? moment(searchParams.fecha_movimiento) : null}
        onChange={(date) => setSearchParams({ ...searchParams, fecha_movimiento: date ? date.toDate() : null })}
        />
        <Button type="primary" onClick={handleSearch}>
          Buscar
        </Button>
      </div>

      <Table dataSource={filteredTarifas} columns={columns} rowKey="id" />

      <Button type="default" onClick={handleDescargarExcel} style={{ marginTop: 16 }}>
        Descargar Excel
      </Button>
    </div>
  );
};

export default Tarifas;
