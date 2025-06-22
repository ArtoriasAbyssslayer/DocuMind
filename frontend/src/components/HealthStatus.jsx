import React, { useEffect, useState } from 'react';

function HealthStatus() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/health/')
      .then(res => res.json())
      .then(setStatus)
      .catch(() => setStatus({ status: 'error' }));
  }, []);

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Health Status</h2>
      {status ? (
        <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(status, null, 2)}</pre>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default HealthStatus;