import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Leaf } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { formatApiError } from '../api/api';

export const AuthContainer = ({ title, subtitle, children }) => (
  <div className="min-h-screen bg-deep-blue flex flex-col justify-center items-center p-4">
    <Link to="/" className="flex items-center mb-8 group">
      <Leaf className="h-8 w-8 text-neon-green mr-2 group-hover:rotate-12 transition-transform" />
      <span className="text-3xl font-bold text-white">
        Carbon<span className="text-neon-green">AI</span>
      </span>
    </Link>
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card p-8 md:p-12 w-full max-w-md relative overflow-hidden"
    >
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-neon-green to-blue-500" />
      <h2 className="text-2xl font-bold text-white mb-2">{title}</h2>
      <p className="text-blue-200/70 mb-8">{subtitle}</p>
      {children}
    </motion.div>
  </div>
);

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(formatApiError(err, 'Invalid email or password'));
    }
  };

  return (
    <AuthContainer title="Welcome Back" subtitle="Log in to access your dashboard.">
      <form onSubmit={handleLogin} className="space-y-6">
        {error && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm">
            {error}
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-blue-100 mb-2">
            Email
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-green"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-100 mb-2">
            Password
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-green"
          />
        </div>
        <button
          type="submit"
          className="w-full py-3 bg-neon-green text-deep-blue font-bold rounded-lg hover:bg-green-400 transition-colors"
        >
          Sign In
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-blue-200/70">
        Don't have an account?{' '}
        <Link to="/register" className="text-neon-green hover:underline">
          Register
        </Link>
      </p>
    </AuthContainer>
  );
};

export const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await register(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(formatApiError(err, 'Registration failed'));
    }
  };

  return (
    <AuthContainer
      title="Create Account"
      subtitle="Start predicting your emissions today."
    >
      <form onSubmit={handleRegister} className="space-y-6">
        {error && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm">
            {error}
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-blue-100 mb-2">
            Email
          </label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-green"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-blue-100 mb-2">
            Password
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-green"
          />
        </div>
        <button
          type="submit"
          className="w-full py-3 bg-white text-deep-blue font-bold rounded-lg hover:bg-gray-200 transition-colors"
        >
          Create Free Account
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-blue-200/70">
        Already have an account?{' '}
        <Link to="/login" className="text-neon-green hover:underline">
          Log in
        </Link>
      </p>
    </AuthContainer>
  );
};