import React, { useState } from 'react';
import { api } from '../api/client';
import { User } from '../types';

interface Props {
  onLogin: (user: User) => void;
}

const users = ['dispatcher', 'master1', 'master2'];

const Login: React.FC<Props> = ({ onLogin }) => {
  const [selected, setSelected] = useState(users[0]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const res = await api.post<{ user: User }>('/auth/login', { name: selected });
      onLogin(res.data.user);
    } catch (err) {
      alert('Ошибка входа');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: '100px auto' }}>
      <h2>Вход в систему</h2>
      <select
        value={selected}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelected(e.target.value)}
        style={{ width: '100%', padding: 8 }}
      >
        {users.map(name => (
          <option key={name} value={name}>
            {name}
          </option>
        ))}
      </select>
      <button type="submit" style={{ marginTop: 16, width: '100%', padding: 8 }}>
        Войти
      </button>
    </form>
  );
};

export default Login;