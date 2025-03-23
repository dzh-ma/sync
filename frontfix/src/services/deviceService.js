import api from './api';

export const fetchDevices = async () => {
  try {
    const response = await api.get('/devices');
    return response.data;
  } catch (error) {
    console.error('Error fetching devices:', error);
    throw error;
  }
};

export const fetchDevice = async (id) => {
  try {
    const response = await api.get(`/devices/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching device ${id}:`, error);
    throw error;
  }
};

export const updateDevice = async (id, data) => {
  try {
    const response = await api.patch(`/devices/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating device ${id}:`, error);
    throw error;
  }
};

export const createDevice = async (data) => {
  try {
    const response = await api.post('/devices', data);
    return response.data;
  } catch (error) {
    console.error('Error creating device:', error);
    throw error;
  }
};

export const deleteDevice = async (id) => {
  try {
    await api.delete(`/devices/${id}`);
    return true;
  } catch (error) {
    console.error(`Error deleting device ${id}:`, error);
    throw error;
  }
};
