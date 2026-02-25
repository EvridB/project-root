import React, { useState } from 'react';
import { api } from '../api/client';

interface Props {
  onRequestCreated: () => void;
  onClose: () => void;
}

const CreateRequestForm: React.FC<Props> = ({ onRequestCreated, onClose }) => {
  const [clientName, setClientName] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [problemText, setProblemText] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/requests', { clientName, phone, address, problemText });
      onRequestCreated();
      onClose();
    } catch (err) {
      alert('Ошибка при создании заявки');
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex', justifyContent: 'center', alignItems: 'center'
    }}>
      <form onSubmit={handleSubmit} style={{ background: 'white', padding: 20, borderRadius: 8, width: 400 }}>
        <h3>Создать заявку</h3>
        <div style={{ marginBottom: 10 }}>
          <label>Клиент *</label>
          <input
            type="text"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            required
            style={{ width: '100%', padding: 8 }}
          />
        </div>
        <div style={{ marginBottom: 10 }}>
          <label>Телефон *</label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            style={{ width: '100%', padding: 8 }}
          />
        </div>
        <div style={{ marginBottom: 10 }}>
          <label>Адрес *</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            required
            style={{ width: '100%', padding: 8 }}
          />
        </div>
        <div style={{ marginBottom: 10 }}>
          <label>Описание проблемы *</label>
          <textarea
            value={problemText}
            onChange={(e) => setProblemText(e.target.value)}
            required
            style={{ width: '100%', padding: 8 }}
            rows={4}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
          <button type="button" onClick={onClose}>Отмена</button>
          <button type="submit">Создать</button>
        </div>
      </form>
    </div>
  );
};

export default CreateRequestForm;