// Simple logger for frontend requests and events

const getTimestamp = () => new Date().toLocaleTimeString('ca-ES');

export const logger = {
  // Request logging
  request: (method: string, endpoint: string, data?: any) => {
    const timestamp = getTimestamp();
    const methodStyle = method === 'GET' ? 'color: #3b82f6' : method === 'POST' ? 'color: #06b6d4' : 'color: #f59e0b';
    
    console.log(
      `%c[${timestamp}]%c ${method} %c${endpoint}`,
      'color: #6b7280; font-size: 11px;',
      `${methodStyle}; font-weight: bold;`,
      'color: #6b7280;'
    );
    
    if (data) {
      console.log('%cPayload:', 'color: #6b7280; font-weight: bold;', data);
    }
  },

  // Response logging
  response: (method: string, endpoint: string, status: number, time: number) => {
    const timestamp = getTimestamp();
    const statusStyle = status >= 200 && status < 300 ? 'color: #10b981' : status >= 400 ? 'color: #ef4444' : 'color: #f59e0b';
    const methodStyle = method === 'GET' ? 'color: #3b82f6' : method === 'POST' ? 'color: #06b6d4' : 'color: #f59e0b';
    
    console.log(
      `%c[${timestamp}]%c ${method} %c${endpoint} %c${status} %c(${time.toFixed(2)}ms)`,
      'color: #6b7280; font-size: 11px;',
      `${methodStyle}; font-weight: bold;`,
      'color: #6b7280;',
      `${statusStyle}; font-weight: bold;`,
      'color: #6b7280; font-size: 10px;'
    );
  },

  // Error logging
  error: (message: string, error?: any) => {
    const timestamp = getTimestamp();
    console.error(
      `%c[${timestamp}]%c [ERROR] %c${message}`,
      'color: #6b7280; font-size: 11px;',
      'color: #ef4444; font-weight: bold;',
      'color: #ef4444;',
      error || ''
    );
  },

  // Info logging
  info: (message: string, data?: any) => {
    const timestamp = getTimestamp();
    console.log(
      `%c[${timestamp}]%c [INFO] %c${message}`,
      'color: #6b7280; font-size: 11px;',
      'color: #3b82f6; font-weight: bold;',
      'color: #3b82f6;',
      data || ''
    );
  },

  // Success logging
  success: (message: string, data?: any) => {
    const timestamp = getTimestamp();
    console.log(
      `%c[${timestamp}]%c [SUCCESS] %c${message}`,
      'color: #6b7280; font-size: 11px;',
      'color: #10b981; font-weight: bold;',
      'color: #10b981;',
      data || ''
    );
  },

  // Warning logging
  warning: (message: string, data?: any) => {
    const timestamp = getTimestamp();
    console.warn(
      `%c[${timestamp}]%c [WARNING] %c${message}`,
      'color: #6b7280; font-size: 11px;',
      'color: #f59e0b; font-weight: bold;',
      'color: #f59e0b;',
      data || ''
    );
  },
};
