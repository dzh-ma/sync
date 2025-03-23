import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Settings, Home, Lightbulb, Clock, BarChart2, FileText, User, Plus, LogOut, Edit, RefreshCw, Download, ChevronLeft } from 'lucide-react';
import { fetchDevices, updateDevice, deleteDevice } from './services/deviceService';
import Login from './components/Login';
import api from './services/api';

// Sample data for energy usage
const energyData = [
  { time: '00:00', usage: 1.5 },
  { time: '04:00', usage: 1.2 },
  { time: '08:00', usage: 2.5 },
  { time: '12:00', usage: 4.2 },
  { time: '16:00', usage: 5.0 },
  { time: '20:00', usage: 4.3 },
  { time: '23:59', usage: 2.7 },
];

const dailyData = [
  { day: 'Mon', usage: 15.2 },
  { day: 'Tue', usage: 12.8 },
  { day: 'Wed', usage: 18.3 },
  { day: 'Thu', usage: 14.5 },
  { day: 'Fri', usage: 16.7 },
  { day: 'Sat', usage: 19.2 },
  { day: 'Sun', usage: 13.8 },
];

// Sample Devices
const devices = [
  { id: '1', name: 'Living Room Light', type: 'light', status: 'online', consumption: '24.3 W' },
  { id: '2', name: 'Smart Thermostat', type: 'thermostat', status: 'online', consumption: '15.7 W' },
  { id: '3', name: 'Kitchen Outlet', type: 'outlet', status: 'offline', consumption: '0 W' },
];

// Sample Rooms
const rooms = [
  { id: '1', name: 'Living Room', type: 'living', devices: 3, consumption: '2.0 kWh' },
  { id: '2', name: 'Kitchen', type: 'kitchen', devices: 2, consumption: '3.5 kWh' },
  { id: '3', name: 'Bedroom', type: 'bedroom', devices: 2, consumption: '1.2 kWh' },
];

// Sample Automations
const automations = [
  { id: '1', name: 'Night Mode', trigger: 'time', time: 'Daily from 22:00 to 06:00', devices: 5, enabled: true },
  { id: '2', name: 'Away Mode', trigger: 'manual', time: '', devices: 8, enabled: false },
  { id: '3', name: 'Energy Saver', trigger: 'sensor', time: 'When no motion for 30min', devices: 4, enabled: true },
];

const App = () => {
  const [activePage, setActivePage] = useState('dashboard');
  const [activeTab, setActiveTab] = useState('daily');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      const credentials = localStorage.getItem('credentials');
      if (credentials) {
        try {
          const response = await api.get('/users/me');
          setUser(response.data);
        } catch (error) {
          // Invalid credentials
          localStorage.removeItem('credentials');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('credentials');
    setUser(null);
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return <Login onLoginSuccess={handleLogin} />;
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard setActiveTab={setActiveTab} activeTab={activeTab} />;
      case 'devices':
        return <DevicesPage />;
      case 'energy':
        return <EnergyPage />;
      case 'automations':
        return <AutomationsPage />;
      case 'rooms':
        return <RoomsPage />;
      case 'profile':
        return <ProfilePage />;
      default:
        return <Dashboard setActiveTab={setActiveTab} activeTab={activeTab} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-16 bg-orange-500 flex flex-col items-center py-4">
        <div className="mb-8 p-2 bg-white rounded-lg">
          <span className="font-bold text-orange-500">Sync</span>
        </div>
        <SidebarIcon 
          icon={<Home size={24} />} 
          active={activePage === 'dashboard'} 
          onClick={() => setActivePage('dashboard')} 
        />
        <SidebarIcon 
          icon={<Lightbulb size={24} />} 
          active={activePage === 'devices'} 
          onClick={() => setActivePage('devices')} 
        />
        <SidebarIcon 
          icon={<Clock size={24} />} 
          active={activePage === 'automations'} 
          onClick={() => setActivePage('automations')} 
        />
        <SidebarIcon 
          icon={<BarChart2 size={24} />} 
          active={activePage === 'energy'} 
          onClick={() => setActivePage('energy')} 
        />
        <SidebarIcon 
          icon={<FileText size={24} />} 
          active={activePage === 'rooms'} 
          onClick={() => setActivePage('rooms')} 
        />
        <SidebarIcon 
          icon={<User size={24} />} 
          active={activePage === 'profile'} 
          onClick={() => setActivePage('profile')} 
        />
        <div className="mt-auto">
          <SidebarIcon icon={<Settings size={24} />} onClick={() => {}} />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {renderPage()}
      </div>
    </div>
  );
};

const SidebarIcon = ({ icon, active, onClick }) => {
  return (
    <div 
      className={`w-12 h-12 flex items-center justify-center rounded-lg mb-4 cursor-pointer ${active ? 'bg-white text-orange-500' : 'text-white hover:bg-orange-400'}`}
      onClick={onClick}
    >
      {icon}
    </div>
  );
};

const Dashboard = ({ activeTab, setActiveTab }) => {
  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <div className="bg-blue-500 text-white p-2 rounded-full mr-4">
          <BarChart2 size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-500">Your smart home overview</p>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Energy Usage Panel */}
        <div className="col-span-8 bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center mb-4">
            <Lightbulb className="text-blue-500 mr-2" />
            <h2 className="text-xl font-bold">Energy Usage</h2>
          </div>
          
          <div className="flex border-b mb-4">
            <button 
              className={`px-4 py-2 ${activeTab === 'daily' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
              onClick={() => setActiveTab('daily')}
            >
              Daily
            </button>
            <button 
              className={`px-4 py-2 ${activeTab === 'weekly' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
              onClick={() => setActiveTab('weekly')}
            >
              Weekly
            </button>
            <button 
              className={`px-4 py-2 ${activeTab === 'monthly' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
              onClick={() => setActiveTab('monthly')}
            >
              Monthly
            </button>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={energyData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="#00BFFF" 
                  strokeWidth={3} 
                  dot={{ stroke: '#00BFFF', strokeWidth: 2, r: 4 }} 
                  activeDot={{ stroke: '#00BFFF', strokeWidth: 2, r: 6 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weather & Energy Panel */}
        <div className="col-span-4 bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-bold mb-4">Weather & Energy</h2>
          
          <div className="flex items-center mb-6">
            <div className="text-yellow-500 mr-4">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="5" fill="currentColor" />
                <path d="M12 2V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M12 20V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M4.93 4.93L6.34 6.34" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M17.66 17.66L19.07 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M2 12H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M20 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M6.34 17.66L4.93 19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M19.07 4.93L17.66 6.34" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <div>
              <h3 className="text-3xl font-bold">72°F</h3>
              <p className="text-gray-500">Sunny</p>
            </div>
            <div className="ml-auto">
              <p className="text-right text-gray-500">45% humidity</p>
              <p className="text-right text-gray-500">8 mph wind</p>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg mb-4">
            <div className="flex items-center">
              <Lightbulb className="text-blue-500 mr-2" />
              <h3 className="font-medium">Today's Energy Tip</h3>
            </div>
            <p className="text-sm mt-1">Perfect day to air-dry laundry instead of using the dryer.</p>
          </div>

          <div className="flex justify-between text-sm">
            <div className="bg-blue-50 p-2 rounded">
              <p>Optimal AC: 74°F</p>
            </div>
            <div className="bg-blue-50 p-2 rounded">
              <p>Peak Hours: 2-6pm</p>
            </div>
          </div>
          
          <p className="text-sm text-amber-600 mt-4">Savings Potential: High</p>
        </div>

        {/* Room Energy Consumption */}
        <div className="col-span-12 bg-white p-6 rounded-lg shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <FileText className="text-blue-500 mr-2" />
              <h2 className="text-xl font-bold">Room Energy Consumption</h2>
            </div>
          </div>

          <div className="border-t border-gray-100 pt-4">
            <div className="flex items-center py-2">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mr-4">
                <Home size={16} />
              </div>
              <div className="flex-1">
                <p className="font-medium">Living Room</p>
              </div>
              <div className="text-right">
                <p className="text-blue-500 font-medium">2.0 kWh</p>
                <p className="text-xs text-gray-500">1/1 devices active</p>
              </div>
            </div>
            <div className="w-full h-2 bg-yellow-200 rounded-full overflow-hidden">
              <div className="h-full bg-yellow-500" style={{ width: '75%' }}></div>
            </div>
          </div>

          <div className="mt-4 pt-2 border-t border-gray-100">
            <p className="font-medium">Total Consumption</p>
            <p className="text-blue-500 font-medium text-right">2.0 kWh</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const DevicesPage = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDevices = async () => {
      try {
        setLoading(true);
        const data = await fetchDevices();
        setDevices(data);
        setError(null);
      } catch (err) {
        setError('Failed to load devices');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadDevices();
  }, []);

  const handleToggleDevice = async (device) => {
    try {
      const newStatus = device.status === 'online' ? 'offline' : 'online';
      await updateDevice(device.id, { status: newStatus });
      
      // Update local state
      setDevices(devices.map(d => 
        d.id === device.id ? {...d, status: newStatus} : d
      ));
    } catch (err) {
      console.error('Error toggling device', err);
    }
  };

  const handleDeleteDevice = async (id) => {
    if (window.confirm('Are you sure you want to delete this device?')) {
      try {
        await deleteDevice(id);
        setDevices(devices.filter(d => d.id !== id));
      } catch (err) {
        console.error('Error deleting device', err);
      }
    }
  };

  if (loading) return <div className="p-6">Loading devices...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      {/* Component content as before, using the devices state */}
    </div>
  );
};

const AutomationsPage = () => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="bg-orange-500 text-white p-2 rounded-full mr-4">
            <Clock size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Automations</h1>
            <p className="text-gray-500">Manage your smart home routines</p>
          </div>
        </div>
        <button className="flex items-center bg-blue-500 text-white px-4 py-2 rounded-lg">
          <Plus size={20} className="mr-2" />
          New Automation
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {automations.map(automation => (
          <div key={automation.id} className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className={`p-4 ${automation.enabled ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'}`}>
              <div className="flex justify-between">
                <h3 className="font-bold text-lg">{automation.name}</h3>
                <div className="relative inline-block w-12 h-6">
                  <input 
                    type="checkbox" 
                    className="peer opacity-0 w-0 h-0"
                    defaultChecked={automation.enabled}
                  />
                  <span className="absolute cursor-pointer top-0 left-0 right-0 bottom-0 bg-gray-300 rounded-full transition duration-300 before:content-[''] before:absolute before:h-4 before:w-4 before:left-1 before:bottom-1 before:bg-white before:rounded-full before:transition before:duration-300 peer-checked:bg-blue-600 peer-checked:before:translate-x-6"></span>
                </div>
              </div>
            </div>
            
            <div className="p-4">
              <div className="flex items-center my-2">
                <div className="bg-blue-100 p-1 rounded-full mr-3">
                  <Clock size={16} className="text-blue-500" />
                </div>
                <div className="text-sm">{automation.time || 'Manual trigger'}</div>
              </div>
              
              <div className="flex justify-between mt-3">
                <div className="px-3 py-1 bg-gray-100 rounded-full text-xs">
                  {automation.devices} devices
                </div>
                
                <div className="flex">
                  <button className="p-2 text-gray-500 hover:text-blue-500">
                    <Edit size={16} />
                  </button>
                  <button className="p-2 text-gray-500 hover:text-red-500">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const EnergyPage = () => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="bg-blue-500 text-white p-2 rounded-full mr-4">
            <BarChart2 size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Energy Statistics</h1>
            <p className="text-gray-500">Monitor and analyze your energy consumption · Last updated: 6:10:38 PM</p>
          </div>
        </div>
        <div className="flex">
          <div className="relative mr-3">
            <select className="appearance-none border border-gray-200 rounded-lg py-2 pl-4 pr-10 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Past Week</option>
              <option>Past Month</option>
              <option>Past Year</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
            </div>
          </div>
          <button className="p-2 border border-gray-200 rounded-lg mr-2">
            <RefreshCw size={20} />
          </button>
          <button className="p-2 border border-gray-200 rounded-lg">
            <Download size={20} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Total Energy Consumed */}
        <div className="bg-blue-500 text-white p-6 rounded-lg">
          <div className="flex items-center mb-3">
            <Lightbulb size={20} className="mr-2" />
            <h2 className="font-bold">Total Energy Consumed</h2>
          </div>
          <div className="flex items-baseline">
            <span className="text-4xl font-bold">6.72</span>
            <span className="ml-1 text-xl">kWh</span>
          </div>
          <div className="mt-2 flex justify-between">
            <span className="bg-white/20 px-2 py-1 rounded text-sm">This Week</span>
            <span className="bg-green-500/20 px-2 py-1 rounded text-sm">10% saved</span>
          </div>
          <div className="mt-4 pt-3 border-t border-white/20 flex justify-between text-sm">
            <span>Real-time Data</span>
            <span>From MongoDB</span>
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-amber-500 text-white p-6 rounded-lg">
          <div className="flex items-center mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
            <h2 className="font-bold">Total Cost</h2>
          </div>
          <div className="flex items-baseline">
            <span className="text-4xl font-bold">3.02</span>
            <span className="ml-1 text-xl">AED</span>
          </div>
          <div className="mt-2">
            <span className="text-sm">based on current energy rates</span>
          </div>
          <div className="mt-4 pt-3 border-t border-white/20 flex justify-between text-sm">
            <span>Projected Monthly</span>
            <span>12.09 AED</span>
          </div>
        </div>

        {/* Most Active Room */}
        <div className="bg-blue-500 text-white p-6 rounded-lg">
          <div className="flex items-center mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            <h2 className="font-bold">Most Active Room</h2>
          </div>
          <div className="text-3xl font-bold mb-2">Living Room</div>
          <div className="flex justify-between mb-1">
            <span>Energy Consumption</span>
            <span>6.72 kWh</span>
          </div>
          <div className="flex justify-between">
            <span>Room Efficiency</span>
            <span>Good</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex">
          <button className="px-4 py-2 border-b-2 border-blue-500 text-blue-500 font-medium">
            <BarChart2 size={16} className="inline mr-1" />
            Overview
          </button>
          <button className="px-4 py-2 text-gray-500">
            <Lightbulb size={16} className="inline mr-1" />
            Devices
          </button>
          <button className="px-4 py-2 text-gray-500">
            <Home size={16} className="inline mr-1" />
            Rooms
          </button>
        </div>
      </div>

      {/* Energy Consumption Trend */}
      <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
        <div className="mb-4">
          <h2 className="text-lg font-bold mb-1">Energy Consumption Trend</h2>
          <p className="text-sm text-gray-500">Daily consumption for the past week</p>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="usage" 
                stroke="#00BFFF" 
                strokeWidth={2} 
                dot={{ stroke: '#00BFFF', strokeWidth: 2, r: 4 }} 
                activeDot={{ stroke: '#00BFFF', strokeWidth: 2, r: 6 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

const RoomsPage = () => {
  const [showAddRoom, setShowAddRoom] = useState(false);
  
  if (showAddRoom) {
    return <AddRoomPage onBack={() => setShowAddRoom(false)} />;
  }
  
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="bg-blue-500 text-white p-2 rounded-full mr-4">
            <Home size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Rooms</h1>
            <p className="text-gray-500">Manage your smart home spaces</p>
          </div>
        </div>
        <button 
          className="flex items-center bg-blue-500 text-white px-4 py-2 rounded-lg"
          onClick={() => setShowAddRoom(true)}
        >
          <Plus size={20} className="mr-2" />
          Add Room
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rooms.map(room => (
          <div key={room.id} className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-xl">{room.name}</h3>
              <button className="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
              </button>
            </div>
            
            <div className="mb-4 bg-gray-100 h-40 rounded-lg flex items-center justify-center">
              <Home size={60} className="text-gray-300" />
            </div>
            
            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-gray-500">Type</p>
                <p className="font-medium">{room.type.charAt(0).toUpperCase() + room.type.slice(1)}</p>
              </div>
              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-gray-500">Devices</p>
                <p className="font-medium">{room.devices} connected</p>
              </div>
            </div>
            
            <div className="bg-blue-50 p-3 rounded-lg mb-4">
              <p className="text-sm text-gray-500">Energy Consumption</p>
              <p className="font-medium text-blue-500">{room.consumption}</p>
            </div>
            
            <div className="flex justify-between">
              <button className="flex items-center text-blue-500 px-3 py-1 border border-blue-200 rounded-lg hover:bg-blue-50">
                <Edit size={16} className="mr-1" />
                Edit
              </button>
              <button className="flex items-center text-red-500 px-3 py-1 border border-red-200 rounded-lg hover:bg-red-50">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AddRoomPage = ({ onBack }) => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="bg-blue-500 text-white p-2 rounded-full mr-4">
            <span className="font-bold text-xl">Sy</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold">Add New Room</h1>
            <p className="text-gray-500">Create a new room in your smart home</p>
          </div>
        </div>
        <div className="flex">
          <button onClick={onBack} className="mr-2">
            <ChevronLeft size={24} />
          </button>
          <button className="p-2">
            <User size={20} />
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm md:w-2/3">
          <h2 className="text-xl font-bold text-blue-500 mb-6">Room Details</h2>
          
          <div className="mb-4">
            <label className="block mb-2">Room Name</label>
            <input 
              type="text" 
              placeholder="Enter room name" 
              className="w-full border border-gray-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="mb-4">
            <label className="block mb-2">Room Type</label>
            <div className="relative">
              <select className="appearance-none w-full border border-gray-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="" disabled selected>Select room type</option>
                <option value="living">Living Room</option>
                <option value="bedroom">Bedroom</option>
                <option value="kitchen">Kitchen</option>
                <option value="bathroom">Bathroom</option>
                <option value="office">Office</option>
                <option value="other">Other</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
              </div>
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block mb-2">Room Image</label>
            <div className="border-2 border-dashed border-blue-200 rounded-lg p-6 flex flex-col items-center justify-center h-48">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-500 mb-3"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              <p className="text-sm text-gray-500 mb-3">Drag and drop an image, or click to select</p>
              <button className="px-4 py-2 border border-blue-500 text-blue-500 rounded-lg">Select Image</button>
            </div>
          </div>
          
          <div className="flex justify-between mt-6">
            <button onClick={onBack} className="px-6 py-3 border border-gray-200 rounded-lg">
              Cancel
            </button>
            <button className="px-6 py-3 bg-blue-500 text-white rounded-lg">
              Add Room
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm md:w-1/3">
          <h2 className="text-xl font-bold mb-4">Current Rooms</h2>
          
          <div className="mb-4">
            <div className="bg-gray-200 rounded-lg h-32 flex items-center justify-center mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><line x1="1" y1="1" x2="23" y2="23"></line><path d="M21 21H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3m3-3h6l2 3h4a2 2 0 0 1 2 2v9.34m-7.72-2.06L9 13"></path></svg>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-medium">Living Room</h3>
                <p className="text-sm text-gray-500">Living</p>
              </div>
              <button className="text-red-500">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProfilePage = () => {
  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <div className="bg-blue-500 text-white p-2 rounded-full mr-4">
          <User size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Profile Dashboard</h1>
          <p className="text-gray-500">Manage your account and family members</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
        <div className="flex items-center">
          <div className="bg-blue-50 p-6 rounded-full mr-6">
            <User size={32} className="text-blue-500" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">John Doe</h2>
            <p className="text-gray-500">john.doe@example.com</p>
          </div>
          <div className="flex">
            <button className="bg-blue-500 text-white px-4 py-2 rounded-lg mr-2">
              Edit Profile
            </button>
            <button className="border border-gray-200 px-4 py-2 rounded-lg flex items-center">
              <LogOut size={16} className="mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>

      <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-sm flex items-center">
          <div className="bg-blue-50 p-4 rounded-full mr-4">
            <Plus size={24} className="text-blue-500" />
          </div>
          <div>
            <h3 className="font-bold mb-1">Create Profile</h3>
            <p className="text-gray-500 text-sm">Add a new user or family member</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm flex items-center">
          <div className="bg-blue-50 p-4 rounded-full mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-500"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </div>
          <div>
            <h3 className="font-bold mb-1">Manage Profiles</h3>
            <p className="text-gray-500 text-sm">View and edit existing profiles</p>
          </div>
        </div>
      </div>

      <h2 className="text-xl font-bold mb-4">Account Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm flex items-center">
          <div className="bg-blue-50 p-4 rounded-full mr-4">
            <BarChart2 size={24} className="text-blue-500" />
          </div>
          <div>
            <h3 className="font-bold mb-1">View Analytics</h3>
            <p className="text-gray-500 text-sm">Check usage statistics and reports</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm flex items-center">
          <div className="bg-blue-50 p-4 rounded-full mr-4">
            <Settings size={24} className="text-blue-500" />
          </div>
          <div>
            <h3 className="font-bold mb-1">Account Settings</h3>
            <p className="text-gray-500 text-sm">Manage preferences and security</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
