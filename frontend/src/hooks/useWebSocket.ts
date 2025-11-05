import { useEffect, useRef, useState } from 'react';
import { createWebSocketConnection } from '../services/api';

interface WebSocketUpdate {
  job_id: string;
  status: string;
  progress: number;
  current_step?: string;
  completed_steps: number;
  total_steps: number;
  error_message?: string;
}

interface UseWebSocketOptions {
  onUpdate?: (update: WebSocketUpdate) => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export const useWebSocket = (jobId: string, options: UseWebSocketOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<WebSocketUpdate | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = options.reconnectAttempts || 5;
  const reconnectInterval = options.reconnectInterval || 3000;

  const connect = () => {
    try {
      ws.current = createWebSocketConnection(jobId);

      ws.current.onopen = () => {
        console.log(`WebSocket connected for job ${jobId}`);
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const update: WebSocketUpdate = JSON.parse(event.data);
          console.log(`WebSocket update for job ${jobId}:`, update);

          setLastUpdate(update);
          options.onUpdate?.(update);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log(`WebSocket disconnected for job ${jobId}:`, event.code, event.reason);
        setIsConnected(false);

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.current++;
            console.log(`Attempting to reconnect WebSocket for job ${jobId} (attempt ${reconnectAttempts.current})`);
            connect();
          }, reconnectInterval);
        }
      };

      ws.current.onerror = (error) => {
        console.error(`WebSocket error for job ${jobId}:`, error);
        setConnectionError('WebSocket connection error');
        options.onError?.(error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionError('Failed to establish WebSocket connection');
    }
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect');
      ws.current = null;
    }
  };

  const sendMessage = (message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  };

  useEffect(() => {
    if (jobId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [jobId]);

  return {
    isConnected,
    lastUpdate,
    connectionError,
    sendMessage,
    disconnect
  };
};

export default useWebSocket;