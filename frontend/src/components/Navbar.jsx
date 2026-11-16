import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, LogOut, User as UserIcon, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="fixed w-full z-50 top-0 start-0 border-b border-white/10 bg-deep-blue/80 backdrop-blur-lg">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between p-4">
        <Link to="/" className="flex items-center space-x-3 rtl:space-x-reverse group">
            <Leaf className="h-8 w-8 text-neon-green group-hover:animate-pulse" />
            <span className="self-center text-2xl font-bold whitespace-nowrap text-white">Carbon<span className="text-neon-green">AI</span></span>
        </Link>
        <div className="flex md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
          {user ? (
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-blue-200 hidden md:inline-block flex items-center">
                 <UserIcon className="w-4 h-4 mr-2 inline" />
                 {user.email}
              </span>
              <Link 
                to="/dashboard"
                className="text-deep-blue bg-neon-green hover:bg-green-400 focus:ring-4 focus:outline-none focus:ring-green-300 font-medium rounded-lg text-sm px-4 py-2 text-center flex items-center"
              >
                <LayoutDashboard className="w-4 h-4 mr-2" /> Dashboard
              </Link>
              <button
                onClick={handleLogout}
                className="text-red-400 hover:text-white border border-red-400 hover:bg-red-500 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-4 py-2 text-center flex items-center transition-colors"
              >
                <LogOut className="w-4 h-4 mr-2" /> Logout
              </button>
            </div>
          ) : (
             <div className="flex items-center space-x-4">
                <Link to="/login" className="text-white hover:text-neon-green font-medium text-sm px-4 py-2 transition-colors">
                  Log in
                </Link>
                <Link to="/register" className="text-deep-blue bg-neon-green hover:bg-green-400 focus:ring-4 focus:outline-none focus:ring-green-300 font-medium rounded-lg text-sm px-4 py-2 text-center transition-colors shadow-[0_0_15px_rgba(57,255,20,0.3)]">
                  Get Started
                </Link>
             </div>
          )}
        </div>
        <div className="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-sticky">
          <ul className="flex flex-col p-4 md:p-0 mt-4 font-medium border border-white/10 rounded-lg bg-white/5 md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-transparent">
            <li>
              <Link to="/" className="block py-2 px-3 text-white rounded hover:bg-white/10 md:hover:bg-transparent md:hover:text-neon-green md:p-0 transition-colors">Home</Link>
            </li>
            <li>
              <Link to="/about" className="block py-2 px-3 text-white rounded hover:bg-white/10 md:hover:bg-transparent md:hover:text-neon-green md:p-0 transition-colors">About</Link>
            </li>
            <li>
              <Link to="/insights" className="block py-2 px-3 text-white rounded hover:bg-white/10 md:hover:bg-transparent md:hover:text-neon-green md:p-0 transition-colors">Data Insights</Link>
            </li>
            <li>
              <Link to="/sectors" className="block py-2 px-3 text-white rounded hover:bg-white/10 md:hover:bg-transparent md:hover:text-neon-green md:p-0 transition-colors">Sector Analytics</Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
