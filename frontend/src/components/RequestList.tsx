import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Request, User } from '../types';
import CreateRequestForm from './CreateRequestForm';

interface Props {
  user: User;
}

const statusColors: Record<string, string> = {
  new: 'blue',
  assigned: 'orange',
  in_progress: 'gold',
  done: 'green',
  canceled: 'red',
};

const RequestList: React.FC<Props> = ({ user }) => {
  const [requests, setRequests] = useState<Request[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [masters, setMasters] = useState<User[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const fetchRequests = async () => {
    try {
      const params = filterStatus ? { status: filterStatus } : {};
      const res = await api.get<Request[]>('/requests', { params });
      setRequests(res.data);
    } catch (err) {
      console.error('Failed to fetch requests', err);
    }
  };

  useEffect(() => {
    if (user.role === 'dispatcher') {
      api.get<User[]>('/users?role=master')
        .then(res => setMasters(res.data))
        .catch(err => console.error('Failed to load masters', err));
    }
  }, [user]);

  useEffect(() => {
    fetchRequests();
  }, [filterStatus, user]);

  const handleAssign = async (requestId: number, masterId: number) => {
    try {
      await api.patch(`/requests/${requestId}/assign?master_id=${masterId}`);
      fetchRequests();
    } catch (err) {
      alert('Не удалось назначить мастера');
    }
  };

  const handleCancel = async (requestId: number) => {
    try {
      await api.patch(`/requests/${requestId}/cancel`);
      fetchRequests();
    } catch (err) {
      alert('Не удалось отменить заявку');
    }
  };

  const handleTake = async (requestId: number) => {
    try {
      await api.patch(`/requests/${requestId}/take`);
      fetchRequests();
    } catch (err: any) {
      if (err.response?.status === 409) {
        alert('Заявка уже взята другим мастером');
      } else {
        alert('Ошибка');
      }
    }
  };

  const handleComplete = async (requestId: number) => {
    try {
      await api.patch(`/requests/${requestId}/complete`);
      fetchRequests();
    } catch (err) {
      alert('Не удалось завершить заявку');
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <label>Фильтр по статусу: </label>
          <select
            value={filterStatus}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFilterStatus(e.target.value)}
          >
            <option value="">Все</option>
            <option value="new">Новые</option>
            <option value="assigned">Назначенные</option>
            <option value="in_progress">В работе</option>
            <option value="done">Выполненные</option>
            <option value="canceled">Отменённые</option>
          </select>
        </div>
        {user.role === 'dispatcher' && (
          <button onClick={() => setShowCreateForm(true)} style={{ padding: '8px 16px' }}>
            Создать заявку
          </button>
        )}
      </div>

      <table border={1} cellPadding={8} style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Клиент</th>
            <th>Телефон</th>
            <th>Адрес</th>
            <th>Проблема</th>
            <th>Статус</th>
            <th>Мастер</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {requests.map(req => (
            <tr key={req.id}>
              <td>{req.id}</td>
              <td>{req.clientName}</td>
              <td>{req.phone}</td>
              <td>{req.address}</td>
              <td>{req.problemText}</td>
              <td style={{ color: statusColors[req.status] }}>{req.status}</td>
              <td>
                {req.assignedTo ? masters.find(m => m.id === req.assignedTo)?.name : '-'}
              </td>
              <td>
                {user.role === 'dispatcher' && (req.status === 'new' || req.status === 'assigned') && (
                  <>
                    <select
                      onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                        handleAssign(req.id, Number(e.target.value))
                      }
                      defaultValue=""
                    >
                      <option value="" disabled>
                        Назначить мастера
                      </option>
                      {masters.map(m => (
                        <option key={m.id} value={m.id}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                    <button onClick={() => handleCancel(req.id)}>Отменить</button>
                  </>
                )}
                {user.role === 'master' &&
                  req.assignedTo === user.id &&
                  req.status === 'assigned' && (
                    <button onClick={() => handleTake(req.id)}>Взять в работу</button>
                  )}
                {user.role === 'master' &&
                  req.assignedTo === user.id &&
                  req.status === 'in_progress' && (
                    <button onClick={() => handleComplete(req.id)}>Завершить</button>
                  )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showCreateForm && (
        <CreateRequestForm
          onRequestCreated={fetchRequests}
          onClose={() => setShowCreateForm(false)}
        />
      )}
    </div>
  );
};

export default RequestList;